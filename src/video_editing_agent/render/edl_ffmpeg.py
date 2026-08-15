from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path
from typing import Any

from video_editing_agent.application.ports.executor import DeterministicToolInvocation
from video_editing_agent.application.ports.renderer import (
    RenderArtifact,
    RenderDiagnostic,
    RenderDiagnosticCode,
    Renderer,
    RenderRequest,
    RenderResult,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.edl.automation import (
    EDLAudioAutomationKind,
    EDLInterpolation,
    EDLSpatialAutomation,
    ExactRational,
)
from video_editing_agent.domain.edl.model import EDL, EDLSegment, EDLTrackFamily
from video_editing_agent.domain.edl.subtitle import (
    EDLSubtitleCue,
    SubtitleEmphasisStyle,
    SubtitleLayoutRegion,
)
from video_editing_agent.domain.edl.validation import validate_edl


@dataclass(frozen=True, slots=True)
class FFmpegRenderPlan:
    invocation: DeterministicToolInvocation
    expected_duration: MediaTime
    expects_audio: bool
    subtitle_artifact_path: Path | None = None
    subtitle_artifact_content: str | None = None


@dataclass(frozen=True, slots=True)
class FFmpegCompilationResult:
    plan: FFmpegRenderPlan | None
    diagnostics: tuple[RenderDiagnostic, ...]


def _seconds(value: MediaTime) -> str:
    return value.to_decimal_seconds_string(fractional_digits=9)


def _fraction(value: Fraction) -> str:
    return (
        str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    )


def _diagnostic(
    code: RenderDiagnosticCode, message: str, segments: tuple[str, ...] = ()
) -> FFmpegCompilationResult:
    return FFmpegCompilationResult(None, (RenderDiagnostic(code, message, segments),))


def _contiguous(segments: tuple[EDLSegment, ...]) -> bool:
    cursor = MediaTime(0, 1)
    for segment in segments:
        if segment.timeline_range.start != cursor:
            return False
        cursor = segment.timeline_range.end
    return bool(segments)


def _ass_time(value: MediaTime) -> str:
    centiseconds = round(value.as_fraction() * 100)
    hours, remainder = divmod(centiseconds, 360_000)
    minutes, remainder = divmod(remainder, 6_000)
    seconds, fraction = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{seconds:02d}.{fraction:02d}"


def _ass_text(value: str) -> str:
    return (
        value.replace("\\", r"\\")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("\r\n", r"\N")
        .replace("\r", r"\N")
        .replace("\n", r"\N")
    )


def _ass_cue_text(cue: EDLSubtitleCue) -> str:
    cursor = 0
    pieces: list[str] = []
    for span in cue.emphasis:
        pieces.append(_ass_text(cue.text[cursor : span.start]))
        if span.style is SubtitleEmphasisStyle.BOLD:
            pieces.extend((r"{\b1}", _ass_text(cue.text[span.start : span.end]), r"{\b0}"))
        else:
            pieces.extend(
                (
                    r"{\c&H00FFFF&}",
                    _ass_text(cue.text[span.start : span.end]),
                    r"{\c&HFFFFFF&}",
                )
            )
        cursor = span.end
    pieces.append(_ass_text(cue.text[cursor:]))
    alignment = "8" if cue.layout is SubtitleLayoutRegion.UPPER_SAFE else "2"
    return rf"{{\an{alignment}}}" + "".join(pieces)


def build_ass_subtitles(edl: EDL, width: int, height: int) -> str:
    cues = edl.ordered_subtitle_cues
    font_size = max(18, (height * 6 + 50) // 100)
    margin = max(12, (height * 8 + 50) // 100)
    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {width}\nPlayResY: {height}\n"
        "WrapStyle: 0\nScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, "
        "ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding\n"
        f"Style: Default,Arial,{font_size},&H00FFFFFF,&H0000FFFF,&H00000000,"
        f"&H64000000,0,0,0,0,100,100,0,0,1,2,1,2,{margin},{margin},{margin},1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    events = "".join(
        "Dialogue: 0,"
        f"{_ass_time(cue.timeline_range.start)},{_ass_time(cue.timeline_range.end)},"
        f"Default,,0,0,0,,{_ass_cue_text(cue)}\n"
        for cue in cues
    )
    return header + events


def _ffmpeg_filter_path(path: Path) -> str:
    value = path.resolve(strict=False).as_posix()
    for character in ("\\", ":", ",", "[", "]", ";"):
        value = value.replace(character, "\\" + character)
    return value.replace("'", r"\\\'")


def _subtitle_artifact_path(request: RenderRequest) -> Path:
    identity = (
        "".join(
            character if character.isascii() and character.isalnum() else "-"
            for character in request.edl.envelope.id
        ).strip("-")
        or "edl"
    )
    spec = request.output_spec
    name = f".{identity}.r{request.edl.envelope.revision}.{spec.width}x{spec.height}.subtitles.ass"
    return spec.path.parent / name


def _hold_expression(automation: EDLSpatialAutomation, attribute: str, start: MediaTime) -> str:
    first, *remaining = automation.keyframes
    expression = str(getattr(first, attribute))
    current = getattr(first, attribute)
    for keyframe in remaining:
        value = getattr(keyframe, attribute)
        if value != current:
            relative = (keyframe.timeline_time - start).as_fraction()
            expression = f"if(gte(t\\,{_fraction(relative)})\\,{value}\\,{expression})"
            current = value
    return expression


def _linear_expression(automation: EDLSpatialAutomation, attribute: str, start: MediaTime) -> str:
    frames = automation.keyframes
    if len(frames) == 1:
        return str(getattr(frames[0], attribute))
    times = tuple((item.timeline_time - start).as_fraction() for item in frames)
    values = tuple(getattr(item, attribute) for item in frames)
    slopes = tuple(
        Fraction(right_value - left_value, 1) / (right_time - left_time)
        for left_value, right_value, left_time, right_time in zip(
            values[:-1], values[1:], times[:-1], times[1:], strict=True
        )
    )
    terms = [str(values[0])]
    previous = Fraction(0)
    for time, slope in zip(times[:-1], slopes, strict=True):
        change = slope - previous
        if change:
            terms.append(f"+({_fraction(change)})*max(t-{_fraction(time)}\\,0)")
        previous = slope
    if previous:
        terms.append(f"+({_fraction(-previous)})*max(t-{_fraction(times[-1])}\\,0)")
    return f"floor({''.join(terms)}+0.5)"


def _video_filter(segment: EDLSegment, width: int, height: int) -> str | None:
    prefix = (
        f"trim=start={_seconds(segment.source_range.start)}:"
        f"duration={_seconds(segment.source_range.duration)},setpts=PTS-STARTPTS"
    )
    automation = segment.spatial_automation
    if automation is None:
        return f"{prefix},scale={width}:{height}:flags=lanczos"
    first = automation.keyframes[0]
    if any(
        item.crop_width != first.crop_width or item.crop_height != first.crop_height
        for item in automation.keyframes
    ):
        return None
    if any(
        item.scale != ExactRational(1)
        or item.position_x != ExactRational(0)
        or item.position_y != ExactRational(0)
        for item in automation.keyframes
    ):
        return None
    if automation.interpolation is EDLInterpolation.HOLD:
        expression = _hold_expression
    elif automation.interpolation is EDLInterpolation.LINEAR:
        expression = _linear_expression
    else:
        return None
    left = expression(automation, "crop_left", segment.timeline_range.start)
    top = expression(automation, "crop_top", segment.timeline_range.start)
    return (
        f"{prefix},crop={first.crop_width}:{first.crop_height}:{left}:{top},"
        f"scale={width}:{height}:flags=lanczos"
    )


def _db(millibels: int) -> str:
    value = Decimal(millibels) / Decimal(100)
    return f"{format(value.normalize(), 'f')}dB"


def _relative(value: MediaTime, segment: EDLSegment) -> str:
    return _seconds(value - segment.timeline_range.start)


def _audio_filters(segment: EDLSegment) -> tuple[str, ...] | None:
    filters: list[str] = []
    base_gains = tuple(
        item for item in segment.audio_automations if item.kind is EDLAudioAutomationKind.GAIN
    )
    base_gain = None
    if base_gains:
        if len(base_gains) != 1:
            return None
        points = base_gains[0].keyframes
        if len(points) != 2 or points[0].gain_millibels != points[1].gain_millibels:
            return None
        base_gain = points[0].gain_millibels
    for automation in segment.audio_automations:
        points = automation.keyframes
        if automation.kind is EDLAudioAutomationKind.GAIN:
            assert base_gain is not None
            filters.append(f"volume={_db(base_gain)}")
        elif automation.kind is EDLAudioAutomationKind.DUCK:
            if (
                base_gain is None
                or len(points) != 2
                or points[0].gain_millibels != points[1].gain_millibels
            ):
                return None
            delta = points[0].gain_millibels - base_gain
            start = _relative(points[0].timeline_time, segment)
            end = _relative(points[1].timeline_time, segment)
            filters.append(f"volume={_db(delta)}:enable='between(t,{start},{end})'")
        elif automation.kind is EDLAudioAutomationKind.FADE:
            if len(points) != 2 or points[0].gain_millibels != points[1].gain_millibels:
                return None
            if points[0].muted and not points[1].muted:
                direction = "in"
            elif not points[0].muted and points[1].muted:
                direction = "out"
            else:
                return None
            start = _relative(points[0].timeline_time, segment)
            duration = _seconds(points[1].timeline_time - points[0].timeline_time)
            filters.append(f"afade=t={direction}:st={start}:d={duration}")
        elif automation.kind is EDLAudioAutomationKind.MUTE:
            if len(points) != 2:
                return None
            start = _relative(points[0].timeline_time, segment)
            end = _relative(points[1].timeline_time, segment)
            filters.append(f"volume=0:enable='between(t,{start},{end})'")
        else:
            return None
    return tuple(filters)


def compile_ffmpeg_render(
    request: RenderRequest, *, ffmpeg_executable: str = "ffmpeg"
) -> FFmpegCompilationResult:
    validation = validate_edl(request.edl)
    if not validation.is_valid:
        return _diagnostic(
            RenderDiagnosticCode.INVALID_EDL,
            "canonical EDL validation failed: "
            + ",".join(item.code.value for item in validation.diagnostics),
        )
    spec = request.output_spec
    if (
        spec.container != "mp4"
        or spec.video_codec != "libx264"
        or spec.audio_codec != "aac"
        or spec.path.suffix.casefold() != ".mp4"
    ):
        return _diagnostic(
            RenderDiagnosticCode.UNSUPPORTED_OUTPUT,
            "Stage-A supports only explicit libx264/AAC MP4 output",
        )
    supported = {
        EDLTrackFamily.VIDEO,
        EDLTrackFamily.SOURCE_AUDIO,
        EDLTrackFamily.BGM,
        EDLTrackFamily.SUBTITLE,
    }
    unsupported = tuple(
        track.track_id for track in request.edl.effective_tracks if track.family not in supported
    )
    if unsupported:
        return _diagnostic(
            RenderDiagnosticCode.UNSUPPORTED_TRACK,
            "Stage-A Renderer received unsupported track families",
            unsupported,
        )

    media: dict[EntityRevisionRef, Path] = {}
    duplicates: set[EntityRevisionRef] = set()
    for item in request.asset_media:
        if item.asset_ref in media:
            duplicates.add(item.asset_ref)
        media[item.asset_ref] = item.path
    if duplicates:
        return _diagnostic(
            RenderDiagnosticCode.AMBIGUOUS_ASSET_MEDIA,
            "multiple local media bindings exist for one exact Asset revision",
        )
    referenced = {segment.asset_ref for segment in request.edl.segments}
    missing = tuple(
        sorted(
            (ref for ref in referenced if ref not in media or not media[ref].is_file()),
            key=lambda ref: (ref.entity_id, ref.revision),
        )
    )
    if missing:
        return _diagnostic(
            RenderDiagnosticCode.MISSING_ASSET_MEDIA,
            "canonical EDL Asset revisions are not resolved to existing local media",
        )
    if any(
        path.resolve(strict=False) == spec.path.resolve(strict=False) for path in media.values()
    ):
        return _diagnostic(
            RenderDiagnosticCode.OUTPUT_CONFLICT,
            "output path must not overwrite canonical source media",
        )
    ordered_refs = tuple(sorted(referenced, key=lambda ref: (ref.entity_id, ref.revision)))
    input_index = {ref: index for index, ref in enumerate(ordered_refs)}

    videos = tuple(
        sorted(
            (item for item in request.edl.segments if item.track_id == "video"),
            key=lambda item: (item.timeline_range.start.as_fraction(), item.segment_id),
        )
    )
    if not _contiguous(videos):
        return _diagnostic(
            RenderDiagnosticCode.TIMELINE_NOT_CONTIGUOUS,
            "VIDEO segments must cover one contiguous timeline beginning at zero",
            tuple(item.segment_id for item in videos),
        )
    expected_duration = videos[-1].timeline_range.end
    graph: list[str] = []
    video_labels: list[str] = []
    for index, segment in enumerate(videos):
        compiled = _video_filter(segment, spec.width, spec.height)
        if compiled is None:
            return _diagnostic(
                RenderDiagnosticCode.UNSUPPORTED_AUTOMATION,
                "spatial automation cannot be represented by the Stage-A FFmpeg adapter",
                (segment.segment_id,),
            )
        label = f"v{index}"
        graph.append(f"[{input_index[segment.asset_ref]}:v:0]{compiled}[{label}]")
        video_labels.append(f"[{label}]")
    subtitle_path: Path | None = None
    subtitle_content: str | None = None
    video_output = "vbase" if request.edl.subtitle_cues else "vout"
    graph.append(
        f"{''.join(video_labels)}concat=n={len(video_labels)}:v=1:a=0,"
        f"fps={spec.frames_per_second}[{video_output}]"
    )
    if request.edl.subtitle_cues:
        subtitle_path = _subtitle_artifact_path(request)
        subtitle_content = build_ass_subtitles(request.edl, spec.width, spec.height)
        escaped_path = _ffmpeg_filter_path(subtitle_path)
        graph.append(f"[vbase]subtitles=filename='{escaped_path}'[vout]")

    audio_track_segments: list[tuple[str, tuple[EDLSegment, ...]]] = []
    for track_id in ("source_audio", "bgm"):
        track_segments = tuple(
            sorted(
                (item for item in request.edl.segments if item.track_id == track_id),
                key=lambda item: (item.timeline_range.start.as_fraction(), item.segment_id),
            )
        )
        if track_segments:
            if (
                not _contiguous(track_segments)
                or track_segments[-1].timeline_range.end != expected_duration
            ):
                return _diagnostic(
                    RenderDiagnosticCode.TIMELINE_NOT_CONTIGUOUS,
                    f"{track_id} must exactly cover the current VIDEO timeline",
                    tuple(item.segment_id for item in track_segments),
                )
            audio_track_segments.append((track_id, track_segments))

    audio_outputs: list[str] = []
    for track_id, track_segments in audio_track_segments:
        labels: list[str] = []
        for index, segment in enumerate(track_segments):
            filters = _audio_filters(segment)
            if filters is None:
                return _diagnostic(
                    RenderDiagnosticCode.UNSUPPORTED_AUTOMATION,
                    "audio automation cannot be represented without guessing",
                    (segment.segment_id,),
                )
            chain = (
                f"atrim=start={_seconds(segment.source_range.start)}:"
                f"duration={_seconds(segment.source_range.duration)},asetpts=PTS-STARTPTS"
            )
            if filters:
                chain += "," + ",".join(filters)
            label = f"{track_id}{index}"
            graph.append(f"[{input_index[segment.asset_ref]}:a:0]{chain}[{label}]")
            labels.append(f"[{label}]")
        output = f"{track_id}out"
        graph.append(f"{''.join(labels)}concat=n={len(labels)}:v=0:a=1[{output}]")
        audio_outputs.append(f"[{output}]")
    if len(audio_outputs) == 2:
        graph.append(f"{''.join(audio_outputs)}amix=inputs=2:duration=first:normalize=0[aout]")
    elif len(audio_outputs) == 1:
        graph.append(f"{audio_outputs[0]}anull[aout]")

    arguments = ["-hide_banner", "-loglevel", "error", "-nostdin", "-y"]
    for ref in ordered_refs:
        arguments.extend(("-i", str(media[ref])))
    arguments.extend(("-filter_complex", ";".join(graph), "-map", "[vout]"))
    if audio_outputs:
        arguments.extend(("-map", "[aout]"))
    arguments.extend(
        (
            "-c:v",
            spec.video_codec,
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(spec.frames_per_second),
        )
    )
    if audio_outputs:
        arguments.extend(("-c:a", spec.audio_codec))
    arguments.extend(("-movflags", "+faststart", str(spec.path)))
    invocation = DeterministicToolInvocation(
        f"render:{request.edl.envelope.id}@{request.edl.envelope.revision}",
        ffmpeg_executable,
        tuple(arguments),
        tuple(f"{ref.entity_id}@{ref.revision}" for ref in ordered_refs),
        (str(spec.path),),
    )
    return FFmpegCompilationResult(
        FFmpegRenderPlan(
            invocation,
            expected_duration,
            bool(audio_outputs),
            subtitle_path,
            subtitle_content,
        ),
        (),
    )


def _ffprobe_invocation(path: Path, ffprobe_executable: str) -> DeterministicToolInvocation:
    return DeterministicToolInvocation(
        f"verify:{path.name}",
        ffprobe_executable,
        (
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,width,height,r_frame_rate",
            "-of",
            "json",
            str(path),
        ),
        (str(path),),
    )


def _run(invocation: DeterministicToolInvocation) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [invocation.tool_id, *invocation.arguments],
        check=False,
        capture_output=True,
        text=True,
        shell=False,
    )


def _verified(content: str, request: RenderRequest, plan: FFmpegRenderPlan) -> bool:
    try:
        root: dict[str, Any] = json.loads(content)
        streams = root["streams"]
        video = next(item for item in streams if item.get("codec_type") == "video")
        audio_present = any(item.get("codec_type") == "audio" for item in streams)
        frame_rate = Fraction(video["r_frame_rate"])
        duration = Decimal(root["format"]["duration"])
    except (InvalidOperation, KeyError, StopIteration, TypeError, ValueError, ZeroDivisionError):
        return False
    expected = Decimal(plan.expected_duration.value) / Decimal(plan.expected_duration.scale)
    tolerance = Decimal(1) / Decimal(request.output_spec.frames_per_second)
    return (
        video.get("width") == request.output_spec.width
        and video.get("height") == request.output_spec.height
        and frame_rate == request.output_spec.frames_per_second
        and audio_present is plan.expects_audio
        and abs(duration - expected) <= tolerance
    )


class FFmpegEDLRenderer(Renderer):
    def __init__(self, ffmpeg_executable: str = "ffmpeg", ffprobe_executable: str = "ffprobe"):
        self._ffmpeg = ffmpeg_executable
        self._ffprobe = ffprobe_executable

    def render(self, request: RenderRequest) -> RenderResult:
        compilation = compile_ffmpeg_render(request, ffmpeg_executable=self._ffmpeg)
        if compilation.plan is None:
            return RenderResult(None, compilation.diagnostics)
        plan = compilation.plan
        request.output_spec.path.parent.mkdir(parents=True, exist_ok=True)
        if plan.subtitle_artifact_path is not None:
            assert plan.subtitle_artifact_content is not None
            plan.subtitle_artifact_path.write_text(
                plan.subtitle_artifact_content, encoding="utf-8", newline="\n"
            )
        try:
            completed = _run(plan.invocation)
        except OSError as exc:
            return RenderResult(
                None,
                (RenderDiagnostic(RenderDiagnosticCode.EXECUTION_FAILED, str(exc)),),
            )
        if completed.returncode != 0:
            return RenderResult(
                None,
                (
                    RenderDiagnostic(
                        RenderDiagnosticCode.EXECUTION_FAILED,
                        completed.stderr.strip() or "FFmpeg render failed",
                    ),
                ),
            )
        probe = _ffprobe_invocation(request.output_spec.path, self._ffprobe)
        try:
            verified = _run(probe)
        except OSError as exc:
            return RenderResult(
                None,
                (RenderDiagnostic(RenderDiagnosticCode.OUTPUT_VERIFICATION_FAILED, str(exc)),),
            )
        if verified.returncode != 0 or not _verified(verified.stdout, request, plan):
            return RenderResult(
                None,
                (
                    RenderDiagnostic(
                        RenderDiagnosticCode.OUTPUT_VERIFICATION_FAILED,
                        verified.stderr.strip() or "ffprobe output did not match canonical EDL",
                    ),
                ),
            )
        artifact = RenderArtifact(
            request.output_spec.path,
            EntityRevisionRef(request.edl.envelope.id, request.edl.envelope.revision),
            request.output_spec,
            plan.invocation,
            probe,
        )
        return RenderResult(artifact, ())

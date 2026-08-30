from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.application.ports.asset_media import ResolvedLocalAssetMedia
from video_editing_agent.application.ports.renderer import (
    OutputSpec,
    RenderDiagnosticCode,
    RenderRequest,
)
from video_editing_agent.domain.common.entity import (
    EntityEnvelope,
    EntityRevisionRef,
    EntityStatus,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edl import (
    EDL,
    EDLAudioAutomation,
    EDLAudioAutomationKind,
    EDLAudioKeyframe,
    EDLInterpolation,
    EDLSegment,
    EDLSpatialAutomation,
    EDLSpatialKeyframe,
    EDLTrack,
    EDLTrackFamily,
    ExactRational,
)
from video_editing_agent.render.edl_ffmpeg import compile_ffmpeg_render


def _envelope() -> EntityEnvelope:
    return EntityEnvelope(
        "edl-render",
        1,
        "0.2",
        EntityStatus.VALID,
        datetime(2026, 8, 16, tzinfo=UTC),
        "test",
    )


def _files(tmp_path: Path) -> tuple[ResolvedLocalAssetMedia, ...]:
    first = tmp_path / "first.mp4"
    second = tmp_path / "second.mp4"
    first.touch()
    second.touch()
    return (
        ResolvedLocalAssetMedia(EntityRevisionRef("asset-b", 1), second),
        ResolvedLocalAssetMedia(EntityRevisionRef("asset-a", 1), first),
    )


def _edl(*, spatial: bool = True, source_audio: bool = False) -> EDL:
    automation = (
        EDLSpatialAutomation(
            EDLInterpolation.LINEAR,
            (
                EDLSpatialKeyframe(MediaTime(0, 1), MediaTime(1, 24), 0, 0, 108, 192),
                EDLSpatialKeyframe(MediaTime(1, 2), MediaTime(13, 24), 20, 0, 108, 192),
            ),
        )
        if spatial
        else None
    )
    video = (
        EDLSegment(
            "video-a",
            EntityRevisionRef("asset-a", 1),
            source_range=MediaTimeRange(MediaTime(1, 24), MediaTime(1, 1)),
            timeline_range=MediaTimeRange(MediaTime(0, 1), MediaTime(1, 1)),
            spatial_automation=automation,
        ),
        EDLSegment(
            "video-b",
            EntityRevisionRef("asset-b", 1),
            source_range=MediaTimeRange(MediaTime(2, 1), MediaTime(1, 1)),
            timeline_range=MediaTimeRange(MediaTime(1, 1), MediaTime(1, 1)),
        ),
    )
    source = tuple(
        EDLSegment(
            f"source-{index}",
            item.asset_ref,
            source_range=item.source_range,
            timeline_range=item.timeline_range,
            track_id="source_audio",
        )
        for index, item in enumerate(video)
    )
    return EDL(
        _envelope(),
        EntityRevisionRef("edit-plan", 1),
        (*video, *(source if source_audio else ())),
        (
            EDLTrack("video", EDLTrackFamily.VIDEO),
            *((EDLTrack("source_audio", EDLTrackFamily.SOURCE_AUDIO),) if source_audio else ()),
        ),
    )


def _request(tmp_path: Path, edl: EDL | None = None) -> RenderRequest:
    return RenderRequest(
        edl or _edl(),
        _files(tmp_path),
        OutputSpec(tmp_path / "output.mp4", 180, 320, 30),
    )


def test_compile_uses_exact_edl_ranges_order_and_spatial_automation(tmp_path: Path) -> None:
    result = compile_ffmpeg_render(_request(tmp_path))

    assert result.plan is not None and not result.diagnostics
    invocation = result.plan.invocation
    graph = invocation.arguments[invocation.arguments.index("-filter_complex") + 1]
    assert "trim=start=0.041666667:duration=1.000" in graph
    assert "trim=start=2.000:duration=1.000" in graph
    assert "crop=108:192:" in graph
    assert "max(t-1/2\\,0)" in graph
    assert "concat=n=2:v=1:a=0,fps=30[vout]" in graph
    assert invocation.arguments[-1].endswith("output.mp4")
    assert invocation.tool_id == "ffmpeg"


def test_compilation_is_independent_of_asset_binding_order(tmp_path: Path) -> None:
    request = _request(tmp_path)
    reversed_request = replace(request, asset_media=tuple(reversed(request.asset_media)))

    first = compile_ffmpeg_render(request)
    second = compile_ffmpeg_render(reversed_request)

    assert first == second


def test_source_audio_presence_changes_filter_and_mapping(tmp_path: Path) -> None:
    muted = compile_ffmpeg_render(_request(tmp_path, _edl(source_audio=False)))
    preserved = compile_ffmpeg_render(_request(tmp_path, _edl(source_audio=True)))

    assert muted.plan is not None and preserved.plan is not None
    assert not muted.plan.expects_audio and preserved.plan.expects_audio
    muted_graph = muted.plan.invocation.arguments[
        muted.plan.invocation.arguments.index("-filter_complex") + 1
    ]
    preserved_graph = preserved.plan.invocation.arguments[
        preserved.plan.invocation.arguments.index("-filter_complex") + 1
    ]
    assert "[aout]" not in muted_graph
    assert "source_audioout" in preserved_graph and "[aout]" in preserved_graph


def test_source_audio_duck_automation_is_executed_without_editorial_inference(
    tmp_path: Path,
) -> None:
    edl = _edl(source_audio=True)
    duck = EDLAudioAutomation(
        EDLAudioAutomationKind.DUCK,
        EDLInterpolation.LINEAR,
        (EDLAudioKeyframe(MediaTime(0, 1), -1200), EDLAudioKeyframe(MediaTime(1, 1), -1200)),
    )
    base = EDLAudioAutomation(
        EDLAudioAutomationKind.GAIN,
        EDLInterpolation.LINEAR,
        (EDLAudioKeyframe(MediaTime(0, 1), 0), EDLAudioKeyframe(MediaTime(1, 1), 0)),
    )
    segments = tuple(
        replace(item, audio_automations=(base, duck)) if item.segment_id == "source-0" else item
        for item in edl.segments
    )

    result = compile_ffmpeg_render(_request(tmp_path, replace(edl, segments=segments)))

    assert result.plan is not None and not result.diagnostics
    graph = result.plan.invocation.arguments[
        result.plan.invocation.arguments.index("-filter_complex") + 1
    ]
    assert "volume=0dB" in graph
    assert "volume=-12dB:enable='between(t,0.000,1.000)'" in graph


def test_gain_fade_and_duck_compile_from_typed_edl(tmp_path: Path) -> None:
    base = EDLAudioAutomation(
        EDLAudioAutomationKind.GAIN,
        EDLInterpolation.LINEAR,
        (EDLAudioKeyframe(MediaTime(0, 1), -1000), EDLAudioKeyframe(MediaTime(2, 1), -1000)),
    )
    duck = EDLAudioAutomation(
        EDLAudioAutomationKind.DUCK,
        EDLInterpolation.LINEAR,
        (EDLAudioKeyframe(MediaTime(1, 2), -2200), EDLAudioKeyframe(MediaTime(3, 2), -2200)),
    )
    fade = EDLAudioAutomation(
        EDLAudioAutomationKind.FADE,
        EDLInterpolation.LINEAR,
        (
            EDLAudioKeyframe(MediaTime(0, 1), -1000, muted=True),
            EDLAudioKeyframe(MediaTime(1, 2), -1000),
        ),
    )
    edl = _edl()
    bgm = EDLSegment(
        "bgm",
        EntityRevisionRef("asset-a", 1),
        source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(2, 1)),
        timeline_range=MediaTimeRange(MediaTime(0, 1), MediaTime(2, 1)),
        track_id="bgm",
        audio_automations=(base, fade, duck),
    )
    edl = replace(
        edl,
        segments=(*edl.segments, bgm),
        tracks=(*edl.tracks, EDLTrack("bgm", EDLTrackFamily.BGM)),
    )

    result = compile_ffmpeg_render(_request(tmp_path, edl))

    assert result.plan is not None
    graph = result.plan.invocation.arguments[
        result.plan.invocation.arguments.index("-filter_complex") + 1
    ]
    assert "volume=-10dB" in graph
    assert "afade=t=in:st=0.000:d=0.500" in graph
    assert "volume=-12dB:enable='between(t,0.500,1.500)'" in graph


@pytest.mark.parametrize(
    ("mutate", "code"),
    (
        ("missing", RenderDiagnosticCode.MISSING_ASSET_MEDIA),
        ("gap", RenderDiagnosticCode.TIMELINE_NOT_CONTIGUOUS),
        ("track", RenderDiagnosticCode.UNSUPPORTED_TRACK),
        ("spatial", RenderDiagnosticCode.UNSUPPORTED_AUTOMATION),
        ("output", RenderDiagnosticCode.OUTPUT_CONFLICT),
    ),
)
def test_unsupported_or_incomplete_execution_fails_closed(
    tmp_path: Path, mutate: str, code: RenderDiagnosticCode
) -> None:
    request = _request(tmp_path)
    if mutate == "missing":
        request = replace(request, asset_media=request.asset_media[:1])
    elif mutate == "gap":
        changed = replace(
            request.edl.segments[1],
            timeline_range=MediaTimeRange(MediaTime(3, 2), MediaTime(1, 1)),
        )
        request = replace(
            request, edl=replace(request.edl, segments=(request.edl.segments[0], changed))
        )
    elif mutate == "track":
        request = replace(
            request,
            edl=replace(
                request.edl,
                tracks=(*request.edl.tracks, EDLTrack("graphics", EDLTrackFamily.GRAPHICS)),
            ),
        )
    elif mutate == "spatial":
        segment = request.edl.segments[0]
        assert segment.spatial_automation is not None
        keyframe = replace(segment.spatial_automation.keyframes[0], position_x=ExactRational(1, 2))
        spatial = replace(
            segment.spatial_automation,
            keyframes=(keyframe, *segment.spatial_automation.keyframes[1:]),
        )
        request = replace(
            request,
            edl=replace(
                request.edl,
                segments=(replace(segment, spatial_automation=spatial), request.edl.segments[1]),
            ),
        )
    else:
        request = replace(
            request,
            output_spec=replace(request.output_spec, path=request.asset_media[0].path),
        )

    result = compile_ffmpeg_render(request)

    assert result.plan is None
    assert result.diagnostics[0].code is code


@pytest.mark.parametrize(
    ("suffix", "container", "video_codec", "audio_codec", "expects_faststart"),
    (
        (".mp4", "mp4", "libopenh264", "aac", True),
        (".mov", "mov", "libopenh264", "aac", True),
        (".mkv", "matroska", "libopenh264", "aac", False),
        (".webm", "webm", "libvpx-vp9", "libopus", False),
    ),
)
def test_supported_output_container_codec_pairs_compile(
    tmp_path: Path,
    suffix: str,
    container: str,
    video_codec: str,
    audio_codec: str,
    expects_faststart: bool,
) -> None:
    request = _request(tmp_path)
    request = replace(
        request,
        output_spec=OutputSpec(
            tmp_path / f"output{suffix}",
            180,
            320,
            30,
            container,
            video_codec,
            audio_codec,
        ),
    )

    result = compile_ffmpeg_render(request)

    assert result.plan is not None and not result.diagnostics
    arguments = result.plan.invocation.arguments
    assert arguments[-1].endswith(suffix)
    assert ("-movflags" in arguments) is expects_faststart
    assert arguments[arguments.index("-c:v") + 1] == video_codec
    if video_codec == "libopenh264":
        assert arguments[arguments.index("-b:v") + 1] == "1000000"
    else:
        assert "-b:v" not in arguments


def test_output_container_codec_extension_mismatch_fails_closed(tmp_path: Path) -> None:
    request = _request(tmp_path)
    request = replace(
        request,
        output_spec=OutputSpec(
            tmp_path / "output.webm",
            180,
            320,
            30,
            "mp4",
            "libopenh264",
            "aac",
        ),
    )

    result = compile_ffmpeg_render(request)

    assert result.plan is None
    assert result.diagnostics[0].code is RenderDiagnosticCode.UNSUPPORTED_OUTPUT

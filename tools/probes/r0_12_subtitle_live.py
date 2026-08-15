from __future__ import annotations

import json
import subprocess
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from video_editing_agent.application.ports.asset_media import ResolvedLocalAssetMedia
from video_editing_agent.application.ports.renderer import OutputSpec, RenderRequest
from video_editing_agent.application.subtitle_builder import compile_subtitle_cues
from video_editing_agent.domain.common.entity import (
    EntityEnvelope,
    EntityRevisionRef,
    EntityStatus,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edl import (
    EDL,
    EDLSegment,
    EDLTrack,
    EDLTrackFamily,
    StructuredSubtitleCue,
    SubtitleEmphasisSpan,
    SubtitleEmphasisStyle,
    SubtitleLayoutRegion,
    decode_edl,
    encode_edl,
)
from video_editing_agent.render.edl_ffmpeg import FFmpegEDLRenderer

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".tools" / "ffmpeg-8.1" / "ffmpeg-8.1-full_build" / "bin"
FFMPEG = BIN / "ffmpeg.exe"
FFPROBE = BIN / "ffprobe.exe"
OUTPUT = ROOT / ".private" / "probes" / "r0_12_subtitle"
WIDTH = 640
HEIGHT = 360


def _run(arguments: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(arguments, check=False, capture_output=True)


def _source(path: Path) -> None:
    result = _run(
        [
            str(FFMPEG),
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=0x303030:s={WIDTH}x{HEIGHT}:r=30:d=4",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(path),
        ]
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors="replace"))


def _edl() -> EDL:
    return EDL(
        EntityEnvelope(
            "subtitle-live-edl",
            1,
            "0.2",
            EntityStatus.VALID,
            datetime(2026, 8, 16, tzinfo=UTC),
            "r0.12-subtitle-live",
        ),
        EntityRevisionRef("subtitle-live-plan", 1),
        (
            EDLSegment(
                "video",
                EntityRevisionRef("subtitle-live-asset", 1),
                source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(4, 1)),
                timeline_range=MediaTimeRange(MediaTime(0, 1), MediaTime(4, 1)),
            ),
        ),
        (EDLTrack("video", EDLTrackFamily.VIDEO),),
    )


def _frame(path: Path, timestamp: str) -> bytes:
    result = _run(
        [
            str(FFMPEG),
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            timestamp,
            "-i",
            str(path),
            "-frames:v",
            "1",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ]
    )
    if result.returncode or len(result.stdout) != WIDTH * HEIGHT * 3:
        raise RuntimeError(result.stderr.decode(errors="replace"))
    return result.stdout


def _region_difference(left: bytes, right: bytes, *, upper: bool) -> int:
    start_y, end_y = (20, 150) if upper else (210, 350)
    count = 0
    for y in range(start_y, end_y):
        start = (y * WIDTH) * 3
        end = ((y + 1) * WIDTH) * 3
        count += sum(a != b for a, b in zip(left[start:end], right[start:end], strict=True))
    return count


def main() -> int:
    if not FFMPEG.is_file() or not FFPROBE.is_file():
        raise RuntimeError("configured local FFmpeg 8.1 toolchain is unavailable")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    source = OUTPUT / "controlled_source.mp4"
    baseline_path = OUTPUT / "baseline.mp4"
    subtitle_path = OUTPUT / "multilingual, quoted's subtitles.mp4"
    _source(source)
    base = _edl()
    structured = compile_subtitle_cues(
        base,
        (
            StructuredSubtitleCue(
                "english",
                MediaTimeRange(MediaTime(1, 2), MediaTime(1, 1)),
                "Safe, exact {English}",
                "en",
                emphasis=(SubtitleEmphasisSpan(6, 11, SubtitleEmphasisStyle.BOLD),),
            ),
            StructuredSubtitleCue(
                "chinese",
                MediaTimeRange(MediaTime(2, 1), MediaTime(1, 1)),
                "中文结构化字幕",
                "zh-CN",
                emphasis=(SubtitleEmphasisSpan(0, 2, SubtitleEmphasisStyle.HIGHLIGHT),),
                layout=SubtitleLayoutRegion.UPPER_SAFE,
            ),
        ),
    )
    ass_path = OUTPUT / ".subtitle-live-edl.r1.640x360.subtitles.ass"
    renderer = FFmpegEDLRenderer(str(FFMPEG), str(FFPROBE))
    media = (ResolvedLocalAssetMedia(EntityRevisionRef("subtitle-live-asset", 1), source),)
    baseline = renderer.render(
        RenderRequest(base, media, OutputSpec(baseline_path, WIDTH, HEIGHT, 30))
    )
    rendered = renderer.render(
        RenderRequest(structured, media, OutputSpec(subtitle_path, WIDTH, HEIGHT, 30))
    )
    if baseline.artifact is None or rendered.artifact is None:
        raise RuntimeError(f"render failed: {baseline.diagnostics!r} {rendered.diagnostics!r}")

    baseline_english = _frame(baseline_path, "1.0")
    rendered_english = _frame(subtitle_path, "1.0")
    baseline_chinese = _frame(baseline_path, "2.5")
    rendered_chinese = _frame(subtitle_path, "2.5")
    baseline_gap = _frame(baseline_path, "1.75")
    rendered_gap = _frame(subtitle_path, "1.75")
    lower_english = _region_difference(baseline_english, rendered_english, upper=False)
    upper_english = _region_difference(baseline_english, rendered_english, upper=True)
    upper_chinese = _region_difference(baseline_chinese, rendered_chinese, upper=True)
    lower_chinese = _region_difference(baseline_chinese, rendered_chinese, upper=False)
    gap_difference = sum(
        left != right for left, right in zip(baseline_gap, rendered_gap, strict=True)
    )
    round_trip = decode_edl(encode_edl(structured))
    gates = {
        "APPROVED_CUES_UNCHANGED": tuple(cue.text for cue in structured.subtitle_cues)
        == ("Safe, exact {English}", "中文结构化字幕"),
        "EXACT_RATIONAL_EDL_ROUND_TRIP": round_trip
        == replace(
            structured,
            segments=structured.ordered_segments,
            tracks=structured.effective_tracks,
            subtitle_cues=structured.ordered_subtitle_cues,
        ),
        "ASS_ARTIFACT_EMITTED": ass_path.is_file(),
        "ENGLISH_LOWER_SAFE_PIXELS": lower_english > 100 and lower_english > upper_english,
        "CHINESE_UPPER_SAFE_PIXELS": upper_chinese > 100 and upper_chinese > lower_chinese,
        "NO_CAPTION_OUTSIDE_CUES": gap_difference == 0,
        "REAL_MP4_VERIFIED": subtitle_path.is_file() and subtitle_path.stat().st_size > 0,
    }
    report = {
        "classification": "ENGINEERING_PROBE_NOT_PRODUCT_PROBE",
        "gates": gates,
        "pixel_differences": {
            "english_lower": lower_english,
            "english_upper": upper_english,
            "chinese_upper": upper_chinese,
            "chinese_lower": lower_chinese,
            "between_cues_total": gap_difference,
        },
        "outputs": {
            "baseline": str(baseline_path),
            "subtitled": str(subtitle_path),
            "ass": str(ass_path),
        },
        "glyph_limit": (
            "FFmpeg/libass render and region pixels are verified; semantic glyph-shape correctness "
            "is not claimed without OCR or human review, and no font is redistributed."
        ),
    }
    (OUTPUT / "probe_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

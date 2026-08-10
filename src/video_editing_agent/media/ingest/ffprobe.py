from __future__ import annotations

import json
import math
import pathlib
import subprocess
from typing import cast

from video_editing_agent.media.ingest.probe import MediaTechnicalMetadata

FFPROBE_SHOW_ENTRIES = (
    "format=duration:"
    "stream=codec_type,codec_name,width,height,avg_frame_rate,r_frame_rate,channels,sample_rate"
)


def _object_dict(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    return cast(dict[str, object], value)


def _string_field(data: dict[str, object], name: str) -> str | None:
    value = data.get(name)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _positive_int_field(data: dict[str, object], name: str) -> int | None:
    value = data.get(name)
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, str):
        try:
            parsed = int(value)
        except ValueError:
            return None
        return parsed if parsed > 0 else None
    return None


def _positive_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        parsed = float(value)
    elif isinstance(value, str):
        try:
            parsed = float(value)
        except ValueError:
            return None
    else:
        return None
    if not math.isfinite(parsed) or parsed <= 0:
        return None
    return parsed


def _frame_rate(value: object) -> float | None:
    if not isinstance(value, str):
        return _positive_float(value)
    if "/" not in value:
        return _positive_float(value)

    numerator_text, denominator_text = value.split("/", maxsplit=1)
    try:
        numerator = float(numerator_text)
        denominator = float(denominator_text)
    except ValueError:
        return None
    if denominator == 0:
        return None
    return _positive_float(numerator / denominator)


def _duration_ms(format_data: dict[str, object]) -> int | None:
    seconds = _positive_float(format_data.get("duration"))
    if seconds is None:
        return None
    return max(1, round(seconds * 1000))


def parse_ffprobe_metadata(payload: str) -> MediaTechnicalMetadata:
    """Normalize the ffprobe JSON subset used by AssetIngest."""
    try:
        root = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError("ffprobe returned invalid JSON") from exc
    if not isinstance(root, dict):
        raise ValueError("ffprobe JSON root must be an object")
    root_data = cast(dict[str, object], root)

    streams_value = root_data.get("streams", [])
    if not isinstance(streams_value, list):
        raise ValueError("ffprobe streams must be a list")
    streams = [item for value in streams_value if (item := _object_dict(value)) is not None]

    video_stream = next(
        (stream for stream in streams if _string_field(stream, "codec_type") == "video"),
        None,
    )
    audio_stream = next(
        (stream for stream in streams if _string_field(stream, "codec_type") == "audio"),
        None,
    )
    if video_stream is None and audio_stream is None:
        raise ValueError("ffprobe found no supported video or audio stream")

    format_data = _object_dict(root_data.get("format")) or {}
    media_kind = "video" if video_stream is not None else "audio"
    primary_stream = video_stream or audio_stream
    assert primary_stream is not None

    fps = None
    if video_stream is not None:
        fps = _frame_rate(video_stream.get("avg_frame_rate")) or _frame_rate(
            video_stream.get("r_frame_rate")
        )

    return MediaTechnicalMetadata(
        media_kind=media_kind,
        duration_ms=_duration_ms(format_data),
        width=_positive_int_field(video_stream, "width") if video_stream is not None else None,
        height=_positive_int_field(video_stream, "height") if video_stream is not None else None,
        fps=fps,
        codec=_string_field(primary_stream, "codec_name"),
        audio_channels=(
            _positive_int_field(audio_stream, "channels") if audio_stream is not None else None
        ),
        sample_rate_hz=(
            _positive_int_field(audio_stream, "sample_rate") if audio_stream is not None else None
        ),
    )


class FfprobeMediaProbe:
    """Technical media probe backed by the external ffprobe executable."""

    def __init__(self, executable: str = "ffprobe") -> None:
        if not executable.strip():
            raise ValueError("ffprobe executable must not be empty")
        self._executable = executable

    def probe(self, path: pathlib.Path) -> MediaTechnicalMetadata:
        command = [
            self._executable,
            "-v",
            "error",
            "-show_entries",
            FFPROBE_SHOW_ENTRIES,
            "-of",
            "json",
            str(path),
        ]
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
        except FileNotFoundError as exc:
            raise RuntimeError(f"ffprobe executable not found: {self._executable}") from exc

        if completed.returncode != 0:
            detail = completed.stderr.strip() or "unknown ffprobe error"
            raise RuntimeError(f"ffprobe failed for {path}: {detail}")
        return parse_ffprobe_metadata(completed.stdout)

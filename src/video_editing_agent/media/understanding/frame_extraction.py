from __future__ import annotations

import pathlib
import subprocess
from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.media.understanding.sampling import FrameSampleSpec, FrameSamplingPlan

PNG_MEDIA_TYPE = "image/png"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@dataclass(frozen=True, slots=True)
class ExtractedFrameSample:
    """Transient image payload ready to be persisted by a future ArtifactStore."""

    sample: FrameSampleSpec
    media_type: str
    content: bytes

    def __post_init__(self) -> None:
        if not self.media_type.strip():
            raise ValueError("media_type must not be empty")
        if not self.content:
            raise ValueError("frame content must not be empty")


class FramePlanExtractor(Protocol):
    def extract(
        self,
        input_video: pathlib.Path,
        plan: FrameSamplingPlan,
    ) -> tuple[ExtractedFrameSample, ...]: ...


class FfmpegPngFrameExtractor:
    """Extract one PNG payload for each deterministic source timestamp in a sampling plan."""

    def __init__(self, executable: str = "ffmpeg") -> None:
        if not executable.strip():
            raise ValueError("ffmpeg executable must not be empty")
        self._executable = executable

    def _extract_one(self, input_video: pathlib.Path, sample: FrameSampleSpec) -> bytes:
        timestamp_text = sample.source_timestamp.to_decimal_seconds_string()
        command = [
            self._executable,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-ss",
            timestamp_text,
            "-i",
            str(input_video),
            "-map",
            "0:v:0",
            "-frames:v",
            "1",
            "-f",
            "image2pipe",
            "-vcodec",
            "png",
            "pipe:1",
        ]
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(f"FFmpeg executable not found: {self._executable}") from exc

        if completed.returncode != 0:
            detail = completed.stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(
                f"FFmpeg frame extraction failed at source {timestamp_text} s: "
                f"{detail or 'unknown FFmpeg error'}"
            )
        if not completed.stdout.startswith(PNG_SIGNATURE):
            raise RuntimeError(f"FFmpeg did not return a PNG frame at source {timestamp_text} s")
        return completed.stdout

    def extract(
        self,
        input_video: pathlib.Path,
        plan: FrameSamplingPlan,
    ) -> tuple[ExtractedFrameSample, ...]:
        path = input_video.expanduser().resolve(strict=True)
        if not path.is_file():
            raise ValueError(f"input_video must be a file: {path}")

        return tuple(
            ExtractedFrameSample(
                sample=sample,
                media_type=PNG_MEDIA_TYPE,
                content=self._extract_one(path, sample),
            )
            for sample in plan.samples
        )

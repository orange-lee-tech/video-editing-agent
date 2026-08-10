from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


RGB24_CHANNELS = 3


@dataclass(frozen=True, slots=True)
class RawRgb24Frames:
    """Complete fixed-size RGB24 frames returned by an FFmpeg decode operation."""

    data: bytes
    frame_count: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.frame_count < 0:
            raise ValueError("frame_count must be >= 0")
        if self.width <= 0:
            raise ValueError("width must be > 0")
        if self.height <= 0:
            raise ValueError("height must be > 0")

        expected_bytes = self.frame_count * self.width * self.height * RGB24_CHANNELS
        if len(self.data) != expected_bytes:
            raise ValueError(
                f"RGB24 payload length mismatch: expected {expected_bytes} bytes, "
                f"got {len(self.data)}"
            )

    @property
    def bytes_per_frame(self) -> int:
        return self.width * self.height * RGB24_CHANNELS


def decode_video_to_rgb24_frames(
    input_video: Path,
    *,
    ffmpeg_executable: str = "ffmpeg",
    frames_per_second: int,
    target_width: int,
    target_height: int,
) -> RawRgb24Frames:
    """Decode a video to fixed-rate, fixed-size RGB24 frames using FFmpeg.

    This function owns only media decoding. It does not know about TransNetV2,
    `Asset`, `Shot`, application workflow state, or output clip creation.
    """
    if isinstance(frames_per_second, bool) or not isinstance(frames_per_second, int):
        raise TypeError("frames_per_second must be an int")
    if frames_per_second <= 0:
        raise ValueError("frames_per_second must be > 0")
    if isinstance(target_width, bool) or not isinstance(target_width, int):
        raise TypeError("target_width must be an int")
    if isinstance(target_height, bool) or not isinstance(target_height, int):
        raise TypeError("target_height must be an int")
    if target_width <= 0 or target_height <= 0:
        raise ValueError("target dimensions must be > 0")
    if not ffmpeg_executable.strip():
        raise ValueError("ffmpeg_executable must not be empty")

    video_filter = (
        f"fps={frames_per_second},"
        f"scale={target_width}:{target_height}:flags=fast_bilinear"
    )
    command = [
        ffmpeg_executable,
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-i",
        str(input_video),
        "-an",
        "-vf",
        video_filter,
        "-pix_fmt",
        "rgb24",
        "-f",
        "rawvideo",
        "pipe:1",
    ]

    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"FFmpeg RGB24 decode failed for {input_video}:\n{stderr}")

    bytes_per_frame = target_width * target_height * RGB24_CHANNELS
    payload_size = len(completed.stdout)
    if payload_size % bytes_per_frame != 0:
        raise RuntimeError(
            "FFmpeg returned an incomplete RGB24 frame payload: "
            f"{payload_size} bytes is not divisible by {bytes_per_frame} bytes/frame"
        )

    return RawRgb24Frames(
        data=completed.stdout,
        frame_count=payload_size // bytes_per_frame,
        width=target_width,
        height=target_height,
    )

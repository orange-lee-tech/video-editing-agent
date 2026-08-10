from __future__ import annotations

import collections.abc
import dataclasses
import pathlib
import subprocess
import tempfile
import typing

RGB24_CHANNELS = 3


@dataclasses.dataclass(frozen=True, slots=True)
class Rgb24FrameSpec:
    """Fixed FFmpeg sampling geometry for a stream of RGB24 frames."""

    frames_per_second: int
    width: int
    height: int

    def __post_init__(self) -> None:
        for name, value in (
            ("frames_per_second", self.frames_per_second),
            ("width", self.width),
            ("height", self.height),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an int")
            if value <= 0:
                raise ValueError(f"{name} must be > 0")

    @property
    def bytes_per_frame(self) -> int:
        return self.width * self.height * RGB24_CHANNELS


def _read_exact(stream: typing.BinaryIO, size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size

    while remaining > 0:
        chunk = stream.read(remaining)
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)

    return b"".join(chunks)


def _read_process_stderr(stderr_file: typing.BinaryIO) -> str:
    stderr_file.flush()
    stderr_file.seek(0)
    return stderr_file.read().decode("utf-8", errors="replace")


def iter_video_rgb24_frames(
    input_video: pathlib.Path,
    *,
    ffmpeg_executable: str = "ffmpeg",
    frames_per_second: int,
    target_width: int,
    target_height: int,
) -> collections.abc.Iterator[bytes]:
    """Stream complete fixed-rate RGB24 frames from FFmpeg.

    Frames are yielded one at a time so video duration does not determine resident raw-frame
    memory. The consumer owns any higher-level model batching/windowing policy.
    """
    spec = Rgb24FrameSpec(
        frames_per_second=frames_per_second,
        width=target_width,
        height=target_height,
    )
    if not ffmpeg_executable.strip():
        raise ValueError("ffmpeg_executable must not be empty")

    video_filter = (
        f"fps={spec.frames_per_second},scale={spec.width}:{spec.height}:flags=fast_bilinear"
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

    with tempfile.TemporaryFile() as stderr_file:
        try:
            process: subprocess.Popen[bytes] = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=stderr_file,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(f"FFmpeg executable not found: {ffmpeg_executable}") from exc

        if process.stdout is None:
            process.kill()
            process.wait()
            raise RuntimeError("FFmpeg stdout pipe was not created")
        stdout_stream = typing.cast(typing.BinaryIO, process.stdout)

        try:
            while True:
                frame = _read_exact(stdout_stream, spec.bytes_per_frame)
                if not frame:
                    break
                if len(frame) != spec.bytes_per_frame:
                    raise RuntimeError(
                        "FFmpeg returned an incomplete RGB24 frame: "
                        f"expected {spec.bytes_per_frame} bytes, got {len(frame)}"
                    )
                yield frame

            return_code = process.wait()
            if return_code != 0:
                stderr = _read_process_stderr(stderr_file)
                raise RuntimeError(f"FFmpeg RGB24 decode failed for {input_video}:\n{stderr}")
        finally:
            stdout_stream.close()
            if process.poll() is None:
                process.kill()
                process.wait()

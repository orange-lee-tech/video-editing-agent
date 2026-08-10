import subprocess
from pathlib import Path

import pytest

from video_editing_agent.media.shot_detection.ffmpeg_frames import (
    RGB24_CHANNELS,
    decode_video_to_rgb24_frames,
)


def test_decode_video_builds_fixed_rate_rgb24_command(monkeypatch: pytest.MonkeyPatch) -> None:
    width = 4
    height = 3
    frame_bytes = width * height * RGB24_CHANNELS
    payload = b"\x01" * (frame_bytes * 2)
    observed_command: list[str] = []

    def fake_run(
        command: list[str],
        *,
        stdout: int,
        stderr: int,
        check: bool,
    ) -> subprocess.CompletedProcess[bytes]:
        del stdout, stderr, check
        observed_command.extend(command)
        return subprocess.CompletedProcess(command, 0, stdout=payload, stderr=b"")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = decode_video_to_rgb24_frames(
        Path("input.mp4"),
        ffmpeg_executable="ffmpeg-test",
        frames_per_second=25,
        target_width=width,
        target_height=height,
    )

    assert result.frame_count == 2
    assert result.data == payload
    assert result.bytes_per_frame == frame_bytes
    assert observed_command[0] == "ffmpeg-test"
    assert "fps=25,scale=4:3:flags=fast_bilinear" in observed_command
    assert observed_command[-2:] == ["rawvideo", "pipe:1"]


def test_decode_video_returns_empty_complete_frame_batch(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(
        command: list[str],
        *,
        stdout: int,
        stderr: int,
        check: bool,
    ) -> subprocess.CompletedProcess[bytes]:
        del stdout, stderr, check
        return subprocess.CompletedProcess(command, 0, stdout=b"", stderr=b"")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = decode_video_to_rgb24_frames(
        Path("empty.mp4"),
        frames_per_second=25,
        target_width=48,
        target_height=27,
    )

    assert result.frame_count == 0
    assert result.data == b""


def test_decode_video_surfaces_ffmpeg_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(
        command: list[str],
        *,
        stdout: int,
        stderr: int,
        check: bool,
    ) -> subprocess.CompletedProcess[bytes]:
        del stdout, stderr, check
        return subprocess.CompletedProcess(command, 1, stdout=b"", stderr=b"bad input")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="bad input"):
        decode_video_to_rgb24_frames(
            Path("broken.mp4"),
            frames_per_second=25,
            target_width=48,
            target_height=27,
        )


def test_decode_video_rejects_incomplete_frame_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(
        command: list[str],
        *,
        stdout: int,
        stderr: int,
        check: bool,
    ) -> subprocess.CompletedProcess[bytes]:
        del stdout, stderr, check
        return subprocess.CompletedProcess(command, 0, stdout=b"abcde", stderr=b"")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="incomplete RGB24 frame payload"):
        decode_video_to_rgb24_frames(
            Path("partial.mp4"),
            frames_per_second=25,
            target_width=2,
            target_height=1,
        )


def test_decode_video_validates_sampling_and_dimensions() -> None:
    with pytest.raises(ValueError, match="frames_per_second"):
        decode_video_to_rgb24_frames(
            Path("input.mp4"),
            frames_per_second=0,
            target_width=48,
            target_height=27,
        )

    with pytest.raises(ValueError, match="target dimensions"):
        decode_video_to_rgb24_frames(
            Path("input.mp4"),
            frames_per_second=25,
            target_width=0,
            target_height=27,
        )

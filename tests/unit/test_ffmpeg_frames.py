import io
import subprocess
from pathlib import Path
from typing import BinaryIO

import pytest

from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.media.shot_detection.ffmpeg_frames import (
    RGB24_CHANNELS,
    Rgb24FrameSpec,
    iter_video_rgb24_frames,
)


class FakeProcess:
    def __init__(self, payload: bytes, *, return_code: int = 0) -> None:
        self.stdout = io.BytesIO(payload)
        self._configured_return_code = return_code
        self._finished = False
        self.killed = False

    def wait(self) -> int:
        self._finished = True
        return self._configured_return_code

    def poll(self) -> int | None:
        if self._finished:
            return self._configured_return_code
        return None

    def kill(self) -> None:
        self.killed = True
        self._configured_return_code = -9
        self._finished = True


def install_fake_popen(
    monkeypatch: pytest.MonkeyPatch,
    *,
    payload: bytes,
    return_code: int = 0,
    stderr_payload: bytes = b"",
) -> tuple[list[str], list[FakeProcess]]:
    observed_command: list[str] = []
    created_processes: list[FakeProcess] = []

    def fake_popen(
        command: list[str],
        *,
        stdout: int,
        stderr: BinaryIO,
        creationflags: int,
    ) -> FakeProcess:
        del stdout, creationflags
        observed_command.extend(command)
        stderr.write(stderr_payload)
        process = FakeProcess(payload, return_code=return_code)
        created_processes.append(process)
        return process

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    return observed_command, created_processes


def test_rgb24_frame_spec_validates_geometry_and_frame_size() -> None:
    spec = Rgb24FrameSpec(frames_per_second=25, width=48, height=27)

    assert spec.bytes_per_frame == 48 * 27 * RGB24_CHANNELS

    with pytest.raises(ValueError, match="frames_per_second"):
        Rgb24FrameSpec(frames_per_second=0, width=48, height=27)

    with pytest.raises(ValueError, match="width"):
        Rgb24FrameSpec(frames_per_second=25, width=0, height=27)


def test_streaming_decode_yields_complete_frames_and_builds_expected_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    width = 4
    height = 3
    frame_bytes = width * height * RGB24_CHANNELS
    first_frame = b"\x01" * frame_bytes
    second_frame = b"\x02" * frame_bytes
    observed_command, _ = install_fake_popen(
        monkeypatch,
        payload=first_frame + second_frame,
    )

    frames = list(
        iter_video_rgb24_frames(
            Path("input.mp4"),
            ffmpeg_executable="ffmpeg-test",
            frames_per_second=25,
            target_width=width,
            target_height=height,
        )
    )

    assert frames == [first_frame, second_frame]
    assert observed_command[0] == "ffmpeg-test"
    assert "fps=25,scale=4:3:flags=fast_bilinear" in observed_command
    assert observed_command[-2:] == ["rawvideo", "pipe:1"]


def test_streaming_decode_allows_empty_clean_stream(monkeypatch: pytest.MonkeyPatch) -> None:
    install_fake_popen(monkeypatch, payload=b"")

    frames = list(
        iter_video_rgb24_frames(
            Path("empty.mp4"),
            frames_per_second=25,
            target_width=48,
            target_height=27,
        )
    )

    assert frames == []


def test_streaming_decode_surfaces_ffmpeg_error(monkeypatch: pytest.MonkeyPatch) -> None:
    install_fake_popen(
        monkeypatch,
        payload=b"",
        return_code=1,
        stderr_payload=b"bad input",
    )

    with pytest.raises(RuntimeError, match="bad input"):
        list(
            iter_video_rgb24_frames(
                Path("broken.mp4"),
                frames_per_second=25,
                target_width=48,
                target_height=27,
            )
        )


def test_streaming_decode_rejects_incomplete_final_frame(monkeypatch: pytest.MonkeyPatch) -> None:
    install_fake_popen(monkeypatch, payload=b"abcde")

    with pytest.raises(RuntimeError, match="incomplete RGB24 frame"):
        list(
            iter_video_rgb24_frames(
                Path("partial.mp4"),
                frames_per_second=25,
                target_width=2,
                target_height=1,
            )
        )


def test_streaming_decode_reports_missing_ffmpeg(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_popen(
        command: list[str],
        *,
        stdout: int,
        stderr: BinaryIO,
        creationflags: int,
    ) -> FakeProcess:
        del command, stdout, stderr, creationflags
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    with pytest.raises(RuntimeError, match="FFmpeg executable not found"):
        list(
            iter_video_rgb24_frames(
                Path("input.mp4"),
                ffmpeg_executable="missing-ffmpeg",
                frames_per_second=25,
                target_width=48,
                target_height=27,
            )
        )


def test_closing_stream_early_kills_unfinished_ffmpeg(monkeypatch: pytest.MonkeyPatch) -> None:
    frame_bytes = 2 * 1 * RGB24_CHANNELS
    _, processes = install_fake_popen(
        monkeypatch,
        payload=(b"\x01" * frame_bytes) + (b"\x02" * frame_bytes),
    )
    frames = iter_video_rgb24_frames(
        Path("input.mp4"),
        frames_per_second=25,
        target_width=2,
        target_height=1,
    )

    assert next(frames) == b"\x01" * frame_bytes
    frames.close()

    assert processes[0].killed is True


def test_shot_scoped_decode_uses_exact_start_and_duration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorded: list[str] = []

    def fake_popen(
        command: list[str],
        *,
        stdout: int,
        stderr: BinaryIO,
        creationflags: int,
    ) -> FakeProcess:
        del stdout, stderr, creationflags
        recorded.extend(command)
        return FakeProcess(b"")

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    list(
        iter_video_rgb24_frames(
            Path("input.mp4"),
            frames_per_second=10,
            target_width=2,
            target_height=2,
            source_range=MediaTimeRange(MediaTime(3, 2), MediaTime(7, 4)),
        )
    )
    assert recorded[recorded.index("-ss") + 1] == "1.500"
    assert recorded[recorded.index("-t") + 1] == "1.750"
    assert recorded.index("-ss") < recorded.index("-i")

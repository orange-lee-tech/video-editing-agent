import subprocess
from pathlib import Path

import pytest

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.media.understanding.frame_extraction import (
    PNG_MEDIA_TYPE,
    PNG_SIGNATURE,
    FfmpegPngFrameExtractor,
)
from video_editing_agent.media.understanding.sampling import (
    FrameSampleSpec,
    FrameSamplingPlan,
)


def make_plan() -> FrameSamplingPlan:
    shot_ref = EntityRevisionRef("sht_1", 2)
    return FrameSamplingPlan(
        shot_ref=shot_ref,
        samples=(
            FrameSampleSpec(shot_ref=shot_ref, ordinal=0, source_timestamp_ms=250),
            FrameSampleSpec(shot_ref=shot_ref, ordinal=1, source_timestamp_ms=1_250),
        ),
    )


def test_ffmpeg_extractor_preserves_sampling_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"video")
    commands: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        del kwargs
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, PNG_SIGNATURE + b"payload", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)

    frames = FfmpegPngFrameExtractor().extract(video, make_plan())

    assert [frame.sample.source_timestamp_ms for frame in frames] == [250, 1_250]
    assert all(frame.media_type == PNG_MEDIA_TYPE for frame in frames)
    assert all(frame.content.startswith(PNG_SIGNATURE) for frame in frames)
    assert commands[0][commands[0].index("-ss") + 1] == "0.250"
    assert commands[1][commands[1].index("-ss") + 1] == "1.250"


def test_ffmpeg_extractor_rejects_non_png_stdout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"video")

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        del kwargs
        return subprocess.CompletedProcess(command, 0, b"not-png", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="did not return a PNG"):
        FfmpegPngFrameExtractor().extract(video, make_plan())


def test_ffmpeg_extractor_surfaces_process_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"video")

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        del kwargs
        return subprocess.CompletedProcess(command, 1, b"", b"decode failed")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="decode failed"):
        FfmpegPngFrameExtractor().extract(video, make_plan())


def test_ffmpeg_executable_must_not_be_blank() -> None:
    with pytest.raises(ValueError, match="executable"):
        FfmpegPngFrameExtractor(" ")

from pathlib import Path

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.media.shot_detection.transnet_backend import (
    ResolvedVideoAsset,
    TransNetV2BackendConfig,
    TransNetV2SceneBoundaryBackend,
)


class StaticResolver:
    def __init__(self, resolved: ResolvedVideoAsset) -> None:
        self._resolved = resolved

    def resolve_video(self, asset_ref: EntityRevisionRef) -> ResolvedVideoAsset:
        del asset_ref
        return self._resolved


class EchoPredictor:
    def predict_single_frame_probabilities(self, frames: tuple[bytes, ...]) -> tuple[float, ...]:
        return tuple(frame[0] / 255.0 for frame in frames)


class RecordingFrameSource:
    def __init__(self, frames: list[bytes]) -> None:
        self._frames = frames
        self.calls: list[tuple[Path, str, int, int, int]] = []

    def __call__(
        self,
        input_video: Path,
        *,
        ffmpeg_executable: str,
        frames_per_second: int,
        target_width: int,
        target_height: int,
    ):
        self.calls.append(
            (
                input_video,
                ffmpeg_executable,
                frames_per_second,
                target_width,
                target_height,
            )
        )
        yield from self._frames


def test_backend_streams_frames_and_returns_normalized_boundaries(tmp_path: Path) -> None:
    video_path = tmp_path / "video.mp4"
    video_path.touch()
    frames = [bytes([255 if index in {24, 25} else 0]) for index in range(75)]
    source = RecordingFrameSource(frames)
    backend = TransNetV2SceneBoundaryBackend(
        StaticResolver(ResolvedVideoAsset(path=video_path, duration_ms=3_000)),
        EchoPredictor(),
        frame_source=source,
    )

    result = backend.detect_boundaries(EntityRevisionRef("ast_1", 1))

    assert result.total_duration_ms == 3_000
    assert result.boundary_times_ms == (1000,)
    assert result.detection_method == "transnetv2-pytorch:1.0.5"
    assert source.calls == [(video_path, "ffmpeg", 25, 48, 27)]


def test_zero_duration_asset_does_not_decode_frames(tmp_path: Path) -> None:
    source = RecordingFrameSource([b"x"])
    backend = TransNetV2SceneBoundaryBackend(
        StaticResolver(ResolvedVideoAsset(path=tmp_path / "zero.mp4", duration_ms=0)),
        EchoPredictor(),
        frame_source=source,
    )

    result = backend.detect_boundaries(EntityRevisionRef("ast_zero", 1))

    assert result.total_duration_ms == 0
    assert result.boundary_times_ms == ()
    assert source.calls == []


def test_backend_config_rejects_invalid_threshold() -> None:
    try:
        TransNetV2BackendConfig(threshold=1.1)
    except ValueError as exc:
        assert "threshold" in str(exc)
    else:
        raise AssertionError("expected ValueError")

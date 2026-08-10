from __future__ import annotations

import collections.abc
import dataclasses
import pathlib
from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.media.shot_detection.detector import SceneBoundaryResult
from video_editing_agent.media.shot_detection.ffmpeg_frames import iter_video_rgb24_frames
from video_editing_agent.media.shot_detection.transnet_predictions import (
    TransNetV2WindowPredictor,
    collect_transnetv2_single_frame_predictions,
)
from video_editing_agent.media.shot_detection.transnet_scenes import (
    single_frame_predictions_to_boundary_times_ms,
)

TRANSNETV2_FRAME_WIDTH = 48
TRANSNETV2_FRAME_HEIGHT = 27
TRANSNETV2_DEFAULT_FPS = 25
TRANSNETV2_DEFAULT_THRESHOLD = 0.5


@dataclasses.dataclass(frozen=True, slots=True)
class ResolvedVideoAsset:
    """Physical media information supplied by Asset storage/metadata infrastructure."""

    path: pathlib.Path
    duration_ms: int

    def __post_init__(self) -> None:
        if isinstance(self.duration_ms, bool) or not isinstance(self.duration_ms, int):
            raise TypeError("duration_ms must be an int")
        if self.duration_ms < 0:
            raise ValueError("duration_ms must be >= 0")


class VideoAssetResolver(Protocol):
    """Resolve an Asset revision to local media plus authoritative source duration."""

    def resolve_video(self, asset_ref: EntityRevisionRef) -> ResolvedVideoAsset: ...


class Rgb24FrameSource(Protocol):
    def __call__(
        self,
        input_video: pathlib.Path,
        *,
        ffmpeg_executable: str,
        frames_per_second: int,
        target_width: int,
        target_height: int,
    ) -> collections.abc.Iterator[bytes]: ...


@dataclasses.dataclass(frozen=True, slots=True)
class TransNetV2BackendConfig:
    threshold: float = TRANSNETV2_DEFAULT_THRESHOLD
    frames_per_second: int = TRANSNETV2_DEFAULT_FPS
    ffmpeg_executable: str = "ffmpeg"
    detection_method: str = "transnetv2-pytorch:1.0.5"

    def __post_init__(self) -> None:
        if isinstance(self.threshold, bool) or not isinstance(self.threshold, (int, float)):
            raise TypeError("threshold must be a number")
        if not 0.0 <= float(self.threshold) <= 1.0:
            raise ValueError("threshold must be between 0 and 1")
        if isinstance(self.frames_per_second, bool) or not isinstance(self.frames_per_second, int):
            raise TypeError("frames_per_second must be an int")
        if self.frames_per_second <= 0:
            raise ValueError("frames_per_second must be > 0")
        if not self.ffmpeg_executable.strip():
            raise ValueError("ffmpeg_executable must not be empty")
        if not self.detection_method.strip():
            raise ValueError("detection_method must not be empty")


class TransNetV2SceneBoundaryBackend:
    """Stream video through TransNetV2 and return normalized internal cut boundaries."""

    def __init__(
        self,
        asset_resolver: VideoAssetResolver,
        predictor: TransNetV2WindowPredictor,
        *,
        config: TransNetV2BackendConfig | None = None,
        frame_source: Rgb24FrameSource = iter_video_rgb24_frames,
    ) -> None:
        self._asset_resolver = asset_resolver
        self._predictor = predictor
        self._config = config or TransNetV2BackendConfig()
        self._frame_source = frame_source

    def detect_boundaries(self, asset_ref: EntityRevisionRef) -> SceneBoundaryResult:
        resolved = self._asset_resolver.resolve_video(asset_ref)
        if resolved.duration_ms == 0:
            return SceneBoundaryResult(
                total_duration_ms=0,
                boundary_times_ms=(),
                detection_method=self._config.detection_method,
            )

        frames = self._frame_source(
            resolved.path,
            ffmpeg_executable=self._config.ffmpeg_executable,
            frames_per_second=self._config.frames_per_second,
            target_width=TRANSNETV2_FRAME_WIDTH,
            target_height=TRANSNETV2_FRAME_HEIGHT,
        )
        predictions = collect_transnetv2_single_frame_predictions(frames, self._predictor)
        boundary_times_ms = single_frame_predictions_to_boundary_times_ms(
            predictions,
            threshold=self._config.threshold,
            frames_per_second=self._config.frames_per_second,
        )

        return SceneBoundaryResult(
            total_duration_ms=resolved.duration_ms,
            boundary_times_ms=boundary_times_ms,
            detection_method=self._config.detection_method,
        )

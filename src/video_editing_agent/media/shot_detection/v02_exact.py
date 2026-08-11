from __future__ import annotations

import dataclasses
import pathlib
from collections.abc import Iterable
from fractions import Fraction
from typing import Protocol

from video_editing_agent.application.ports.shot_detector import (
    ShotBoundaryProposal,
    ShotDetectionOptions,
    ShotDetector,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.media.shot_detection.ffmpeg_frames import iter_video_rgb24_frames
from video_editing_agent.media.shot_detection.transnet_backend import (
    TRANSNETV2_DEFAULT_FPS,
    TRANSNETV2_DEFAULT_THRESHOLD,
    TRANSNETV2_FRAME_HEIGHT,
    TRANSNETV2_FRAME_WIDTH,
    Rgb24FrameSource,
    TransNetV2BackendConfig,
)
from video_editing_agent.media.shot_detection.transnet_predictions import (
    TransNetV2WindowPredictor,
    collect_transnetv2_single_frame_predictions,
)


def _positive_optional_milliseconds(value: int | None) -> MediaTime | None:
    if value is None or value == 0:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("duration policy value must be an int or None")
    if value < 0:
        raise ValueError("duration policy value must be >= 0")
    return MediaTime.from_milliseconds(value)


def _normalize_cut_points(
    values: Iterable[MediaTime],
    total_duration: MediaTime,
) -> tuple[MediaTime, ...]:
    total = total_duration.as_fraction()
    return tuple(
        sorted(
            {value for value in values if Fraction(0, 1) < value.as_fraction() < total},
            key=MediaTime.as_fraction,
        )
    )


def _merge_short_segments(
    cuts: tuple[MediaTime, ...],
    total_duration: MediaTime,
    minimum: MediaTime | None,
) -> tuple[MediaTime, ...]:
    if minimum is None:
        return cuts
    kept: list[MediaTime] = []
    start = MediaTime(0, 1)
    minimum_fraction = minimum.as_fraction()
    for cut in cuts:
        if (cut - start).as_fraction() < minimum_fraction:
            continue
        kept.append(cut)
        start = cut
    if kept and (total_duration - kept[-1]).as_fraction() < minimum_fraction:
        kept.pop()
    return tuple(kept)


def _ceil_fraction(value: Fraction) -> int:
    return (value.numerator + value.denominator - 1) // value.denominator


def _partition_segment(
    start: MediaTime,
    end: MediaTime,
    minimum: MediaTime | None,
    maximum: MediaTime,
) -> tuple[MediaTime, ...]:
    duration = end - start
    duration_fraction = duration.as_fraction()
    maximum_fraction = maximum.as_fraction()
    if duration_fraction <= maximum_fraction:
        return ()
    count = _ceil_fraction(duration_fraction / maximum_fraction)
    if minimum is not None and count > int(duration_fraction / minimum.as_fraction()):
        raise ValueError("exact source segment cannot satisfy both Shot duration constraints")
    return tuple(
        start + MediaTime(duration.value * index, duration.scale * count)
        for index in range(1, count)
    )


def _apply_duration_policy(
    cuts: Iterable[MediaTime],
    total_duration: MediaTime,
    options: ShotDetectionOptions,
) -> tuple[MediaTime, ...]:
    minimum = _positive_optional_milliseconds(options.min_shot_duration_ms)
    maximum = _positive_optional_milliseconds(options.max_shot_duration_ms)
    normalized = _normalize_cut_points(cuts, total_duration)
    merged = _merge_short_segments(normalized, total_duration, minimum)
    if maximum is None:
        return merged
    boundaries = (MediaTime(0, 1), *merged, total_duration)
    result = set(merged)
    for start, end in zip(boundaries[:-1], boundaries[1:], strict=True):
        result.update(_partition_segment(start, end, minimum, maximum))
    return tuple(sorted(result, key=MediaTime.as_fraction))


def _ranges_from_cuts(
    cuts: Iterable[MediaTime],
    total_duration: MediaTime,
) -> tuple[MediaTimeRange, ...]:
    normalized = _normalize_cut_points(cuts, total_duration)
    boundaries = (MediaTime(0, 1), *normalized, total_duration)
    return tuple(
        MediaTimeRange(start=start, duration=end - start)
        for start, end in zip(boundaries[:-1], boundaries[1:], strict=True)
        if end.as_fraction() > start.as_fraction()
    )


def _prediction_boundaries(
    predictions: Iterable[float],
    *,
    threshold: float,
    frames_per_second: int,
) -> tuple[MediaTime, ...]:
    values = tuple(float(value) for value in predictions)
    transition_start: int | None = None
    frames: list[int] = []
    for index, probability in enumerate(values):
        active = probability > threshold
        if active and transition_start is None:
            transition_start = index
            continue
        if active or transition_start is None:
            continue
        transition_end = index - 1
        if transition_start > 0 and transition_end < len(values) - 1:
            frames.append((transition_start + transition_end + 1) // 2)
        transition_start = None
    if transition_start is not None:
        transition_end = len(values) - 1
        if transition_start > 0 and transition_end < len(values) - 1:
            frames.append((transition_start + transition_end + 1) // 2)
    return tuple(MediaTime(frame, frames_per_second) for frame in dict.fromkeys(frames))


@dataclasses.dataclass(frozen=True, slots=True)
class ExactSceneBoundaryResult:
    total_duration: MediaTime
    boundary_times: tuple[MediaTime, ...]
    detection_method: str

    def __post_init__(self) -> None:
        if self.total_duration.as_fraction() < 0:
            raise ValueError("total_duration must be >= 0")
        if not self.detection_method.strip():
            raise ValueError("detection_method must not be empty")
        normalized = _normalize_cut_points(self.boundary_times, self.total_duration)
        if normalized != self.boundary_times:
            raise ValueError("boundary_times must be unique, increasing and inside duration")


class ExactSceneBoundaryBackend(Protocol):
    def detect_boundaries(self, asset_ref: EntityRevisionRef) -> ExactSceneBoundaryResult: ...


@dataclasses.dataclass(frozen=True, slots=True)
class ExactResolvedVideoAsset:
    path: pathlib.Path
    duration: MediaTime

    def __post_init__(self) -> None:
        if self.duration.as_fraction() < 0:
            raise ValueError("duration must be >= 0")


class ExactVideoAssetResolver(Protocol):
    def resolve_video(self, asset_ref: EntityRevisionRef) -> ExactResolvedVideoAsset: ...


class ExactPolicyDrivenShotDetector(ShotDetector):
    """v0.2 ShotDetector path whose backend and duration policy remain exact rational time."""

    def __init__(self, backend: ExactSceneBoundaryBackend) -> None:
        self._backend = backend

    def detect(
        self,
        asset_ref: EntityRevisionRef,
        options: ShotDetectionOptions,
    ) -> tuple[ShotBoundaryProposal, ...]:
        result = self._backend.detect_boundaries(asset_ref)
        if result.total_duration.value == 0:
            return ()
        cuts = _apply_duration_policy(result.boundary_times, result.total_duration, options)
        return tuple(
            ShotBoundaryProposal(
                asset_ref=asset_ref,
                source_range=source_range,
                detection_method=result.detection_method,
            )
            for source_range in _ranges_from_cuts(cuts, result.total_duration)
        )


class ExactTransNetV2SceneBoundaryBackend:
    """v0.2 TransNetV2 adapter that never converts authoritative duration/cuts through ms."""

    def __init__(
        self,
        asset_resolver: ExactVideoAssetResolver,
        predictor: TransNetV2WindowPredictor,
        *,
        config: TransNetV2BackendConfig | None = None,
        frame_source: Rgb24FrameSource = iter_video_rgb24_frames,
    ) -> None:
        self._asset_resolver = asset_resolver
        self._predictor = predictor
        self._config = config or TransNetV2BackendConfig(
            threshold=TRANSNETV2_DEFAULT_THRESHOLD,
            frames_per_second=TRANSNETV2_DEFAULT_FPS,
        )
        self._frame_source = frame_source

    def detect_boundaries(self, asset_ref: EntityRevisionRef) -> ExactSceneBoundaryResult:
        resolved = self._asset_resolver.resolve_video(asset_ref)
        if resolved.duration.value == 0:
            return ExactSceneBoundaryResult(
                total_duration=resolved.duration,
                boundary_times=(),
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
        return ExactSceneBoundaryResult(
            total_duration=resolved.duration,
            boundary_times=_prediction_boundaries(
                predictions,
                threshold=self._config.threshold,
                frames_per_second=self._config.frames_per_second,
            ),
            detection_method=self._config.detection_method,
        )

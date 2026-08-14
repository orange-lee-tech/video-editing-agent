from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from video_editing_agent.application.ports.seeded_tracking import NormalizedRectangle
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.resolution import ResolvedSelection


def _unit_interval(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number")
    normalized = float(value)
    if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise ValueError(f"{name} must be finite and between 0 and 1")


@dataclass(frozen=True, slots=True)
class OutputCanvas:
    width: int
    height: int

    def __post_init__(self) -> None:
        for name, value in (("width", self.width), ("height", self.height)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an int")
            if value <= 0:
                raise ValueError(f"{name} must be > 0")


@dataclass(frozen=True, slots=True)
class SourceFrameGeometry:
    width: int
    height: int

    def __post_init__(self) -> None:
        OutputCanvas(self.width, self.height)


@dataclass(frozen=True, slots=True)
class PixelCrop:
    left: int
    top: int
    width: int
    height: int

    def __post_init__(self) -> None:
        for name, value in (
            ("left", self.left),
            ("top", self.top),
            ("width", self.width),
            ("height", self.height),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an int")
        if self.left < 0 or self.top < 0 or self.width <= 0 or self.height <= 0:
            raise ValueError("pixel crop must have non-negative origin and positive size")


@dataclass(frozen=True, slots=True)
class ReframeIntent:
    output_canvas: OutputCanvas
    mandatory_focus_refs: tuple[str, ...] = ()
    preferred_focus_refs: tuple[str, ...] = ()
    framing_style: str = "hold"

    def __post_init__(self) -> None:
        if not self.framing_style.strip():
            raise ValueError("framing_style must not be empty")
        refs = (*self.mandatory_focus_refs, *self.preferred_focus_refs)
        if any(not item.strip() for item in refs):
            raise ValueError("focus refs must be non-empty")


@dataclass(frozen=True, slots=True)
class SpatialEvidenceView:
    evidence_id: str
    shot_ref: EntityRevisionRef
    source_range: MediaTimeRange
    focus_ref: str
    bounds: NormalizedRectangle
    confidence: float

    def __post_init__(self) -> None:
        if not self.evidence_id.strip() or not self.focus_ref.strip():
            raise ValueError("spatial evidence identity must not be empty")
        _unit_interval("confidence", self.confidence)
        values = (self.bounds.x, self.bounds.y, self.bounds.width, self.bounds.height)
        if (
            any(not math.isfinite(value) for value in values)
            or self.bounds.x < 0
            or self.bounds.y < 0
            or self.bounds.width <= 0
            or self.bounds.height <= 0
            or self.bounds.x + self.bounds.width > 1
            or self.bounds.y + self.bounds.height > 1
        ):
            raise ValueError("spatial evidence bounds must be normalized inside the source frame")


@dataclass(frozen=True, slots=True)
class SpatialFocusObservation:
    source_time: MediaTime
    status: str
    bounds: NormalizedRectangle | None
    confidence: float
    loss_reason: str | None = None

    def __post_init__(self) -> None:
        if self.source_time.as_fraction() < 0:
            raise ValueError("source_time must be >= 0")
        _unit_interval("confidence", self.confidence)
        if self.status == "available":
            if self.bounds is None or self.loss_reason is not None:
                raise ValueError("available observation requires bounds and no loss reason")
            values = (
                self.bounds.x,
                self.bounds.y,
                self.bounds.width,
                self.bounds.height,
            )
            if (
                any(not math.isfinite(value) for value in values)
                or self.bounds.x < 0
                or self.bounds.y < 0
                or self.bounds.width <= 0
                or self.bounds.height <= 0
                or self.bounds.x + self.bounds.width > 1
                or self.bounds.y + self.bounds.height > 1
            ):
                raise ValueError("available observation bounds must be normalized")
        elif self.status == "lost":
            if self.bounds is not None or not self.loss_reason:
                raise ValueError("lost observation requires reason and no focus geometry")
        else:
            raise ValueError("unsupported spatial observation status")


@dataclass(frozen=True, slots=True)
class SpatialEvidenceTrack:
    track_id: str
    selection_id: str
    shot_ref: EntityRevisionRef
    analyzed_source_range: MediaTimeRange
    source_geometry: SourceFrameGeometry
    focus_ref: str
    provider_id: str
    provider_revision: str
    sampling_fps: int
    observations: tuple[SpatialFocusObservation, ...]
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        values = (
            self.track_id,
            self.selection_id,
            self.focus_ref,
            self.provider_id,
            self.provider_revision,
        )
        if any(not value.strip() for value in values) or not self.observations:
            raise ValueError("spatial evidence track requires identity, provider, and observations")
        if (
            isinstance(self.sampling_fps, bool)
            or not isinstance(self.sampling_fps, int)
            or self.sampling_fps <= 0
        ):
            raise ValueError("sampling_fps must be a positive int")
        times = tuple(item.source_time.as_fraction() for item in self.observations)
        if times != tuple(sorted(set(times))):
            raise ValueError("spatial observations must be unique and source-time ordered")
        if any(
            item.source_time.as_fraction() < self.analyzed_source_range.start.as_fraction()
            or item.source_time.as_fraction() >= self.analyzed_source_range.end.as_fraction()
            for item in self.observations
        ):
            raise ValueError("spatial observation must stay inside half-open analyzed source range")


@dataclass(frozen=True, slots=True)
class SpatialPathPolicy:
    version: str = "r0.11-stability-recovery-candidate-v2"
    center_dead_zone_pixels: int = 12
    max_center_velocity_pixels_per_second: int = 800
    max_lost_hold_gap: MediaTime = MediaTime(1, 1)
    max_reacquisition_gap: MediaTime = MediaTime(4, 1)
    suppress_redundant_keyframes: bool = True

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError("spatial path policy version must not be empty")
        for name, value in (
            ("center_dead_zone_pixels", self.center_dead_zone_pixels),
            (
                "max_center_velocity_pixels_per_second",
                self.max_center_velocity_pixels_per_second,
            ),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative int")
        if self.max_lost_hold_gap.as_fraction() < 0:
            raise ValueError("max_lost_hold_gap must be >= 0")
        if self.max_reacquisition_gap.as_fraction() < self.max_lost_hold_gap.as_fraction():
            raise ValueError("max_reacquisition_gap must be >= max_lost_hold_gap")


@dataclass(frozen=True, slots=True)
class SpatialPathQc:
    focus_observation_count: int
    contained_focus_count: int
    source_bound_violations: int
    target_aspect_violations: int
    max_center_displacement_pixels: float
    max_center_velocity_pixels_per_second: float
    direction_change_count: int
    held_loss_count: int
    held_loss_duration_seconds: float
    suppressed_keyframe_count: int
    unresolved_reason: str | None = None
    recovery_bridge_count: int = 0
    recovery_bridge_duration_seconds: float = 0.0
    maximum_reacquisition_gap_observed_seconds: float = 0.0
    terminal_held_loss_count: int = 0
    terminal_held_loss_duration_seconds: float = 0.0


@dataclass(frozen=True, slots=True)
class SpatialCropKeyframe:
    source_time: MediaTime
    crop: PixelCrop

    def __post_init__(self) -> None:
        if self.source_time.as_fraction() < 0:
            raise ValueError("source_time must be >= 0")


@dataclass(frozen=True, slots=True)
class ManualCropLock:
    lock_id: str
    keyframe: SpatialCropKeyframe

    def __post_init__(self) -> None:
        if not self.lock_id.strip():
            raise ValueError("lock_id must not be empty")


class SpatialInterpolationMode(StrEnum):
    HOLD = "hold"
    LINEAR = "linear"


@dataclass(frozen=True, slots=True)
class SpatialTransformPlan:
    selection_id: str
    shot_ref: EntityRevisionRef
    source_range: MediaTimeRange
    source_geometry: SourceFrameGeometry
    output_canvas: OutputCanvas
    keyframes: tuple[SpatialCropKeyframe, ...]
    interpolation: SpatialInterpolationMode = SpatialInterpolationMode.HOLD

    def __post_init__(self) -> None:
        if not self.selection_id.strip() or not self.keyframes:
            raise ValueError("spatial transform plan requires identity and keyframes")
        if not isinstance(self.interpolation, SpatialInterpolationMode):
            raise ValueError("unsupported spatial interpolation mode")
        times = tuple(item.source_time.as_fraction() for item in self.keyframes)
        if times != tuple(sorted(set(times))):
            raise ValueError("crop keyframe source times must be unique and increasing")
        for item in self.keyframes:
            if not (
                self.source_range.start.as_fraction()
                <= item.source_time.as_fraction()
                < self.source_range.end.as_fraction()
            ):
                raise ValueError("crop keyframe must stay inside resolved source range")
            crop = item.crop
            if (
                crop.left + crop.width > self.source_geometry.width
                or crop.top + crop.height > self.source_geometry.height
            ):
                raise ValueError("crop keyframe escapes source geometry")
            if crop.width * self.output_canvas.height != crop.height * self.output_canvas.width:
                raise ValueError("crop keyframe must preserve output canvas aspect ratio")


@dataclass(frozen=True, slots=True)
class NormalizedCanvasRegion:
    left: float
    top: float
    right: float
    bottom: float

    def __post_init__(self) -> None:
        for name, value in (
            ("left", self.left),
            ("top", self.top),
            ("right", self.right),
            ("bottom", self.bottom),
        ):
            _unit_interval(name, value)
        if self.right <= self.left or self.bottom <= self.top:
            raise ValueError("normalized region must have positive area")


@dataclass(frozen=True, slots=True)
class SpatialTransformKeyframe:
    """Source-time spatial intent; EDLBuilder later maps it to exact timeline automation."""

    source_time: MediaTime
    crop_center_x: float
    crop_center_y: float
    scale: float

    def __post_init__(self) -> None:
        if self.source_time.as_fraction() < 0:
            raise ValueError("source_time must be >= 0")
        _unit_interval("crop_center_x", self.crop_center_x)
        _unit_interval("crop_center_y", self.crop_center_y)
        if isinstance(self.scale, bool) or not isinstance(self.scale, (int, float)):
            raise TypeError("scale must be a number")
        if not math.isfinite(float(self.scale)) or self.scale <= 0:
            raise ValueError("scale must be finite and > 0")


@dataclass(frozen=True, slots=True)
class SpatialCompositionRequest:
    selection: ResolvedSelection
    source_geometry: SourceFrameGeometry
    intent: ReframeIntent
    spatial_evidence: tuple[SpatialEvidenceView, ...] = ()
    spatial_tracks: tuple[SpatialEvidenceTrack, ...] = ()
    path_policy: SpatialPathPolicy = SpatialPathPolicy()
    manual_locks: tuple[ManualCropLock, ...] = ()
    protected_regions: tuple[NormalizedCanvasRegion, ...] = ()
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ReframeDecision:
    decision_id: str
    selection_id: str
    mode: str
    keyframes: tuple[SpatialTransformKeyframe, ...]
    confidence: float
    evidence_refs: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    infeasible_reason: str | None = None
    transform_plan: SpatialTransformPlan | None = None
    spatial_qc: SpatialPathQc | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("decision_id", self.decision_id),
            ("selection_id", self.selection_id),
            ("mode", self.mode),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        _unit_interval("confidence", self.confidence)
        times = tuple(keyframe.source_time.as_fraction() for keyframe in self.keyframes)
        if times != tuple(sorted(set(times))):
            raise ValueError("spatial keyframe source times must be unique and increasing")
        if self.infeasible_reason is not None and self.keyframes:
            raise ValueError("infeasible reframe decision must not contain executable keyframes")
        if self.infeasible_reason is not None and self.transform_plan is not None:
            raise ValueError("infeasible reframe decision must not contain a transform plan")
        if self.transform_plan is not None:
            if self.transform_plan.selection_id != self.selection_id:
                raise ValueError("reframe decision and transform plan selection must agree")
            if len(self.keyframes) != len(self.transform_plan.keyframes):
                raise ValueError("legacy keyframe view must derive from the transform plan")
            source = self.transform_plan.source_geometry
            for legacy, canonical in zip(
                self.keyframes, self.transform_plan.keyframes, strict=True
            ):
                crop = canonical.crop
                expected = (
                    canonical.source_time,
                    (crop.left + crop.width / 2) / source.width,
                    (crop.top + crop.height / 2) / source.height,
                    source.width / crop.width,
                )
                observed = (
                    legacy.source_time,
                    legacy.crop_center_x,
                    legacy.crop_center_y,
                    legacy.scale,
                )
                if observed != expected:
                    raise ValueError("legacy keyframe view diverges from transform plan")


class SpatialComposer(Protocol):
    """Own spatial-resolution decisions; renderer/trackers are not spatial authority."""

    def compose(self, request: SpatialCompositionRequest) -> ReframeDecision: ...

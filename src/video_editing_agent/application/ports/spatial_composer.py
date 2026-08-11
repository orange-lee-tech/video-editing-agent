from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.domain.common.media_time import MediaTime
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
    output_canvas: OutputCanvas
    protected_regions: tuple[NormalizedCanvasRegion, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    manual_lock_refs: tuple[str, ...] = ()


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


class SpatialComposer(Protocol):
    """Own spatial-resolution decisions; renderer/trackers are not spatial authority."""

    def compose(self, request: SpatialCompositionRequest) -> ReframeDecision: ...

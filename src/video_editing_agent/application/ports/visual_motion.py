from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTimeRange


@dataclass(frozen=True, slots=True)
class VisualMotionRequest:
    shot_ref: EntityRevisionRef
    local_media_path: pathlib.Path
    source_range: MediaTimeRange


@dataclass(frozen=True, slots=True)
class VisualMotionMeasurement:
    relative_range: MediaTimeRange
    status: str
    reason: str | None
    feature_count: int
    tracked_count: int
    coverage: float
    inlier_count: int
    inlier_ratio: float
    translation_x: float | None
    translation_y: float | None
    rotation_radians: float | None
    scale: float | None
    fit_error: float | None
    global_displacement: float | None
    raw_displacement_median: float
    residual_median: float | None
    residual_p95: float | None
    residual_max: float | None


@dataclass(frozen=True, slots=True)
class VisualMotionProposal:
    shot_ref: EntityRevisionRef
    provider_id: str
    provider_revision: str
    frames_per_second: int
    width: int
    height: int
    measurements: tuple[VisualMotionMeasurement, ...]


class VisualMotionPort(Protocol):
    def measure(self, request: VisualMotionRequest) -> VisualMotionProposal: ...

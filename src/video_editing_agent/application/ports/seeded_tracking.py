from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange


@dataclass(frozen=True, slots=True)
class NormalizedRectangle:
    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True, slots=True)
class SeededTrackingRequest:
    shot_ref: EntityRevisionRef
    local_media_path: pathlib.Path
    source_range: MediaTimeRange
    seed_id: str
    seed_rectangle: NormalizedRectangle


@dataclass(frozen=True, slots=True)
class TrackingSample:
    relative_time: MediaTime
    status: str
    reason: str | None
    rectangle: NormalizedRectangle | None
    support_count: int
    support_ratio: float


@dataclass(frozen=True, slots=True)
class SeededTrackingProposal:
    shot_ref: EntityRevisionRef
    analyzed_source_range: MediaTimeRange
    seed_id: str
    seed_rectangle: NormalizedRectangle
    provider_id: str
    provider_revision: str
    frames_per_second: int
    width: int
    height: int
    samples: tuple[TrackingSample, ...]


class SeededTrackingPort(Protocol):
    def track(self, request: SeededTrackingRequest) -> SeededTrackingProposal: ...

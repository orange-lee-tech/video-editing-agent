from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange


def _confidence(value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("confidence must be a number")
    normalized = float(value)
    if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise ValueError("confidence must be finite and between 0 and 1")


@dataclass(frozen=True, slots=True)
class MusicIntent:
    description: str
    target_duration: MediaTime | None = None
    platform: str | None = None
    genre_hint: str | None = None
    mood_tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("description must not be empty")
        if self.target_duration is not None and self.target_duration.as_fraction() <= 0:
            raise ValueError("target_duration must be > 0")


@dataclass(frozen=True, slots=True)
class MusicSourceSegment:
    order: int
    source_range: MediaTimeRange

    def __post_init__(self) -> None:
        if isinstance(self.order, bool) or not isinstance(self.order, int):
            raise TypeError("order must be an int")
        if self.order < 0:
            raise ValueError("order must be >= 0")


@dataclass(frozen=True, slots=True)
class MusicSelectionRequest:
    intent: MusicIntent
    candidate_asset_refs: tuple[EntityRevisionRef, ...]
    rights_evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.candidate_asset_refs:
            raise ValueError("candidate_asset_refs must not be empty")


@dataclass(frozen=True, slots=True)
class MusicSelectionDecision:
    decision_id: str
    selected_asset_ref: EntityRevisionRef
    source_segments: tuple[MusicSourceSegment, ...]
    rights_evidence_refs: tuple[str, ...]
    score: float
    confidence: float
    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    alternative_asset_refs: tuple[EntityRevisionRef, ...] = ()

    def __post_init__(self) -> None:
        if not self.decision_id.strip():
            raise ValueError("decision_id must not be empty")
        if not self.source_segments:
            raise ValueError("source_segments must not be empty")
        orders = tuple(segment.order for segment in self.source_segments)
        if orders != tuple(range(len(self.source_segments))):
            raise ValueError("MusicSourceSegment order must be contiguous from zero")
        _confidence(self.score)
        _confidence(self.confidence)


class MusicSelectionService(Protocol):
    """Own rights-aware music choice/moment selection, never EDL placement."""

    def select(self, request: MusicSelectionRequest) -> MusicSelectionDecision: ...

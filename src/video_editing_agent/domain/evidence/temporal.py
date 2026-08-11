from __future__ import annotations

import math
from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange


def _validate_confidence(value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("confidence must be a number")
    normalized = float(value)
    if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise ValueError("confidence must be finite and between 0 and 1")


@dataclass(frozen=True, slots=True)
class TemporalEvidence:
    evidence_id: str
    shot_ref: EntityRevisionRef
    kind: str
    method: str
    producer_version: str
    confidence: float
    source_range: MediaTimeRange | None = None
    artifact_refs: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("evidence_id", self.evidence_id),
            ("kind", self.kind),
            ("method", self.method),
            ("producer_version", self.producer_version),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        if self.source_range is not None and self.source_range.start.as_fraction() < 0:
            raise ValueError("source_range must start at >= 0")
        _validate_confidence(self.confidence)


@dataclass(frozen=True, slots=True)
class TemporalAnchor:
    anchor_id: str
    shot_ref: EntityRevisionRef
    kind: str
    source_time: MediaTime
    confidence: float
    evidence_refs: tuple[str, ...]
    method: str
    semantic_label: str | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("anchor_id", self.anchor_id),
            ("kind", self.kind),
            ("method", self.method),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        if self.source_time.as_fraction() < 0:
            raise ValueError("source_time must be >= 0")
        if not self.evidence_refs or any(not value.strip() for value in self.evidence_refs):
            raise ValueError("evidence_refs must contain non-empty evidence identifiers")
        _validate_confidence(self.confidence)

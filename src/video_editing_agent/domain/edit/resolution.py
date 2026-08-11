from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTimeRange


def _validate_confidence(value: float | None) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("confidence must be a number or None")
    normalized = float(value)
    if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise ValueError("confidence must be finite and between 0 and 1")


class ResolutionDecisionType(StrEnum):
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True, slots=True)
class CandidateWindow:
    candidate_id: str
    shot_ref: EntityRevisionRef
    source_range: MediaTimeRange
    confidence: float | None = None
    in_anchor_ref: str | None = None
    out_anchor_ref: str | None = None
    internal_event_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("candidate_id must not be empty")
        if self.source_range.start.as_fraction() < 0:
            raise ValueError("CandidateWindow source range must start at >= 0")
        _validate_confidence(self.confidence)


@dataclass(frozen=True, slots=True)
class ResolvedSelection:
    selection_id: str
    shot_ref: EntityRevisionRef
    selected_source_range: MediaTimeRange
    order: int
    role: str = "primary"
    anchor_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.selection_id.strip():
            raise ValueError("selection_id must not be empty")
        if self.selected_source_range.start.as_fraction() < 0:
            raise ValueError("selected_source_range must start at >= 0")
        if isinstance(self.order, bool) or not isinstance(self.order, int):
            raise TypeError("order must be an int")
        if self.order < 0:
            raise ValueError("order must be >= 0")
        if not self.role.strip():
            raise ValueError("role must not be empty")


@dataclass(frozen=True, slots=True)
class ResolutionDecision:
    decision_id: str
    edit_plan_ref: EntityRevisionRef
    target_slot_ids: tuple[str, ...]
    decision_type: ResolutionDecisionType
    selections: tuple[ResolvedSelection, ...] = ()
    score: float | None = None
    confidence: float | None = None
    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.decision_id.strip():
            raise ValueError("decision_id must not be empty")
        if not self.target_slot_ids or any(not value.strip() for value in self.target_slot_ids):
            raise ValueError("target_slot_ids must contain non-empty slot identifiers")
        orders = tuple(selection.order for selection in self.selections)
        if orders != tuple(range(len(self.selections))):
            raise ValueError("ResolvedSelection order must be contiguous from zero")
        if self.decision_type is ResolutionDecisionType.RESOLVED and not self.selections:
            raise ValueError("resolved decision requires at least one selection")
        if self.decision_type is ResolutionDecisionType.UNRESOLVED and self.selections:
            raise ValueError("unresolved decision must not contain selections")
        _validate_confidence(self.score)
        _validate_confidence(self.confidence)

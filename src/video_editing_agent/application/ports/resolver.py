from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.edit.resolution import ResolutionDecision


@dataclass(frozen=True, slots=True)
class ResolutionRequest:
    edit_plan_ref: EntityRevisionRef
    target_slot_ids: tuple[str, ...]
    shot_analysis_refs: tuple[str, ...] = ()
    temporal_anchor_refs: tuple[str, ...] = ()
    beat_map_ref: EntityRevisionRef | None = None
    policy_version_refs: tuple[str, ...] = ()
    locked_decision_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.target_slot_ids or any(not value.strip() for value in self.target_slot_ids):
            raise ValueError("target_slot_ids must contain non-empty slot identifiers")


class ShotResolver(Protocol):
    """Own concrete source selection; EDLBuilder owns final timeline placement."""

    def resolve(self, request: ResolutionRequest) -> ResolutionDecision: ...

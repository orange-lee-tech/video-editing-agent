from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef


@dataclass(frozen=True, slots=True)
class EditSlot:
    slot_id: str
    purpose: str


@dataclass(frozen=True, slots=True)
class EditPlan:
    envelope: EntityEnvelope
    script_plan_ref: EntityRevisionRef
    shooting_plan_ref: EntityRevisionRef
    slots: tuple[EditSlot, ...]

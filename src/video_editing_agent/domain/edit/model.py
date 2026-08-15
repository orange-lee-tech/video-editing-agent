from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime


@dataclass(frozen=True, slots=True)
class DurationConstraint:
    minimum: MediaTime
    maximum: MediaTime

    def __post_init__(self) -> None:
        if (
            self.minimum.as_fraction() <= 0
            or self.maximum.as_fraction() < self.minimum.as_fraction()
        ):
            raise ValueError("invalid rational duration constraint")


@dataclass(frozen=True, slots=True)
class EditSlot:
    slot_id: str
    purpose: str
    order: int = 0
    narrative_role: str = "support"
    semantic_query: str = ""
    target_duration: DurationConstraint | None = None
    pacing: str = "neutral"
    continuity_hint: str | None = None
    allow_reuse: bool = False
    importance: int = 1

    def __post_init__(self) -> None:
        if not self.slot_id.strip() or not self.purpose.strip():
            raise ValueError("EditSlot identity/purpose must not be empty")
        if self.order < 0 or not 1 <= self.importance <= 3:
            raise ValueError("invalid EditSlot order/importance")


@dataclass(frozen=True, slots=True)
class EditPlan:
    envelope: EntityEnvelope
    script_plan_ref: EntityRevisionRef | None
    shooting_plan_ref: EntityRevisionRef | None
    slots: tuple[EditSlot, ...]
    brief_ref: EntityRevisionRef | None = None

    def __post_init__(self) -> None:
        if self.shooting_plan_ref is not None and self.script_plan_ref is None:
            raise ValueError("EditPlan cannot reference ShootingPlan without ScriptPlan")
        if self.brief_ref is None and (
            self.script_plan_ref is None or self.shooting_plan_ref is None
        ):
            raise ValueError(
                "EditPlan requires Brief provenance or complete legacy Planning provenance"
            )
        if not self.slots or len({x.slot_id for x in self.slots}) != len(self.slots):
            raise ValueError("EditPlan requires unique slots")
        if tuple(x.order for x in self.slots) != tuple(sorted(x.order for x in self.slots)):
            raise ValueError("EditPlan slots must be ordered")

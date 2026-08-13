from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange


@dataclass(frozen=True, slots=True)
class EditSlot:
    slot_id: str
    order: int
    narrative_role: str
    purpose: str
    semantic_query: str
    target_duration: MediaTimeRange
    pacing: str = "neutral"
    continuity_hint: str | None = None
    allow_reuse: bool = False
    importance: int = 1

    def __post_init__(self) -> None:
        if any(
            not value.strip()
            for value in (self.slot_id, self.narrative_role, self.purpose, self.semantic_query)
        ):
            raise ValueError("EditSlot identity and intent text must not be empty")
        if self.order < 0 or not 1 <= self.importance <= 3:
            raise ValueError("invalid EditSlot order/importance")
        if self.target_duration.start.as_fraction() <= 0:
            raise ValueError("target duration minimum must be positive")

    @property
    def minimum_duration(self) -> MediaTime:
        return self.target_duration.start

    @property
    def maximum_duration(self) -> MediaTime:
        return self.target_duration.end


@dataclass(frozen=True, slots=True)
class EditPlan:
    plan_id: str
    slots: tuple[EditSlot, ...]

    def __post_init__(self) -> None:
        if not self.plan_id.strip() or not self.slots:
            raise ValueError("EditPlan requires identity and slots")
        if len({x.slot_id for x in self.slots}) != len(self.slots):
            raise ValueError("EditPlan slot identities must be unique")
        if tuple(x.order for x in self.slots) != tuple(sorted(x.order for x in self.slots)):
            raise ValueError("EditPlan slots must be ordered")

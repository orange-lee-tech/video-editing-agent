from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.domain.brief.model import Brief
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.script.model import ScriptPlan
from video_editing_agent.domain.shooting.model import ShootingPlan
from video_editing_agent.domain.shot.analysis import AnalysisProfile


@dataclass(frozen=True, slots=True)
class DirectorFootageEvidence:
    shot_ref: EntityRevisionRef
    asset_ref: EntityRevisionRef
    analysis_revision: int
    profile: AnalysisProfile
    summary: str | None
    tags: tuple[str, ...]
    subjects: tuple[str, ...]
    actions: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.analysis_revision < 1:
            raise ValueError("analysis_revision must be >= 1")


@dataclass(frozen=True, slots=True)
class DirectorRequest:
    brief: Brief
    footage: tuple[DirectorFootageEvidence, ...]
    script_plan: ScriptPlan | None = None
    shooting_plan: ShootingPlan | None = None
    policy_guidance: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        brief_ref = EntityRevisionRef(self.brief.envelope.id, self.brief.envelope.revision)
        if not self.footage:
            raise ValueError("Director requires eligible analyzed visual footage")
        if self.script_plan is not None and self.script_plan.brief_ref != brief_ref:
            raise ValueError("ScriptPlan must reference the exact Director Brief")
        if self.shooting_plan is not None:
            if self.script_plan is None:
                raise ValueError("ShootingPlan context requires ScriptPlan context")
            script_ref = EntityRevisionRef(
                self.script_plan.envelope.id, self.script_plan.envelope.revision
            )
            if self.shooting_plan.script_plan_ref != script_ref:
                raise ValueError("ShootingPlan must reference the exact Director ScriptPlan")
        if any(not value.strip() for value in self.policy_guidance):
            raise ValueError("policy_guidance must not contain empty values")


@dataclass(frozen=True, slots=True)
class EditSlotProposal:
    slot_id: str
    order: int
    narrative_role: str
    purpose: str
    semantic_query: str
    minimum_duration: MediaTime | None = None
    maximum_duration: MediaTime | None = None
    pacing: str = "neutral"
    continuity_hint: str | None = None
    allow_reuse: bool = False
    importance: int = 1

    def __post_init__(self) -> None:
        for name, value in (
            ("slot_id", self.slot_id),
            ("narrative_role", self.narrative_role),
            ("purpose", self.purpose),
            ("semantic_query", self.semantic_query),
            ("pacing", self.pacing),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.continuity_hint is not None and (
            not isinstance(self.continuity_hint, str) or not self.continuity_hint.strip()
        ):
            raise ValueError("continuity_hint must be a non-empty string when provided")
        if isinstance(self.order, bool) or not isinstance(self.order, int) or self.order < 0:
            raise ValueError("order must be a non-negative int")
        if not isinstance(self.allow_reuse, bool):
            raise TypeError("allow_reuse must be a bool")
        if (
            isinstance(self.importance, bool)
            or not isinstance(self.importance, int)
            or not 1 <= self.importance <= 3
        ):
            raise ValueError("importance must be an int between 1 and 3")
        if (self.minimum_duration is None) != (self.maximum_duration is None):
            raise ValueError("duration bounds must be both provided or both omitted")
        if self.minimum_duration is not None and self.maximum_duration is not None:
            if (
                self.minimum_duration.as_fraction() <= 0
                or self.maximum_duration.as_fraction() < self.minimum_duration.as_fraction()
            ):
                raise ValueError("invalid Director duration bounds")


@dataclass(frozen=True, slots=True)
class DirectorProposal:
    slots: tuple[EditSlotProposal, ...]

    def __post_init__(self) -> None:
        if not self.slots:
            raise ValueError("Director proposal must contain slots")
        slot_ids = tuple(item.slot_id for item in self.slots)
        orders = tuple(item.order for item in self.slots)
        if len(set(slot_ids)) != len(slot_ids):
            raise ValueError("Director proposal requires unique slot_id values")
        if len(set(orders)) != len(orders):
            raise ValueError("Director proposal requires unique slot order values")


class DirectorPort(Protocol):
    """Provider-neutral proposal seam with no source-selection or timeline authority."""

    def propose(self, request: DirectorRequest) -> DirectorProposal: ...

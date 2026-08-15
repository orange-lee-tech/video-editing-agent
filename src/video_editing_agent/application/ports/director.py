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


@dataclass(frozen=True, slots=True)
class DirectorProposal:
    slots: tuple[EditSlotProposal, ...]


class DirectorPort(Protocol):
    """Provider-neutral proposal seam with no source-selection or timeline authority."""

    def propose(self, request: DirectorRequest) -> DirectorProposal: ...

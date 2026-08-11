from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.domain.brief.model import Brief
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.script.model import ScriptPlan
from video_editing_agent.domain.shooting.model import ProductionConstraints, ShootingPlan


def _entity_ref(entity: Brief | ScriptPlan | ShootingPlan) -> EntityRevisionRef:
    return EntityRevisionRef(entity.envelope.id, entity.envelope.revision)


def _validate_instruction(instruction: str | None) -> None:
    if instruction is not None and not instruction.strip():
        raise ValueError("instruction must not be empty when provided")


def _require_nonempty(name: str, value: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} must not be empty")


@dataclass(frozen=True, slots=True)
class PlanningPolicyGuidance:
    """Neutral, inspectable policy context supplied to a replaceable planning provider."""

    platform_profile_id: str
    platform_profile_version: str
    skill_id: str
    skill_version: str
    guidance: tuple[str, ...]
    marketing_objective: str | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("platform_profile_id", self.platform_profile_id),
            ("platform_profile_version", self.platform_profile_version),
            ("skill_id", self.skill_id),
            ("skill_version", self.skill_version),
        ):
            _require_nonempty(name, value)
        if not self.guidance:
            raise ValueError("guidance must not be empty")
        if any(not item.strip() for item in self.guidance):
            raise ValueError("guidance must not contain empty values")
        if self.marketing_objective is not None:
            _require_nonempty("marketing_objective", self.marketing_objective)


@dataclass(frozen=True, slots=True)
class NarrativeSectionProposal:
    section_id: str
    narrative_role: str
    information_goal: str
    spoken_content: str | None = None
    visual_requirement: str | None = None
    target_duration: MediaTime | None = None
    on_screen_text_intent: str | None = None
    emotion: str | None = None
    pacing: str | None = None
    music_intent: str | None = None
    editing_intent: str | None = None
    importance: str | None = None
    protected_fact_ids: tuple[str, ...] = ()
    locked: bool = False


@dataclass(frozen=True, slots=True)
class ScriptPlanProposal:
    sections: tuple[NarrativeSectionProposal, ...]


@dataclass(frozen=True, slots=True)
class ScriptPlanningRequest:
    brief: Brief
    current_script: ScriptPlan | None = None
    instruction: str | None = None
    policy_guidance: PlanningPolicyGuidance | None = None

    def __post_init__(self) -> None:
        _validate_instruction(self.instruction)
        if self.current_script is not None and self.current_script.brief_ref != _entity_ref(
            self.brief
        ):
            raise ValueError(
                "current_script must reference the exact Brief revision in the request"
            )


class ScriptPlanningPort(Protocol):
    """Replaceable model/provider seam that returns Script proposal DTOs only."""

    def propose(self, request: ScriptPlanningRequest) -> ScriptPlanProposal: ...


@dataclass(frozen=True, slots=True)
class ShotRequirementProposal:
    requirement_id: str
    script_section_ref: str
    purpose: str
    subject: str
    action: str | None = None
    environment: str | None = None
    framing: str | None = None
    camera_motion: str | None = None
    target_duration: MediaTime | None = None
    minimum_duration: MediaTime | None = None
    audio_dialogue_requirement: str | None = None
    continuity_hint: str | None = None
    visual_constraints: tuple[str, ...] = ()
    priority: str = "recommended"
    backup_intent: str | None = None
    capture_instruction: str | None = None
    alternate_coverage: tuple[str, ...] = ()
    handle_before: MediaTime | None = None
    handle_after: MediaTime | None = None


@dataclass(frozen=True, slots=True)
class ShootingPlanProposal:
    requirements: tuple[ShotRequirementProposal, ...]
    notes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ShootingPlanningRequest:
    brief: Brief
    script_plan: ScriptPlan
    constraints: ProductionConstraints
    current_shooting_plan: ShootingPlan | None = None
    instruction: str | None = None
    policy_guidance: PlanningPolicyGuidance | None = None

    def __post_init__(self) -> None:
        _validate_instruction(self.instruction)
        brief_ref = _entity_ref(self.brief)
        script_ref = _entity_ref(self.script_plan)
        if self.script_plan.brief_ref != brief_ref:
            raise ValueError("script_plan must reference the exact Brief revision in the request")
        if (
            self.current_shooting_plan is not None
            and self.current_shooting_plan.script_plan_ref != script_ref
        ):
            raise ValueError(
                "current_shooting_plan must reference the exact ScriptPlan revision in the request"
            )


class ShootingPlanningPort(Protocol):
    """Replaceable model/provider seam that cannot rewrite ProductionConstraints."""

    def propose(self, request: ShootingPlanningRequest) -> ShootingPlanProposal: ...

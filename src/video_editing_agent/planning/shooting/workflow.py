from __future__ import annotations

from video_editing_agent.application.ports.brief_repository import BriefRepository
from video_editing_agent.application.ports.preproduction_planning import (
    ShootingPlanningPort,
    ShootingPlanningRequest,
    ShotRequirementProposal,
)
from video_editing_agent.application.ports.script_plan_repository import ScriptPlanRepository
from video_editing_agent.application.ports.shooting_plan_repository import ShootingPlanRepository
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shooting.model import (
    CoveragePriority,
    ProductionConstraints,
    ShootingPlan,
    ShotRequirement,
)
from video_editing_agent.planning.shooting.service import ShootingPlanner


def _requirement_from_proposal(proposal: ShotRequirementProposal) -> ShotRequirement:
    try:
        priority = CoveragePriority(proposal.priority)
    except ValueError as exc:
        raise ValueError(f"invalid ShotRequirement priority: {proposal.priority!r}") from exc
    return ShotRequirement(
        requirement_id=proposal.requirement_id,
        script_section_ref=proposal.script_section_ref,
        purpose=proposal.purpose,
        subject=proposal.subject,
        action=proposal.action,
        environment=proposal.environment,
        framing=proposal.framing,
        camera_motion=proposal.camera_motion,
        target_duration=proposal.target_duration,
        minimum_duration=proposal.minimum_duration,
        audio_dialogue_requirement=proposal.audio_dialogue_requirement,
        continuity_hint=proposal.continuity_hint,
        visual_constraints=proposal.visual_constraints,
        priority=priority,
        backup_intent=proposal.backup_intent,
        capture_instruction=proposal.capture_instruction,
        alternate_coverage=proposal.alternate_coverage,
        handle_before=proposal.handle_before,
        handle_after=proposal.handle_after,
    )


def _requirements_from_proposal(
    proposals: tuple[ShotRequirementProposal, ...],
) -> tuple[ShotRequirement, ...]:
    if not proposals:
        raise ValueError("ShootingPlan proposal must contain at least one ShotRequirement")
    return tuple(_requirement_from_proposal(proposal) for proposal in proposals)


class ShootingPlanningWorkflow:
    """Proposal -> deterministic validation -> ShootingPlanner owner commit."""

    def __init__(
        self,
        *,
        brief_repository: BriefRepository,
        script_plan_repository: ScriptPlanRepository,
        shooting_plan_repository: ShootingPlanRepository,
        planning_port: ShootingPlanningPort,
        planner: ShootingPlanner,
    ) -> None:
        self._brief_repository = brief_repository
        self._script_plan_repository = script_plan_repository
        self._shooting_plan_repository = shooting_plan_repository
        self._planning_port = planning_port
        self._planner = planner

    def generate(
        self,
        script_plan_ref: EntityRevisionRef,
        constraints: ProductionConstraints,
        *,
        created_by: str = "model-proposal",
    ) -> ShootingPlan:
        script_plan = self._script_plan_repository.load(script_plan_ref)
        brief = self._brief_repository.load(script_plan.brief_ref)
        proposal = self._planning_port.propose(
            ShootingPlanningRequest(
                brief=brief,
                script_plan=script_plan,
                constraints=constraints,
            )
        )
        requirements = _requirements_from_proposal(proposal.requirements)
        return self._planner.create(
            script_plan_ref,
            requirements,
            constraints=constraints,
            notes=proposal.notes,
            created_by=created_by,
        )

    def revise(
        self,
        current_ref: EntityRevisionRef,
        instruction: str,
        *,
        script_plan_ref: EntityRevisionRef | None = None,
        constraints: ProductionConstraints | None = None,
        created_by: str = "model-proposal",
    ) -> ShootingPlan:
        if not instruction.strip():
            raise ValueError("instruction must not be empty")
        current = self._shooting_plan_repository.load(current_ref)
        target_script_ref = script_plan_ref or current.script_plan_ref
        script_plan = self._script_plan_repository.load(target_script_ref)
        brief = self._brief_repository.load(script_plan.brief_ref)
        effective_constraints = current.constraints if constraints is None else constraints
        proposal = self._planning_port.propose(
            ShootingPlanningRequest(
                brief=brief,
                script_plan=script_plan,
                constraints=effective_constraints,
                current_shooting_plan=current,
                instruction=instruction,
            )
        )
        requirements = _requirements_from_proposal(proposal.requirements)
        return self._planner.revise(
            current_ref,
            requirements,
            script_plan_ref=target_script_ref,
            constraints=effective_constraints,
            notes=proposal.notes,
            created_by=created_by,
        )

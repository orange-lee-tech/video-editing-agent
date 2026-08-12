from __future__ import annotations

from video_editing_agent.application.ports.brief_repository import BriefRepository
from video_editing_agent.application.ports.preproduction_planning import (
    PlanningPolicyGuidance,
    ReferenceStyleGuidance,
    ShootingPlanningPort,
    ShootingPlanningRequest,
    ShootingPlanProposal,
    ShotRequirementProposal,
)
from video_editing_agent.application.ports.preproduction_review import (
    ShootingProposalReview,
    ShootingProposalReviewPort,
    ShootingProposalReviewRequest,
)
from video_editing_agent.application.ports.script_plan_repository import ScriptPlanRepository
from video_editing_agent.application.ports.shooting_plan_repository import ShootingPlanRepository
from video_editing_agent.domain.brief.model import Brief
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.script.model import ScriptPlan
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
        location_ref=proposal.location_ref,
        environment_description=proposal.environment_description,
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


def _brief_requires_review(brief: Brief, constraints: ProductionConstraints) -> bool:
    return bool(
        brief.authoritative_facts
        or brief.prohibited_content
        or brief.brand_constraints
        or constraints.locations
    )


def _review_summary(review: ShootingProposalReview) -> str:
    return "; ".join(
        f"{violation.code}@{violation.requirement_id or 'plan'}: {violation.reason}"
        for violation in review.violations
    )


class ShootingProposalRejectedError(ValueError):
    """A semantic reviewer vetoed the proposal before owner commit."""

    def __init__(self, review: ShootingProposalReview) -> None:
        self.review = review
        super().__init__(f"Shooting proposal rejected: {_review_summary(review)}")


class ShootingPlanningWorkflow:
    """Proposal -> deterministic preflight -> semantic review -> owner commit."""

    def __init__(
        self,
        *,
        brief_repository: BriefRepository,
        script_plan_repository: ScriptPlanRepository,
        shooting_plan_repository: ShootingPlanRepository,
        planning_port: ShootingPlanningPort,
        planner: ShootingPlanner,
        review_port: ShootingProposalReviewPort | None = None,
    ) -> None:
        self._brief_repository = brief_repository
        self._script_plan_repository = script_plan_repository
        self._shooting_plan_repository = shooting_plan_repository
        self._planning_port = planning_port
        self._planner = planner
        self._review_port = review_port

    def _review_or_raise(
        self,
        *,
        brief: Brief,
        script_plan: ScriptPlan,
        constraints: ProductionConstraints,
        proposal: ShootingPlanProposal,
        current_shooting_plan: ShootingPlan | None,
        instruction: str | None,
        policy_guidance: PlanningPolicyGuidance | None,
    ) -> None:
        if self._review_port is None:
            if _brief_requires_review(brief, constraints):
                raise RuntimeError(
                    "guarded Shooting proposal requires ShootingProposalReviewPort before model "
                    "proposal commit"
                )
            return
        review = self._review_port.review(
            ShootingProposalReviewRequest(
                brief=brief,
                script_plan=script_plan,
                constraints=constraints,
                proposal=proposal,
                current_shooting_plan=current_shooting_plan,
                instruction=instruction,
                policy_guidance=policy_guidance,
            )
        )
        if not review.accepted:
            raise ShootingProposalRejectedError(review)

    def generate(
        self,
        script_plan_ref: EntityRevisionRef,
        constraints: ProductionConstraints,
        *,
        policy_guidance: PlanningPolicyGuidance | None = None,
        reference_guidance: tuple[ReferenceStyleGuidance, ...] = (),
        created_by: str = "model-proposal",
    ) -> ShootingPlan:
        script_plan = self._script_plan_repository.load(script_plan_ref)
        brief = self._brief_repository.load(script_plan.brief_ref)
        proposal = self._planning_port.propose(
            ShootingPlanningRequest(
                brief=brief,
                script_plan=script_plan,
                constraints=constraints,
                policy_guidance=policy_guidance,
                reference_guidance=reference_guidance,
            )
        )
        requirements = _requirements_from_proposal(proposal.requirements)
        self._planner.validate_create(
            script_plan_ref,
            requirements,
            constraints=constraints,
            notes=proposal.notes,
        )
        self._review_or_raise(
            brief=brief,
            script_plan=script_plan,
            constraints=constraints,
            proposal=proposal,
            current_shooting_plan=None,
            instruction=None,
            policy_guidance=policy_guidance,
        )
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
        policy_guidance: PlanningPolicyGuidance | None = None,
        reference_guidance: tuple[ReferenceStyleGuidance, ...] = (),
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
                policy_guidance=policy_guidance,
                reference_guidance=reference_guidance,
            )
        )
        requirements = _requirements_from_proposal(proposal.requirements)
        self._planner.validate_revision(
            current_ref,
            requirements,
            script_plan_ref=target_script_ref,
            constraints=effective_constraints,
            notes=proposal.notes,
        )
        self._review_or_raise(
            brief=brief,
            script_plan=script_plan,
            constraints=effective_constraints,
            proposal=proposal,
            current_shooting_plan=current,
            instruction=instruction,
            policy_guidance=policy_guidance,
        )
        return self._planner.revise(
            current_ref,
            requirements,
            script_plan_ref=target_script_ref,
            constraints=effective_constraints,
            notes=proposal.notes,
            created_by=created_by,
        )

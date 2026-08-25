from __future__ import annotations

from video_editing_agent.application.ports.brief_repository import BriefRepository
from video_editing_agent.application.ports.preproduction_planning import (
    NarrativeSectionProposal,
    PlanningPolicyGuidance,
    ReferenceStyleGuidance,
    ScriptPlanningPort,
    ScriptPlanningRequest,
    ScriptPlanProposal,
)
from video_editing_agent.application.ports.preproduction_review import (
    ScriptProposalReview,
    ScriptProposalReviewPort,
    ScriptProposalReviewRequest,
)
from video_editing_agent.application.ports.script_plan_repository import ScriptPlanRepository
from video_editing_agent.domain.brief.model import Brief
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.script.model import NarrativeSection, ScriptPlan
from video_editing_agent.planning.script.service import ScriptPlanner


def _section_from_proposal(proposal: NarrativeSectionProposal) -> NarrativeSection:
    return NarrativeSection(
        section_id=proposal.section_id,
        narrative_role=proposal.narrative_role,
        information_goal=proposal.information_goal,
        spoken_content=proposal.spoken_content,
        visual_requirement=proposal.visual_requirement,
        target_duration=proposal.target_duration,
        on_screen_text_intent=proposal.on_screen_text_intent,
        emotion=proposal.emotion,
        pacing=proposal.pacing,
        music_intent=proposal.music_intent,
        editing_intent=proposal.editing_intent,
        importance=proposal.importance,
        protected_fact_ids=proposal.protected_fact_ids,
        locked=proposal.locked,
    )


def _sections_from_proposal(
    proposals: tuple[NarrativeSectionProposal, ...],
) -> tuple[NarrativeSection, ...]:
    if not proposals:
        raise ValueError("ScriptPlan proposal must contain at least one NarrativeSection")
    return tuple(_section_from_proposal(proposal) for proposal in proposals)


def _brief_requires_review(brief: Brief) -> bool:
    return bool(brief.authoritative_facts or brief.prohibited_content or brief.brand_constraints)


def _review_summary(review: ScriptProposalReview) -> str:
    return "; ".join(
        f"{violation.code}@{violation.section_id or 'plan'}: {violation.reason}"
        for violation in review.violations
    )


def _repair_instruction(review: ScriptProposalReview, original: str | None) -> str:
    diagnostics = "\n".join(
        f"- code={violation.code}; section_id={violation.section_id or 'plan'}; "
        f"reason={violation.reason}"
        + (f"; excerpt={violation.excerpt}" if violation.excerpt is not None else "")
        for violation in review.violations
    )
    original_instruction = original or "Create a new proposal."
    return (
        f"Original instruction: {original_instruction}\n"
        "The semantic reviewer feedback below identifies defects only. It is not an "
        "authoritative product fact and must not be used as support for new claims. Regenerate the "
        "proposal under the ORIGINAL Brief, authoritative facts, constraints, policy, reference "
        "guidance, and current revision authority. For every unsupported-claim violation, remove "
        "the unsupported semantic property itself. Do not paraphrase it, replace it with a "
        "synonym, or soften its wording while retaining the same implication. After removing the "
        "unsupported property, you may preserve the Brief's positioning intent only through "
        "non-claim framing or a neutral observable action/state that does not assert a successful "
        "fit, adequacy, ease, convenience, operability, or outcome. For example, an unsupported "
        "commute-convenience idea may show a person placing, carrying, or taking out the product in "
        "a commute setting, but must not say or imply that doing so is easy, convenient, adequate, "
        "or that the product fits successfully. Do not turn a neutral action into a demonstration "
        "of the unsupported result. Reviewer diagnostics are non-authoritative and cannot support "
        "replacement facts. Do not change locked or authoritative state.\n"
        f"Reviewer diagnostics:\n{diagnostics}"
    )


class ScriptProposalRejectedError(ValueError):
    """A semantic reviewer vetoed the proposal before owner commit."""

    def __init__(self, review: ScriptProposalReview) -> None:
        self.review = review
        super().__init__(f"Script proposal rejected: {_review_summary(review)}")


class ScriptPlanningWorkflow:
    """Proposal -> deterministic preflight -> semantic review -> owner commit."""

    def __init__(
        self,
        *,
        brief_repository: BriefRepository,
        script_plan_repository: ScriptPlanRepository,
        planning_port: ScriptPlanningPort,
        planner: ScriptPlanner,
        review_port: ScriptProposalReviewPort | None = None,
    ) -> None:
        self._brief_repository = brief_repository
        self._script_plan_repository = script_plan_repository
        self._planning_port = planning_port
        self._planner = planner
        self._review_port = review_port

    def _review(
        self,
        *,
        brief: Brief,
        proposal: ScriptPlanProposal,
        current_script: ScriptPlan | None,
        instruction: str | None,
        policy_guidance: PlanningPolicyGuidance | None,
    ) -> ScriptProposalReview | None:
        if self._review_port is None:
            if _brief_requires_review(brief):
                raise RuntimeError(
                    "guarded Brief requires ScriptProposalReviewPort before model proposal commit"
                )
            return None
        return self._review_port.review(
            ScriptProposalReviewRequest(
                brief=brief,
                proposal=proposal,
                current_script=current_script,
                instruction=instruction,
                policy_guidance=policy_guidance,
            )
        )

    def generate(
        self,
        brief_ref: EntityRevisionRef,
        *,
        policy_guidance: PlanningPolicyGuidance | None = None,
        reference_guidance: tuple[ReferenceStyleGuidance, ...] = (),
        created_by: str = "model-proposal",
    ) -> ScriptPlan:
        brief = self._brief_repository.load(brief_ref)
        request = ScriptPlanningRequest(
            brief=brief,
            policy_guidance=policy_guidance,
            reference_guidance=reference_guidance,
        )
        for attempt in range(2):
            proposal = self._planning_port.propose(request)
            sections = _sections_from_proposal(proposal.sections)
            self._planner.validate_create(brief_ref, sections)
            review = self._review(
                brief=brief,
                proposal=proposal,
                current_script=None,
                instruction=request.instruction,
                policy_guidance=policy_guidance,
            )
            if review is None or review.accepted:
                break
            if attempt == 1:
                raise ScriptProposalRejectedError(review)
            request = ScriptPlanningRequest(
                brief=brief,
                instruction=_repair_instruction(review, None),
                policy_guidance=policy_guidance,
                reference_guidance=reference_guidance,
            )
        return self._planner.create(brief_ref, sections, created_by=created_by)

    def revise(
        self,
        current_ref: EntityRevisionRef,
        instruction: str,
        *,
        policy_guidance: PlanningPolicyGuidance | None = None,
        reference_guidance: tuple[ReferenceStyleGuidance, ...] = (),
        created_by: str = "model-proposal",
    ) -> ScriptPlan:
        if not instruction.strip():
            raise ValueError("instruction must not be empty")
        current = self._script_plan_repository.load(current_ref)
        brief = self._brief_repository.load(current.brief_ref)
        request = ScriptPlanningRequest(
            brief=brief,
            current_script=current,
            instruction=instruction,
            policy_guidance=policy_guidance,
            reference_guidance=reference_guidance,
        )
        for attempt in range(2):
            proposal = self._planning_port.propose(request)
            sections = _sections_from_proposal(proposal.sections)
            self._planner.validate_revision(current_ref, sections)
            review = self._review(
                brief=brief,
                proposal=proposal,
                current_script=current,
                instruction=request.instruction,
                policy_guidance=policy_guidance,
            )
            if review is None or review.accepted:
                break
            if attempt == 1:
                raise ScriptProposalRejectedError(review)
            request = ScriptPlanningRequest(
                brief=brief,
                current_script=current,
                instruction=_repair_instruction(review, instruction),
                policy_guidance=policy_guidance,
                reference_guidance=reference_guidance,
            )
        return self._planner.revise(
            current_ref,
            sections,
            created_by=created_by,
        )

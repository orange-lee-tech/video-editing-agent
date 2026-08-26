from __future__ import annotations

from dataclasses import replace

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
        "commute-convenience idea may show a person placing, carrying, or taking out the product "
        "in a commute setting, but must not say or imply that doing so is easy, convenient, "
        "adequate, or that the product fits successfully. Do not turn a neutral action into a "
        "demonstration of the unsupported result. Reviewer diagnostics are non-authoritative and "
        "cannot support replacement facts. Do not change locked or authoritative state.\n"
        f"Reviewer diagnostics:\n{diagnostics}"
    )


def _is_unsupported_claim_review(review: ScriptProposalReview) -> bool:
    if not review.violations:
        return False
    for violation in review.violations:
        code = violation.code.casefold()
        if code != "unsupported_claim" and not (
            code.startswith("unsupported_") and "claim" in code
        ):
            return False
    return True


def _fallback_role(narrative_role: str) -> str:
    role = narrative_role.casefold()
    if any(token in role for token in ("demo", "demonstr", "proof", "feature", "detail")):
        return "demonstration"
    if any(token in role for token in ("hook", "open", "intro")):
        return "hook"
    if any(token in role for token in ("closing", "close", "outro", "ending", "end", "cta")):
        return "closing"
    return "body"


def _fallback_role_priority(narrative_role: str) -> int:
    return {
        "demonstration": 0,
        "body": 1,
        "hook": 2,
        "closing": 3,
    }[_fallback_role(narrative_role)]


def _fallback_fact_owners(
    proposal: ScriptPlanProposal,
    targeted_ids: set[str],
    *,
    sanitize_all: bool,
    facts_by_id: dict[str, str],
) -> dict[str, str]:
    owners: dict[str, tuple[int, int, str]] = {}
    for index, section in enumerate(proposal.sections):
        if not sanitize_all and section.section_id not in targeted_ids:
            continue
        priority = _fallback_role_priority(section.narrative_role)
        for fact_id in section.protected_fact_ids:
            if fact_id not in facts_by_id:
                continue
            candidate = (priority, index, section.section_id)
            current = owners.get(fact_id)
            if current is None or candidate < current:
                owners[fact_id] = candidate
    return {fact_id: candidate[2] for fact_id, candidate in owners.items()}


def _brief_output_language(brief: Brief) -> str:
    text = " ".join(
        value
        for value in (
            brief.title,
            brief.objective,
            brief.audience,
            brief.platform,
            brief.core_message,
            brief.product_topic or "",
            brief.user_notes or "",
            *(fact.statement for fact in brief.authoritative_facts),
        )
        if value
    )
    cjk = sum("\u3400" <= char <= "\u9fff" for char in text)
    latin = sum(char.isascii() and char.isalpha() for char in text)
    return "zh-CN" if cjk >= latin else "en"


def _claim_free_fallback_content(
    narrative_role: str,
    exact_fact_text: str,
    language: str,
) -> tuple[str, str | None, str, str | None]:
    role = _fallback_role(narrative_role)
    if language == "zh-CN":
        if role == "hook":
            return (
                "用不包含产品性能断言的方式快速建立主体。",
                None,
                "先清楚展示产品本身，不演示是否装得下、是否方便、是否易用或任何结果。",
                None,
            )
        if role == "demonstration":
            return (
                "展示可直接观察的产品细节，并且只陈述分配给本段的已确认事实。",
                exact_fact_text or None,
                "用近景或中景展示产品外观与可见细节，不安排便利性、适配性、性能或结果演示。",
                None,
            )
        if role == "closing":
            return (
                "用稳定的产品画面收尾，不增加新的产品事实或性能断言。",
                None,
                "最后保持一个稳定、干净的产品画面，不增加便利性、适配性、性能或结果演示。",
                None,
            )
        return (
            "继续展示产品可直接观察的内容，不增加未经证实的产品断言。",
            exact_fact_text or None,
            "使用中性的产品画面，不演示便利性、适配性、性能或任何结果。",
            None,
        )
    if role == "hook":
        return (
            "Open with a claim-free product reveal that establishes the subject immediately.",
            None,
            "Begin with a clear neutral product reveal. Do not demonstrate fit, ease, "
            "performance, or any outcome.",
            None,
        )
    if role == "demonstration":
        return (
            "Show neutral observable product details and state only any verified fact assigned "
            "to this section.",
            exact_fact_text or None,
            "Show close or medium detail coverage of visible product form. Do not stage a fit, "
            "ease, performance, or outcome demonstration.",
            None,
        )
    if role == "closing":
        return (
            "Close with a stable product view without adding a new product claim.",
            None,
            "End on a stable neutral product view. Do not add a fit, ease, performance, or "
            "outcome demonstration.",
            None,
        )
    return (
        "Continue with neutral product coverage without adding an unsupported product claim.",
        exact_fact_text or None,
        "Use neutral coverage of visible product form without demonstrating fit, ease, "
        "performance, or any outcome.",
        None,
    )


def _deterministic_claim_fallback(
    brief: Brief,
    proposal: ScriptPlanProposal,
    review: ScriptProposalReview,
    *,
    current_script: ScriptPlan | None,
) -> ScriptPlanProposal | None:
    """Strip repeatedly vetoed claim-bearing copy without inventing replacement facts."""

    if not _is_unsupported_claim_review(review):
        return None

    targeted_ids = {
        violation.section_id for violation in review.violations if violation.section_id is not None
    }
    sanitize_all = any(violation.section_id is None for violation in review.violations)
    if current_script is not None:
        locked_ids = set(current_script.locked_section_ids)
        if (sanitize_all and locked_ids) or targeted_ids.intersection(locked_ids):
            return None

    facts_by_id = {fact.fact_id: fact.statement for fact in brief.authoritative_facts}
    fact_owners = _fallback_fact_owners(
        proposal,
        targeted_ids,
        sanitize_all=sanitize_all,
        facts_by_id=facts_by_id,
    )
    language = _brief_output_language(brief)
    sanitized: list[NarrativeSectionProposal] = []
    for section in proposal.sections:
        if not sanitize_all and section.section_id not in targeted_ids:
            sanitized.append(section)
            continue

        fact_statements = tuple(
            facts_by_id[fact_id]
            for fact_id in section.protected_fact_ids
            if fact_id in facts_by_id and fact_owners.get(fact_id) == section.section_id
        )
        exact_fact_text = " ".join(fact_statements).strip()
        information_goal, spoken_content, visual_requirement, on_screen_text_intent = (
            _claim_free_fallback_content(section.narrative_role, exact_fact_text, language)
        )

        sanitized.append(
            replace(
                section,
                information_goal=information_goal,
                spoken_content=spoken_content,
                visual_requirement=visual_requirement,
                on_screen_text_intent=on_screen_text_intent,
                editing_intent=None,
            )
        )
    return ScriptPlanProposal(tuple(sanitized))


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
                fallback = _deterministic_claim_fallback(
                    brief,
                    proposal,
                    review,
                    current_script=None,
                )
                if fallback is None:
                    raise ScriptProposalRejectedError(review)
                fallback_sections = _sections_from_proposal(fallback.sections)
                self._planner.validate_create(brief_ref, fallback_sections)
                fallback_review = self._review(
                    brief=brief,
                    proposal=fallback,
                    current_script=None,
                    instruction="Deterministic conservative fallback after repeated claim veto.",
                    policy_guidance=policy_guidance,
                )
                if fallback_review is not None and not fallback_review.accepted:
                    raise ScriptProposalRejectedError(fallback_review)
                sections = fallback_sections
                break
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
                fallback = _deterministic_claim_fallback(
                    brief,
                    proposal,
                    review,
                    current_script=current,
                )
                if fallback is None:
                    raise ScriptProposalRejectedError(review)
                fallback_sections = _sections_from_proposal(fallback.sections)
                self._planner.validate_revision(current_ref, fallback_sections)
                fallback_review = self._review(
                    brief=brief,
                    proposal=fallback,
                    current_script=current,
                    instruction="Deterministic conservative fallback after repeated claim veto.",
                    policy_guidance=policy_guidance,
                )
                if fallback_review is not None and not fallback_review.accepted:
                    raise ScriptProposalRejectedError(fallback_review)
                sections = fallback_sections
                break
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

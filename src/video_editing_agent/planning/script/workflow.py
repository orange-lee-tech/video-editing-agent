from __future__ import annotations

from video_editing_agent.application.ports.brief_repository import BriefRepository
from video_editing_agent.application.ports.preproduction_planning import (
    NarrativeSectionProposal,
    ScriptPlanningPort,
    ScriptPlanningRequest,
)
from video_editing_agent.application.ports.script_plan_repository import ScriptPlanRepository
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


class ScriptPlanningWorkflow:
    """Proposal -> deterministic validation -> ScriptPlanner owner commit."""

    def __init__(
        self,
        *,
        brief_repository: BriefRepository,
        script_plan_repository: ScriptPlanRepository,
        planning_port: ScriptPlanningPort,
        planner: ScriptPlanner,
    ) -> None:
        self._brief_repository = brief_repository
        self._script_plan_repository = script_plan_repository
        self._planning_port = planning_port
        self._planner = planner

    def generate(
        self,
        brief_ref: EntityRevisionRef,
        *,
        created_by: str = "model-proposal",
    ) -> ScriptPlan:
        brief = self._brief_repository.load(brief_ref)
        proposal = self._planning_port.propose(ScriptPlanningRequest(brief=brief))
        sections = _sections_from_proposal(proposal.sections)
        return self._planner.create(brief_ref, sections, created_by=created_by)

    def revise(
        self,
        current_ref: EntityRevisionRef,
        instruction: str,
        *,
        created_by: str = "model-proposal",
    ) -> ScriptPlan:
        if not instruction.strip():
            raise ValueError("instruction must not be empty")
        current = self._script_plan_repository.load(current_ref)
        brief = self._brief_repository.load(current.brief_ref)
        proposal = self._planning_port.propose(
            ScriptPlanningRequest(
                brief=brief,
                current_script=current,
                instruction=instruction,
            )
        )
        sections = _sections_from_proposal(proposal.sections)
        return self._planner.revise(
            current_ref,
            sections,
            created_by=created_by,
        )

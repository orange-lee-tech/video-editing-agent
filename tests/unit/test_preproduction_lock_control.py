from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.application.ports.preproduction_planning import (
    NarrativeSectionProposal,
    ScriptPlanProposal,
)
from video_editing_agent.application.ports.preproduction_review import ScriptProposalReview
from video_editing_agent.domain.brief.model import AuthoritativeFact
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.script.model import NarrativeSection
from video_editing_agent.planning.brief.service import BriefContent, BriefService
from video_editing_agent.planning.script.service import ScriptPlanner
from video_editing_agent.planning.script.workflow import ScriptPlanningWorkflow
from video_editing_agent.storage.repositories.preproduction_repositories import (
    SqliteBriefRepository,
    SqliteScriptPlanRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase

NOW = datetime(2026, 8, 11, 19, 15, tzinfo=UTC)


class MutableScriptPort:
    def __init__(self, proposal: ScriptPlanProposal) -> None:
        self.proposal = proposal

    def propose(self, request):
        del request
        return self.proposal


class AcceptingReviewPort:
    def __init__(self) -> None:
        self.calls = 0

    def review(self, request) -> ScriptProposalReview:
        del request
        self.calls += 1
        return ScriptProposalReview(accepted=True)


def setup(tmp_path: Path):
    database = SqliteProjectDatabase(tmp_path / "project.sqlite3")
    database.initialize()
    briefs = SqliteBriefRepository(database)
    scripts = SqliteScriptPlanRepository(database)
    brief = BriefService(
        briefs,
        brief_id_factory=lambda: "brf_lock_control",
        clock=lambda: NOW,
    ).create(
        BriefContent(
            title="Launch",
            objective="Explain value",
            audience="Buyer",
            platform="short-form",
            core_message="Approved value",
            authoritative_facts=(AuthoritativeFact("fact_price", "Price is 99 USD."),),
        )
    )
    planner = ScriptPlanner(
        brief_repository=briefs,
        script_plan_repository=scripts,
        script_plan_id_factory=lambda: "scp_lock_control",
        clock=lambda: NOW,
    )
    return briefs, scripts, brief, planner


def test_explicit_lock_and_unlock_are_revisioned_user_operations(tmp_path: Path) -> None:
    _, scripts, brief, planner = setup(tmp_path)
    brief_ref = EntityRevisionRef(brief.envelope.id, 1)
    first = planner.create(
        brief_ref,
        (
            NarrativeSection(
                "hook",
                "hook",
                "Earn attention",
                spoken_content="Original hook",
                protected_fact_ids=("fact_price",),
            ),
        ),
    )
    first_ref = EntityRevisionRef(first.envelope.id, 1)

    locked = planner.set_section_lock(first_ref, "hook", locked=True, created_by="user")
    locked_ref = EntityRevisionRef(locked.envelope.id, 2)
    unlocked = planner.set_section_lock(locked_ref, "hook", locked=False, created_by="user")

    assert locked.envelope.revision == 2
    assert locked.envelope.derived_from == (first_ref, brief_ref)
    assert locked.sections[0].locked is True
    assert unlocked.envelope.revision == 3
    assert unlocked.sections[0].locked is False
    assert scripts.load(first_ref) == first
    assert scripts.load(locked_ref) == locked


def test_automatic_revision_fails_while_locked_then_succeeds_after_user_unlock(
    tmp_path: Path,
) -> None:
    briefs, scripts, brief, planner = setup(tmp_path)
    brief_ref = EntityRevisionRef(brief.envelope.id, 1)
    first = planner.create(
        brief_ref,
        (NarrativeSection("hook", "hook", "Earn attention", spoken_content="Approved"),),
    )
    first_ref = EntityRevisionRef(first.envelope.id, 1)
    locked = planner.set_section_lock(first_ref, "hook", locked=True)
    locked_ref = EntityRevisionRef(locked.envelope.id, 2)
    port = MutableScriptPort(
        ScriptPlanProposal(
            (
                NarrativeSectionProposal(
                    "hook",
                    "hook",
                    "Earn attention",
                    spoken_content="Model revision",
                    locked=True,
                ),
            )
        )
    )
    reviewer = AcceptingReviewPort()
    workflow = ScriptPlanningWorkflow(
        brief_repository=briefs,
        script_plan_repository=scripts,
        planning_port=port,
        planner=planner,
        review_port=reviewer,
    )

    with pytest.raises(ValueError, match="locked section"):
        workflow.revise(locked_ref, "rewrite the hook")
    assert reviewer.calls == 0

    unlocked = planner.set_section_lock(locked_ref, "hook", locked=False)
    unlocked_ref = EntityRevisionRef(unlocked.envelope.id, 3)
    port.proposal = ScriptPlanProposal(
        (
            NarrativeSectionProposal(
                "hook",
                "hook",
                "Earn attention",
                spoken_content="Model revision",
                locked=False,
            ),
        )
    )
    revised = workflow.revise(unlocked_ref, "rewrite the hook")

    assert reviewer.calls == 1
    assert revised.envelope.revision == 4
    assert revised.sections[0].spoken_content == "Model revision"
    assert revised.sections[0].locked is False
    assert briefs.load(brief_ref).authoritative_facts == brief.authoritative_facts


def test_lock_operation_rejects_unknown_section_without_new_revision(tmp_path: Path) -> None:
    _, scripts, brief, planner = setup(tmp_path)
    first = planner.create(
        EntityRevisionRef(brief.envelope.id, 1),
        (NarrativeSection("body", "body", "Explain value"),),
    )
    first_ref = EntityRevisionRef(first.envelope.id, 1)

    with pytest.raises(ValueError, match="unknown Script section"):
        planner.set_section_lock(first_ref, "missing", locked=True)
    with pytest.raises(KeyError):
        scripts.load(EntityRevisionRef(first.envelope.id, 2))

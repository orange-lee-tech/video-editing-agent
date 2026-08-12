from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.application.ports.preproduction_planning import (
    NarrativeSectionProposal,
    ScriptPlanningRequest,
    ScriptPlanProposal,
    ShootingPlanningRequest,
    ShootingPlanProposal,
    ShotRequirementProposal,
)
from video_editing_agent.application.ports.preproduction_review import (
    ScriptProposalReview,
    ShootingProposalReview,
)
from video_editing_agent.domain.brief.model import AuthoritativeFact
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.script.model import NarrativeSection
from video_editing_agent.domain.shooting.model import ProductionConstraints
from video_editing_agent.planning.brief.service import BriefContent, BriefService
from video_editing_agent.planning.script.service import ScriptPlanner
from video_editing_agent.planning.script.workflow import ScriptPlanningWorkflow
from video_editing_agent.planning.shooting.service import ShootingPlanner
from video_editing_agent.planning.shooting.workflow import ShootingPlanningWorkflow
from video_editing_agent.storage.repositories.preproduction_repositories import (
    SqliteBriefRepository,
    SqliteScriptPlanRepository,
    SqliteShootingPlanRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase

NOW = datetime(2026, 8, 11, 19, 0, tzinfo=UTC)


class StaticScriptPlanningPort:
    def __init__(self, proposal: ScriptPlanProposal) -> None:
        self.proposal = proposal
        self.requests: list[ScriptPlanningRequest] = []

    def propose(self, request: ScriptPlanningRequest) -> ScriptPlanProposal:
        self.requests.append(request)
        return self.proposal


class AcceptingScriptReviewPort:
    def review(self, request) -> ScriptProposalReview:
        del request
        return ScriptProposalReview(accepted=True)


class StaticShootingPlanningPort:
    def __init__(self, proposal: ShootingPlanProposal) -> None:
        self.proposal = proposal
        self.requests: list[ShootingPlanningRequest] = []

    def propose(self, request: ShootingPlanningRequest) -> ShootingPlanProposal:
        self.requests.append(request)
        return self.proposal


class AcceptingShootingReviewPort:
    def review(self, request) -> ShootingProposalReview:
        del request
        return ShootingProposalReview(accepted=True)


def repositories(path: Path):
    database = SqliteProjectDatabase(path)
    database.initialize()
    return (
        SqliteBriefRepository(database),
        SqliteScriptPlanRepository(database),
        SqliteShootingPlanRepository(database),
    )


def create_brief(briefs: SqliteBriefRepository, *, brief_id: str = "brf_proposal"):
    return BriefService(
        briefs,
        brief_id_factory=lambda: brief_id,
        clock=lambda: NOW,
    ).create(
        BriefContent(
            title="Launch clip",
            objective="Drive consideration",
            audience="First-time buyers",
            platform="short-form vertical",
            core_message="Simple to use",
            target_duration=MediaTime(30, 1),
            authoritative_facts=(AuthoritativeFact("fact_price", "Approved price is 99 USD."),),
        )
    )


def script_workflow(
    briefs: SqliteBriefRepository,
    scripts: SqliteScriptPlanRepository,
    port: StaticScriptPlanningPort,
    *,
    script_id: str = "scp_proposal",
) -> ScriptPlanningWorkflow:
    planner = ScriptPlanner(
        brief_repository=briefs,
        script_plan_repository=scripts,
        script_plan_id_factory=lambda: script_id,
        clock=lambda: NOW,
    )
    return ScriptPlanningWorkflow(
        brief_repository=briefs,
        script_plan_repository=scripts,
        planning_port=port,
        planner=planner,
        review_port=AcceptingScriptReviewPort(),
    )


def test_script_provider_proposal_commits_only_through_owner(tmp_path: Path) -> None:
    briefs, scripts, _ = repositories(tmp_path / "project.sqlite3")
    brief = create_brief(briefs)
    brief_ref = EntityRevisionRef(brief.envelope.id, 1)
    port = StaticScriptPlanningPort(
        ScriptPlanProposal(
            sections=(
                NarrativeSectionProposal(
                    section_id="hook",
                    narrative_role="hook",
                    information_goal="Earn attention",
                    spoken_content="Only 99 USD.",
                    protected_fact_ids=("fact_price",),
                ),
            )
        )
    )

    script = script_workflow(briefs, scripts, port).generate(brief_ref)

    assert script.envelope.id == "scp_proposal"
    assert script.brief_ref == brief_ref
    assert scripts.load(EntityRevisionRef("scp_proposal", 1)) == script
    assert port.requests[0].brief == brief


def test_script_proposal_cannot_reference_unknown_authoritative_fact(tmp_path: Path) -> None:
    briefs, scripts, _ = repositories(tmp_path / "project.sqlite3")
    brief = create_brief(briefs)
    port = StaticScriptPlanningPort(
        ScriptPlanProposal(
            sections=(
                NarrativeSectionProposal(
                    "proof",
                    "proof",
                    "State a claim",
                    protected_fact_ids=("fact_invented",),
                ),
            )
        )
    )

    with pytest.raises(ValueError, match="unknown protected facts"):
        script_workflow(briefs, scripts, port).generate(EntityRevisionRef(brief.envelope.id, 1))
    with pytest.raises(KeyError):
        scripts.load(EntityRevisionRef("scp_proposal", 1))


def test_automated_script_revision_cannot_change_locked_section(tmp_path: Path) -> None:
    briefs, scripts, _ = repositories(tmp_path / "project.sqlite3")
    brief = create_brief(briefs)
    brief_ref = EntityRevisionRef(brief.envelope.id, 1)
    locked = NarrativeSectionProposal(
        "hook",
        "hook",
        "Earn attention",
        spoken_content="Approved hook",
        locked=True,
    )
    body = NarrativeSectionProposal("body", "body", "Explain value", spoken_content="Body")
    port = StaticScriptPlanningPort(ScriptPlanProposal((locked, body)))
    workflow = script_workflow(briefs, scripts, port, script_id="scp_locked_provider")
    first = workflow.generate(brief_ref)

    port.proposal = ScriptPlanProposal(
        (
            NarrativeSectionProposal(
                "hook",
                "hook",
                "Earn attention",
                spoken_content="Model changed the approved hook",
                locked=True,
            ),
            body,
        )
    )
    with pytest.raises(ValueError, match="locked section"):
        workflow.revise(EntityRevisionRef(first.envelope.id, 1), "make the script punchier")
    with pytest.raises(KeyError):
        scripts.load(EntityRevisionRef(first.envelope.id, 2))


def create_script_for_shooting(
    briefs: SqliteBriefRepository,
    scripts: SqliteScriptPlanRepository,
):
    brief = create_brief(briefs, brief_id="brf_shooting_proposal")
    brief_ref = EntityRevisionRef(brief.envelope.id, 1)
    script = ScriptPlanner(
        brief_repository=briefs,
        script_plan_repository=scripts,
        script_plan_id_factory=lambda: "scp_shooting_proposal",
        clock=lambda: NOW,
    ).create(
        brief_ref,
        (
            NarrativeSection(
                "demo",
                "proof",
                "Demonstrate the product",
                target_duration=MediaTime(5, 1),
            ),
        ),
    )
    return brief, script


def shooting_workflow(
    briefs: SqliteBriefRepository,
    scripts: SqliteScriptPlanRepository,
    shooting_plans: SqliteShootingPlanRepository,
    port: StaticShootingPlanningPort,
) -> ShootingPlanningWorkflow:
    planner = ShootingPlanner(
        script_plan_repository=scripts,
        shooting_plan_repository=shooting_plans,
        shooting_plan_id_factory=lambda: "shp_proposal",
        clock=lambda: NOW,
    )
    return ShootingPlanningWorkflow(
        brief_repository=briefs,
        script_plan_repository=scripts,
        shooting_plan_repository=shooting_plans,
        planning_port=port,
        planner=planner,
        review_port=AcceptingShootingReviewPort(),
    )


def test_shooting_provider_cannot_rewrite_user_production_constraints(tmp_path: Path) -> None:
    briefs, scripts, shooting_plans = repositories(tmp_path / "project.sqlite3")
    _, script = create_script_for_shooting(briefs, scripts)
    constraints = ProductionConstraints(
        camera_or_phone="user phone",
        stabilizer="no stabilizer",
        people_count=1,
        locations=("home desk",),
    )
    port = StaticShootingPlanningPort(
        ShootingPlanProposal(
            requirements=(
                ShotRequirementProposal(
                    "req_demo",
                    "demo",
                    "Show operation",
                    "Product and hand",
                    priority="required",
                    capture_instruction="Hold the phone still and operate the product once.",
                ),
            ),
            notes=("Capture one backup take.",),
        )
    )

    plan = shooting_workflow(briefs, scripts, shooting_plans, port).generate(
        EntityRevisionRef(script.envelope.id, 1),
        constraints,
    )

    assert plan.constraints == constraints
    assert port.requests[0].constraints == constraints
    assert plan.requirements[0].priority.value == "required"


def test_invalid_provider_priority_fails_before_shooting_owner_commit(tmp_path: Path) -> None:
    briefs, scripts, shooting_plans = repositories(tmp_path / "project.sqlite3")
    _, script = create_script_for_shooting(briefs, scripts)
    port = StaticShootingPlanningPort(
        ShootingPlanProposal(
            requirements=(
                ShotRequirementProposal(
                    "req_bad",
                    "demo",
                    "Show operation",
                    "Product",
                    priority="mandatory-ish",
                ),
            )
        )
    )

    with pytest.raises(ValueError, match="invalid ShotRequirement priority"):
        shooting_workflow(briefs, scripts, shooting_plans, port).generate(
            EntityRevisionRef(script.envelope.id, 1),
            ProductionConstraints(camera_or_phone="phone"),
        )
    with pytest.raises(KeyError):
        shooting_plans.load(EntityRevisionRef("shp_proposal", 1))


def test_provider_requirement_for_unknown_section_fails_owner_validation(tmp_path: Path) -> None:
    briefs, scripts, shooting_plans = repositories(tmp_path / "project.sqlite3")
    _, script = create_script_for_shooting(briefs, scripts)
    port = StaticShootingPlanningPort(
        ShootingPlanProposal(
            requirements=(
                ShotRequirementProposal(
                    "req_missing",
                    "not-a-section",
                    "Show something",
                    "Product",
                ),
            )
        )
    )

    with pytest.raises(ValueError, match="unknown Script section"):
        shooting_workflow(briefs, scripts, shooting_plans, port).generate(
            EntityRevisionRef(script.envelope.id, 1),
            ProductionConstraints(camera_or_phone="phone"),
        )

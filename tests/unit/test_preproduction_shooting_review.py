from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from video_editing_agent.application.ports.preproduction_planning import (
    ShootingPlanningRequest,
    ShootingPlanProposal,
    ShotRequirementProposal,
)
from video_editing_agent.application.ports.preproduction_review import (
    ShootingProposalReview,
    ShootingProposalReviewRequest,
    ShootingProposalViolation,
)
from video_editing_agent.domain.brief.model import AuthoritativeFact
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.script.model import NarrativeSection
from video_editing_agent.domain.shooting.model import ProductionConstraints, ProductionLocation
from video_editing_agent.planning.brief.service import BriefContent, BriefService
from video_editing_agent.planning.script.service import ScriptPlanner
from video_editing_agent.planning.shooting.service import ShootingPlanner
from video_editing_agent.planning.shooting.workflow import (
    ShootingPlanningWorkflow,
    ShootingProposalRejectedError,
)
from video_editing_agent.providers.llm.deepseek_preproduction_review import (
    DeepSeekShootingProposalReviewPort,
)
from video_editing_agent.storage.repositories.preproduction_repositories import (
    SqliteBriefRepository,
    SqliteScriptPlanRepository,
    SqliteShootingPlanRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase

NOW = datetime(2026, 8, 12, 2, 0, tzinfo=UTC)


class CountingPlanningPort:
    def __init__(self, proposal: ShootingPlanProposal) -> None:
        self.proposal = proposal
        self.requests: list[ShootingPlanningRequest] = []

    def propose(self, request: ShootingPlanningRequest) -> ShootingPlanProposal:
        self.requests.append(request)
        return self.proposal


class StaticReviewPort:
    def __init__(self, review: ShootingProposalReview) -> None:
        self.result = review
        self.requests: list[ShootingProposalReviewRequest] = []

    def review(self, request: ShootingProposalReviewRequest) -> ShootingProposalReview:
        self.requests.append(request)
        return self.result


class FakeTransport:
    def __init__(self, content: dict[str, Any]) -> None:
        self.content = content
        self.payloads: list[dict[str, Any]] = []

    def create_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.payloads.append(payload)
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": json.dumps(self.content)},
                }
            ]
        }


def repositories(path: Path):
    database = SqliteProjectDatabase(path)
    database.initialize()
    return (
        SqliteBriefRepository(database),
        SqliteScriptPlanRepository(database),
        SqliteShootingPlanRepository(database),
    )


def project_chain(path: Path):
    briefs, scripts, shooting = repositories(path)
    brief = BriefService(
        briefs,
        brief_id_factory=lambda: "brf_shoot_review",
        clock=lambda: NOW,
    ).create(
        BriefContent(
            title="500 mL commuter bottle",
            objective="Create a factual short product ad.",
            audience="commuters",
            platform="vertical short-form",
            core_message="Show a simple bottle in a commuting context.",
            product_topic="bottle",
            authoritative_facts=(
                AuthoritativeFact("fact_capacity", "The bottle capacity is 500 mL."),
                AuthoritativeFact("fact_lid", "The bottle has a screw-on lid."),
            ),
            prohibited_content=("Do not claim leak resistance.",),
        )
    )
    script = ScriptPlanner(
        brief_repository=briefs,
        script_plan_repository=scripts,
        script_plan_id_factory=lambda: "scp_shoot_review",
        clock=lambda: NOW,
    ).create(
        EntityRevisionRef(brief.envelope.id, 1),
        (
            NarrativeSection(
                "demo",
                "proof",
                "Show the screw-on lid without extra claims.",
                spoken_content="The bottle has a screw-on lid.",
                protected_fact_ids=("fact_lid",),
            ),
        ),
    )
    planner = ShootingPlanner(
        script_plan_repository=scripts,
        shooting_plan_repository=shooting,
        shooting_plan_id_factory=lambda: "shp_shoot_review",
        clock=lambda: NOW,
    )
    return briefs, scripts, shooting, brief, script, planner


def constraints() -> ProductionConstraints:
    return ProductionConstraints(
        camera_or_phone="ordinary smartphone",
        stabilizer="no stabilizer",
        people_count=1,
        locations=(
            ProductionLocation(
                "loc_entryway",
                "entryway",
                "Use only the home's entryway area.",
            ),
        ),
        user_skill_level="beginner",
    )


def safe_proposal() -> ShootingPlanProposal:
    return ShootingPlanProposal(
        (
            ShotRequirementProposal(
                "req_demo",
                "demo",
                "Show the screw-on lid",
                "bottle and hand",
                action="Rotate the lid once.",
                location_ref="loc_entryway",
                environment_description="fixed phone position in the entryway",
                capture_instruction="Place the phone in the entryway and rotate the lid once.",
                priority="required",
            ),
        )
    )


def mismatched_location_proposal() -> ShootingPlanProposal:
    return ShootingPlanProposal(
        (
            ShotRequirementProposal(
                "req_demo",
                "demo",
                "Show the screw-on lid",
                "bottle and hand",
                action="Rotate the lid once.",
                location_ref="loc_entryway",
                environment_description="near the sink",
                capture_instruction="Stand near the sink and rotate the lid once.",
                priority="required",
            ),
        )
    )


def workflow(
    *,
    briefs: SqliteBriefRepository,
    scripts: SqliteScriptPlanRepository,
    shooting: SqliteShootingPlanRepository,
    planner: ShootingPlanner,
    planning_port: CountingPlanningPort,
    review_port: StaticReviewPort | None,
) -> ShootingPlanningWorkflow:
    return ShootingPlanningWorkflow(
        brief_repository=briefs,
        script_plan_repository=scripts,
        shooting_plan_repository=shooting,
        planning_port=planning_port,
        planner=planner,
        review_port=review_port,
    )


def test_guarded_shooting_proposal_requires_reviewer_before_owner_commit(
    tmp_path: Path,
) -> None:
    briefs, scripts, shooting, _, script, planner = project_chain(tmp_path / "project.sqlite3")
    planning_port = CountingPlanningPort(safe_proposal())

    with pytest.raises(RuntimeError, match="requires ShootingProposalReviewPort"):
        workflow(
            briefs=briefs,
            scripts=scripts,
            shooting=shooting,
            planner=planner,
            planning_port=planning_port,
            review_port=None,
        ).generate(EntityRevisionRef(script.envelope.id, 1), constraints())

    assert len(planning_port.requests) == 1
    with pytest.raises(KeyError):
        shooting.load(EntityRevisionRef("shp_shoot_review", 1))


def test_shooting_deterministic_preflight_runs_before_semantic_review(tmp_path: Path) -> None:
    briefs, scripts, shooting, _, script, planner = project_chain(tmp_path / "project.sqlite3")
    planning_port = CountingPlanningPort(
        ShootingPlanProposal(
            (
                ShotRequirementProposal(
                    "req_demo",
                    "demo",
                    "Show the lid",
                    "bottle",
                    location_ref="loc_kitchen_sink",
                    environment_description="near the sink",
                ),
            )
        )
    )
    review_port = StaticReviewPort(ShootingProposalReview(accepted=True))

    with pytest.raises(ValueError, match="unknown production location"):
        workflow(
            briefs=briefs,
            scripts=scripts,
            shooting=shooting,
            planner=planner,
            planning_port=planning_port,
            review_port=review_port,
        ).generate(EntityRevisionRef(script.envelope.id, 1), constraints())

    assert review_port.requests == []
    with pytest.raises(KeyError):
        shooting.load(EntityRevisionRef("shp_shoot_review", 1))


def test_semantic_veto_rejects_valid_location_id_with_conflicting_description(
    tmp_path: Path,
) -> None:
    briefs, scripts, shooting, _, script, planner = project_chain(tmp_path / "project.sqlite3")
    planning_port = CountingPlanningPort(mismatched_location_proposal())
    violation = ShootingProposalViolation(
        code="location_identity_mismatch",
        requirement_id="req_demo",
        excerpt="Stand near the sink",
        reason="loc_entryway authorizes the entryway, not a sink location.",
    )
    review_port = StaticReviewPort(ShootingProposalReview(False, (violation,)))

    with pytest.raises(ShootingProposalRejectedError) as captured:
        workflow(
            briefs=briefs,
            scripts=scripts,
            shooting=shooting,
            planner=planner,
            planning_port=planning_port,
            review_port=review_port,
        ).generate(EntityRevisionRef(script.envelope.id, 1), constraints())

    assert captured.value.review.violations == (violation,)
    assert len(review_port.requests) == 1
    assert review_port.requests[0].proposal == planning_port.proposal
    with pytest.raises(KeyError):
        shooting.load(EntityRevisionRef("shp_shoot_review", 1))


def test_accepted_shooting_semantic_review_allows_owner_commit(tmp_path: Path) -> None:
    briefs, scripts, shooting, _, script, planner = project_chain(tmp_path / "project.sqlite3")
    planning_port = CountingPlanningPort(safe_proposal())
    review_port = StaticReviewPort(ShootingProposalReview(accepted=True))

    plan = workflow(
        briefs=briefs,
        scripts=scripts,
        shooting=shooting,
        planner=planner,
        planning_port=planning_port,
        review_port=review_port,
    ).generate(EntityRevisionRef(script.envelope.id, 1), constraints())

    assert len(review_port.requests) == 1
    assert shooting.load(EntityRevisionRef(plan.envelope.id, plan.envelope.revision)) == plan


def test_shooting_review_result_is_veto_only_and_internally_consistent() -> None:
    violation = ShootingProposalViolation(code="location_mismatch", reason="Wrong location.")

    with pytest.raises(ValueError, match="accepted.*cannot contain violations"):
        ShootingProposalReview(accepted=True, violations=(violation,))
    with pytest.raises(ValueError, match="rejected.*must contain"):
        ShootingProposalReview(accepted=False)


def test_deepseek_shooting_reviewer_sees_location_identity_and_conflicting_prose(
    tmp_path: Path,
) -> None:
    transport = FakeTransport(
        {
            "accepted": False,
            "violations": [
                {
                    "code": "location_identity_mismatch",
                    "requirement_id": "req_demo",
                    "excerpt": "near the sink",
                    "reason": "The referenced entryway does not authorize a sink location.",
                }
            ],
        }
    )
    briefs, _, _, brief, script, _ = project_chain(tmp_path / "project.sqlite3")
    del briefs
    adapter = DeepSeekShootingProposalReviewPort(transport=transport)

    review = adapter.review(
        ShootingProposalReviewRequest(
            brief=brief,
            script_plan=script,
            constraints=constraints(),
            proposal=mismatched_location_proposal(),
        )
    )

    assert not review.accepted
    assert review.violations[0].code == "location_identity_mismatch"
    payload = transport.payloads[0]
    assert payload["thinking"] == {"type": "enabled"}
    assert payload["max_tokens"] == 3_000
    assert "valid ID does not excuse" in payload["messages"][0]["content"]
    assert "entryway" in payload["messages"][0]["content"]
    assert "sink" in payload["messages"][0]["content"]
    context = json.loads(payload["messages"][1]["content"])
    assert context["production_constraints"]["locations"] == [
        {
            "location_id": "loc_entryway",
            "label": "entryway",
            "notes": "Use only the home's entryway area.",
        }
    ]
    requirement = context["proposal"]["requirements"][0]
    assert requirement["location_ref"] == "loc_entryway"
    assert requirement["environment_description"] == "near the sink"
    assert requirement["capture_instruction"] == "Stand near the sink and rotate the lid once."

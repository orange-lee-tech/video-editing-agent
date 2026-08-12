from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

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
    ScriptProposalReviewRequest,
    ScriptProposalViolation,
    ShootingProposalReview,
    ShootingProposalReviewRequest,
    ShootingProposalViolation,
)
from video_editing_agent.domain.brief.model import AuthoritativeFact
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shooting.model import ProductionConstraints, ProductionLocation
from video_editing_agent.planning.brief.service import BriefContent, BriefService
from video_editing_agent.planning.coverage.service import CoverageAction, CoverageService
from video_editing_agent.planning.policy.builtin import (
    GENERIC_VERTICAL_SHORT_FORM_V1,
    NATURAL_VLOG_V1,
    PERFORMANCE_PRODUCT_AD_V1,
)
from video_editing_agent.planning.policy.guidance import to_planning_policy_guidance
from video_editing_agent.planning.policy.model import (
    CommercialPolicySelection,
    MarketingObjective,
)
from video_editing_agent.planning.script.service import ScriptPlanner
from video_editing_agent.planning.script.workflow import ScriptPlanningWorkflow
from video_editing_agent.planning.shooting.service import ShootingPlanner
from video_editing_agent.planning.shooting.workflow import ShootingPlanningWorkflow
from video_editing_agent.storage.repositories.preproduction_codec import (
    encode_script_plan,
    encode_shooting_plan,
)
from video_editing_agent.storage.repositories.preproduction_repositories import (
    SqliteBriefRepository,
    SqliteScriptPlanRepository,
    SqliteShootingPlanRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase

NOW = datetime(2026, 8, 12, 12, 0, tzinfo=UTC)


class ScriptedPort[Request, Proposal]:
    def __init__(self, *proposals: Proposal) -> None:
        self.proposals = proposals
        self.requests: list[Request] = []

    def propose(self, request: Request) -> Proposal:
        self.requests.append(request)
        return self.proposals[len(self.requests) - 1]


class ScriptedReviewer[Request, Review]:
    def __init__(self, *reviews: Review) -> None:
        self.reviews = reviews
        self.requests: list[Request] = []

    def review(self, request: Request) -> Review:
        self.requests.append(request)
        return self.reviews[len(self.requests) - 1]


class EmptyShotIndex:
    def search(self, query: str, *, limit: int = 20):
        del query, limit
        return ()


class UnusedRepository:
    def load(self, ref):
        raise AssertionError(f"no repository load expected for unmatched coverage: {ref}")


def repositories(path: Path):
    database = SqliteProjectDatabase(path)
    database.initialize()
    return (
        SqliteBriefRepository(database),
        SqliteScriptPlanRepository(database),
        SqliteShootingPlanRepository(database),
    )


def test_product_ad_full_preproduction_path_with_bounded_repairs(tmp_path: Path) -> None:
    briefs, scripts, shooting = repositories(tmp_path / "product-ad.sqlite3")
    brief = BriefService(briefs, brief_id_factory=lambda: "brf_product", clock=lambda: NOW).create(
        BriefContent(
            title="500 mL commuter bottle",
            objective="Create a factual short product ad.",
            audience="commuters",
            platform="vertical short-form",
            core_message="Show the bottle in a commute context.",
            product_topic="bottle",
            authoritative_facts=(
                AuthoritativeFact("fact_capacity", "The capacity is 500 mL."),
                AuthoritativeFact("fact_lid", "The bottle has a screw-on lid."),
            ),
            prohibited_content=("Do not claim leak resistance or unsupported fit.",),
        )
    )
    brief_ref = EntityRevisionRef(brief.envelope.id, 1)
    policy = to_planning_policy_guidance(
        CommercialPolicySelection(
            GENERIC_VERTICAL_SHORT_FORM_V1,
            PERFORMANCE_PRODUCT_AD_V1,
            MarketingObjective.CONVERSION,
        )
    )
    unsafe = ScriptPlanProposal(
        (
            NarrativeSectionProposal(
                "demo",
                "proof",
                "Show capacity and lid.",
                spoken_content="500 mL is enough all day and the lid keeps bags leak-free.",
                protected_fact_ids=("fact_capacity", "fact_lid"),
            ),
        )
    )
    safe = ScriptPlanProposal(
        (
            NarrativeSectionProposal(
                "demo",
                "proof",
                "Show capacity and lid.",
                spoken_content="Capacity: 500 mL. The bottle has a screw-on lid.",
                protected_fact_ids=("fact_capacity", "fact_lid"),
            ),
        )
    )
    script_port = ScriptedPort[ScriptPlanningRequest, ScriptPlanProposal](unsafe, safe)
    script_violation = ScriptProposalViolation(
        "unsupported_claim",
        "Unsupported adequacy and leak-resistance implications.",
        section_id="demo",
        excerpt="enough all day",
    )
    script_reviewer = ScriptedReviewer[ScriptProposalReviewRequest, ScriptProposalReview](
        ScriptProposalReview(False, (script_violation,)), ScriptProposalReview(True)
    )
    script_planner = ScriptPlanner(
        brief_repository=briefs,
        script_plan_repository=scripts,
        script_plan_id_factory=lambda: "scp_product",
        clock=lambda: NOW,
    )
    script_workflow = ScriptPlanningWorkflow(
        brief_repository=briefs,
        script_plan_repository=scripts,
        planning_port=script_port,
        planner=script_planner,
        review_port=script_reviewer,
    )
    script = script_workflow.generate(brief_ref, policy_guidance=policy)

    assert len(script_port.requests) == len(script_reviewer.requests) == 2
    assert scripts.load(EntityRevisionRef(script.envelope.id, 1)) == script
    assert "not an authoritative product fact" in (script_port.requests[1].instruction or "")
    assert script_port.requests[1].brief.authoritative_facts == brief.authoritative_facts
    assert script_reviewer.requests[0].proposal == unsafe
    assert script_reviewer.requests[1].proposal == safe

    locked = script_planner.set_section_lock(
        EntityRevisionRef(script.envelope.id, 1), "demo", locked=True, created_by="user"
    )
    revision_port = ScriptedPort[ScriptPlanningRequest, ScriptPlanProposal](
        ScriptPlanProposal(
            (
                NarrativeSectionProposal(
                    "demo",
                    "proof",
                    "Show capacity and lid.",
                    spoken_content=locked.sections[0].spoken_content,
                    protected_fact_ids=("fact_capacity", "fact_lid"),
                    locked=True,
                ),
            )
        )
    )
    revised = ScriptPlanningWorkflow(
        brief_repository=briefs,
        script_plan_repository=scripts,
        planning_port=revision_port,
        planner=script_planner,
        review_port=ScriptedReviewer(ScriptProposalReview(True)),
    ).revise(EntityRevisionRef(locked.envelope.id, 2), "Keep the approved locked section.")
    assert scripts.load(EntityRevisionRef(revised.envelope.id, 3)).locked_section_ids == ("demo",)

    constraints = ProductionConstraints(
        camera_or_phone="ordinary smartphone",
        stabilizer="fixed support",
        people_count=1,
        locations=(ProductionLocation("loc_entryway", "entryway", "No sink is present."),),
        user_skill_level="beginner",
    )
    unsafe_shooting = ShootingPlanProposal(
        (
            ShotRequirementProposal(
                "req_demo",
                "demo",
                "Show lid",
                "bottle",
                location_ref="loc_entryway",
                environment_description="near the sink",
                priority="required",
            ),
        )
    )
    safe_shooting = ShootingPlanProposal(
        (
            ShotRequirementProposal(
                "req_demo",
                "demo",
                "Show lid",
                "bottle",
                action="Rotate the lid",
                location_ref="loc_entryway",
                environment_description="entryway",
                priority="required",
                capture_instruction="Film the lid in the entryway.",
            ),
        )
    )
    shooting_port = ScriptedPort[ShootingPlanningRequest, ShootingPlanProposal](
        unsafe_shooting, safe_shooting
    )
    shooting_violation = ShootingProposalViolation(
        "location_identity_mismatch",
        "The entryway does not authorize a sink.",
        requirement_id="req_demo",
        excerpt="near the sink",
    )
    shooting_reviewer = ScriptedReviewer[ShootingProposalReviewRequest, ShootingProposalReview](
        ShootingProposalReview(False, (shooting_violation,)), ShootingProposalReview(True)
    )
    plan = ShootingPlanningWorkflow(
        brief_repository=briefs,
        script_plan_repository=scripts,
        shooting_plan_repository=shooting,
        planning_port=shooting_port,
        planner=ShootingPlanner(
            script_plan_repository=scripts,
            shooting_plan_repository=shooting,
            shooting_plan_id_factory=lambda: "shp_product",
            clock=lambda: NOW,
        ),
        review_port=shooting_reviewer,
    ).generate(EntityRevisionRef(revised.envelope.id, 3), constraints, policy_guidance=policy)

    assert len(shooting_port.requests) == len(shooting_reviewer.requests) == 2
    assert shooting_port.requests[1].constraints == constraints
    assert shooting.load(EntityRevisionRef(plan.envelope.id, 1)) == plan
    assert json.loads(encode_script_plan(revised))["sections"][0]["locked"] is True
    encoded_plan = json.loads(encode_shooting_plan(plan))
    assert encoded_plan["constraints"]["locations"][0]["location_id"] == "loc_entryway"
    coverage = CoverageService(
        shot_index=EmptyShotIndex(),
        shot_repository=UnusedRepository(),
        asset_repository=UnusedRepository(),
    ).evaluate(plan)
    assert coverage.assessments[0].action is CoverageAction.RESHOOT_REQUIRED
    assert coverage.assessments[0].reshoot_instruction == "Film the lid in the entryway."
    assert "stock" not in coverage.assessments[0].reason.lower()
    assert "generated" not in coverage.assessments[0].reason.lower()


def test_natural_vlog_uses_distinct_policy_without_repair(tmp_path: Path) -> None:
    briefs, scripts, _ = repositories(tmp_path / "vlog.sqlite3")
    brief = BriefService(briefs, brief_id_factory=lambda: "brf_vlog", clock=lambda: NOW).create(
        BriefContent(
            title="Ordinary evening",
            objective="Document cooking, cleaning, then reading.",
            audience="daily-life viewers",
            platform="vertical short-form",
            core_message="A calm ordinary evening.",
            prohibited_content=("Do not invent drama.",),
        )
    )
    proposal = ScriptPlanProposal(
        tuple(
            NarrativeSectionProposal(name, "sequence", f"Show {name}.", spoken_content=name)
            for name in ("cooking", "cleaning", "reading")
        )
    )
    port = ScriptedPort[ScriptPlanningRequest, ScriptPlanProposal](proposal)
    reviewer = ScriptedReviewer[ScriptProposalReviewRequest, ScriptProposalReview](
        ScriptProposalReview(True)
    )
    policy = to_planning_policy_guidance(
        CommercialPolicySelection(GENERIC_VERTICAL_SHORT_FORM_V1, NATURAL_VLOG_V1)
    )
    result = ScriptPlanningWorkflow(
        brief_repository=briefs,
        script_plan_repository=scripts,
        planning_port=port,
        planner=ScriptPlanner(
            brief_repository=briefs,
            script_plan_repository=scripts,
            script_plan_id_factory=lambda: "scp_vlog",
            clock=lambda: NOW,
        ),
        review_port=reviewer,
    ).generate(EntityRevisionRef(brief.envelope.id, 1), policy_guidance=policy)

    assert len(port.requests) == len(reviewer.requests) == 1
    assert port.requests[0].policy_guidance is not None
    assert port.requests[0].policy_guidance.skill_id == NATURAL_VLOG_V1.skill_id
    assert tuple(section.section_id for section in result.sections) == (
        "cooking",
        "cleaning",
        "reading",
    )

from datetime import UTC, datetime
from pathlib import Path

from video_editing_agent.application.ports.preproduction_planning import (
    NarrativeSectionProposal,
    PlanningPolicyGuidance,
    ScriptPlanProposal,
    ScriptPlanningRequest,
    ShootingPlanProposal,
    ShootingPlanningRequest,
    ShotRequirementProposal,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.script.model import NarrativeSection
from video_editing_agent.domain.shooting.model import ProductionConstraints
from video_editing_agent.planning.brief.service import BriefContent, BriefService
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
from video_editing_agent.storage.repositories.preproduction_repositories import (
    SqliteBriefRepository,
    SqliteScriptPlanRepository,
    SqliteShootingPlanRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase

NOW = datetime(2026, 8, 11, 19, 30, tzinfo=UTC)


class CapturingScriptPort:
    def __init__(self) -> None:
        self.requests: list[ScriptPlanningRequest] = []

    def propose(self, request: ScriptPlanningRequest) -> ScriptPlanProposal:
        self.requests.append(request)
        return ScriptPlanProposal(
            (
                NarrativeSectionProposal(
                    "hook",
                    "hook",
                    "Earn attention",
                    spoken_content="Show the value quickly.",
                ),
            )
        )


class CapturingShootingPort:
    def __init__(self) -> None:
        self.requests: list[ShootingPlanningRequest] = []

    def propose(self, request: ShootingPlanningRequest) -> ShootingPlanProposal:
        self.requests.append(request)
        return ShootingPlanProposal(
            (
                ShotRequirementProposal(
                    "req_hook",
                    "hook",
                    "Show the product",
                    "Product",
                    capture_instruction="Hold the phone still and show the product clearly.",
                ),
            )
        )


def repositories(path: Path):
    database = SqliteProjectDatabase(path)
    database.initialize()
    return (
        SqliteBriefRepository(database),
        SqliteScriptPlanRepository(database),
        SqliteShootingPlanRepository(database),
    )


def test_policy_projection_preserves_versioned_identity_and_qualitative_guidance() -> None:
    selection = CommercialPolicySelection(
        platform_profile=GENERIC_VERTICAL_SHORT_FORM_V1,
        skill=PERFORMANCE_PRODUCT_AD_V1,
        marketing_objective=MarketingObjective.CONVERSION,
    )

    guidance = to_planning_policy_guidance(selection)

    assert guidance.platform_profile_id == GENERIC_VERTICAL_SHORT_FORM_V1.profile_id
    assert guidance.platform_profile_version == GENERIC_VERTICAL_SHORT_FORM_V1.version
    assert guidance.skill_id == PERFORMANCE_PRODUCT_AD_V1.skill_id
    assert guidance.skill_version == PERFORMANCE_PRODUCT_AD_V1.version
    assert guidance.marketing_objective == "conversion"
    assert any("proof or demonstration" in item for item in guidance.guidance)


def test_product_ad_and_vlog_project_distinct_provider_contexts() -> None:
    ad = to_planning_policy_guidance(
        CommercialPolicySelection(
            platform_profile=GENERIC_VERTICAL_SHORT_FORM_V1,
            skill=PERFORMANCE_PRODUCT_AD_V1,
            marketing_objective=MarketingObjective.CONSIDERATION,
        )
    )
    vlog = to_planning_policy_guidance(
        CommercialPolicySelection(
            platform_profile=GENERIC_VERTICAL_SHORT_FORM_V1,
            skill=NATURAL_VLOG_V1,
        )
    )

    assert ad.platform_profile_id == vlog.platform_profile_id
    assert ad.skill_id != vlog.skill_id
    assert ad.guidance != vlog.guidance
    assert any("call to action" in item for item in ad.guidance)
    assert any("reaction holds" in item for item in vlog.guidance)


def test_script_workflow_passes_neutral_policy_context_to_provider(tmp_path: Path) -> None:
    briefs, scripts, _ = repositories(tmp_path / "project.sqlite3")
    brief = BriefService(
        briefs,
        brief_id_factory=lambda: "brf_policy_script",
        clock=lambda: NOW,
    ).create(
        BriefContent(
            title="Product clip",
            objective="Explain value",
            audience="Buyer",
            platform="vertical short-form",
            core_message="Simple to use",
        )
    )
    port = CapturingScriptPort()
    planner = ScriptPlanner(
        brief_repository=briefs,
        script_plan_repository=scripts,
        script_plan_id_factory=lambda: "scp_policy_script",
        clock=lambda: NOW,
    )
    workflow = ScriptPlanningWorkflow(
        brief_repository=briefs,
        script_plan_repository=scripts,
        planning_port=port,
        planner=planner,
    )
    guidance = to_planning_policy_guidance(
        CommercialPolicySelection(
            platform_profile=GENERIC_VERTICAL_SHORT_FORM_V1,
            skill=PERFORMANCE_PRODUCT_AD_V1,
            marketing_objective=MarketingObjective.CONVERSION,
        )
    )

    workflow.generate(
        EntityRevisionRef(brief.envelope.id, 1),
        policy_guidance=guidance,
    )

    assert port.requests[0].policy_guidance == guidance


def test_shooting_workflow_passes_same_policy_context_without_rewriting_constraints(
    tmp_path: Path,
) -> None:
    briefs, scripts, shooting_plans = repositories(tmp_path / "project.sqlite3")
    brief = BriefService(
        briefs,
        brief_id_factory=lambda: "brf_policy_shoot",
        clock=lambda: NOW,
    ).create(
        BriefContent(
            title="Vlog",
            objective="Tell a natural story",
            audience="Viewers",
            platform="vertical short-form",
            core_message="Show the day naturally",
        )
    )
    script = ScriptPlanner(
        brief_repository=briefs,
        script_plan_repository=scripts,
        script_plan_id_factory=lambda: "scp_policy_shoot",
        clock=lambda: NOW,
    ).create(
        EntityRevisionRef(brief.envelope.id, 1),
        (NarrativeSection("hook", "hook", "Open the story"),),
    )
    port = CapturingShootingPort()
    planner = ShootingPlanner(
        script_plan_repository=scripts,
        shooting_plan_repository=shooting_plans,
        shooting_plan_id_factory=lambda: "shp_policy_shoot",
        clock=lambda: NOW,
    )
    workflow = ShootingPlanningWorkflow(
        brief_repository=briefs,
        script_plan_repository=scripts,
        shooting_plan_repository=shooting_plans,
        planning_port=port,
        planner=planner,
    )
    constraints = ProductionConstraints(
        camera_or_phone="user phone",
        stabilizer="handheld",
        people_count=1,
    )
    guidance = to_planning_policy_guidance(
        CommercialPolicySelection(
            platform_profile=GENERIC_VERTICAL_SHORT_FORM_V1,
            skill=NATURAL_VLOG_V1,
        )
    )

    plan = workflow.generate(
        EntityRevisionRef(script.envelope.id, 1),
        constraints,
        policy_guidance=guidance,
    )

    assert port.requests[0].policy_guidance == guidance
    assert port.requests[0].constraints == constraints
    assert plan.constraints == constraints


def test_policy_guidance_rejects_empty_or_unversioned_context() -> None:
    try:
        PlanningPolicyGuidance(
            platform_profile_id="",
            platform_profile_version="v1",
            skill_id="skill",
            skill_version="v1",
            guidance=("Prefer clarity.",),
        )
    except ValueError as exc:
        assert "platform_profile_id" in str(exc)
    else:
        raise AssertionError("empty policy identity must be rejected")

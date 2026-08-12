from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from video_editing_agent.domain.brief.model import AuthoritativeFact
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.shooting.model import ProductionConstraints, ProductionLocation
from video_editing_agent.planning.brief.service import BriefContent, BriefService
from video_editing_agent.planning.policy.builtin import (
    GENERIC_VERTICAL_SHORT_FORM_V1,
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
from video_editing_agent.providers.llm.deepseek_chat import (
    DeepSeekChatConfig,
    DeepSeekScriptPlanningPort,
    DeepSeekShootingPlanningPort,
    UrllibDeepSeekChatTransport,
)
from video_editing_agent.providers.llm.deepseek_preproduction_review import (
    DeepSeekScriptProposalReviewPort,
    DeepSeekShootingProposalReviewPort,
)
from video_editing_agent.storage.repositories.preproduction_repositories import (
    SqliteBriefRepository,
    SqliteScriptPlanRepository,
    SqliteShootingPlanRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase


def _ref(entity_id: str, revision: int) -> EntityRevisionRef:
    return EntityRevisionRef(entity_id=entity_id, revision=revision)


def main() -> None:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key.strip():
        raise RuntimeError("DEEPSEEK_API_KEY is required for the live engineering probe")

    with tempfile.TemporaryDirectory(prefix="video-editing-agent-r0.7b-") as directory:
        database_path = Path(directory) / "project.sqlite3"
        database = SqliteProjectDatabase(database_path)
        database.initialize()

        briefs = SqliteBriefRepository(database)
        scripts = SqliteScriptPlanRepository(database)
        shooting_plans = SqliteShootingPlanRepository(database)

        brief = BriefService(
            briefs,
            brief_id_factory=lambda: "brf_r07b_deepseek_live",
        ).create(
            BriefContent(
                title="500 mL commuter bottle short advertisement",
                objective="Create a practical 30-second product advertisement plan.",
                audience="Everyday commuters who carry a drink in a bag.",
                platform="generic vertical short-form",
                core_message="Show a 500 mL bottle in a simple commute-oriented context.",
                product_topic="500 mL commuter bottle",
                target_duration=MediaTime(value=30, scale=1),
                authoritative_facts=(
                    AuthoritativeFact(
                        fact_id="fact_capacity",
                        statement="The bottle capacity is 500 mL.",
                        source_note="R0.7B engineering probe fixture",
                    ),
                    AuthoritativeFact(
                        fact_id="fact_lid",
                        statement="The bottle has a screw-on lid.",
                        source_note="R0.7B engineering probe fixture",
                    ),
                ),
                prohibited_content=(
                    "Do not invent certifications or unsupported thermal-performance duration.",
                    (
                        "Do not infer leak resistance, one-hand operation, bag fit, "
                        "or use-case adequacy."
                    ),
                ),
                user_notes="Keep the plan feasible for one beginner filming alone at home.",
            ),
            created_by="r0.7b-live-probe",
        )
        brief_ref = _ref(brief.envelope.id, brief.envelope.revision)
        authoritative_facts = brief.authoritative_facts

        policy = to_planning_policy_guidance(
            CommercialPolicySelection(
                platform_profile=GENERIC_VERTICAL_SHORT_FORM_V1,
                skill=PERFORMANCE_PRODUCT_AD_V1,
                marketing_objective=MarketingObjective.CONVERSION,
            )
        )

        transport = UrllibDeepSeekChatTransport(api_key=api_key)
        config = DeepSeekChatConfig(
            model="deepseek-v4-flash",
            thinking_enabled=False,
            max_tokens=4_000,
        )

        script_planner = ScriptPlanner(
            brief_repository=briefs,
            script_plan_repository=scripts,
            script_plan_id_factory=lambda: "scp_r07b_deepseek_live",
        )
        script_workflow = ScriptPlanningWorkflow(
            brief_repository=briefs,
            script_plan_repository=scripts,
            planning_port=DeepSeekScriptPlanningPort(transport=transport, config=config),
            planner=script_planner,
            review_port=DeepSeekScriptProposalReviewPort(transport=transport),
        )
        script = script_workflow.generate(
            brief_ref,
            policy_guidance=policy,
            created_by="deepseek-v4-flash-proposal",
        )
        script_ref = _ref(script.envelope.id, script.envelope.revision)

        constraints = ProductionConstraints(
            camera_or_phone="ordinary smartphone",
            stabilizer="handheld only",
            lighting="window light and normal room lighting",
            people_count=1,
            locations=(
                ProductionLocation(
                    location_id="loc_home_desk",
                    label="home desk",
                    notes="Desk area and a fixed phone position immediately beside it are allowed.",
                ),
                ProductionLocation(
                    location_id="loc_entryway",
                    label="entryway",
                    notes="Use only the home's entryway area.",
                ),
            ),
            available_time_notes="about 20 minutes",
            user_skill_level="beginner",
            notes=("No assistant or specialist camera equipment is available.",),
        )
        shooting_planner = ShootingPlanner(
            script_plan_repository=scripts,
            shooting_plan_repository=shooting_plans,
            shooting_plan_id_factory=lambda: "shp_r07b_deepseek_live",
        )
        shooting_workflow = ShootingPlanningWorkflow(
            brief_repository=briefs,
            script_plan_repository=scripts,
            shooting_plan_repository=shooting_plans,
            planning_port=DeepSeekShootingPlanningPort(transport=transport, config=config),
            planner=shooting_planner,
            review_port=DeepSeekShootingProposalReviewPort(transport=transport),
        )
        shooting_plan = shooting_workflow.generate(
            script_ref,
            constraints,
            policy_guidance=policy,
            created_by="deepseek-v4-flash-proposal",
        )
        shooting_ref = _ref(
            shooting_plan.envelope.id,
            shooting_plan.envelope.revision,
        )

        if briefs.load(brief_ref).authoritative_facts != authoritative_facts:
            raise AssertionError("provider path changed authoritative Brief facts")
        if shooting_plan.constraints != constraints:
            raise AssertionError("provider path changed user ProductionConstraints")
        if not script.sections:
            raise AssertionError("live provider produced no NarrativeSections")
        if not shooting_plan.requirements:
            raise AssertionError("live provider produced no ShotRequirements")

        section_ids = {section.section_id for section in script.sections}
        if any(
            requirement.script_section_ref not in section_ids
            for requirement in shooting_plan.requirements
        ):
            raise AssertionError("ShootingPlan contains an invalid Script section reference")
        location_ids = {location.location_id for location in constraints.locations}
        if any(
            requirement.location_ref is not None and requirement.location_ref not in location_ids
            for requirement in shooting_plan.requirements
        ):
            raise AssertionError("ShootingPlan contains an invalid production location reference")
        if any(
            constraints.locations
            and requirement.environment_description is not None
            and requirement.location_ref is None
            for requirement in shooting_plan.requirements
        ):
            raise AssertionError("ShootingPlan contains an unbound environment description")

        reopened_database = SqliteProjectDatabase(database_path)
        reopened_database.initialize()
        reopened_briefs = SqliteBriefRepository(reopened_database)
        reopened_scripts = SqliteScriptPlanRepository(reopened_database)
        reopened_shooting = SqliteShootingPlanRepository(reopened_database)

        if reopened_database.schema_version() != 3:
            raise AssertionError("live probe database did not reopen as schema v3")
        if reopened_briefs.load(brief_ref) != brief:
            raise AssertionError("Brief exact revision did not survive SQLite reopen")
        if reopened_scripts.load(script_ref) != script:
            raise AssertionError("ScriptPlan exact revision did not survive SQLite reopen")
        if reopened_shooting.load(shooting_ref) != shooting_plan:
            raise AssertionError("ShootingPlan exact revision did not survive SQLite reopen")

        print(
            json.dumps(
                {
                    "probe": "r0.7b-deepseek-live",
                    "status": "passed",
                    "model": config.model,
                    "generation_thinking_enabled": config.thinking_enabled,
                    "script_semantic_review_enabled": True,
                    "shooting_semantic_review_enabled": True,
                    "reviewer_thinking_enabled": True,
                    "structured_location_identity": True,
                    "schema_version": reopened_database.schema_version(),
                    "script_sections": len(script.sections),
                    "shot_requirements": len(shooting_plan.requirements),
                    "brief_fact_count": len(authoritative_facts),
                    "production_constraints_preserved": True,
                    "exact_revision_reopen": True,
                },
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()

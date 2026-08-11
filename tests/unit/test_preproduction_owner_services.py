from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.domain.brief.model import AuthoritativeFact
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.script.model import NarrativeSection
from video_editing_agent.domain.shooting.model import (
    CoveragePriority,
    ProductionConstraints,
    ShotRequirement,
)
from video_editing_agent.planning.brief.service import BriefContent, BriefService
from video_editing_agent.planning.script.service import ScriptPlanner
from video_editing_agent.planning.shooting.service import ShootingPlanner
from video_editing_agent.storage.repositories.preproduction_repositories import (
    SqliteBriefRepository,
    SqliteScriptPlanRepository,
    SqliteShootingPlanRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase

NOW = datetime(2026, 8, 11, 18, 40, tzinfo=UTC)


def repositories(path: Path):
    database = SqliteProjectDatabase(path)
    database.initialize()
    return (
        SqliteBriefRepository(database),
        SqliteScriptPlanRepository(database),
        SqliteShootingPlanRepository(database),
    )


def brief_content() -> BriefContent:
    return BriefContent(
        title="Product launch",
        objective="Drive consideration",
        audience="First-time buyers",
        platform="short-form vertical",
        core_message="The product is easy to use.",
        product_topic="Example product",
        target_duration=MediaTime(30, 1),
        authoritative_facts=(
            AuthoritativeFact("fact_price", "The approved launch price is 99 USD."),
        ),
    )


def test_brief_service_owns_identity_revision_and_history(tmp_path: Path) -> None:
    briefs, _, _ = repositories(tmp_path / "project.sqlite3")
    service = BriefService(
        briefs,
        brief_id_factory=lambda: "brf_owner",
        clock=lambda: NOW,
    )

    first = service.create(brief_content(), created_by="user")
    first_ref = EntityRevisionRef("brf_owner", 1)
    revised_content = replace(
        BriefContent.from_brief(first),
        core_message="The product is simple and fast to use.",
    )
    second = service.revise(first_ref, revised_content, created_by="user")

    assert first.envelope.revision == 1
    assert second.envelope.id == first.envelope.id
    assert second.envelope.revision == 2
    assert second.envelope.derived_from == (first_ref,)
    assert briefs.load(first_ref) == first
    assert briefs.load(EntityRevisionRef("brf_owner", 2)) == second


def test_script_planner_rejects_unknown_protected_fact(tmp_path: Path) -> None:
    briefs, scripts, _ = repositories(tmp_path / "project.sqlite3")
    brief = BriefService(
        briefs,
        brief_id_factory=lambda: "brf_script",
        clock=lambda: NOW,
    ).create(brief_content())
    planner = ScriptPlanner(
        brief_repository=briefs,
        script_plan_repository=scripts,
        script_plan_id_factory=lambda: "scp_owner",
        clock=lambda: NOW,
    )

    with pytest.raises(ValueError, match="unknown protected facts"):
        planner.create(
            EntityRevisionRef(brief.envelope.id, brief.envelope.revision),
            (
                NarrativeSection(
                    "hook",
                    "hook",
                    "Earn attention",
                    protected_fact_ids=("fact_missing",),
                ),
            ),
        )


def test_script_planner_preserves_locked_sections_without_override(tmp_path: Path) -> None:
    briefs, scripts, _ = repositories(tmp_path / "project.sqlite3")
    brief = BriefService(
        briefs,
        brief_id_factory=lambda: "brf_lock",
        clock=lambda: NOW,
    ).create(brief_content())
    brief_ref = EntityRevisionRef(brief.envelope.id, brief.envelope.revision)
    planner = ScriptPlanner(
        brief_repository=briefs,
        script_plan_repository=scripts,
        script_plan_id_factory=lambda: "scp_lock",
        clock=lambda: NOW,
    )
    locked = NarrativeSection(
        "hook",
        "hook",
        "Earn attention",
        spoken_content="Approved hook",
        protected_fact_ids=("fact_price",),
        locked=True,
    )
    body = NarrativeSection("body", "proof", "Explain value", spoken_content="Old body")
    first = planner.create(brief_ref, (locked, body))
    first_ref = EntityRevisionRef(first.envelope.id, first.envelope.revision)

    second = planner.revise(
        first_ref,
        (locked, replace(body, spoken_content="Improved body")),
    )
    second_ref = EntityRevisionRef(second.envelope.id, second.envelope.revision)
    assert second.sections[0] == locked

    changed_lock = replace(locked, spoken_content="Changed hook")
    with pytest.raises(ValueError, match="locked section"):
        planner.revise(second_ref, (changed_lock, second.sections[1]))

    third = planner.revise(
        second_ref,
        (changed_lock, second.sections[1]),
        allow_locked_changes=True,
    )
    assert third.envelope.revision == 3
    assert third.sections[0].spoken_content == "Changed hook"


def test_script_revision_against_new_brief_revalidates_protected_facts(tmp_path: Path) -> None:
    briefs, scripts, _ = repositories(tmp_path / "project.sqlite3")
    brief_service = BriefService(
        briefs,
        brief_id_factory=lambda: "brf_fact",
        clock=lambda: NOW,
    )
    first_brief = brief_service.create(brief_content())
    first_brief_ref = EntityRevisionRef(first_brief.envelope.id, 1)
    planner = ScriptPlanner(
        brief_repository=briefs,
        script_plan_repository=scripts,
        script_plan_id_factory=lambda: "scp_fact",
        clock=lambda: NOW,
    )
    section = NarrativeSection(
        "proof",
        "proof",
        "State approved offer",
        protected_fact_ids=("fact_price",),
    )
    script = planner.create(first_brief_ref, (section,))

    second_brief = brief_service.revise(
        first_brief_ref,
        replace(BriefContent.from_brief(first_brief), authoritative_facts=()),
    )
    with pytest.raises(ValueError, match="unknown protected facts"):
        planner.revise(
            EntityRevisionRef(script.envelope.id, 1),
            (section,),
            brief_ref=EntityRevisionRef(second_brief.envelope.id, 2),
        )


def test_shooting_planner_rejects_requirement_for_unknown_script_section(tmp_path: Path) -> None:
    briefs, scripts, shooting_plans = repositories(tmp_path / "project.sqlite3")
    brief = BriefService(
        briefs,
        brief_id_factory=lambda: "brf_shoot",
        clock=lambda: NOW,
    ).create(brief_content())
    script = ScriptPlanner(
        brief_repository=briefs,
        script_plan_repository=scripts,
        script_plan_id_factory=lambda: "scp_shoot",
        clock=lambda: NOW,
    ).create(
        EntityRevisionRef(brief.envelope.id, 1),
        (NarrativeSection("hook", "hook", "Earn attention"),),
    )
    planner = ShootingPlanner(
        script_plan_repository=scripts,
        shooting_plan_repository=shooting_plans,
        shooting_plan_id_factory=lambda: "shp_owner",
        clock=lambda: NOW,
    )

    with pytest.raises(ValueError, match="unknown Script section"):
        planner.create(
            EntityRevisionRef(script.envelope.id, 1),
            (ShotRequirement("req_bad", "missing", "Show product", "Product"),),
        )


def test_owner_chain_persists_and_reopens_exact_revisions(tmp_path: Path) -> None:
    path = tmp_path / "project.sqlite3"
    briefs, scripts, shooting_plans = repositories(path)
    brief = BriefService(
        briefs,
        brief_id_factory=lambda: "brf_chain",
        clock=lambda: NOW,
    ).create(brief_content())
    brief_ref = EntityRevisionRef(brief.envelope.id, 1)
    script = ScriptPlanner(
        brief_repository=briefs,
        script_plan_repository=scripts,
        script_plan_id_factory=lambda: "scp_chain",
        clock=lambda: NOW,
    ).create(
        brief_ref,
        (
            NarrativeSection(
                "hook",
                "hook",
                "Earn attention",
                target_duration=MediaTime(3, 1),
            ),
        ),
    )
    script_ref = EntityRevisionRef(script.envelope.id, 1)
    requirement = ShotRequirement(
        "req_hook",
        "hook",
        "Show product immediately",
        "Product",
        target_duration=MediaTime(3, 1),
        minimum_duration=MediaTime(2, 1),
        priority=CoveragePriority.REQUIRED,
        capture_instruction="Hold the product close to the phone for three seconds.",
    )
    shooting_plan = ShootingPlanner(
        script_plan_repository=scripts,
        shooting_plan_repository=shooting_plans,
        shooting_plan_id_factory=lambda: "shp_chain",
        clock=lambda: NOW,
    ).create(
        script_ref,
        (requirement,),
        constraints=ProductionConstraints(camera_or_phone="phone", people_count=1),
    )

    reopened_briefs, reopened_scripts, reopened_shooting = repositories(path)
    assert reopened_briefs.load(brief_ref) == brief
    assert reopened_scripts.load(script_ref) == script
    assert reopened_shooting.load(EntityRevisionRef("shp_chain", 1)) == shooting_plan
    assert script.envelope.derived_from == (brief_ref,)
    assert shooting_plan.envelope.derived_from == (script_ref,)


def test_shooting_revision_preserves_constraints_unless_replaced(tmp_path: Path) -> None:
    path = tmp_path / "project.sqlite3"
    briefs, scripts, shooting_plans = repositories(path)
    brief = BriefService(
        briefs,
        brief_id_factory=lambda: "brf_revision",
        clock=lambda: NOW,
    ).create(brief_content())
    script = ScriptPlanner(
        brief_repository=briefs,
        script_plan_repository=scripts,
        script_plan_id_factory=lambda: "scp_revision",
        clock=lambda: NOW,
    ).create(
        EntityRevisionRef(brief.envelope.id, 1),
        (NarrativeSection("body", "body", "Explain product"),),
    )
    script_ref = EntityRevisionRef(script.envelope.id, 1)
    planner = ShootingPlanner(
        script_plan_repository=scripts,
        shooting_plan_repository=shooting_plans,
        shooting_plan_id_factory=lambda: "shp_revision",
        clock=lambda: NOW,
    )
    constraints = ProductionConstraints(camera_or_phone="phone", locations=("desk",))
    first_requirement = ShotRequirement("req_body", "body", "Explain visually", "Product")
    first = planner.create(script_ref, (first_requirement,), constraints=constraints)
    first_ref = EntityRevisionRef(first.envelope.id, 1)

    second_requirement = replace(first_requirement, purpose="Demonstrate operation")
    second = planner.revise(first_ref, (second_requirement,))

    assert second.envelope.revision == 2
    assert second.constraints == constraints
    assert second.envelope.derived_from == (first_ref, script_ref)

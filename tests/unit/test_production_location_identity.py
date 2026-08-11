from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.script.model import NarrativeSection
from video_editing_agent.domain.shooting.model import (
    ProductionConstraints,
    ProductionLocation,
    ShootingPlan,
    ShotRequirement,
)
from video_editing_agent.planning.brief.service import BriefContent, BriefService
from video_editing_agent.planning.script.service import ScriptPlanner
from video_editing_agent.planning.shooting.service import ShootingPlanner
from video_editing_agent.storage.repositories.preproduction_codec import (
    decode_shooting_plan,
    encode_shooting_plan,
)
from video_editing_agent.storage.repositories.preproduction_repositories import (
    SqliteBriefRepository,
    SqliteScriptPlanRepository,
    SqliteShootingPlanRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase

NOW = datetime(2026, 8, 12, 1, 0, tzinfo=UTC)


def project_chain(path: Path):
    database = SqliteProjectDatabase(path)
    database.initialize()
    briefs = SqliteBriefRepository(database)
    scripts = SqliteScriptPlanRepository(database)
    shooting = SqliteShootingPlanRepository(database)
    brief = BriefService(
        briefs,
        brief_id_factory=lambda: "brf_location_identity",
        clock=lambda: NOW,
    ).create(
        BriefContent(
            title="Desk demo",
            objective="Plan a small product demo",
            audience="viewer",
            platform="vertical short-form",
            core_message="Show the product clearly",
        )
    )
    script = ScriptPlanner(
        brief_repository=briefs,
        script_plan_repository=scripts,
        script_plan_id_factory=lambda: "scp_location_identity",
        clock=lambda: NOW,
    ).create(
        EntityRevisionRef(brief.envelope.id, 1),
        (NarrativeSection("demo", "proof", "Show the product"),),
    )
    planner = ShootingPlanner(
        script_plan_repository=scripts,
        shooting_plan_repository=shooting,
        shooting_plan_id_factory=lambda: "shp_location_identity",
        clock=lambda: NOW,
    )
    return database, shooting, script, planner


def desk_constraints() -> ProductionConstraints:
    return ProductionConstraints(
        camera_or_phone="phone",
        locations=(
            ProductionLocation(
                location_id="loc_home_desk",
                label="家中书桌",
                notes="书桌区域均可，允许在桌旁放置固定机位。",
            ),
        ),
    )


def test_structured_location_ref_allows_descriptive_camera_position_without_exact_string(
    tmp_path: Path,
) -> None:
    _, shooting, script, planner = project_chain(tmp_path / "project.sqlite3")
    requirement = ShotRequirement(
        "req_demo",
        "demo",
        "Show product operation",
        "Product and hand",
        location_ref="loc_home_desk",
        environment_description="家中书桌旁固定机位",
    )

    plan = planner.create(
        EntityRevisionRef(script.envelope.id, 1),
        (requirement,),
        constraints=desk_constraints(),
    )

    assert plan.requirements[0].location_ref == "loc_home_desk"
    assert plan.requirements[0].environment_description == "家中书桌旁固定机位"
    assert shooting.load(EntityRevisionRef(plan.envelope.id, 1)) == plan


def test_unknown_or_unreferenced_declared_location_is_rejected_before_owner_save(
    tmp_path: Path,
) -> None:
    _, shooting, script, planner = project_chain(tmp_path / "project.sqlite3")
    script_ref = EntityRevisionRef(script.envelope.id, 1)

    with pytest.raises(ValueError, match="unknown production location"):
        planner.create(
            script_ref,
            (
                ShotRequirement(
                    "req_unknown",
                    "demo",
                    "Show product",
                    "Product",
                    location_ref="loc_kitchen_sink",
                    environment_description="厨房水槽旁",
                ),
            ),
            constraints=desk_constraints(),
        )

    with pytest.raises(ValueError, match="no structured location_ref"):
        planner.create(
            script_ref,
            (
                ShotRequirement(
                    "req_unbound",
                    "demo",
                    "Show product",
                    "Product",
                    environment_description="家中书桌或厨房水槽",
                ),
            ),
            constraints=desk_constraints(),
        )

    with pytest.raises(KeyError):
        shooting.load(EntityRevisionRef("shp_location_identity", 1))


def test_production_constraints_require_unique_location_identity() -> None:
    with pytest.raises(ValueError, match="unique location_id"):
        ProductionConstraints(
            locations=(
                ProductionLocation("loc_same", "desk"),
                ProductionLocation("loc_same", "entryway"),
            )
        )


def _legacy_v1_payload() -> str:
    return json.dumps(
        {
            "codec_version": 1,
            "record_type": "shooting_plan",
            "envelope": {
                "id": "shp_legacy_location",
                "revision": 1,
                "schema_version": "0.2",
                "status": "draft",
                "created_at": NOW.isoformat(),
                "created_by": "legacy-test",
                "derived_from": [
                    {"entity_id": "scp_location_identity", "revision": 1},
                ],
            },
            "script_plan_ref": {"entity_id": "scp_location_identity", "revision": 1},
            "requirements": [
                {
                    "requirement_id": "req_legacy",
                    "script_section_ref": "demo",
                    "purpose": "Show product",
                    "subject": "Product",
                    "action": None,
                    "environment": "家中书桌旁固定机位",
                    "framing": None,
                    "camera_motion": None,
                    "target_duration": None,
                    "minimum_duration": None,
                    "audio_dialogue_requirement": None,
                    "continuity_hint": None,
                    "visual_constraints": [],
                    "priority": "recommended",
                    "backup_intent": None,
                    "capture_instruction": None,
                    "alternate_coverage": [],
                    "handle_before": None,
                    "handle_after": None,
                }
            ],
            "constraints": {
                "camera_or_phone": "phone",
                "stabilizer": None,
                "lighting": None,
                "microphones": [],
                "people_count": 1,
                "locations": ["家中书桌"],
                "available_time_notes": None,
                "user_skill_level": None,
                "notes": [],
            },
            "notes": [],
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def test_legacy_v1_shooting_payload_is_readable_without_inventing_location_authority() -> None:
    plan = decode_shooting_plan(_legacy_v1_payload())

    assert plan.constraints.locations == (
        ProductionLocation("loc_legacy_001", "家中书桌"),
    )
    assert plan.requirements[0].location_ref is None
    assert plan.requirements[0].environment_description == "家中书桌旁固定机位"
    upgraded = json.loads(encode_shooting_plan(plan))
    assert upgraded["codec_version"] == 2
    assert upgraded["constraints"]["locations"][0]["location_id"] == "loc_legacy_001"
    assert upgraded["requirements"][0]["location_ref"] is None


def test_repository_treats_legacy_revision_as_idempotent_by_domain_equivalence(
    tmp_path: Path,
) -> None:
    database, shooting, _, _ = project_chain(tmp_path / "project.sqlite3")
    payload = _legacy_v1_payload()
    with database.write_connection() as connection:
        connection.execute(
            """
            INSERT INTO shooting_plans (
                entity_id,
                revision,
                script_plan_entity_id,
                script_plan_revision,
                payload_json
            ) VALUES (?, ?, ?, ?, ?)
            """,
            ("shp_legacy_location", 1, "scp_location_identity", 1, payload),
        )

    loaded = shooting.load(EntityRevisionRef("shp_legacy_location", 1))
    shooting.save(loaded)

    assert isinstance(loaded, ShootingPlan)
    with database.read_connection() as connection:
        stored = connection.execute(
            "SELECT payload_json FROM shooting_plans WHERE entity_id = ? AND revision = ?",
            ("shp_legacy_location", 1),
        ).fetchone()
    assert stored is not None
    assert str(stored["payload_json"]) == payload

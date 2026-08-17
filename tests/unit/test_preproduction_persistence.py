from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.domain.brief.model import AuthoritativeFact, Brief, BriefReference
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.script.model import NarrativeSection, ScriptPlan
from video_editing_agent.domain.shooting.model import (
    CoveragePriority,
    ProductionConstraints,
    ShootingPlan,
    ShotRequirement,
)
from video_editing_agent.storage.repositories import sqlite_database as sqlite_database_module
from video_editing_agent.storage.repositories.preproduction_repositories import (
    PreproductionRevisionConflictError,
    SqliteBriefRepository,
    SqliteScriptPlanRepository,
    SqliteShootingPlanRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase

NOW = datetime(2026, 8, 11, 18, 20, tzinfo=UTC)


def envelope(entity_id: str, revision: int = 1) -> EntityEnvelope:
    return EntityEnvelope(
        id=entity_id,
        revision=revision,
        schema_version="0.2",
        status=EntityStatus.VALID,
        created_at=NOW,
        created_by="test",
    )


def make_brief(*, title: str = "Launch clip") -> Brief:
    return Brief(
        envelope=envelope("brf_persist"),
        title=title,
        objective="Drive consideration",
        audience="First-time buyers",
        platform="short-form vertical",
        core_message="Simple to use",
        product_topic="Example product",
        target_duration=MediaTime(30, 1),
        authoritative_facts=(AuthoritativeFact("fact_price", "Price is 99 USD"),),
        references=(BriefReference("ref_style", "video", "Use structure only"),),
    )


def make_script() -> ScriptPlan:
    return ScriptPlan(
        envelope=envelope("scp_persist"),
        brief_ref=EntityRevisionRef("brf_persist", 1),
        sections=(
            NarrativeSection(
                "hook",
                "hook",
                "Earn attention",
                target_duration=MediaTime(3, 1),
                protected_fact_ids=("fact_price",),
                locked=True,
            ),
        ),
    )


def make_shooting_plan() -> ShootingPlan:
    return ShootingPlan(
        envelope=envelope("shp_persist"),
        script_plan_ref=EntityRevisionRef("scp_persist", 1),
        requirements=(
            ShotRequirement(
                "req_hook",
                "hook",
                "Show product immediately",
                "Product",
                target_duration=MediaTime(3, 1),
                minimum_duration=MediaTime(2, 1),
                priority=CoveragePriority.REQUIRED,
                capture_instruction="Hold the product close to the phone for three seconds.",
            ),
        ),
        constraints=ProductionConstraints(camera_or_phone="phone", people_count=1),
    )


def database(path: Path) -> SqliteProjectDatabase:
    result = SqliteProjectDatabase(path)
    result.initialize()
    return result


def test_schema_v3_round_trip_survives_reopen(tmp_path: Path) -> None:
    path = tmp_path / "project.sqlite3"
    db = database(path)
    briefs = SqliteBriefRepository(db)
    scripts = SqliteScriptPlanRepository(db)
    shooting = SqliteShootingPlanRepository(db)
    brief = make_brief()
    script = make_script()
    shooting_plan = make_shooting_plan()

    briefs.save(brief)
    scripts.save(script)
    shooting.save(shooting_plan)

    reopened = database(path)
    assert reopened.schema_version() == 7
    assert SqliteBriefRepository(reopened).load(EntityRevisionRef("brf_persist", 1)) == brief
    assert SqliteScriptPlanRepository(reopened).load(EntityRevisionRef("scp_persist", 1)) == script
    assert (
        SqliteShootingPlanRepository(reopened).load(EntityRevisionRef("shp_persist", 1))
        == shooting_plan
    )


def test_preproduction_exact_revision_is_idempotent_but_not_mutable(tmp_path: Path) -> None:
    repository = SqliteBriefRepository(database(tmp_path / "project.sqlite3"))
    original = make_brief()
    repository.save(original)
    repository.save(original)

    with pytest.raises(PreproductionRevisionConflictError):
        repository.save(make_brief(title="Changed at same revision"))


def test_script_plan_requires_exact_brief_revision(tmp_path: Path) -> None:
    repository = SqliteScriptPlanRepository(database(tmp_path / "project.sqlite3"))

    with pytest.raises(sqlite3.IntegrityError):
        repository.save(make_script())


def test_shooting_plan_requires_exact_script_plan_revision(tmp_path: Path) -> None:
    path = tmp_path / "project.sqlite3"
    db = database(path)
    SqliteBriefRepository(db).save(make_brief())
    repository = SqliteShootingPlanRepository(db)

    with pytest.raises(sqlite3.IntegrityError):
        repository.save(make_shooting_plan())


def test_v2_database_migrates_to_v3_without_touching_existing_tables(tmp_path: Path) -> None:
    path = tmp_path / "v2.sqlite3"
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE assets (
            entity_id TEXT NOT NULL,
            revision INTEGER NOT NULL,
            payload_json TEXT NOT NULL,
            PRIMARY KEY (entity_id, revision)
        );
        CREATE TABLE shots (
            entity_id TEXT NOT NULL,
            revision INTEGER NOT NULL,
            asset_entity_id TEXT NOT NULL,
            asset_revision INTEGER NOT NULL,
            payload_json TEXT NOT NULL,
            PRIMARY KEY (entity_id, revision)
        );
        CREATE TABLE shot_analyses (
            shot_entity_id TEXT NOT NULL,
            shot_revision INTEGER NOT NULL,
            analysis_revision INTEGER NOT NULL,
            payload_json TEXT NOT NULL,
            PRIMARY KEY (shot_entity_id, shot_revision, analysis_revision)
        );
        CREATE TABLE project_migrations (
            migration_id TEXT NOT NULL PRIMARY KEY,
            from_version INTEGER NOT NULL,
            to_version INTEGER NOT NULL,
            applied_at TEXT NOT NULL
        );
        PRAGMA user_version = 2;
        """
    )
    connection.close()

    db = database(path)

    assert db.schema_version() == 7
    with db.read_connection() as reopened:
        migration = reopened.execute(
            """
            SELECT from_version, to_version
            FROM project_migrations
            WHERE migration_id = 'schema-2-to-3'
            """
        ).fetchone()
        tables = {
            str(row[0])
            for row in reopened.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
    assert migration is not None
    assert (migration["from_version"], migration["to_version"]) == (2, 3)
    assert {"briefs", "script_plans", "shooting_plans"} <= tables


def test_v2_to_v3_migration_rolls_back_transactionally(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "v2-failure.sqlite3"
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE assets (
            entity_id TEXT NOT NULL,
            revision INTEGER NOT NULL,
            payload_json TEXT NOT NULL,
            PRIMARY KEY (entity_id, revision)
        );
        CREATE TABLE shots (
            entity_id TEXT NOT NULL,
            revision INTEGER NOT NULL,
            asset_entity_id TEXT NOT NULL,
            asset_revision INTEGER NOT NULL,
            payload_json TEXT NOT NULL,
            PRIMARY KEY (entity_id, revision)
        );
        CREATE TABLE shot_analyses (
            shot_entity_id TEXT NOT NULL,
            shot_revision INTEGER NOT NULL,
            analysis_revision INTEGER NOT NULL,
            payload_json TEXT NOT NULL,
            PRIMARY KEY (shot_entity_id, shot_revision, analysis_revision)
        );
        CREATE TABLE project_migrations (
            migration_id TEXT NOT NULL PRIMARY KEY,
            from_version INTEGER NOT NULL,
            to_version INTEGER NOT NULL,
            applied_at TEXT NOT NULL
        );
        PRAGMA user_version = 2;
        """
    )
    connection.close()
    original_create = sqlite_database_module._create_v3_tables

    def fail_after_create(connection: sqlite3.Connection) -> None:
        original_create(connection)
        raise RuntimeError("injected v3 migration failure")

    monkeypatch.setattr(sqlite_database_module, "_create_v3_tables", fail_after_create)

    with pytest.raises(RuntimeError, match="injected v3 migration failure"):
        SqliteProjectDatabase(path).initialize()

    connection = sqlite3.connect(path)
    try:
        version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        brief_table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='briefs'"
        ).fetchone()
    finally:
        connection.close()

    assert version == 2
    assert brief_table is None

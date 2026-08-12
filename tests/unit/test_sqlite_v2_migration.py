from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.asset.policy import (
    AssetUsageRole,
    is_visual_resolver_eligible,
)
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.storage.repositories import sqlite_database as sqlite_database_module
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase
from video_editing_agent.storage.repositories.sqlite_repositories import (
    SqliteAssetRepository,
    SqliteShotRepository,
)

NOW = datetime(2026, 8, 11, 3, 0, tzinfo=UTC)


def _create_v1_database(path: Path, *, origin: str = "remote_allowed") -> str:
    payload = json.dumps(
        {
            "codec_version": 1,
            "record_type": "asset",
            "envelope": {
                "id": "ast_legacy",
                "revision": 1,
                "schema_version": "0.1.1",
                "status": "valid",
                "created_at": NOW.isoformat(),
                "created_by": "legacy-test",
            },
            "media_kind": "video",
            "origin": origin,
            "storage_ref": "file:///tmp/legacy.mp4",
            "content_hash": "sha256:" + "5" * 64,
            "byte_size": 10,
            "provenance": {
                "origin_type": origin,
                "provider": None,
                "provider_asset_id": None,
                "source_page": None,
                "creator": None,
                "retrieved_at": None,
                "license_information": None,
                "attribution": None,
            },
            "imported_at": NOW.isoformat(),
            "duration_ms": 2500,
            "width": 320,
            "height": 180,
            "fps": 25.0,
            "codec": "h264",
            "audio_channels": 2,
            "sample_rate_hz": 48000,
            "user_labels": [],
            "collection_refs": [],
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE assets (
            entity_id TEXT NOT NULL,
            revision INTEGER NOT NULL CHECK (revision >= 1),
            payload_json TEXT NOT NULL,
            PRIMARY KEY (entity_id, revision)
        );
        CREATE TABLE shots (
            entity_id TEXT NOT NULL,
            revision INTEGER NOT NULL CHECK (revision >= 1),
            asset_entity_id TEXT NOT NULL,
            asset_revision INTEGER NOT NULL CHECK (asset_revision >= 1),
            payload_json TEXT NOT NULL,
            PRIMARY KEY (entity_id, revision),
            FOREIGN KEY (asset_entity_id, asset_revision)
                REFERENCES assets (entity_id, revision) ON DELETE RESTRICT
        );
        CREATE TABLE shot_analyses (
            shot_entity_id TEXT NOT NULL,
            shot_revision INTEGER NOT NULL CHECK (shot_revision >= 1),
            analysis_revision INTEGER NOT NULL CHECK (analysis_revision >= 1),
            payload_json TEXT NOT NULL,
            PRIMARY KEY (shot_entity_id, shot_revision, analysis_revision),
            FOREIGN KEY (shot_entity_id, shot_revision)
                REFERENCES shots (entity_id, revision) ON DELETE RESTRICT
        );
        PRAGMA user_version = 1;
        """
    )
    connection.execute(
        "INSERT INTO assets (entity_id, revision, payload_json) VALUES (?, ?, ?)",
        ("ast_legacy", 1, payload),
    )
    connection.commit()
    connection.close()
    return payload


def _envelope(entity_id: str) -> EntityEnvelope:
    return EntityEnvelope(
        id=entity_id,
        revision=1,
        schema_version="0.2",
        status=EntityStatus.VALID,
        created_at=NOW,
        created_by="test",
    )


def test_v1_database_migrates_without_rewriting_legacy_payload(tmp_path: Path) -> None:
    path = tmp_path / "legacy.sqlite3"
    original_payload = _create_v1_database(path)
    database = SqliteProjectDatabase(path)

    database.initialize()

    assert database.schema_version() == 4
    with database.read_connection() as connection:
        row = connection.execute(
            "SELECT payload_json FROM assets WHERE entity_id = 'ast_legacy' AND revision = 1"
        ).fetchone()
        migrations = connection.execute(
            "SELECT from_version, to_version FROM project_migrations ORDER BY to_version"
        ).fetchall()
    assert row is not None
    assert str(row["payload_json"]) == original_payload
    assert [(item["from_version"], item["to_version"]) for item in migrations] == [
        (1, 2),
        (2, 3),
        (3, 4),
    ]


def test_legacy_remote_visual_migrates_fail_closed(tmp_path: Path) -> None:
    path = tmp_path / "legacy.sqlite3"
    _create_v1_database(path, origin="remote_allowed")
    database = SqliteProjectDatabase(path)
    database.initialize()

    loaded = SqliteAssetRepository(database).load(EntityRevisionRef("ast_legacy", 1))

    assert loaded.usage_role is AssetUsageRole.RESTRICTED_LEGACY_VISUAL
    assert not is_visual_resolver_eligible(
        media_kind=loaded.media_kind,
        origin=loaded.origin,
        usage_role=loaded.usage_role,
    )


def test_legacy_local_visual_retains_historical_editable_role(tmp_path: Path) -> None:
    path = tmp_path / "legacy.sqlite3"
    _create_v1_database(path, origin="local")
    database = SqliteProjectDatabase(path)
    database.initialize()

    loaded = SqliteAssetRepository(database).load(EntityRevisionRef("ast_legacy", 1))

    assert loaded.usage_role is AssetUsageRole.EDITABLE_VISUAL_FOOTAGE


def test_schema_migration_is_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "legacy.sqlite3"
    _create_v1_database(path)
    database = SqliteProjectDatabase(path)

    database.initialize()
    database.initialize()

    with database.read_connection() as connection:
        count = int(connection.execute("SELECT COUNT(*) FROM project_migrations").fetchone()[0])
    assert count == 3


def test_schema_migration_rolls_back_transactionally(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "legacy.sqlite3"
    _create_v1_database(path)
    original_create = sqlite_database_module._create_v2_tables

    def fail_after_create(connection: sqlite3.Connection) -> None:
        original_create(connection)
        raise RuntimeError("injected migration failure")

    monkeypatch.setattr(sqlite_database_module, "_create_v2_tables", fail_after_create)

    with pytest.raises(RuntimeError, match="injected migration failure"):
        SqliteProjectDatabase(path).initialize()

    connection = sqlite3.connect(path)
    try:
        version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        migration_table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='project_migrations'"
        ).fetchone()
    finally:
        connection.close()

    assert version == 1
    assert migration_table is None


def test_v2_repository_round_trip_preserves_exact_time_and_usage_role(tmp_path: Path) -> None:
    path = tmp_path / "project.sqlite3"
    database = SqliteProjectDatabase(path)
    database.initialize()
    assets = SqliteAssetRepository(database)
    shots = SqliteShotRepository(database)
    exact_asset = Asset(
        envelope=_envelope("ast_exact"),
        media_kind="video",
        origin="local",
        usage_role=AssetUsageRole.REFERENCE_ANALYSIS_ONLY,
        storage_ref="file:///tmp/exact.mp4",
        content_hash="sha256:" + "6" * 64,
        byte_size=10,
        provenance=AssetProvenance(origin_type="local"),
        imported_at=NOW,
        duration=MediaTime(1001, 400),
    )
    exact_shot = Shot(
        envelope=_envelope("sht_exact"),
        asset_ref=EntityRevisionRef("ast_exact", 1),
        source_range=MediaTimeRange(
            start=MediaTime(1, 24),
            duration=MediaTime(1, 24),
        ),
        boundary_method="exact-test",
    )

    assets.save(exact_asset)
    shots.save(exact_shot)

    reopened = SqliteProjectDatabase(path)
    reopened.initialize()
    loaded_asset = SqliteAssetRepository(reopened).load(EntityRevisionRef("ast_exact", 1))
    loaded_shot = SqliteShotRepository(reopened).load(EntityRevisionRef("sht_exact", 1))

    assert loaded_asset == exact_asset
    assert loaded_shot == exact_shot
    with reopened.read_connection() as connection:
        asset_payload = json.loads(
            str(
                connection.execute(
                    "SELECT payload_json FROM assets WHERE entity_id='ast_exact' AND revision=1"
                ).fetchone()[0]
            )
        )
    assert asset_payload["codec_version"] == 2
    assert asset_payload["duration"] == {"scale": 400, "value": 1001}
    assert asset_payload["usage_role"] == "reference_analysis_only"

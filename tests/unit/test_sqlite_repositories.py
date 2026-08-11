from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.shot.analysis import (
    AnalysisProfile,
    NamedQualityScore,
    ShotAnalysis,
    SpeechContent,
    VisualSemantics,
)
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.storage.repositories.sqlite_database import (
    SqliteProjectDatabase,
    UnsupportedSchemaVersionError,
)
from video_editing_agent.storage.repositories.sqlite_repositories import (
    RevisionConflictError,
    SqliteAssetRepository,
    SqliteShotAnalysisRepository,
    SqliteShotRepository,
)

NOW = datetime(2026, 8, 10, 8, 30, tzinfo=UTC)


def envelope(entity_id: str, revision: int = 1) -> EntityEnvelope:
    return EntityEnvelope(
        id=entity_id,
        revision=revision,
        schema_version="0.1.1",
        status=EntityStatus.VALID,
        created_at=NOW,
        created_by="test",
    )


def asset(*, storage_ref: str = "file:///tmp/example.mp4") -> Asset:
    return Asset(
        envelope=envelope("ast_sqlite"),
        media_kind="video",
        origin="local",
        storage_ref=storage_ref,
        content_hash="sha256:" + "1" * 64,
        byte_size=1234,
        provenance=AssetProvenance(
            origin_type="local",
            creator="tester",
            retrieved_at=NOW,
            license_information="private-source",
        ),
        imported_at=NOW,
        duration_ms=4_000,
        width=320,
        height=180,
        fps=25.0,
        codec="mpeg4",
        audio_channels=1,
        sample_rate_hz=48_000,
        user_labels=("probe", "local"),
        collection_refs=("collection-a",),
    )


def shot(*, entity_id: str = "sht_sqlite", asset_revision: int = 1) -> Shot:
    return Shot(
        envelope=envelope(entity_id),
        asset_ref=EntityRevisionRef("ast_sqlite", asset_revision),
        source_start_ms=0,
        source_end_ms=1_000,
        boundary_method="transnetv2",
    )


def analysis(*, revision: int, shot_revision: int = 1) -> ShotAnalysis:
    return ShotAnalysis(
        shot_ref=EntityRevisionRef("sht_sqlite", shot_revision),
        revision=revision,
        profile=AnalysisProfile.EDITORIAL,
        analyzed_at=NOW,
        technical_quality=(NamedQualityScore("aesthetic", 0.82),),
        visual=VisualSemantics(
            summary="Person enters the room.",
            tags=("person", "room"),
            subjects=("person",),
            actions=("entering",),
            environment="indoors",
            framing="medium",
            camera_motion="static",
        ),
        speech=SpeechContent(transcript="hello", language="en"),
        artifact_refs=("art_sha256_abc", "art_sha256_def"),
    )


def database(path: Path) -> SqliteProjectDatabase:
    result = SqliteProjectDatabase(path)
    result.initialize()
    return result


def test_schema_bootstrap_sets_version_and_creates_parent(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "project.sqlite3"
    db = database(path)

    assert path.is_file()
    assert db.schema_version() == 3


def test_rejects_unknown_existing_schema_version(tmp_path: Path) -> None:
    path = tmp_path / "future.sqlite3"
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA user_version = 99")
    connection.close()

    with pytest.raises(UnsupportedSchemaVersionError, match="99"):
        SqliteProjectDatabase(path).initialize()


def test_asset_round_trip_survives_repository_reopen(tmp_path: Path) -> None:
    path = tmp_path / "project.sqlite3"
    first_db = database(path)
    expected = asset()
    SqliteAssetRepository(first_db).save(expected)

    reopened = database(path)
    loaded = SqliteAssetRepository(reopened).load(EntityRevisionRef("ast_sqlite", 1))

    assert loaded == expected


def test_exact_revision_save_is_idempotent_but_not_mutable(tmp_path: Path) -> None:
    repository = SqliteAssetRepository(database(tmp_path / "project.sqlite3"))
    original = asset()
    repository.save(original)
    repository.save(original)

    with pytest.raises(RevisionConflictError):
        repository.save(asset(storage_ref="file:///tmp/different.mp4"))


def test_shot_requires_exact_asset_revision_and_round_trips(tmp_path: Path) -> None:
    db = database(tmp_path / "project.sqlite3")
    shots = SqliteShotRepository(db)

    with pytest.raises(sqlite3.IntegrityError):
        shots.save(shot())

    SqliteAssetRepository(db).save(asset())
    expected = shot()
    shots.save(expected)

    reopened = database(tmp_path / "project.sqlite3")
    assert SqliteShotRepository(reopened).load(EntityRevisionRef("sht_sqlite", 1)) == expected


def test_analysis_requires_exact_shot_revision(tmp_path: Path) -> None:
    db = database(tmp_path / "project.sqlite3")
    analyses = SqliteShotAnalysisRepository(db)

    with pytest.raises(sqlite3.IntegrityError):
        analyses.save(analysis(revision=1))


def test_latest_analysis_is_scoped_to_exact_shot_revision_after_reopen(tmp_path: Path) -> None:
    path = tmp_path / "project.sqlite3"
    db = database(path)
    SqliteAssetRepository(db).save(asset())
    SqliteShotRepository(db).save(shot())
    repository = SqliteShotAnalysisRepository(db)
    first = analysis(revision=1)
    second = analysis(revision=2)
    repository.save(first)
    repository.save(second)

    reopened = database(path)
    reopened_repository = SqliteShotAnalysisRepository(reopened)

    assert reopened_repository.latest(EntityRevisionRef("sht_sqlite", 1)) == second
    assert reopened_repository.latest(EntityRevisionRef("sht_sqlite", 2)) is None


def test_analysis_exact_revision_conflict_does_not_replace_history(tmp_path: Path) -> None:
    db = database(tmp_path / "project.sqlite3")
    SqliteAssetRepository(db).save(asset())
    SqliteShotRepository(db).save(shot())
    repository = SqliteShotAnalysisRepository(db)
    original = analysis(revision=1)
    repository.save(original)

    changed = ShotAnalysis(
        shot_ref=original.shot_ref,
        revision=original.revision,
        profile=original.profile,
        analyzed_at=original.analyzed_at,
        visual=VisualSemantics(summary="different"),
    )
    with pytest.raises(RevisionConflictError):
        repository.save(changed)

    assert repository.latest(original.shot_ref) == original

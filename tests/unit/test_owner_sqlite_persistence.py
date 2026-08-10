from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.application.ports.shot_detector import ShotBoundaryProposal
from video_editing_agent.domain.asset.model import AssetProvenance
from video_editing_agent.domain.common.entity import (
    EntityEnvelope,
    EntityRevisionRef,
    EntityStatus,
)
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.ingest.probe import MediaTechnicalMetadata
from video_editing_agent.media.ingest.service import AssetIngestService
from video_editing_agent.media.ingest.source import LocalMediaSource
from video_editing_agent.media.shot_detection.catalog import ShotCatalog
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase
from video_editing_agent.storage.repositories.sqlite_repositories import (
    RevisionConflictError,
    SqliteAssetRepository,
    SqliteShotRepository,
)


class StaticProbe:
    def probe(self, path: Path) -> MediaTechnicalMetadata:
        assert path.is_file()
        return MediaTechnicalMetadata(media_kind="video", duration_ms=2_000)


class SequentialIds:
    def __init__(self) -> None:
        self.index = 0

    def __call__(self) -> str:
        self.index += 1
        return f"sht_persist_{self.index}"


def test_asset_and_shot_owner_commits_survive_reopen(tmp_path: Path) -> None:
    database_path = tmp_path / "project.sqlite3"
    database = SqliteProjectDatabase(database_path)
    database.initialize()
    asset_repository = SqliteAssetRepository(database)
    shot_repository = SqliteShotRepository(database)

    media_path = tmp_path / "clip.mp4"
    media_path.write_bytes(b"persistent-media")
    now = datetime(2026, 8, 10, 9, 30, tzinfo=UTC)
    ingest = AssetIngestService(
        StaticProbe(),
        repository=asset_repository,
        asset_id_factory=lambda: "ast_persist",
        clock=lambda: now,
    )
    asset = ingest.ingest(
        LocalMediaSource(
            path=media_path,
            origin="local",
            provenance=AssetProvenance(origin_type="local"),
        )
    )

    asset_ref = EntityRevisionRef(asset.envelope.id, asset.envelope.revision)
    catalog = ShotCatalog(
        repository=shot_repository,
        shot_id_factory=SequentialIds(),
        clock=lambda: now,
    )
    shots = catalog.commit_boundaries(
        (
            ShotBoundaryProposal(asset_ref, 0, 1_000, "test"),
            ShotBoundaryProposal(asset_ref, 1_000, 2_000, "test"),
        )
    )

    reopened = SqliteProjectDatabase(database_path)
    reopened.initialize()
    assert SqliteAssetRepository(reopened).load(asset_ref) == asset
    loaded = tuple(
        SqliteShotRepository(reopened).load(
            EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
        )
        for shot in shots
    )
    assert loaded == shots


def test_shot_batch_write_rolls_back_on_conflicting_revision(tmp_path: Path) -> None:
    database = SqliteProjectDatabase(tmp_path / "rollback.sqlite3")
    database.initialize()
    assets = SqliteAssetRepository(database)
    shots = SqliteShotRepository(database)

    media_path = tmp_path / "rollback.mp4"
    media_path.write_bytes(b"rollback")
    now = datetime(2026, 8, 10, 9, 31, tzinfo=UTC)
    asset = AssetIngestService(
        StaticProbe(),
        repository=assets,
        asset_id_factory=lambda: "ast_rollback",
        clock=lambda: now,
    ).ingest(
        LocalMediaSource(
            path=media_path,
            origin="local",
            provenance=AssetProvenance(origin_type="local"),
        )
    )
    asset_ref = EntityRevisionRef(asset.envelope.id, 1)

    existing = Shot(
        envelope=EntityEnvelope(
            id="sht_conflict",
            revision=1,
            schema_version="0.1.1",
            status=EntityStatus.VALID,
            created_at=now,
            created_by="test",
        ),
        asset_ref=asset_ref,
        source_start_ms=0,
        source_end_ms=1_000,
        boundary_method="test",
    )
    shots.save(existing)

    first_new = Shot(
        envelope=EntityEnvelope(
            id="sht_should_rollback",
            revision=1,
            schema_version="0.1.1",
            status=EntityStatus.VALID,
            created_at=now,
            created_by="test",
        ),
        asset_ref=asset_ref,
        source_start_ms=1_000,
        source_end_ms=1_500,
        boundary_method="test",
    )
    conflicting = Shot(
        envelope=existing.envelope,
        asset_ref=asset_ref,
        source_start_ms=0,
        source_end_ms=900,
        boundary_method="different",
    )

    with pytest.raises(RevisionConflictError):
        shots.save_many((first_new, conflicting))

    with pytest.raises(KeyError):
        shots.load(EntityRevisionRef("sht_should_rollback", 1))
    assert shots.load(EntityRevisionRef("sht_conflict", 1)) == existing

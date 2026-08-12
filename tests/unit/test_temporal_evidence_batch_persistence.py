from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.evidence.temporal import TemporalEvidence
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase
from video_editing_agent.storage.repositories.sqlite_repositories import (
    SqliteAssetRepository,
    SqliteShotRepository,
)
from video_editing_agent.storage.repositories.temporal_evidence_repository import (
    SqliteTemporalEvidenceRepository,
    TemporalEvidenceConflictError,
)

NOW = datetime(2026, 8, 12, 17, 0, tzinfo=UTC)


def _repository(path: Path) -> tuple[SqliteTemporalEvidenceRepository, EntityRevisionRef]:
    database = SqliteProjectDatabase(path)
    database.initialize()
    asset = Asset(
        envelope=EntityEnvelope(
            "ast_batch",
            1,
            "0.2",
            EntityStatus.VALID,
            NOW,
            "test",
        ),
        media_kind="video",
        origin="imported_local",
        storage_ref="file:///batch.mp4",
        content_hash="sha256:" + "8" * 64,
        byte_size=10,
        provenance=AssetProvenance("imported_local"),
        imported_at=NOW,
        duration=MediaTime(5, 1),
    )
    shot = Shot(
        envelope=EntityEnvelope(
            "sht_batch",
            1,
            "0.2",
            EntityStatus.VALID,
            NOW,
            "test",
        ),
        asset_ref=EntityRevisionRef("ast_batch", 1),
        source_range=MediaTimeRange(MediaTime(1, 1), MediaTime(3, 1)),
        boundary_method="test",
    )
    SqliteAssetRepository(database).save(asset)
    SqliteShotRepository(database).save(shot)
    return SqliteTemporalEvidenceRepository(database), EntityRevisionRef("sht_batch", 1)


def _evidence(
    evidence_id: str,
    shot_ref: EntityRevisionRef,
    *,
    start: int,
    duration: int,
    confidence: float,
) -> TemporalEvidence:
    return TemporalEvidence(
        evidence_id=evidence_id,
        shot_ref=shot_ref,
        kind="silence",
        method="fake-vad",
        producer_version="r1",
        confidence=confidence,
        source_range=MediaTimeRange(MediaTime(start, 10), MediaTime(duration, 10)),
    )


def test_batch_save_is_idempotent_and_persists_complete_set(tmp_path: Path) -> None:
    repository, shot_ref = _repository(tmp_path / "project.sqlite3")
    first = _evidence("tev_a", shot_ref, start=10, duration=5, confidence=0.9)
    second = _evidence("tev_b", shot_ref, start=15, duration=5, confidence=0.8)

    repository.save_evidence_batch((first, second))
    repository.save_evidence_batch((first, second))

    assert repository.list_evidence(shot_ref) == (first, second)


def test_batch_conflict_rolls_back_earlier_new_rows(tmp_path: Path) -> None:
    repository, shot_ref = _repository(tmp_path / "project.sqlite3")
    original = _evidence("tev_existing", shot_ref, start=20, duration=5, confidence=0.7)
    repository.save_evidence(original)
    new = _evidence("tev_new", shot_ref, start=10, duration=5, confidence=0.9)
    conflict = replace(original, confidence=0.2)

    with pytest.raises(TemporalEvidenceConflictError):
        repository.save_evidence_batch((new, conflict))

    assert repository.list_evidence(shot_ref) == (original,)

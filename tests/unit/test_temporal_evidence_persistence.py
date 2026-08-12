from __future__ import annotations

from datetime import UTC, datetime

import pytest

from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.evidence.temporal import TemporalAnchor, TemporalEvidence
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase
from video_editing_agent.storage.repositories.sqlite_repositories import (
    SqliteAssetRepository,
    SqliteShotRepository,
)
from video_editing_agent.storage.repositories.temporal_evidence_repository import (
    SqliteTemporalEvidenceRepository,
)

NOW = datetime(2026, 8, 13, tzinfo=UTC)


def _database(path):
    database = SqliteProjectDatabase(path)
    database.initialize()
    envelope = EntityEnvelope("ast_temporal", 1, "0.2", EntityStatus.VALID, NOW, "test")
    SqliteAssetRepository(database).save(
        Asset(
            envelope,
            "video",
            "imported_local",
            "file:///local.mp4",
            "sha256:" + "1" * 64,
            10,
            AssetProvenance("imported_local"),
            NOW,
            duration=MediaTime(10, 1),
        )
    )
    SqliteShotRepository(database).save(
        Shot(
            EntityEnvelope("sht_temporal", 1, "0.2", EntityStatus.VALID, NOW, "test"),
            EntityRevisionRef("ast_temporal", 1),
            source_range=MediaTimeRange(MediaTime(1, 3), MediaTime(5, 7)),
            boundary_method="test",
        )
    )
    return database


def test_temporal_evidence_and_anchor_round_trip_after_reopen(tmp_path) -> None:
    path = tmp_path / "project.sqlite3"
    shot_ref = EntityRevisionRef("sht_temporal", 1)
    repository = SqliteTemporalEvidenceRepository(_database(path))
    evidence = TemporalEvidence(
        "tev_one",
        shot_ref,
        "speech",
        "fixture",
        "1.2.3",
        0.75,
        MediaTimeRange(MediaTime(1, 3), MediaTime(5, 7)),
        ("art_sha256_abc",),
        ("source",),
    )
    anchor = TemporalAnchor(
        "tan_one",
        shot_ref,
        "word",
        MediaTime(13, 11),
        0.8,
        (evidence.evidence_id,),
        "fixture",
        "hello",
    )
    repository.save_evidence(evidence)
    repository.save_anchor(anchor)

    reopened = SqliteTemporalEvidenceRepository(SqliteProjectDatabase(path))
    assert reopened.list_evidence(shot_ref) == (evidence,)
    assert reopened.list_anchors(shot_ref) == (anchor,)


def test_anchor_rejects_missing_exact_shot_evidence_without_partial_write(tmp_path) -> None:
    shot_ref = EntityRevisionRef("sht_temporal", 1)
    repository = SqliteTemporalEvidenceRepository(_database(tmp_path / "project.sqlite3"))
    anchor = TemporalAnchor(
        "tan_bad", shot_ref, "event", MediaTime(1, 2), 0.5, ("missing",), "fixture"
    )

    with pytest.raises(ValueError, match="unknown evidence"):
        repository.save_anchor(anchor)
    assert repository.list_anchors(shot_ref) == ()

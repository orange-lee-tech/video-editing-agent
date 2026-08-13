from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.application.ports.asset_media import ResolvedLocalAssetMedia
from video_editing_agent.application.ports.visual_motion import (
    VisualMotionMeasurement,
    VisualMotionProposal,
)
from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.temporal.visual_motion import VisualMotionEvidenceService
from video_editing_agent.storage.artifact.lifecycle_repository import (
    LocalArtifactLifecycleRepository,
)
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase
from video_editing_agent.storage.repositories.sqlite_repositories import (
    SqliteAssetRepository,
    SqliteShotRepository,
)
from video_editing_agent.storage.repositories.temporal_evidence_repository import (
    SqliteTemporalEvidenceRepository,
)

NOW = datetime(2026, 8, 13, tzinfo=UTC)
SHOT = EntityRevisionRef("sht_motion", 1)


def _measurement(start: int = 0) -> VisualMotionMeasurement:
    return VisualMotionMeasurement(
        MediaTimeRange(MediaTime(start, 10), MediaTime(1, 10)),
        "available",
        None,
        50,
        45,
        0.8,
        40,
        0.88,
        2.0,
        0.0,
        0.0,
        1.0,
        0.01,
        2.0,
        2.0,
        0.02,
        0.1,
        0.2,
    )


class Port:
    def __init__(self, proposal: VisualMotionProposal):
        self.proposal = proposal

    def measure(self, request):
        return self.proposal


class Resolver:
    def __init__(self, path: Path):
        self.path = path

    def resolve_local(self, asset_ref):
        return ResolvedLocalAssetMedia(asset_ref, self.path)


def _service(tmp_path: Path, proposal: VisualMotionProposal | None = None):
    db_path = tmp_path / "project.sqlite3"
    db = SqliteProjectDatabase(db_path)
    db.initialize()

    def envelope(identity: str) -> EntityEnvelope:
        return EntityEnvelope(identity, 1, "0.2", EntityStatus.VALID, NOW, "test")

    asset_ref = EntityRevisionRef("ast_motion", 1)
    media = tmp_path / "media.mp4"
    media.write_bytes(b"x")
    SqliteAssetRepository(db).save(
        Asset(
            envelope("ast_motion"),
            "video",
            "local",
            media.as_uri(),
            "sha256:" + "1" * 64,
            1,
            AssetProvenance("local"),
            NOW,
            duration=MediaTime(10, 1),
        )
    )
    SqliteShotRepository(db).save(
        Shot(
            envelope("sht_motion"),
            asset_ref,
            source_range=MediaTimeRange(MediaTime(3, 1), MediaTime(2, 1)),
            boundary_method="test",
        )
    )
    proposal = proposal or VisualMotionProposal(
        SHOT, "provider", "r1", 10, 320, 180, (_measurement(),)
    )
    store = LocalArtifactStore(tmp_path / "artifacts")
    service = VisualMotionEvidenceService(
        shot_repository=SqliteShotRepository(db),
        asset_media_resolver=Resolver(media),
        temporal_evidence_repository=SqliteTemporalEvidenceRepository(db),
        artifact_store=store,
        artifact_lifecycle_repository=LocalArtifactLifecycleRepository(tmp_path / "artifacts"),
        motion_port=Port(proposal),
    )
    return service, db_path, store


def test_owner_maps_offset_persists_and_canonical_artifact_is_stable(tmp_path: Path) -> None:
    service, db_path, store = _service(tmp_path)
    evidence = service.measure(SHOT)
    assert {item.kind for item in evidence} == {"visual_motion_measurement_set"}
    assert all(item.source_range.start == MediaTime(3, 1) for item in evidence if item.source_range)
    loaded = SqliteTemporalEvidenceRepository(SqliteProjectDatabase(db_path)).list_evidence(SHOT)
    assert loaded == tuple(sorted(evidence, key=lambda item: item.evidence_id))
    artifact_id = evidence[0].artifact_refs[0]
    assert (
        b'"schema_version":"r0.8c-visual-motion-v1"'
        in next(
            (tmp_path / "artifacts").rglob(artifact_id.removeprefix("art_sha256_"))
        ).read_bytes()
    )


@pytest.mark.parametrize(
    "change,message",
    [
        ({"shot_ref": EntityRevisionRef("wrong", 1)}, "different Shot"),
        ({"measurements": (_measurement(20),)}, "inside exact Shot"),
        ({"measurements": (_measurement(5), _measurement(0))}, "ordered"),
    ],
)
def test_owner_rejects_invalid_proposals(tmp_path: Path, change, message: str) -> None:
    proposal = replace(
        VisualMotionProposal(SHOT, "provider", "r1", 10, 320, 180, (_measurement(),)), **change
    )
    service, _, _ = _service(tmp_path, proposal)
    with pytest.raises(ValueError, match=message):
        service.measure(SHOT)


def test_unavailable_is_not_zero_and_nan_is_rejected(tmp_path: Path) -> None:
    unavailable = replace(
        _measurement(), status="unavailable", reason="weak_global_fit", translation_x=0.0
    )
    service, _, _ = _service(
        tmp_path / "a", VisualMotionProposal(SHOT, "p", "r", 10, 320, 180, (unavailable,))
    )
    with pytest.raises(ValueError, match="masquerade"):
        service.measure(SHOT)
    invalid = replace(_measurement(), residual_max=float("nan"))
    service, _, _ = _service(
        tmp_path / "b", VisualMotionProposal(SHOT, "p", "r", 10, 320, 180, (invalid,))
    )
    with pytest.raises(ValueError, match="finite"):
        service.measure(SHOT)

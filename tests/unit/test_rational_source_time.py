from datetime import UTC, datetime

import pytest

from video_editing_agent.application.ports.artifact_store import StoredArtifactRef
from video_editing_agent.application.ports.shot_detector import ShotBoundaryProposal
from video_editing_agent.application.ports.visual_understanding import VisualFrameReference
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.shot_detection.catalog import ShotCatalog
from video_editing_agent.media.understanding.sampling import (
    FrameSamplingOptions,
    plan_uniform_frame_samples,
)


def envelope(entity_id: str) -> EntityEnvelope:
    return EntityEnvelope(
        id=entity_id,
        revision=1,
        schema_version="0.2",
        status=EntityStatus.VALID,
        created_at=datetime(2026, 8, 11, 2, 30, tzinfo=UTC),
        created_by="test",
    )


def test_shot_stores_canonical_submillisecond_source_range() -> None:
    shot = Shot(
        envelope=envelope("sht_exact"),
        asset_ref=EntityRevisionRef("ast_exact", 1),
        source_range=MediaTimeRange(
            start=MediaTime(1, 24),
            duration=MediaTime(1, 3),
        ),
        boundary_method="exact-test",
    )

    assert shot.source_range.start == MediaTime(1, 24)
    assert shot.source_range.end == MediaTime(3, 8)
    with pytest.raises(ValueError, match="exact integer millisecond"):
        _ = shot.source_start_ms


def test_catalog_commits_contiguous_rational_proposals_without_ms_conversion() -> None:
    proposals = (
        ShotBoundaryProposal(
            asset_ref=EntityRevisionRef("ast_exact", 1),
            source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(1, 24)),
            detection_method="exact-test",
        ),
        ShotBoundaryProposal(
            asset_ref=EntityRevisionRef("ast_exact", 1),
            source_range=MediaTimeRange(MediaTime(1, 24), MediaTime(1, 24)),
            detection_method="exact-test",
        ),
    )
    ids = iter(("sht_a", "sht_b"))
    catalog = ShotCatalog(shot_id_factory=lambda: next(ids))

    shots = catalog.commit_boundaries(proposals)

    assert shots[0].source_range.end == shots[1].source_range.start
    assert shots[1].source_range.end == MediaTime(1, 12)


def test_fractional_shot_sampling_remains_exact_and_inside_source_range() -> None:
    shot = Shot(
        envelope=envelope("sht_sample_exact"),
        asset_ref=EntityRevisionRef("ast_exact", 1),
        source_range=MediaTimeRange(MediaTime(1, 24), MediaTime(1, 24)),
        boundary_method="exact-test",
    )

    plan = plan_uniform_frame_samples(shot, FrameSamplingOptions(max_frames=3))

    assert [sample.source_timestamp for sample in plan.samples] == [
        MediaTime(7, 144),
        MediaTime(1, 16),
        MediaTime(11, 144),
    ]
    assert all(
        shot.source_range.start.as_fraction()
        < sample.source_timestamp.as_fraction()
        < shot.source_range.end.as_fraction()
        for sample in plan.samples
    )


def test_visual_frame_reference_accepts_exact_non_ms_timestamp() -> None:
    artifact = StoredArtifactRef(
        artifact_id="art_sha256_" + "1" * 64,
        content_hash="sha256:" + "1" * 64,
        media_type="image/png",
        byte_size=1,
    )
    frame = VisualFrameReference(
        artifact_ref=artifact,
        ordinal=0,
        source_timestamp=MediaTime(1, 24),
    )

    assert frame.source_timestamp.to_decimal_seconds_string() == "0.041666667"
    with pytest.raises(ValueError, match="exact integer millisecond"):
        _ = frame.source_timestamp_ms

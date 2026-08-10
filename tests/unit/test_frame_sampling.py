from datetime import UTC, datetime

import pytest

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.understanding.sampling import (
    FrameSamplingOptions,
    plan_uniform_frame_samples,
)


def make_shot(start_ms: int, end_ms: int, *, revision: int = 1) -> Shot:
    return Shot(
        envelope=EntityEnvelope(
            id="sht_sample",
            revision=revision,
            schema_version="0.1.1",
            status=EntityStatus.VALID,
            created_at=datetime(2026, 8, 10, 8, 5, tzinfo=UTC),
            created_by="test",
        ),
        asset_ref=EntityRevisionRef("ast_1", 1),
        source_start_ms=start_ms,
        source_end_ms=end_ms,
        boundary_method="test",
    )


def test_uniform_sampling_uses_midpoints_of_equal_bins() -> None:
    plan = plan_uniform_frame_samples(make_shot(1_000, 2_000))

    assert plan.shot_ref == EntityRevisionRef("sht_sample", 1)
    assert [sample.source_timestamp_ms for sample in plan.samples] == [
        1_100,
        1_300,
        1_500,
        1_700,
        1_900,
    ]
    assert [sample.ordinal for sample in plan.samples] == [0, 1, 2, 3, 4]


def test_sampling_never_creates_duplicate_millisecond_positions() -> None:
    plan = plan_uniform_frame_samples(
        make_shot(2_000, 2_002),
        FrameSamplingOptions(max_frames=5),
    )

    assert [sample.source_timestamp_ms for sample in plan.samples] == [2_000, 2_001]


def test_sampling_tracks_exact_shot_revision() -> None:
    plan = plan_uniform_frame_samples(make_shot(0, 100, revision=4))

    assert all(sample.shot_ref == EntityRevisionRef("sht_sample", 4) for sample in plan.samples)


def test_sampling_is_deterministic() -> None:
    shot = make_shot(500, 1_500)
    options = FrameSamplingOptions(max_frames=7)

    assert plan_uniform_frame_samples(shot, options) == plan_uniform_frame_samples(shot, options)


def test_sampling_options_require_positive_frame_budget() -> None:
    with pytest.raises(ValueError, match="max_frames"):
        FrameSamplingOptions(max_frames=0)

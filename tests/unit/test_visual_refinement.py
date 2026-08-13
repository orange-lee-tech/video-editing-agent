from __future__ import annotations

import pytest
from test_visual_motion_events import _item
from test_visual_motion_foundation import SHOT, _service

from video_editing_agent.application.ports.visual_motion import VisualMotionProposal
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.evidence.temporal import TemporalEvidence
from video_editing_agent.media.temporal.visual_events import (
    MotionEventPolicy,
    VisualMotionEventService,
)
from video_editing_agent.media.temporal.visual_refinement import (
    VisualMotionRefinementService,
    VisualRefinementPolicy,
)
from video_editing_agent.storage.repositories.temporal_evidence_repository import (
    SqliteTemporalEvidenceRepository,
)


def test_refinement_uses_bounded_subrange_and_persists_asset_time(tmp_path) -> None:
    proposal = VisualMotionProposal(
        SHOT,
        "provider",
        "r1",
        30,
        320,
        180,
        tuple(_item(index, 0, 3) for index in range(6)),
    )
    owner, _, store = _service(tmp_path, proposal)
    repository = SqliteTemporalEvidenceRepository(owner._evidence._database)
    coarse = TemporalEvidence(
        "tev_coarse",
        SHOT,
        "residual_motion_region",
        "coarse",
        "v1",
        0.9,
        MediaTimeRange(MediaTime(7, 2), MediaTime(1, 2)),
    )
    repository.save_evidence(coarse)
    event_policy = MotionEventPolicy("fine-events-v1", 0.03, 0.02, 0.03, 0.02, 2, 0)
    service = VisualMotionRefinementService(
        shot_repository=owner._shots,
        temporal_evidence_repository=repository,
        motion_evidence_service=owner,
        event_service=VisualMotionEventService(
            shot_repository=owner._shots,
            temporal_evidence_repository=repository,
            artifact_store=store,
        ),
    )
    regions, anchors = service.refine(
        SHOT,
        coarse.evidence_id,
        VisualRefinementPolicy("fine-v1", MediaTime(1, 10), event_policy),
    )
    measurement = next(
        item
        for item in repository.list_evidence(SHOT)
        if item.kind == "visual_motion_measurement_set"
    )
    assert measurement.source_range == MediaTimeRange(MediaTime(17, 5), MediaTime(7, 10))
    assert all(
        item.source_range.start.as_fraction() >= MediaTime(17, 5).as_fraction()
        for item in regions
        if item.source_range
    )
    assert [item.source_time.as_fraction() for item in anchors] == sorted(
        item.source_time.as_fraction() for item in anchors
    )


def test_refinement_clips_to_shot_and_rejects_wrong_input(tmp_path) -> None:
    proposal = VisualMotionProposal(
        SHOT, "provider", "r1", 30, 320, 180, tuple(_item(i, 0, 3) for i in range(3))
    )
    owner, _, store = _service(tmp_path, proposal)
    repository = SqliteTemporalEvidenceRepository(owner._evidence._database)
    wrong = TemporalEvidence(
        "wrong", SHOT, "silence", "x", "v1", 1.0, MediaTimeRange(MediaTime(3, 1), MediaTime(1, 10))
    )
    repository.save_evidence(wrong)
    service = VisualMotionRefinementService(
        shot_repository=owner._shots,
        temporal_evidence_repository=repository,
        motion_evidence_service=owner,
        event_service=VisualMotionEventService(
            shot_repository=owner._shots,
            temporal_evidence_repository=repository,
            artifact_store=store,
        ),
    )
    policy = VisualRefinementPolicy(
        "fine", MediaTime(1, 1), MotionEventPolicy("events", 0.03, 0.02, 0.03, 0.02, 2, 0)
    )
    with pytest.raises(ValueError, match="coarse motion region"):
        service.refine(SHOT, wrong.evidence_id, policy)

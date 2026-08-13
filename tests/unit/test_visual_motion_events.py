from __future__ import annotations

from dataclasses import replace

from test_visual_motion_foundation import SHOT, _service

from video_editing_agent.application.ports.visual_motion import (
    VisualMotionMeasurement,
    VisualMotionProposal,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.media.temporal.visual_events import (
    MotionEventPolicy,
    VisualMotionEventService,
)
from video_editing_agent.storage.repositories.temporal_evidence_repository import (
    SqliteTemporalEvidenceRepository,
)

POLICY = MotionEventPolicy("controlled-v1", 0.03, 0.02, 0.03, 0.02, 2, 0)


def _item(index: int, global_px: float, residual_px: float, status: str = "available"):
    return VisualMotionMeasurement(
        MediaTimeRange(MediaTime(index, 10), MediaTime(1, 10)),
        status,
        None if status == "available" else "tracking_failure",
        50,
        45,
        0.8,
        40,
        0.9,
        0.0 if status == "available" else None,
        0.0 if status == "available" else None,
        0.0 if status == "available" else None,
        1.0 if status == "available" else None,
        0.01 if status == "available" else None,
        global_px if status == "available" else None,
        global_px,
        0.01 if status == "available" else None,
        residual_px if status == "available" else None,
        residual_px if status == "available" else None,
    )


def _run(tmp_path, values, *, legacy=False):
    proposal = VisualMotionProposal(
        SHOT,
        "provider",
        "r1",
        10,
        320,
        180,
        tuple(_item(i, *value) for i, value in enumerate(values)),
    )
    owner, db_path, store = _service(tmp_path, proposal)
    measurement = owner.measure(SHOT)[0]
    repository = SqliteTemporalEvidenceRepository(owner._evidence._database)
    if legacy:
        measurement = replace(measurement, evidence_id="legacy", kind="residual_motion_measurement")
        repository.save_evidence(measurement)
    regions, anchors = VisualMotionEventService(
        shot_repository=owner._shots, temporal_evidence_repository=repository, artifact_store=store
    ).reduce(SHOT, measurement.evidence_id, POLICY)
    return regions, anchors


def test_controlled_event_matrix_and_anchor_order(tmp_path) -> None:
    static = _run(tmp_path / "static", [(0, 0)] * 5)
    assert static == ((), ())
    pan_regions, pan_anchors = _run(tmp_path / "pan", [(2, 0.01)] * 5)
    assert [x.kind for x in pan_regions] == ["camera_motion_region"]
    assert all("residual" not in x.kind for x in pan_anchors)
    local_regions, local_anchors = _run(tmp_path / "local", [(0, 3)] * 5)
    assert [x.kind for x in local_regions] == ["residual_motion_region"]
    assert [x.source_time.as_fraction() for x in local_anchors] == sorted(
        x.source_time.as_fraction() for x in local_anchors
    )
    both, _ = _run(tmp_path / "both", [(2, 3)] * 5)
    assert {x.kind for x in both} == {"camera_motion_region", "residual_motion_region"}


def test_bursts_and_unavailable_gap_split_and_legacy_matches(tmp_path) -> None:
    values = [(0, 3), (0, 3), (0, 0), (0, 0), (0, 3), (0, 3)]
    regions, anchors = _run(tmp_path / "bursts", values)
    assert len(regions) == 2 and len(anchors) == 6
    gap = [(0, 3), (0, 3), (0, 0, "unavailable"), (0, 3), (0, 3)]
    regions, _ = _run(tmp_path / "gap", gap)
    assert len(regions) == 2
    legacy, _ = _run(tmp_path / "legacy", values, legacy=True)
    assert [x.source_range for x in legacy] == [
        x.source_range for x in _run(tmp_path / "new", values)[0]
    ]

from __future__ import annotations

from dataclasses import replace

import pytest
from test_visual_motion_foundation import SHOT, _service

from video_editing_agent.application.ports.seeded_tracking import (
    NormalizedRectangle,
    SeededTrackingProposal,
    TrackingSample,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.media.temporal.seeded_tracking import SeededTrackingEvidenceService
from video_editing_agent.storage.artifact.lifecycle_repository import (
    LocalArtifactLifecycleRepository,
)
from video_editing_agent.storage.repositories.temporal_evidence_repository import (
    SqliteTemporalEvidenceRepository,
)


class Port:
    def __init__(self, proposal):
        self.proposal = proposal

    def track(self, request):
        return replace(
            self.proposal,
            analyzed_source_range=request.source_range,
            seed_id=request.seed_id,
            seed_rectangle=request.seed_rectangle,
        )


def _tracking_service(tmp_path, proposal):
    motion, db_path, store = _service(tmp_path)
    return (
        SeededTrackingEvidenceService(
            shot_repository=motion._shots,
            asset_media_resolver=motion._media,
            temporal_evidence_repository=SqliteTemporalEvidenceRepository(
                motion._evidence._database
            ),
            artifact_store=store,
            artifact_lifecycle_repository=LocalArtifactLifecycleRepository(tmp_path / "artifacts"),
            tracking_port=Port(proposal),
        ),
        db_path,
        store,
    )


def _proposal(samples):
    seed = NormalizedRectangle(0.2, 0.3, 0.2, 0.2)
    return SeededTrackingProposal(
        SHOT,
        MediaTimeRange(MediaTime(3, 1), MediaTime(1, 1)),
        "seed",
        seed,
        "provider",
        "r1",
        30,
        320,
        180,
        tuple(samples),
    )


def test_tracking_owner_persists_reopens_and_is_deterministic(tmp_path) -> None:
    seed = NormalizedRectangle(0.2, 0.3, 0.2, 0.2)
    samples = (
        TrackingSample(MediaTime(0, 30), "available", None, seed, 12, 1.0),
        TrackingSample(MediaTime(1, 30), "available", None, replace(seed, x=0.21), 11, 0.92),
    )
    service, db_path, store = _tracking_service(tmp_path, _proposal(samples))
    analysis = MediaTimeRange(MediaTime(3, 1), MediaTime(1, 1))
    first = service.track(SHOT, analysis, "seed", seed)
    second = service.track(SHOT, analysis, "seed", seed)
    assert (
        first == second and len(first) == 1 and first[0].kind == "seeded_tracking_measurement_set"
    )
    assert (
        SqliteTemporalEvidenceRepository(service._repository._database).list_evidence(SHOT) == first
    )
    assert store.get_by_id(first[0].artifact_refs[0]).startswith(b'{"proposal"')


@pytest.mark.parametrize(
    "seed", [NormalizedRectangle(-0.1, 0, 0.2, 0.2), NormalizedRectangle(0.9, 0, 0.2, 0.2)]
)
def test_tracking_owner_rejects_invalid_normalized_seed(tmp_path, seed) -> None:
    service, _, _ = _tracking_service(tmp_path, _proposal(()))
    with pytest.raises(ValueError, match="normalized"):
        service.track(SHOT, MediaTimeRange(MediaTime(3, 1), MediaTime(1, 1)), "seed", seed)


def test_lost_sample_cannot_hallucinate_geometry(tmp_path) -> None:
    seed = NormalizedRectangle(0.2, 0.3, 0.2, 0.2)
    invalid = TrackingSample(MediaTime(0, 30), "lost", "occlusion", seed, 0, 0)
    service, _, _ = _tracking_service(tmp_path, _proposal((invalid,)))
    with pytest.raises(ValueError, match="must not contain geometry"):
        service.track(SHOT, MediaTimeRange(MediaTime(3, 1), MediaTime(1, 1)), "seed", seed)

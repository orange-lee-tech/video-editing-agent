from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.application.ports.asset_media import ResolvedLocalAssetMedia
from video_editing_agent.application.ports.voice_activity import (
    VoiceActivityProposal,
    VoiceActivityRequest,
    VoiceActivitySpanProposal,
    VoiceActivityState,
)
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.evidence.temporal import TemporalEvidence
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.speech.voice_activity import (
    ProviderNeutralVoiceActivityService,
    SILENCE_KIND,
    SPEECH_ACTIVITY_KIND,
)

NOW = datetime(2026, 8, 12, 17, 10, tzinfo=UTC)


class StaticShotRepository:
    def __init__(self, shot: Shot) -> None:
        self.shot = shot

    def load(self, shot_ref: EntityRevisionRef) -> Shot:
        del shot_ref
        return self.shot


class StaticMediaResolver:
    def __init__(self, resolved: ResolvedLocalAssetMedia) -> None:
        self.resolved = resolved

    def resolve_local(self, asset_ref: EntityRevisionRef) -> ResolvedLocalAssetMedia:
        del asset_ref
        return self.resolved


class MemoryTemporalEvidenceRepository:
    def __init__(self) -> None:
        self.items: dict[str, TemporalEvidence] = {}
        self.batch_calls = 0

    def save_evidence_batch(self, evidence: tuple[TemporalEvidence, ...]) -> None:
        self.batch_calls += 1
        staged = dict(self.items)
        for item in evidence:
            existing = staged.get(item.evidence_id)
            if existing is not None and existing != item:
                raise ValueError("immutable evidence conflict")
            staged[item.evidence_id] = item
        self.items = staged

    def list_evidence(self, shot_ref: EntityRevisionRef) -> tuple[TemporalEvidence, ...]:
        return tuple(item for item in self.items.values() if item.shot_ref == shot_ref)


class RecordingVoiceActivityPort:
    def __init__(self, proposal: VoiceActivityProposal) -> None:
        self.proposal = proposal
        self.requests: list[VoiceActivityRequest] = []

    def analyze(self, request: VoiceActivityRequest) -> VoiceActivityProposal:
        self.requests.append(request)
        return self.proposal


def _range(start: int, duration: int) -> MediaTimeRange:
    return MediaTimeRange(MediaTime(start, 10), MediaTime(duration, 10))


def _shot() -> Shot:
    return Shot(
        envelope=EntityEnvelope(
            id="sht_vad",
            revision=2,
            schema_version="0.2",
            status=EntityStatus.VALID,
            created_at=NOW,
            created_by="test",
        ),
        asset_ref=EntityRevisionRef("ast_vad", 3),
        source_range=MediaTimeRange(MediaTime(101, 10), MediaTime(3, 1)),
        boundary_method="test",
    )


def _proposal() -> VoiceActivityProposal:
    return VoiceActivityProposal(
        provider_id="fake-vad",
        provider_revision="r1",
        spans=(
            VoiceActivitySpanProposal(VoiceActivityState.SILENCE, _range(0, 2), 0.95),
            VoiceActivitySpanProposal(VoiceActivityState.SPEECH, _range(2, 11), 0.82),
            VoiceActivitySpanProposal(VoiceActivityState.SILENCE, _range(13, 17), 0.91),
        ),
    )


def _service(tmp_path: Path, proposal: VoiceActivityProposal):
    shot = _shot()
    path = tmp_path / "source.mp4"
    path.write_bytes(b"media")
    repository = MemoryTemporalEvidenceRepository()
    port = RecordingVoiceActivityPort(proposal)
    service = ProviderNeutralVoiceActivityService(
        shot_repository=StaticShotRepository(shot),
        asset_media_resolver=StaticMediaResolver(
            ResolvedLocalAssetMedia(asset_ref=shot.asset_ref, path=path)
        ),
        temporal_evidence_repository=repository,
        voice_activity_port=port,
    )
    return service, repository, port


def test_service_maps_complete_partition_to_original_asset_time(tmp_path: Path) -> None:
    service, repository, port = _service(tmp_path, _proposal())
    shot_ref = EntityRevisionRef("sht_vad", 2)

    evidence = service.analyze(shot_ref)

    assert [item.kind for item in evidence] == [SILENCE_KIND, SPEECH_ACTIVITY_KIND, SILENCE_KIND]
    assert evidence[0].source_range == MediaTimeRange(MediaTime(101, 10), MediaTime(1, 5))
    assert evidence[1].source_range == MediaTimeRange(MediaTime(103, 10), MediaTime(11, 10))
    assert evidence[2].source_range == MediaTimeRange(MediaTime(57, 5), MediaTime(17, 10))
    assert [item.confidence for item in evidence] == [0.95, 0.82, 0.91]
    assert repository.batch_calls == 1
    assert port.requests[0].shot_ref == shot_ref
    assert port.requests[0].source_range == _shot().source_range


@pytest.mark.parametrize(
    ("spans", "message"),
    [
        (
            (
                VoiceActivitySpanProposal(VoiceActivityState.SILENCE, _range(0, 2), 0.9),
                VoiceActivitySpanProposal(VoiceActivityState.SPEECH, _range(3, 27), 0.8),
            ),
            "gaps",
        ),
        (
            (
                VoiceActivitySpanProposal(VoiceActivityState.SILENCE, _range(0, 4), 0.9),
                VoiceActivitySpanProposal(VoiceActivityState.SPEECH, _range(3, 27), 0.8),
            ),
            "overlaps",
        ),
        (
            (
                VoiceActivitySpanProposal(VoiceActivityState.SILENCE, _range(0, 2), 0.9),
                VoiceActivitySpanProposal(VoiceActivityState.SILENCE, _range(2, 28), 0.8),
            ),
            "same state",
        ),
        (
            (VoiceActivitySpanProposal(VoiceActivityState.SPEECH, _range(0, 31), 0.8),),
            "inside the exact Shot",
        ),
        (
            (VoiceActivitySpanProposal(VoiceActivityState.SILENCE, _range(0, 29), 0.9),),
            "complete Shot",
        ),
    ],
)
def test_invalid_partition_is_rejected_before_any_persistence(
    tmp_path: Path,
    spans: tuple[VoiceActivitySpanProposal, ...],
    message: str,
) -> None:
    proposal = VoiceActivityProposal("fake-vad", "r1", spans)
    service, repository, _ = _service(tmp_path, proposal)

    with pytest.raises(ValueError, match=message):
        service.analyze(EntityRevisionRef("sht_vad", 2))

    assert repository.items == {}
    assert repository.batch_calls == 0


def test_same_provider_revision_is_idempotent_for_same_partition(tmp_path: Path) -> None:
    service, repository, _ = _service(tmp_path, _proposal())
    shot_ref = EntityRevisionRef("sht_vad", 2)

    first = service.analyze(shot_ref)
    second = service.analyze(shot_ref)

    assert second == first
    assert repository.batch_calls == 2
    assert len(repository.items) == 3


def test_same_provider_revision_cannot_silently_change_partition(tmp_path: Path) -> None:
    service, repository, port = _service(tmp_path, _proposal())
    shot_ref = EntityRevisionRef("sht_vad", 2)
    first = service.analyze(shot_ref)
    port.proposal = VoiceActivityProposal(
        provider_id="fake-vad",
        provider_revision="r1",
        spans=(
            VoiceActivitySpanProposal(VoiceActivityState.SILENCE, _range(0, 3), 0.95),
            VoiceActivitySpanProposal(VoiceActivityState.SPEECH, _range(3, 10), 0.82),
            VoiceActivitySpanProposal(VoiceActivityState.SILENCE, _range(13, 17), 0.91),
        ),
    )

    with pytest.raises(ValueError, match="different partition"):
        service.analyze(shot_ref)

    assert tuple(repository.items.values()) == first
    assert repository.batch_calls == 1


def test_invalid_confidence_is_rejected_before_persistence(tmp_path: Path) -> None:
    proposal = VoiceActivityProposal(
        "fake-vad",
        "r1",
        (VoiceActivitySpanProposal(VoiceActivityState.SILENCE, _range(0, 30), 1.1),),
    )
    service, repository, _ = _service(tmp_path, proposal)

    with pytest.raises(ValueError, match="confidence"):
        service.analyze(EntityRevisionRef("sht_vad", 2))

    assert repository.batch_calls == 0

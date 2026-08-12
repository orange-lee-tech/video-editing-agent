from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.application.ports.asset_media import ResolvedLocalAssetMedia
from video_editing_agent.application.ports.speech_recognition import (
    SpeechRecognitionProposal,
    SpeechRecognitionRequest,
    SpeechSegmentProposal,
    SpeechWordProposal,
)
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.evidence.speech import SpeechTranscript
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.speech.service import ProviderNeutralSpeechRecognitionService

NOW = datetime(2026, 8, 12, 16, 40, tzinfo=UTC)


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


class MemoryTranscriptRepository:
    def __init__(self) -> None:
        self.saved: list[SpeechTranscript] = []

    def save(self, transcript: SpeechTranscript) -> None:
        self.saved.append(transcript)

    def load(self, shot_ref: EntityRevisionRef, revision: int) -> SpeechTranscript:
        return next(
            item
            for item in self.saved
            if item.shot_ref == shot_ref and item.revision == revision
        )

    def latest(self, shot_ref: EntityRevisionRef) -> SpeechTranscript | None:
        matches = [item for item in self.saved if item.shot_ref == shot_ref]
        return matches[-1] if matches else None


class RecordingSpeechPort:
    def __init__(self, proposal: SpeechRecognitionProposal) -> None:
        self.proposal = proposal
        self.requests: list[SpeechRecognitionRequest] = []

    def recognize(self, request: SpeechRecognitionRequest) -> SpeechRecognitionProposal:
        self.requests.append(request)
        return self.proposal


def _relative_range(start: int, duration: int) -> MediaTimeRange:
    return MediaTimeRange(MediaTime(start, 10), MediaTime(duration, 10))


def _shot() -> Shot:
    return Shot(
        envelope=EntityEnvelope(
            id="sht_speech",
            revision=3,
            schema_version="0.2",
            status=EntityStatus.VALID,
            created_at=NOW,
            created_by="test",
        ),
        asset_ref=EntityRevisionRef("ast_speech", 2),
        source_range=MediaTimeRange(MediaTime(101, 10), MediaTime(30, 10)),
        boundary_method="test",
    )


def _proposal() -> SpeechRecognitionProposal:
    return SpeechRecognitionProposal(
        provider_id="fake-asr",
        provider_revision="model-r1",
        text="hello world",
        language="en",
        segments=(
            SpeechSegmentProposal(
                text="hello world",
                relative_range=_relative_range(2, 10),
                words=(
                    SpeechWordProposal("hello", _relative_range(2, 4), confidence=0.9),
                    SpeechWordProposal("world", _relative_range(7, 4), confidence=0.8),
                ),
                confidence=0.85,
            ),
        ),
    )


def _service(tmp_path: Path, proposal: SpeechRecognitionProposal):
    shot = _shot()
    path = tmp_path / "source.mp4"
    path.write_bytes(b"media")
    repository = MemoryTranscriptRepository()
    port = RecordingSpeechPort(proposal)
    service = ProviderNeutralSpeechRecognitionService(
        shot_repository=StaticShotRepository(shot),
        asset_media_resolver=StaticMediaResolver(
            ResolvedLocalAssetMedia(asset_ref=shot.asset_ref, path=path)
        ),
        transcript_repository=repository,
        speech_port=port,
        clock=lambda: NOW,
    )
    return service, repository, port


def test_service_maps_shot_relative_proposal_to_original_asset_time(tmp_path: Path) -> None:
    service, repository, port = _service(tmp_path, _proposal())
    shot_ref = EntityRevisionRef("sht_speech", 3)

    transcript = service.recognize(shot_ref)

    assert transcript.revision == 1
    assert transcript.shot_ref == shot_ref
    assert transcript.segments[0].source_range.start == MediaTime(103, 10)
    assert transcript.segments[0].words[0].source_range.start == MediaTime(103, 10)
    assert transcript.segments[0].words[1].source_range.start == MediaTime(108, 10)
    assert repository.saved == [transcript]
    assert port.requests[0].shot_ref == shot_ref
    assert port.requests[0].source_range == _shot().source_range


def test_service_rejects_provider_range_past_shot_boundary_before_commit(tmp_path: Path) -> None:
    proposal = SpeechRecognitionProposal(
        provider_id="fake-asr",
        provider_revision="r1",
        text="outside",
        segments=(SpeechSegmentProposal("outside", _relative_range(29, 2)),),
    )
    service, repository, _ = _service(tmp_path, proposal)

    with pytest.raises(ValueError, match="inside the exact Shot"):
        service.recognize(EntityRevisionRef("sht_speech", 3))

    assert repository.saved == []


def test_service_rejects_out_of_order_provider_segments(tmp_path: Path) -> None:
    proposal = SpeechRecognitionProposal(
        provider_id="fake-asr",
        provider_revision="r1",
        text="two one",
        segments=(
            SpeechSegmentProposal("two", _relative_range(10, 5)),
            SpeechSegmentProposal("one", _relative_range(5, 4)),
        ),
    )
    service, repository, _ = _service(tmp_path, proposal)

    with pytest.raises(ValueError, match="ordered"):
        service.recognize(EntityRevisionRef("sht_speech", 3))

    assert repository.saved == []


def test_rerecognize_creates_next_revision(tmp_path: Path) -> None:
    service, repository, _ = _service(tmp_path, _proposal())
    shot_ref = EntityRevisionRef("sht_speech", 3)

    first = service.recognize(shot_ref)
    second = service.rerecognize(shot_ref)

    assert first.revision == 1
    assert second.revision == 2
    assert repository.saved == [first, second]


def test_existing_speech_requires_rerecognize(tmp_path: Path) -> None:
    service, _, _ = _service(tmp_path, _proposal())
    shot_ref = EntityRevisionRef("sht_speech", 3)
    service.recognize(shot_ref)

    with pytest.raises(ValueError, match="rerecognize"):
        service.recognize(shot_ref)

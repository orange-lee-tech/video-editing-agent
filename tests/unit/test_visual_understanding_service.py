from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.application.ports.artifact_store import ArtifactPayload
from video_editing_agent.application.ports.asset_media import ResolvedLocalAssetMedia
from video_editing_agent.application.ports.visual_understanding import (
    VisualSemanticsProposal,
    VisualUnderstandingRequest,
)
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.shot.analysis import AnalysisProfile, ShotAnalysis
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.understanding.frame_extraction import (
    PNG_MEDIA_TYPE,
    PNG_SIGNATURE,
    ExtractedFrameSample,
)
from video_editing_agent.media.understanding.service import (
    ProviderNeutralVisualUnderstandingService,
    UnsupportedAnalysisProfile,
)
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore


class StaticShotRepository:
    def __init__(self, shot: Shot) -> None:
        self._shot = shot

    def load(self, shot_ref: EntityRevisionRef) -> Shot:
        del shot_ref
        return self._shot


class StaticMediaResolver:
    def __init__(self, resolved: ResolvedLocalAssetMedia) -> None:
        self._resolved = resolved

    def resolve_local(self, asset_ref: EntityRevisionRef) -> ResolvedLocalAssetMedia:
        del asset_ref
        return self._resolved


class MemoryAnalysisRepository:
    def __init__(self) -> None:
        self.saved: list[ShotAnalysis] = []

    def latest(self, shot_ref: EntityRevisionRef) -> ShotAnalysis | None:
        matches = [analysis for analysis in self.saved if analysis.shot_ref == shot_ref]
        return matches[-1] if matches else None

    def save(self, analysis: ShotAnalysis) -> None:
        self.saved.append(analysis)


class FakeFrameExtractor:
    def extract(self, input_video: Path, plan):
        del input_video
        return tuple(
            ExtractedFrameSample(
                sample=sample,
                media_type=PNG_MEDIA_TYPE,
                content=PNG_SIGNATURE + bytes([sample.ordinal + 1]),
            )
            for sample in plan.samples
        )


class RecordingVisualPort:
    def __init__(self) -> None:
        self.requests: list[VisualUnderstandingRequest] = []

    def analyze(self, request: VisualUnderstandingRequest) -> VisualSemanticsProposal:
        self.requests.append(request)
        return VisualSemanticsProposal(
            summary="  Person enters room. ",
            tags=("person", " room ", "person"),
            actions=("walking",),
        )


def make_shot() -> Shot:
    return Shot(
        envelope=EntityEnvelope(
            id="sht_service",
            revision=2,
            schema_version="0.1.1",
            status=EntityStatus.VALID,
            created_at=datetime(2026, 8, 10, 8, 20, tzinfo=UTC),
            created_by="test",
        ),
        asset_ref=EntityRevisionRef("ast_service", 1),
        source_start_ms=0,
        source_end_ms=2_000,
        boundary_method="test",
    )


def make_service(tmp_path: Path):
    shot = make_shot()
    video_path = tmp_path / "video.mp4"
    video_path.write_bytes(b"video")
    repository = MemoryAnalysisRepository()
    visual_port = RecordingVisualPort()
    service = ProviderNeutralVisualUnderstandingService(
        shot_repository=StaticShotRepository(shot),
        asset_media_resolver=StaticMediaResolver(
            ResolvedLocalAssetMedia(asset_ref=shot.asset_ref, path=video_path)
        ),
        analysis_repository=repository,
        frame_extractor=FakeFrameExtractor(),
        artifact_store=LocalArtifactStore(tmp_path / "artifacts"),
        visual_port=visual_port,
        clock=lambda: datetime(2026, 8, 10, 8, 30, tzinfo=UTC),
    )
    return service, repository, visual_port


def test_analyze_owns_first_revision_and_persists_frame_artifacts(tmp_path: Path) -> None:
    service, repository, visual_port = make_service(tmp_path)
    shot_ref = EntityRevisionRef("sht_service", 2)

    analysis = service.analyze(shot_ref, AnalysisProfile.SEMANTIC)

    assert analysis.shot_ref == shot_ref
    assert analysis.revision == 1
    assert analysis.profile is AnalysisProfile.SEMANTIC
    assert analysis.visual is not None
    assert analysis.visual.summary == "Person enters room."
    assert analysis.visual.tags == ("person", "room")
    assert len(analysis.artifact_refs) == 3
    assert repository.saved == [analysis]
    assert len(visual_port.requests) == 1
    assert visual_port.requests[0].shot_ref == shot_ref
    assert [frame.source_timestamp_ms for frame in visual_port.requests[0].frames] == [
        333,
        1_000,
        1_666,
    ]


def test_reanalyze_creates_next_analysis_revision(tmp_path: Path) -> None:
    service, repository, _ = make_service(tmp_path)
    shot_ref = EntityRevisionRef("sht_service", 2)

    first = service.analyze(shot_ref, AnalysisProfile.SEMANTIC)
    second = service.reanalyze(shot_ref, AnalysisProfile.EDITORIAL)

    assert first.revision == 1
    assert second.revision == 2
    assert second.profile is AnalysisProfile.EDITORIAL
    assert repository.saved == [first, second]


def test_analyze_rejects_existing_analysis(tmp_path: Path) -> None:
    service, _, _ = make_service(tmp_path)
    shot_ref = EntityRevisionRef("sht_service", 2)
    service.analyze(shot_ref, AnalysisProfile.SEMANTIC)

    with pytest.raises(ValueError, match="reanalyze"):
        service.analyze(shot_ref, AnalysisProfile.SEMANTIC)


def test_reanalyze_requires_existing_analysis(tmp_path: Path) -> None:
    service, _, _ = make_service(tmp_path)

    with pytest.raises(ValueError, match="analyze"):
        service.reanalyze(EntityRevisionRef("sht_service", 2), AnalysisProfile.SEMANTIC)


def test_unsupported_profiles_fail_before_provider_call(tmp_path: Path) -> None:
    service, repository, visual_port = make_service(tmp_path)

    with pytest.raises(UnsupportedAnalysisProfile, match="speech"):
        service.analyze(EntityRevisionRef("sht_service", 2), AnalysisProfile.SPEECH)

    assert repository.saved == []
    assert visual_port.requests == []


def test_artifact_store_stays_non_authoritative(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "artifacts")
    ref = store.put(ArtifactPayload(media_type="image/png", content=PNG_SIGNATURE + b"one"))

    assert ref.artifact_id.startswith("art_sha256_")
    assert store.get(ref) == PNG_SIGNATURE + b"one"

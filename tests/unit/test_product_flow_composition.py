from __future__ import annotations

import hashlib
import wave
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest

from video_editing_agent.adapters.product.presentation import (
    editing_presentation,
    planning_presentation,
)
from video_editing_agent.application.ports.audio_acquisition import (
    AcquiredAudioMaterial,
    AudioAcquisitionResult,
)
from video_editing_agent.application.ports.audio_material_provider import (
    AudioMaterialCandidate,
    MusicDiscoveryQuery,
)
from video_editing_agent.application.ports.director import (
    DirectorProposal,
    DirectorRequest,
    EditSlotProposal,
)
from video_editing_agent.application.ports.executor import DeterministicToolInvocation
from video_editing_agent.application.ports.preproduction_planning import (
    NarrativeSectionProposal,
    ScriptPlanningRequest,
    ScriptPlanProposal,
    ShootingPlanningRequest,
    ShootingPlanProposal,
    ShotRequirementProposal,
)
from video_editing_agent.application.ports.preproduction_review import (
    ScriptProposalReview,
    ScriptProposalReviewRequest,
    ShootingProposalReview,
    ShootingProposalReviewRequest,
)
from video_editing_agent.application.ports.reference_acquisition import (
    AcquiredReferenceMedia,
    ReferenceAcquisitionResult,
)
from video_editing_agent.application.ports.rendered_media_qc import RenderedMediaQc
from video_editing_agent.application.ports.renderer import (
    RenderArtifact,
    RenderRequest,
    RenderResult,
)
from video_editing_agent.application.ports.shot_detector import (
    ShotBoundaryProposal,
    ShotDetectionOptions,
)
from video_editing_agent.application.ports.speech_recognition import (
    SpeechRecognitionCapabilityUnavailable,
)
from video_editing_agent.application.use_cases.product_flow import (
    EditingMusicInput,
    EditingOutputProfile,
    EditingProductRequest,
    PlanningProductRequest,
    PlanningReferenceInput,
    PlanningReferenceKind,
    ProductBriefInput,
    ProductFlowEventLevel,
    ProductFlowOutcome,
)
from video_editing_agent.application.use_cases.review_runtime import ReviewRequest
from video_editing_agent.domain.asset.policy import (
    AssetUsageRole,
    is_visual_resolver_eligible,
)
from video_editing_agent.domain.asset.rights import LicenseSnapshot, RightsEligibility
from video_editing_agent.domain.brief.model import AuthoritativeFact
from video_editing_agent.domain.common.entity import (
    EntityEnvelope,
    EntityRevisionRef,
    EntityStatus,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edl.subtitle import SubtitleStyleProfile
from video_editing_agent.domain.evidence.speech import SpeechSegment, SpeechTranscript
from video_editing_agent.domain.evidence.temporal import TemporalEvidence
from video_editing_agent.domain.review.model import (
    ReviewCorrectionRoute,
    ReviewDisposition,
    ReviewReport,
    ReviewStage,
    ReviewVerdict,
)
from video_editing_agent.domain.shooting.model import ProductionConstraints
from video_editing_agent.domain.shot.analysis import (
    AnalysisProfile,
    ShotAnalysis,
    VisualSemantics,
)
from video_editing_agent.media.ingest.probe import MediaTechnicalMetadata
from video_editing_agent.providers.audio.wikimedia import (
    VerifiedWikimediaAudio,
    WikimediaRightsDiagnostic,
    WikimediaRightsDiagnosticCode,
    WikimediaVerificationResult,
)
from video_editing_agent.render.edl_ffmpeg import compile_ffmpeg_render
from video_editing_agent.storage.project import product_flow as composition_module
from video_editing_agent.storage.project.product_flow import (
    EditingProductCapabilities,
    PlanningProductCapabilities,
    PlanningReferenceCapabilities,
    build_editing_product_flow,
    build_planning_product_flow,
)
from video_editing_agent.storage.project.workspace import ProjectWorkspace

NOW = datetime(2026, 8, 17, 14, 0, tzinfo=UTC)


class FakeScriptPlanning:
    def propose(self, request: ScriptPlanningRequest) -> ScriptPlanProposal:
        assert request.brief.core_message == "value product"
        return ScriptPlanProposal(
            (
                NarrativeSectionProposal(
                    "sec_value",
                    "hook",
                    "show value",
                    spoken_content="Here is the value.",
                    visual_requirement="show the product",
                ),
            )
        )


class AcceptScriptReview:
    def review(self, request: ScriptProposalReviewRequest) -> ScriptProposalReview:
        assert request.proposal.sections
        return ScriptProposalReview(True)


class FakeShootingPlanning:
    def propose(self, request: ShootingPlanningRequest) -> ShootingPlanProposal:
        assert request.script_plan.sections[0].section_id == "sec_value"
        return ShootingPlanProposal(
            (
                ShotRequirementProposal(
                    "req_value",
                    "sec_value",
                    "show value",
                    "product",
                    action="show",
                    priority="required",
                ),
            )
        )


class AcceptShootingReview:
    def review(self, request: ShootingProposalReviewRequest) -> ShootingProposalReview:
        assert request.proposal.requirements
        return ShootingProposalReview(True)


class CapturingScriptPlanning(FakeScriptPlanning):
    def __init__(self) -> None:
        self.guidance = ()

    def propose(self, request: ScriptPlanningRequest) -> ScriptPlanProposal:
        self.guidance = request.reference_guidance
        return super().propose(request)


class CapturingShootingPlanning(FakeShootingPlanning):
    def __init__(self) -> None:
        self.guidance = ()

    def propose(self, request: ShootingPlanningRequest) -> ShootingPlanProposal:
        self.guidance = request.reference_guidance
        return super().propose(request)


class FakeReferenceAcquirer:
    def __init__(
        self,
        path: Path,
        *,
        provider: str = "direct_https",
        provider_item_id: str | None = None,
    ) -> None:
        self._path = path
        self._provider = provider
        self._provider_item_id = provider_item_id

    def acquire(self, request) -> ReferenceAcquisitionResult:  # type: ignore[no-untyped-def]
        return ReferenceAcquisitionResult(
            AcquiredReferenceMedia(
                self._path.resolve(),
                request.url,
                request.url,
                self._provider,
                self._provider_item_id,
                NOW,
                "sha256:" + "a" * 64,
                self._path.stat().st_size,
                "video/mp4",
            )
        )


class FakeMediaProbe:
    def probe(self, path: Path) -> MediaTechnicalMetadata:
        assert path.is_file()
        if path.suffix.casefold() in {".wav", ".wave", ".mp3", ".flac", ".ogg", ".opus", ".m4a"}:
            return MediaTechnicalMetadata(
                "audio",
                duration=MediaTime(6, 1),
                codec=("pcm_s16le" if path.suffix.casefold() in {".wav", ".wave"} else "mp3"),
                audio_channels=1,
                sample_rate_hz=8_000,
            )
        return MediaTechnicalMetadata(
            "video",
            duration=MediaTime(4, 1),
            width=320,
            height=180,
            fps=30.0,
            codec="h264",
            audio_channels=1,
            sample_rate_hz=48_000,
        )


class FakeShotDetector:
    def detect(
        self,
        asset_ref: EntityRevisionRef,
        options: ShotDetectionOptions,
    ) -> tuple[ShotBoundaryProposal, ...]:
        assert options == ShotDetectionOptions()
        return (
            ShotBoundaryProposal(
                asset_ref,
                detection_method="product-composition-test",
                confidence=1.0,
                source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(4, 1)),
            ),
        )


class FakeUnderstanding:
    def __init__(self, workspace: ProjectWorkspace) -> None:
        self._workspace = workspace

    def analyze(self, shot_ref: EntityRevisionRef, profile: AnalysisProfile) -> ShotAnalysis:
        analysis = ShotAnalysis(
            shot_ref,
            1,
            profile,
            NOW,
            visual=VisualSemantics(
                summary="show value product",
                tags=("value", "product"),
                subjects=("product",),
                actions=("show",),
            ),
        )
        self._workspace.analyses.save(analysis)
        return analysis

    def reanalyze(self, shot_ref: EntityRevisionRef, profile: AnalysisProfile) -> ShotAnalysis:
        return self.analyze(shot_ref, profile)


class FakeDirector:
    def propose(self, request: DirectorRequest) -> DirectorProposal:
        assert request.footage
        return DirectorProposal(
            (
                EditSlotProposal(
                    "slot_value",
                    0,
                    "proof",
                    "show value",
                    "value product",
                    minimum_duration=MediaTime(2, 1),
                    maximum_duration=MediaTime(3, 1),
                ),
            )
        )


class FakeRenderer:
    def __init__(self) -> None:
        self.requests: list[RenderRequest] = []

    def render(self, request: RenderRequest) -> RenderResult:
        self.requests.append(request)
        request.output_spec.path.parent.mkdir(parents=True, exist_ok=True)
        request.output_spec.path.write_bytes(b"rendered-product-flow")
        invocation = DeterministicToolInvocation("fixture", "fixture", ())
        return RenderResult(
            RenderArtifact(
                request.output_spec.path,
                EntityRevisionRef(request.edl.envelope.id, request.edl.envelope.revision),
                request.output_spec,
                invocation,
                invocation,
            ),
            (),
        )


class UnusedRenderedMediaQc:
    def inspect(self, path: Path):  # type: ignore[no-untyped-def]
        raise AssertionError(f"unit composition test must not execute PCM QC: {path}")


class FakeReviewRuntime:
    def __init__(self, rendered_media_qc: RenderedMediaQc) -> None:
        self._rendered_media_qc = rendered_media_qc

    def review(self, request: ReviewRequest) -> ReviewVerdict:
        report = ReviewReport(
            EntityEnvelope(
                f"review:{request.edl_ref.entity_id}",
                1,
                "review-report/v1",
                EntityStatus.VALID,
                NOW,
                "test-review",
                derived_from=(request.edl_ref,),
            ),
            ReviewStage.FINAL_TECHNICAL_QC,
            request.edl_ref,
            True,
        )
        return ReviewVerdict(
            ReviewDisposition.PASS,
            report,
            ReviewCorrectionRoute.NONE,
            request.repair_attempt,
        )


def _brief() -> ProductBriefInput:
    return ProductBriefInput(
        "Product value",
        "show the product value",
        "buyers",
        "short-video",
        "value product",
    )


def test_concrete_planning_composition_persists_script_and_shooting_plan(tmp_path: Path) -> None:
    workspace = ProjectWorkspace.open(tmp_path / "planning-project")
    flow = build_planning_product_flow(
        workspace,
        PlanningProductCapabilities(
            FakeScriptPlanning(),
            AcceptScriptReview(),
            FakeShootingPlanning(),
            AcceptShootingReview(),
        ),
    )

    result = flow.run(
        PlanningProductRequest(
            workspace.root,
            _brief(),
            ProductionConstraints(),
        )
    )

    assert result.outcome is ProductFlowOutcome.COMPLETED
    assert result.brief_ref is not None
    assert result.script_plan_ref is not None
    assert result.shooting_plan_ref is not None
    assert workspace.briefs.load(result.brief_ref).envelope.id == result.brief_ref.entity_id
    assert workspace.scripts.load(result.script_plan_ref).brief_ref == result.brief_ref
    assert (
        workspace.shooting_plans.load(result.shooting_plan_ref).script_plan_ref
        == result.script_plan_ref
    )
    presentation = planning_presentation(result)
    assert "ScriptPlan" in presentation and "Here is the value." in presentation
    assert "ShootingPlan" in presentation and "req_value" in presentation


@pytest.mark.parametrize("kind", ["url", "local"])
def test_product_reference_bridge_keeps_references_only_and_forwards_guidance(
    tmp_path: Path, kind: str
) -> None:
    workspace = ProjectWorkspace.open(tmp_path / "reference-project")
    reference_file = tmp_path / "reference.mp4"
    reference_file.write_bytes(b"reference-original")
    script, shooting = CapturingScriptPlanning(), CapturingShootingPlanning()
    flow = build_planning_product_flow(
        workspace,
        PlanningProductCapabilities(
            script,
            AcceptScriptReview(),
            shooting,
            AcceptShootingReview(),
            PlanningReferenceCapabilities(
                FakeMediaProbe(),
                FakeShotDetector(),
                ShotDetectionOptions(),
                FakeUnderstanding(workspace),
                FakeReferenceAcquirer(reference_file),
            ),
        ),
    )
    brief = ProductBriefInput(
        "Product value",
        "show the product value",
        "buyers",
        "short-video",
        "value product",
        authoritative_facts=(AuthoritativeFact("fact_volume", "Volume is 500 mL"),),
    )
    reference_input = (
        PlanningReferenceInput(
            "reference_001",
            PlanningReferenceKind.DIRECT_HTTPS_VIDEO,
            "User reference",
            url="https://example.test/reference.mp4",
        )
        if kind == "url"
        else PlanningReferenceInput(
            "reference_001",
            PlanningReferenceKind.LOCAL_VIDEO,
            "User reference",
            local_path=reference_file,
        )
    )
    result = flow.run(
        PlanningProductRequest(
            workspace.root,
            brief,
            ProductionConstraints(),
            reference_inputs=(reference_input,),
        )
    )

    assert result.outcome is ProductFlowOutcome.COMPLETED and result.brief_ref is not None
    persisted = workspace.briefs.load(result.brief_ref)
    assert persisted.authoritative_facts == brief.authoritative_facts
    assert persisted.references[0].asset_ref is not None
    asset = workspace.assets.load(persisted.references[0].asset_ref)
    assert asset.usage_role is AssetUsageRole.REFERENCE_ANALYSIS_ONLY
    assert not is_visual_resolver_eligible(
        media_kind=asset.media_kind,
        origin=asset.origin,
        usage_role=asset.usage_role,
    )
    assert script.guidance and script.guidance == shooting.guidance
    assert script.guidance[0].reference_asset_ref == persisted.references[0].asset_ref
    assert reference_file.read_bytes() == b"reference-original"


def test_bilibili_acquired_contract_enters_existing_planning_reference_chain(
    tmp_path: Path,
) -> None:
    workspace = ProjectWorkspace.open(tmp_path / "bilibili-reference-project")
    acquired_media = tmp_path / "bilibili-reference.m4s"
    acquired_media.write_bytes(b"public-reference-video")
    script, shooting = CapturingScriptPlanning(), CapturingShootingPlanning()
    flow = build_planning_product_flow(
        workspace,
        PlanningProductCapabilities(
            script,
            AcceptScriptReview(),
            shooting,
            AcceptShootingReview(),
            PlanningReferenceCapabilities(
                FakeMediaProbe(),
                FakeShotDetector(),
                ShotDetectionOptions(),
                FakeUnderstanding(workspace),
                FakeReferenceAcquirer(
                    acquired_media,
                    provider="bilibili_public_page",
                    provider_item_id="BV1Mq4y187xR",
                ),
            ),
        ),
    )

    result = flow.run(
        PlanningProductRequest(
            workspace.root,
            _brief(),
            ProductionConstraints(),
            reference_inputs=(
                PlanningReferenceInput(
                    "reference_bilibili",
                    PlanningReferenceKind.DIRECT_HTTPS_VIDEO,
                    "Public Bilibili reference",
                    url=("https://www.bilibili.com/video/BV1Mq4y187xR?share_source=copy_web"),
                ),
            ),
        )
    )

    assert result.outcome is ProductFlowOutcome.COMPLETED
    assert result.brief_ref is not None
    reference = workspace.briefs.load(result.brief_ref).references[0]
    assert reference.asset_ref is not None
    asset = workspace.assets.load(reference.asset_ref)
    assert asset.provenance.provider == "bilibili_public_page"
    assert asset.provenance.provider_asset_id == "BV1Mq4y187xR"
    assert asset.usage_role is AssetUsageRole.REFERENCE_ANALYSIS_ONLY
    assert script.guidance and shooting.guidance


def test_concrete_editing_composition_reaches_durable_edl_render_and_review(
    tmp_path: Path,
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(composition_module, "ReviewApplicationRuntime", FakeReviewRuntime)
    workspace = ProjectWorkspace.open(tmp_path / "editing-project")
    source = tmp_path / "source.mp4"
    source.write_bytes(b"original-user-media")
    output = tmp_path / "output" / "final.mp4"
    renderer = FakeRenderer()

    def recognize_speech(shot_ref: EntityRevisionRef) -> SpeechTranscript:
        transcript = SpeechTranscript(
            shot_ref,
            1,
            NOW,
            "trusted-test-asr",
            "v1",
            "Original spoken words",
            "en",
            (
                SpeechSegment(
                    "Original spoken words",
                    MediaTimeRange(MediaTime(1, 4), MediaTime(3, 4)),
                ),
            ),
            ("artifact:trusted-transcript",),
        )
        workspace.transcripts.save(transcript)
        return transcript

    flow = build_editing_product_flow(
        workspace,
        EditingProductCapabilities(
            FakeMediaProbe(),
            FakeShotDetector(),
            ShotDetectionOptions(),
            FakeUnderstanding(workspace),
            FakeDirector(),
            renderer,
            cast(RenderedMediaQc, UnusedRenderedMediaQc()),
            edit_plan_id_factory=lambda: "epl_product_composition",
            edl_id_factory=lambda: "edl_product_composition",
            clock=lambda: NOW,
            speech_recognition=recognize_speech,
        ),
    )

    result = flow.run(
        EditingProductRequest(
            workspace.root,
            _brief(),
            (source,),
            output,
            output_profile=EditingOutputProfile("test_320x180_30", 320, 180, 30),
            subtitle_style=SubtitleStyleProfile.BACKED,
        )
    )

    assert result.outcome is ProductFlowOutcome.COMPLETED
    assert result.output_path == output
    assert result.edl_ref == EntityRevisionRef("edl_product_composition", 1)
    assert source.read_bytes() == b"original-user-media"
    assert output.read_bytes() == b"rendered-product-flow"
    assert workspace.edit_plans.count() == 1
    assert workspace.edls.count() == 1
    persisted_edl = workspace.edls.load(EntityRevisionRef("edl_product_composition", 1))
    assert persisted_edl == renderer.requests[0].edl
    assert renderer.requests[0].output_spec.width == 320
    assert renderer.requests[0].output_spec.height == 180
    assert renderer.requests[0].output_spec.frames_per_second == 30
    assert renderer.requests[0].asset_media[0].path == source.resolve()
    assert renderer.requests[0].edl.segments[0].source_range == MediaTimeRange(
        MediaTime(0, 1),
        MediaTime(3, 1),
    )
    assert any(segment.track_id == "source_audio" for segment in renderer.requests[0].edl.segments)
    assert len(persisted_edl.subtitle_cues) == 1
    cue = persisted_edl.subtitle_cues[0]
    assert cue.text == "Original spoken words"
    assert cue.timeline_range == MediaTimeRange(MediaTime(1, 4), MediaTime(3, 4))
    assert cue.style_profile is SubtitleStyleProfile.BACKED
    assert cue.evidence_refs[0] == "artifact:trusted-transcript"
    assert cue.evidence_refs[1].startswith("speech_transcript:")
    assert str(output) in editing_presentation(result)


def test_concrete_editing_composition_wires_rights_attested_local_music_into_edl(
    tmp_path: Path,
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(composition_module, "ReviewApplicationRuntime", FakeReviewRuntime)
    workspace = ProjectWorkspace.open(tmp_path / "editing-music-project")
    source = tmp_path / "source.mp4"
    source.write_bytes(b"original-user-media")
    music = tmp_path / "music.wav"
    with wave.open(str(music), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(8_000)
        sample = (1_000).to_bytes(2, "little", signed=True)
        stream.writeframes(sample * (8_000 * 6))
    output = tmp_path / "output" / "with-music.mp4"
    renderer = FakeRenderer()

    def unavailable_asr(_shot_ref: EntityRevisionRef) -> SpeechTranscript:
        raise SpeechRecognitionCapabilityUnavailable("faster-whisper speech-runtime unavailable")

    flow = build_editing_product_flow(
        workspace,
        EditingProductCapabilities(
            FakeMediaProbe(),
            FakeShotDetector(),
            ShotDetectionOptions(),
            FakeUnderstanding(workspace),
            FakeDirector(),
            renderer,
            cast(RenderedMediaQc, UnusedRenderedMediaQc()),
            edit_plan_id_factory=lambda: "epl_product_music",
            edl_id_factory=lambda: "edl_product_music",
            clock=lambda: NOW,
            speech_recognition=unavailable_asr,
        ),
    )

    result = flow.run(
        EditingProductRequest(
            workspace.root,
            _brief(),
            (source,),
            output,
            output_profile=EditingOutputProfile("test_320x180_30", 320, 180, 30),
            music=EditingMusicInput(music, True),
        )
    )

    assert result.outcome is ProductFlowOutcome.COMPLETED
    rendered_edl = renderer.requests[0].edl
    assert any(track.track_id == "bgm" for track in rendered_edl.effective_tracks)
    bgm = [segment for segment in rendered_edl.segments if segment.track_id == "bgm"]
    assert len(bgm) == 1
    assert bgm[0].timeline_range.duration == MediaTime(3, 1)
    assert bgm[0].audio_automations
    music_asset = workspace.assets.load(bgm[0].asset_ref)
    assert music_asset.usage_role is AssetUsageRole.MUSIC
    assert music_asset.storage_ref == music.resolve().as_uri()
    assert any(segment.track_id == "source_audio" for segment in rendered_edl.segments)
    assert rendered_edl.subtitle_cues == ()
    subtitle_events = tuple(
        event
        for event in result.events
        if event.stage.value == "subtitle_compilation" and "SKIPPED" in event.message
    )
    assert len(subtitle_events) == 1
    bound_paths = {item.path for item in renderer.requests[0].asset_media}
    assert source.resolve() in bound_paths and music.resolve() in bound_paths
    rights_files = tuple(
        item for item in (workspace.root / "artifacts" / "sha256").rglob("*") if item.is_file()
    )
    assert rights_files
    assert b"local-music-rights-attestation/v1" in rights_files[0].read_bytes()
    assert source.read_bytes() == b"original-user-media"


def test_grounded_speech_without_asr_capability_fails_closed_at_subtitle_stage(
    tmp_path: Path,
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(composition_module, "ReviewApplicationRuntime", FakeReviewRuntime)
    workspace = ProjectWorkspace.open(tmp_path / "grounded-speech-project")
    source = tmp_path / "speech.mp4"
    source.write_bytes(b"original-speech-media")

    class GroundedSpeechUnderstanding(FakeUnderstanding):
        def analyze(self, shot_ref: EntityRevisionRef, profile: AnalysisProfile) -> ShotAnalysis:
            analysis = super().analyze(shot_ref, profile)
            workspace.temporal.save_evidence(
                TemporalEvidence(
                    "tev_grounded_speech",
                    shot_ref,
                    "speech_activity",
                    "trusted-vad",
                    "v1",
                    0.99,
                    MediaTimeRange(MediaTime(0, 1), MediaTime(1, 1)),
                )
            )
            return analysis

    renderer = FakeRenderer()
    flow = build_editing_product_flow(
        workspace,
        EditingProductCapabilities(
            FakeMediaProbe(),
            FakeShotDetector(),
            ShotDetectionOptions(),
            GroundedSpeechUnderstanding(workspace),
            FakeDirector(),
            renderer,
            cast(RenderedMediaQc, UnusedRenderedMediaQc()),
            edit_plan_id_factory=lambda: "epl_grounded_speech",
            edl_id_factory=lambda: "edl_grounded_speech",
            clock=lambda: NOW,
        ),
    )

    result = flow.run(
        EditingProductRequest(
            workspace.root,
            _brief(),
            (source,),
            tmp_path / "grounded-speech.mp4",
            output_profile=EditingOutputProfile("test_320x180_30", 320, 180, 30),
        )
    )

    assert result.outcome is ProductFlowOutcome.FAILED
    assert result.diagnostic is not None
    assert "stage=subtitle_compilation" in result.diagnostic
    assert "grounded speech requires subtitles" in result.diagnostic
    assert renderer.requests == []
    assert source.read_bytes() == b"original-speech-media"


def test_public_music_discovery_falls_back_when_specific_query_is_empty() -> None:
    class FallbackProvider:
        def __init__(self) -> None:
            self.queries: list[str] = []

        def search_music(self, query: MusicDiscoveryQuery) -> tuple[AudioMaterialCandidate, ...]:
            self.queries.append(query.query)
            if query.query != "instrumental background music":
                return ()
            return (
                AudioMaterialCandidate(
                    "wikimedia_commons_via_openverse",
                    "File:Fallback Music.ogg",
                    RightsEligibility.UNKNOWN,
                ),
            )

    provider = FallbackProvider()
    candidates = composition_module._discover_public_music_candidates(provider, _brief())

    assert candidates
    assert len(provider.queries) == 3
    assert "value product" in provider.queries[0]
    assert provider.queries[1] == "instrumental background music"
    assert provider.queries[2] == "piano instrumental"


def test_public_music_failure_summary_is_bounded_but_keeps_late_diagnostics() -> None:
    failures = [f"candidate-{index}: rights verification failed" for index in range(20)]
    failures.append("candidate-21: decisive acquisition failed")

    summary = composition_module._bounded_failure_summary(failures)

    assert "attempted=21" in summary
    assert "rights verification failed (20)" in summary
    assert "intermediate diagnostic(s) omitted" in summary
    assert "candidate-21: decisive acquisition failed" in summary


class FakeAutomaticPublicMusicProvider:
    queries: list[MusicDiscoveryQuery] = []

    def __init__(self, *, page_size: int = 20) -> None:
        assert page_size == 20

    def search_music(self, query: MusicDiscoveryQuery) -> tuple[AudioMaterialCandidate, ...]:
        self.queries.append(query)
        return (
            AudioMaterialCandidate(
                "wikimedia_commons_via_openverse",
                "File:Public Music.wav",
                RightsEligibility.UNKNOWN,
                title="Public Music",
                source_page="https://commons.wikimedia.org/wiki/File:Public_Music.wav",
            ),
        )


class FakeAutomaticPublicMusicVerifier:
    rights_ref = "art_sha256_" + "a" * 64

    def __init__(self, artifacts, *, clock) -> None:  # type: ignore[no-untyped-def]
        del artifacts
        self._clock = clock

    def verify(self, provider_item_id: str) -> WikimediaVerificationResult:
        assert provider_item_id == "File:Public Music.wav"
        captured = self._clock()
        snapshot = LicenseSnapshot(
            "lic_public_music",
            "wikimedia_commons",
            provider_item_id,
            captured,
            RightsEligibility.ELIGIBLE,
            license_identifier="CC0 1.0",
            terms_ref="https://creativecommons.org/publicdomain/zero/1.0/",
            commercial_scope="verified_stage_a_commercial_reuse",
            advertising_scope="verified_stage_a_commercial_reuse",
            evidence_artifact_refs=(self.rights_ref,),
        )
        return WikimediaVerificationResult(
            VerifiedWikimediaAudio(
                provider_item_id,
                "https://commons.wikimedia.org/wiki/File:Public_Music.wav",
                "https://upload.wikimedia.org/wikipedia/commons/public.wav",
                "b" * 40,
                1,
                "audio/wav",
                "Public Creator",
                "CC0 1.0",
                "https://creativecommons.org/publicdomain/zero/1.0/",
                None,
                False,
                snapshot,
                self.rights_ref,
            )
        )


class FakeAutomaticPublicMusicAcquirer:
    source: Path | None = None

    def __init__(self, root: Path, *, clock) -> None:  # type: ignore[no-untyped-def]
        del root
        self._clock = clock

    def acquire(self, request) -> AudioAcquisitionResult:  # type: ignore[no-untyped-def]
        assert request.provider == "wikimedia_commons"
        assert request.rights_eligibility is RightsEligibility.ELIGIBLE
        assert self.source is not None
        payload = self.source.read_bytes()
        return AudioAcquisitionResult(
            AcquiredAudioMaterial(
                "wikimedia_commons",
                request.provider_item_id,
                self.source.resolve(),
                request.source_page,
                request.approved_source_url,
                self._clock(),
                len(payload),
                "sha256:" + hashlib.sha256(payload).hexdigest(),
                "audio/wav",
                request.license_snapshot_ref,
                "b" * 40,
            )
        )


def test_public_music_selection_reaches_eligible_candidate_after_first_ten(
    tmp_path: Path,
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    class ElevenCandidateProvider:
        def __init__(self, *, page_size: int = 20) -> None:
            assert page_size == 20

        def search_music(self, query: MusicDiscoveryQuery) -> tuple[AudioMaterialCandidate, ...]:
            del query
            return tuple(
                AudioMaterialCandidate(
                    "wikimedia_commons_via_openverse",
                    f"File:Candidate {index}.wav",
                    RightsEligibility.UNKNOWN,
                )
                for index in range(1, 12)
            )

    class EleventhEligibleVerifier(FakeAutomaticPublicMusicVerifier):
        checked: list[str] = []

        def verify(self, provider_item_id: str) -> WikimediaVerificationResult:
            self.checked.append(provider_item_id)
            if provider_item_id != "File:Candidate 11.wav":
                return WikimediaVerificationResult(
                    None,
                    (
                        WikimediaRightsDiagnostic(
                            WikimediaRightsDiagnosticCode.RIGHTS_UNKNOWN,
                            "fixture candidate is not automatically eligible",
                        ),
                    ),
                )
            captured = self._clock()
            snapshot = LicenseSnapshot(
                "lic_candidate_11",
                "wikimedia_commons",
                provider_item_id,
                captured,
                RightsEligibility.ELIGIBLE,
                license_identifier="CC0 1.0",
                terms_ref="https://creativecommons.org/publicdomain/zero/1.0/",
                commercial_scope="verified_stage_a_commercial_reuse",
                advertising_scope="verified_stage_a_commercial_reuse",
                evidence_artifact_refs=(self.rights_ref,),
            )
            return WikimediaVerificationResult(
                VerifiedWikimediaAudio(
                    provider_item_id,
                    "https://commons.wikimedia.org/wiki/File:Candidate_11.wav",
                    "https://upload.wikimedia.org/candidate-11.wav",
                    "b" * 40,
                    1,
                    "audio/wav",
                    "Public Creator",
                    "CC0 1.0",
                    "https://creativecommons.org/publicdomain/zero/1.0/",
                    None,
                    False,
                    snapshot,
                    self.rights_ref,
                )
            )

    monkeypatch.setattr(composition_module, "ReviewApplicationRuntime", FakeReviewRuntime)
    public_music = tmp_path / "candidate-11.wav"
    with wave.open(str(public_music), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(8_000)
        stream.writeframes((1_000).to_bytes(2, "little", signed=True) * (8_000 * 6))
    FakeAutomaticPublicMusicAcquirer.source = public_music
    EleventhEligibleVerifier.checked = []
    monkeypatch.setattr(
        composition_module, "OpenverseWikimediaAudioProvider", ElevenCandidateProvider
    )
    monkeypatch.setattr(
        composition_module, "WikimediaAudioRightsVerifier", EleventhEligibleVerifier
    )
    monkeypatch.setattr(
        composition_module, "WikimediaAudioAcquirer", FakeAutomaticPublicMusicAcquirer
    )
    workspace = ProjectWorkspace.open(tmp_path / "candidate-eleven-project")
    source = tmp_path / "source.mp4"
    source.write_bytes(b"original-user-media")
    flow = build_editing_product_flow(
        workspace,
        EditingProductCapabilities(
            FakeMediaProbe(),
            FakeShotDetector(),
            ShotDetectionOptions(),
            FakeUnderstanding(workspace),
            FakeDirector(),
            FakeRenderer(),
            cast(RenderedMediaQc, UnusedRenderedMediaQc()),
            edit_plan_id_factory=lambda: "epl_candidate_11",
            edl_id_factory=lambda: "edl_candidate_11",
            clock=lambda: NOW,
            ffmpeg_executable="ffmpeg",
            automatic_public_music=True,
        ),
    )

    result = flow.run(
        EditingProductRequest(
            workspace.root,
            _brief(),
            (source,),
            tmp_path / "output" / "candidate-11.mp4",
            output_profile=EditingOutputProfile("test_320x180_30", 320, 180, 30),
        )
    )

    assert result.outcome is ProductFlowOutcome.COMPLETED
    assert EleventhEligibleVerifier.checked == [
        f"File:Candidate {index}.wav" for index in range(1, 12)
    ]
    messages = tuple(event.message for event in result.events)
    assert any("11 unique candidate" in message for message in messages)
    assert any(
        "Rights gate checking public music candidate 11/11" in message for message in messages
    )
    assert any("Public music acquisition completed" in message for message in messages)
    assert any("BeatMap analysis completed" in message for message in messages)


def test_blank_music_field_auto_selects_rights_verified_public_bgm(
    tmp_path: Path,
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(composition_module, "ReviewApplicationRuntime", FakeReviewRuntime)
    FakeAutomaticPublicMusicProvider.queries = []
    public_music = tmp_path / "public.wav"
    with wave.open(str(public_music), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(8_000)
        sample = (1_000).to_bytes(2, "little", signed=True)
        stream.writeframes(sample * (8_000 * 6))
    FakeAutomaticPublicMusicAcquirer.source = public_music
    monkeypatch.setattr(
        composition_module,
        "OpenverseWikimediaAudioProvider",
        FakeAutomaticPublicMusicProvider,
    )
    monkeypatch.setattr(
        composition_module,
        "WikimediaAudioRightsVerifier",
        FakeAutomaticPublicMusicVerifier,
    )
    monkeypatch.setattr(
        composition_module,
        "WikimediaAudioAcquirer",
        FakeAutomaticPublicMusicAcquirer,
    )

    workspace = ProjectWorkspace.open(tmp_path / "editing-public-music-project")
    source = tmp_path / "source.mp4"
    source.write_bytes(b"original-user-media")
    renderer = FakeRenderer()
    flow = build_editing_product_flow(
        workspace,
        EditingProductCapabilities(
            FakeMediaProbe(),
            FakeShotDetector(),
            ShotDetectionOptions(),
            FakeUnderstanding(workspace),
            FakeDirector(),
            renderer,
            cast(RenderedMediaQc, UnusedRenderedMediaQc()),
            edit_plan_id_factory=lambda: "epl_public_music",
            edl_id_factory=lambda: "edl_public_music",
            clock=lambda: NOW,
            ffmpeg_executable="ffmpeg",
            automatic_public_music=True,
        ),
    )

    result = flow.run(
        EditingProductRequest(
            workspace.root,
            _brief(),
            (source,),
            tmp_path / "output" / "public-music.mp4",
            output_profile=EditingOutputProfile("test_320x180_30", 320, 180, 30),
        )
    )

    assert result.outcome is ProductFlowOutcome.COMPLETED
    assert FakeAutomaticPublicMusicProvider.queries
    query = FakeAutomaticPublicMusicProvider.queries[0]
    assert "value product" in query.query
    rendered_edl = renderer.requests[0].edl
    bgm = [segment for segment in rendered_edl.segments if segment.track_id == "bgm"]
    assert len(bgm) == 1 and bgm[0].audio_automations
    music_asset = workspace.assets.load(bgm[0].asset_ref)
    assert music_asset.usage_role is AssetUsageRole.MUSIC
    assert music_asset.origin == "provider_acquired_audio"
    assert music_asset.provenance.provider == "wikimedia_commons"
    assert music_asset.provenance.license_information == "CC0 1.0"
    assert source.read_bytes() == b"original-user-media"


def test_public_music_audio_editorial_mutation_reaches_canonical_edl_and_renderer(
    tmp_path: Path,
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(composition_module, "ReviewApplicationRuntime", FakeReviewRuntime)
    FakeAutomaticPublicMusicProvider.queries = []

    public_music = tmp_path / "mutation-public.wav"
    with wave.open(str(public_music), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(8_000)
        sample = (1_200).to_bytes(2, "little", signed=True)
        stream.writeframes(sample * (8_000 * 6))
    FakeAutomaticPublicMusicAcquirer.source = public_music

    monkeypatch.setattr(
        composition_module,
        "OpenverseWikimediaAudioProvider",
        FakeAutomaticPublicMusicProvider,
    )
    monkeypatch.setattr(
        composition_module,
        "WikimediaAudioRightsVerifier",
        FakeAutomaticPublicMusicVerifier,
    )
    monkeypatch.setattr(
        composition_module,
        "WikimediaAudioAcquirer",
        FakeAutomaticPublicMusicAcquirer,
    )

    source = tmp_path / "mutation-source.mp4"
    source.write_bytes(b"original-user-media")

    def run_once(suffix: str) -> tuple[object, str]:
        workspace = ProjectWorkspace.open(tmp_path / f"mutation-project-{suffix}")
        renderer = FakeRenderer()
        flow = build_editing_product_flow(
            workspace,
            EditingProductCapabilities(
                FakeMediaProbe(),
                FakeShotDetector(),
                ShotDetectionOptions(),
                FakeUnderstanding(workspace),
                FakeDirector(),
                renderer,
                cast(RenderedMediaQc, UnusedRenderedMediaQc()),
                edit_plan_id_factory=lambda: f"epl_mutation_{suffix}",
                edl_id_factory=lambda: f"edl_mutation_{suffix}",
                clock=lambda: NOW,
                ffmpeg_executable="ffmpeg",
                automatic_public_music=True,
            ),
        )
        result = flow.run(
            EditingProductRequest(
                workspace.root,
                _brief(),
                (source,),
                tmp_path / "output" / f"mutation-{suffix}.mp4",
                output_profile=EditingOutputProfile("test_320x180_30", 320, 180, 30),
            )
        )
        assert result.outcome is ProductFlowOutcome.COMPLETED
        assert len(renderer.requests) == 1
        request = renderer.requests[0]
        assert any(segment.track_id == "bgm" for segment in request.edl.segments)
        assert any(media.path == public_music.resolve() for media in request.asset_media)
        compiled = compile_ffmpeg_render(request)
        assert compiled.plan is not None and not compiled.diagnostics
        arguments = compiled.plan.invocation.arguments
        graph = arguments[arguments.index("-filter_complex") + 1]
        return request.edl, graph

    baseline_edl, baseline_graph = run_once("baseline")
    assert "volume=-10dB" in baseline_graph

    original_plan_basic_mix = composition_module.plan_basic_mix

    def mutated_plan_basic_mix(edit_plan_ref, bgm_ref, duration, speech_ranges):  # type: ignore[no-untyped-def]
        decision = original_plan_basic_mix(edit_plan_ref, bgm_ref, duration, speech_ranges)
        intents = tuple(
            replace(intent, gain_db=-16.0) if intent.kind.value == "gain" else intent
            for intent in decision.automation_intents
        )
        return replace(decision, automation_intents=intents)

    monkeypatch.setattr(composition_module, "plan_basic_mix", mutated_plan_basic_mix)

    mutated_edl, mutated_graph = run_once("mutated")
    assert "volume=-16dB" in mutated_graph
    assert baseline_graph != mutated_graph

    baseline_bgm = tuple(segment for segment in baseline_edl.segments if segment.track_id == "bgm")
    mutated_bgm = tuple(segment for segment in mutated_edl.segments if segment.track_id == "bgm")
    assert len(baseline_bgm) == len(mutated_bgm) == 1
    assert baseline_bgm[0].audio_automations != mutated_bgm[0].audio_automations


class FakeShortPublicMusicProbe(FakeMediaProbe):
    def probe(self, path: Path) -> MediaTechnicalMetadata:
        if path.suffix.casefold() == ".wav":
            return MediaTechnicalMetadata(
                "audio",
                duration=MediaTime(1, 1),
                codec="pcm_s16le",
                audio_channels=1,
                sample_rate_hz=8_000,
            )
        return super().probe(path)


def test_short_public_music_loops_instead_of_aborting(
    tmp_path: Path,
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(composition_module, "ReviewApplicationRuntime", FakeReviewRuntime)
    FakeAutomaticPublicMusicProvider.queries = []

    public_music = tmp_path / "short-public.wav"
    with wave.open(str(public_music), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(8_000)
        sample = (1_400).to_bytes(2, "little", signed=True)
        stream.writeframes(sample * 8_000)
    FakeAutomaticPublicMusicAcquirer.source = public_music

    monkeypatch.setattr(
        composition_module,
        "OpenverseWikimediaAudioProvider",
        FakeAutomaticPublicMusicProvider,
    )
    monkeypatch.setattr(
        composition_module,
        "WikimediaAudioRightsVerifier",
        FakeAutomaticPublicMusicVerifier,
    )
    monkeypatch.setattr(
        composition_module,
        "WikimediaAudioAcquirer",
        FakeAutomaticPublicMusicAcquirer,
    )

    workspace = ProjectWorkspace.open(tmp_path / "editing-short-public-music-project")
    source = tmp_path / "short-source.mp4"
    source.write_bytes(b"original-user-media")
    renderer = FakeRenderer()
    flow = build_editing_product_flow(
        workspace,
        EditingProductCapabilities(
            FakeShortPublicMusicProbe(),
            FakeShotDetector(),
            ShotDetectionOptions(),
            FakeUnderstanding(workspace),
            FakeDirector(),
            renderer,
            cast(RenderedMediaQc, UnusedRenderedMediaQc()),
            edit_plan_id_factory=lambda: "epl_short_public_music",
            edl_id_factory=lambda: "edl_short_public_music",
            clock=lambda: NOW,
            ffmpeg_executable="ffmpeg",
            automatic_public_music=True,
        ),
    )

    result = flow.run(
        EditingProductRequest(
            workspace.root,
            _brief(),
            (source,),
            tmp_path / "output" / "short-public-music.mp4",
            output_profile=EditingOutputProfile("test_320x180_30", 320, 180, 30),
        )
    )

    assert result.outcome is ProductFlowOutcome.COMPLETED
    request = renderer.requests[0]
    bgm = [segment for segment in request.edl.segments if segment.track_id == "bgm"]
    assert len(bgm) == 3
    assert (
        sum(
            (segment.timeline_range.duration.as_fraction() for segment in bgm),
            start=MediaTime(0, 1).as_fraction(),
        )
        == MediaTime(3, 1).as_fraction()
    )
    assert all(segment.asset_ref == bgm[0].asset_ref for segment in bgm)
    assert any(media.path == public_music.resolve() for media in request.asset_media)


def test_local_mp3_music_uses_transient_pcm_analysis_and_preserves_original_asset(
    tmp_path: Path,
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(composition_module, "ReviewApplicationRuntime", FakeReviewRuntime)
    decoded_paths: list[Path] = []

    def fake_decode(command, **kwargs):  # type: ignore[no-untyped-def]
        assert "-map" in command and "0:a:0" in command
        assert "pcm_s16le" in command
        target = Path(command[-1])
        decoded_paths.append(target)
        with wave.open(str(target), "wb") as stream:
            stream.setnchannels(1)
            stream.setsampwidth(2)
            stream.setframerate(48_000)
            sample = (1_200).to_bytes(2, "little", signed=True)
            stream.writeframes(sample * (48_000 * 6))
        return composition_module.subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(composition_module.subprocess, "run", fake_decode)

    workspace = ProjectWorkspace.open(tmp_path / "editing-mp3-music-project")
    source = tmp_path / "source.mp4"
    source.write_bytes(b"original-user-media")
    music = tmp_path / "music.mp3"
    music.write_bytes(b"original-user-mp3")
    renderer = FakeRenderer()
    flow = build_editing_product_flow(
        workspace,
        EditingProductCapabilities(
            FakeMediaProbe(),
            FakeShotDetector(),
            ShotDetectionOptions(),
            FakeUnderstanding(workspace),
            FakeDirector(),
            renderer,
            cast(RenderedMediaQc, UnusedRenderedMediaQc()),
            edit_plan_id_factory=lambda: "epl_mp3_music",
            edl_id_factory=lambda: "edl_mp3_music",
            clock=lambda: NOW,
            ffmpeg_executable="ffmpeg",
        ),
    )

    result = flow.run(
        EditingProductRequest(
            workspace.root,
            _brief(),
            (source,),
            tmp_path / "output" / "with-mp3-music.mp4",
            output_profile=EditingOutputProfile("test_320x180_30", 320, 180, 30),
            music=EditingMusicInput(music, True),
        )
    )

    assert result.outcome is ProductFlowOutcome.COMPLETED
    assert len(decoded_paths) == 1
    assert not decoded_paths[0].exists()
    request = renderer.requests[0]
    assert any(media.path == music.resolve() for media in request.asset_media)
    assert all(media.path != decoded_paths[0] for media in request.asset_media)


def test_visual_input_fails_closed_when_probe_reports_audio(
    tmp_path: Path,
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(composition_module, "ReviewApplicationRuntime", FakeReviewRuntime)
    workspace = ProjectWorkspace.open(tmp_path / "editing-audio-as-video-project")
    source = tmp_path / "not-video.mp3"
    source.write_bytes(b"audio")

    flow = build_editing_product_flow(
        workspace,
        EditingProductCapabilities(
            FakeMediaProbe(),
            FakeShotDetector(),
            ShotDetectionOptions(),
            FakeUnderstanding(workspace),
            FakeDirector(),
            FakeRenderer(),
            cast(RenderedMediaQc, UnusedRenderedMediaQc()),
            edit_plan_id_factory=lambda: "epl_audio_as_video",
            edl_id_factory=lambda: "edl_audio_as_video",
            clock=lambda: NOW,
        ),
    )

    result = flow.run(
        EditingProductRequest(
            workspace.root,
            _brief(),
            (source,),
            tmp_path / "output" / "should-not-render.mp4",
            output_profile=EditingOutputProfile("test_320x180_30", 320, 180, 30),
        )
    )

    assert result.outcome is ProductFlowOutcome.FAILED
    assert result.diagnostic is not None
    assert "did not probe as video" in result.diagnostic


def test_public_music_exhaustion_degrades_to_grounded_source_audio(
    tmp_path: Path,
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    class OneCandidateProvider:
        def __init__(self, *, page_size: int = 20) -> None:
            assert page_size == 20

        def search_music(self, query: MusicDiscoveryQuery) -> tuple[AudioMaterialCandidate, ...]:
            del query
            return (
                AudioMaterialCandidate(
                    "wikimedia_commons_via_openverse",
                    "File:Needs Attribution.wav",
                    RightsEligibility.UNKNOWN,
                ),
            )

    class AttributionVerifier:
        def __init__(self, artifacts, *, clock) -> None:  # type: ignore[no-untyped-def]
            del artifacts, clock

        def verify(self, provider_item_id: str) -> WikimediaVerificationResult:
            assert provider_item_id == "File:Needs Attribution.wav"
            return WikimediaVerificationResult(
                None,
                (
                    WikimediaRightsDiagnostic(
                        WikimediaRightsDiagnosticCode.RIGHTS_INELIGIBLE,
                        "fixture requires attribution",
                    ),
                ),
            )

    monkeypatch.setattr(composition_module, "ReviewApplicationRuntime", FakeReviewRuntime)
    monkeypatch.setattr(
        composition_module,
        "OpenverseWikimediaAudioProvider",
        OneCandidateProvider,
    )
    monkeypatch.setattr(
        composition_module,
        "WikimediaAudioRightsVerifier",
        AttributionVerifier,
    )

    workspace = ProjectWorkspace.open(tmp_path / "editing-no-public-bgm-project")
    source = tmp_path / "source.mp4"
    source.write_bytes(b"original-user-media")
    renderer = FakeRenderer()
    flow = build_editing_product_flow(
        workspace,
        EditingProductCapabilities(
            FakeMediaProbe(),
            FakeShotDetector(),
            ShotDetectionOptions(),
            FakeUnderstanding(workspace),
            FakeDirector(),
            renderer,
            cast(RenderedMediaQc, UnusedRenderedMediaQc()),
            edit_plan_id_factory=lambda: "epl_no_public_bgm",
            edl_id_factory=lambda: "edl_no_public_bgm",
            clock=lambda: NOW,
            ffmpeg_executable="ffmpeg",
            automatic_public_music=True,
        ),
    )

    result = flow.run(
        EditingProductRequest(
            workspace.root,
            _brief(),
            (source,),
            tmp_path / "output" / "no-public-bgm.mp4",
            output_profile=EditingOutputProfile("test_320x180_30", 320, 180, 30),
        )
    )

    assert result.outcome is ProductFlowOutcome.COMPLETED
    assert renderer.requests
    rendered_edl = renderer.requests[0].edl
    assert not any(segment.track_id == "bgm" for segment in rendered_edl.segments)
    assert any(segment.track_id == "source_audio" for segment in rendered_edl.segments)
    assert any(
        event.level is ProductFlowEventLevel.WARNING
        and "continuing without BGM" in event.message
        for event in result.events
    )
    assert source.read_bytes() == b"original-user-media"


def test_public_music_exhaustion_without_source_audio_requests_local_music(
    tmp_path: Path,
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    class NoAudioProbe(FakeMediaProbe):
        def probe(self, path: Path) -> MediaTechnicalMetadata:
            result = super().probe(path)
            if result.media_kind == "video":
                return replace(result, audio_channels=0, sample_rate_hz=None)
            return result

    class EmptyProvider:
        def __init__(self, *, page_size: int = 20) -> None:
            assert page_size == 20

        def search_music(self, query: MusicDiscoveryQuery) -> tuple[AudioMaterialCandidate, ...]:
            del query
            return ()

    monkeypatch.setattr(composition_module, "ReviewApplicationRuntime", FakeReviewRuntime)
    monkeypatch.setattr(
        composition_module,
        "OpenverseWikimediaAudioProvider",
        EmptyProvider,
    )

    workspace = ProjectWorkspace.open(tmp_path / "editing-no-audio-fallback-project")
    source = tmp_path / "silent-source.mp4"
    source.write_bytes(b"silent-user-media")
    flow = build_editing_product_flow(
        workspace,
        EditingProductCapabilities(
            NoAudioProbe(),
            FakeShotDetector(),
            ShotDetectionOptions(),
            FakeUnderstanding(workspace),
            FakeDirector(),
            FakeRenderer(),
            cast(RenderedMediaQc, UnusedRenderedMediaQc()),
            edit_plan_id_factory=lambda: "epl_no_audio_fallback",
            edl_id_factory=lambda: "edl_no_audio_fallback",
            clock=lambda: NOW,
            ffmpeg_executable="ffmpeg",
            automatic_public_music=True,
        ),
    )

    result = flow.run(
        EditingProductRequest(
            workspace.root,
            _brief(),
            (source,),
            tmp_path / "output" / "silent.mp4",
            output_profile=EditingOutputProfile("test_320x180_30", 320, 180, 30),
        )
    )

    assert result.outcome is ProductFlowOutcome.FAILED
    assert result.diagnostic is not None
    assert "Select a local music file" in result.diagnostic
    assert "rights needed to use it" in result.diagnostic

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import uuid
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from video_editing_agent.application.edl_builder import DeterministicEDLBuilder, EDLBuildRequest
from video_editing_agent.application.ports.artifact_store import ArtifactPayload
from video_editing_agent.application.ports.audio_acquisition import AudioAcquisitionRequest
from video_editing_agent.application.ports.audio_editorial import AudioMixDecision
from video_editing_agent.application.ports.audio_material_provider import (
    AudioMaterialCandidate,
    AudioMaterialProvider,
    MusicDiscoveryQuery,
)
from video_editing_agent.application.ports.audio_separation import AudioSeparationPort
from video_editing_agent.application.ports.director import DirectorPort
from video_editing_agent.application.ports.music_selection import MusicIntent
from video_editing_agent.application.ports.preproduction_planning import (
    ReferenceStyleGuidance,
    ScriptPlanningPort,
    ShootingPlanningPort,
)
from video_editing_agent.application.ports.preproduction_review import (
    ScriptProposalReviewPort,
    ShootingProposalReviewPort,
)
from video_editing_agent.application.ports.reference_acquisition import (
    ReferenceAcquisitionPort,
    ReferenceAcquisitionRequest,
)
from video_editing_agent.application.ports.rendered_media_qc import RenderedMediaQc
from video_editing_agent.application.ports.renderer import (
    OutputSpec,
    Renderer,
    RenderRequest,
    RenderResult,
)
from video_editing_agent.application.ports.shot_detector import ShotDetectionOptions, ShotDetector
from video_editing_agent.application.ports.speech_recognition import (
    SpeechRecognitionCapabilityUnavailable,
)
from video_editing_agent.application.ports.speech_synthesis import SpeechSynthesisPort
from video_editing_agent.application.ports.understanding import UnderstandingService
from video_editing_agent.application.subtitle_builder import compile_subtitle_cues
from video_editing_agent.application.use_cases.editing_director import GenerateEditPlanRequest
from video_editing_agent.application.use_cases.product_audio import (
    build_conservative_source_audio_mix,
)
from video_editing_agent.application.use_cases.product_flow import (
    EditingMusicInput,
    EditingOutputProfile,
    EditingProductFlow,
    EditingProductOperations,
    PlanningProductFlow,
    PlanningProductOperations,
    PlanningReferenceInput,
    PlanningReferenceKind,
    PreparedEditingMusic,
    PreparedPlanningReferences,
    ProductBriefInput,
    ProductFlowEventLevel,
    VoiceMode,
)
from video_editing_agent.application.use_cases.review_runtime import (
    ReviewApplicationRuntime,
    ReviewRequest,
)
from video_editing_agent.domain.asset.model import AssetProvenance
from video_editing_agent.domain.asset.policy import AssetOrigin, AssetUsageRole
from video_editing_agent.domain.asset.rights import RightsAttestation, RightsEligibility
from video_editing_agent.domain.brief.model import Brief, BriefReference
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.model import EditPlan
from video_editing_agent.domain.edit.resolution import ResolutionDecision, ResolutionDecisionType
from video_editing_agent.domain.edl.model import EDL
from video_editing_agent.domain.edl.subtitle import (
    StructuredSubtitleCue,
    SubtitleLayoutRegion,
    SubtitleStyleProfile,
)
from video_editing_agent.domain.evidence.speech import SpeechTranscript
from video_editing_agent.domain.music.model import BeatMap
from video_editing_agent.domain.review.model import ReviewVerdict
from video_editing_agent.domain.shot.analysis import AnalysisProfile
from video_editing_agent.editing.resolver.product_resolution import GroundedEditPlanResolver
from video_editing_agent.media.ingest.probe import MediaProbe
from video_editing_agent.media.ingest.service import AssetIngestService
from video_editing_agent.media.ingest.source import LocalMediaSource
from video_editing_agent.media.speech.voice_activity import SPEECH_ACTIVITY_KIND
from video_editing_agent.music.audio_editorial import plan_basic_mix
from video_editing_agent.music.beat_analysis.service import WaveEnergyBeatAnalysisService
from video_editing_agent.music.selection.service import (
    generate_music_windows,
    local_rights_eligibility,
    select_music,
)
from video_editing_agent.planning.brief.service import BriefContent
from video_editing_agent.planning.reference.guidance import to_reference_style_guidance
from video_editing_agent.planning.reference.service import ReferenceStyleEvidenceService
from video_editing_agent.providers.audio.openverse import OpenverseWikimediaAudioProvider
from video_editing_agent.providers.audio.wikimedia import WikimediaAudioRightsVerifier
from video_editing_agent.providers.audio.wikimedia_acquisition import WikimediaAudioAcquirer
from video_editing_agent.storage.asset.repository_media import RepositoryLocalAssetMediaResolver
from video_editing_agent.storage.project.workspace import ProjectWorkspace


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _edit_plan_id() -> str:
    return f"epl_{uuid.uuid4().hex}"


def _edl_id() -> str:
    return f"edl_{uuid.uuid4().hex}"


_OUTPUT_FORMATS: dict[str, tuple[str, str, str]] = {
    ".mp4": ("mp4", "libx264", "aac"),
    ".mov": ("mov", "libx264", "aac"),
    ".mkv": ("matroska", "libx264", "aac"),
    ".webm": ("webm", "libvpx-vp9", "libopus"),
}


def _output_spec(path: Path, profile: EditingOutputProfile) -> OutputSpec:
    suffix = path.suffix.casefold()
    selected = _OUTPUT_FORMATS.get(suffix)
    if selected is None:
        raise ValueError("unsupported output format; choose MP4, MOV, MKV, or WebM")
    container, video_codec, audio_codec = selected
    return OutputSpec(
        path,
        profile.width,
        profile.height,
        profile.frames_per_second,
        container,
        video_codec,
        audio_codec,
    )


def _public_music_queries(brief: ProductBriefInput) -> tuple[str, ...]:
    parts = (
        *brief.style_emotion,
        brief.product_topic or "",
        brief.objective,
        brief.core_message,
        "background music",
    )
    primary = " ".join(part.strip() for part in parts if part.strip())[:240]
    return tuple(
        dict.fromkeys(
            (
                primary or "background music",
                "instrumental background music",
                "piano instrumental",
            )
        )
    )


def _discover_public_music_candidates(
    provider: AudioMaterialProvider,
    brief: ProductBriefInput,
    report: Callable[[ProductFlowEventLevel, str], None] | None = None,
) -> tuple[AudioMaterialCandidate, ...]:
    discovered: list[AudioMaterialCandidate] = []
    seen: set[str] = set()
    for index, query in enumerate(_public_music_queries(brief), start=1):
        candidates = provider.search_music(MusicDiscoveryQuery(query))
        if report is not None:
            report(
                ProductFlowEventLevel.INFO if candidates else ProductFlowEventLevel.WARNING,
                f"Public music query {index} returned {len(candidates)} candidate(s)",
            )
            if not candidates and index < 3:
                report(
                    ProductFlowEventLevel.WARNING,
                    "Public music query produced no candidates; trying the next bounded fallback",
                )
        for candidate in candidates:
            if candidate.provider_item_id in seen:
                continue
            seen.add(candidate.provider_item_id)
            discovered.append(candidate)
    if report is not None:
        report(
            ProductFlowEventLevel.INFO,
            f"Public music discovery produced {len(discovered)} unique candidate(s)",
        )
    return tuple(discovered)


def _bounded_failure_summary(failures: list[str], *, detail_limit: int = 12) -> str:
    if not failures:
        return ""
    categories = Counter(failure.partition(": ")[2] or failure for failure in failures)
    category_summary = ", ".join(
        f"{reason} ({count})" for reason, count in categories.most_common(6)
    )
    if len(failures) <= detail_limit:
        details = failures
    else:
        half = detail_limit // 2
        details = [
            *failures[:half],
            f"... {len(failures) - detail_limit} intermediate diagnostic(s) omitted ...",
            *failures[-half:],
        ]
    return f"attempted={len(failures)}; categories={category_summary}; details=" + "; ".join(
        details
    )


@dataclass(frozen=True, slots=True)
class PlanningProductCapabilities:
    script_planning: ScriptPlanningPort
    script_review: ScriptProposalReviewPort
    shooting_planning: ShootingPlanningPort
    shooting_review: ShootingProposalReviewPort
    reference: PlanningReferenceCapabilities | None = None


@dataclass(frozen=True, slots=True)
class PlanningReferenceCapabilities:
    media_probe: MediaProbe
    shot_detector: ShotDetector
    shot_detection_options: ShotDetectionOptions
    understanding: UnderstandingService
    acquisition: ReferenceAcquisitionPort | None = None
    analysis_profile: AnalysisProfile = AnalysisProfile.SEMANTIC


@dataclass(frozen=True, slots=True)
class EditingProductCapabilities:
    media_probe: MediaProbe
    shot_detector: ShotDetector
    shot_detection_options: ShotDetectionOptions
    understanding: UnderstandingService
    director: DirectorPort
    renderer: Renderer
    rendered_media_qc: RenderedMediaQc
    analysis_profile: AnalysisProfile = AnalysisProfile.SEMANTIC
    edit_plan_id_factory: Callable[[], str] = _edit_plan_id
    edl_id_factory: Callable[[], str] = _edl_id
    clock: Callable[[], datetime] = _utc_now
    ffmpeg_executable: str | Path | None = None
    automatic_public_music: bool = False
    speech_recognition: Callable[[EntityRevisionRef], SpeechTranscript] | None = None
    speech_synthesis: SpeechSynthesisPort | None = None
    audio_separation: AudioSeparationPort | None = None


def _brief_content(value: ProductBriefInput) -> BriefContent:
    return BriefContent(
        title=value.title,
        objective=value.objective,
        audience=value.audience,
        platform=value.platform,
        core_message=value.core_message,
        product_topic=value.product_topic,
        target_duration=value.target_duration,
        authoritative_facts=value.authoritative_facts,
        style_emotion=value.style_emotion,
        success_criteria=value.success_criteria,
        prohibited_content=value.prohibited_content,
        brand_constraints=value.brand_constraints,
        user_notes=value.user_notes,
        references=value.references,
    )


def _create_brief(
    workspace: ProjectWorkspace,
    value: ProductBriefInput,
    created_by: str,
) -> Brief:
    return workspace.brief_service.create(_brief_content(value), created_by=created_by)


def build_planning_product_flow(
    workspace: ProjectWorkspace,
    capabilities: PlanningProductCapabilities,
) -> PlanningProductFlow:
    runtime = workspace.runtime(
        script_planning=capabilities.script_planning,
        script_review=capabilities.script_review,
        shooting_planning=capabilities.shooting_planning,
        shooting_review=capabilities.shooting_review,
    )
    prepare_references = None
    if capabilities.reference is not None:
        reference_capabilities = capabilities.reference
        ingest = AssetIngestService(reference_capabilities.media_probe, repository=workspace.assets)
        evidence_service = ReferenceStyleEvidenceService(workspace.artifacts)

        def prepare(
            values: tuple[PlanningReferenceInput, ...],
        ) -> PreparedPlanningReferences:
            brief_references: list[BriefReference] = []
            guidance: list[ReferenceStyleGuidance] = []
            for value in values:
                if value.kind is PlanningReferenceKind.DIRECT_HTTPS_VIDEO:
                    if reference_capabilities.acquisition is None:
                        raise RuntimeError("direct HTTPS reference acquisition is unavailable")
                    assert value.url is not None
                    acquired = reference_capabilities.acquisition.acquire(
                        ReferenceAcquisitionRequest(value.url)
                    )
                    if acquired.acquired is None:
                        message = "; ".join(item.message for item in acquired.diagnostics)
                        raise RuntimeError(f"reference acquisition failed: {message}")
                    path = acquired.acquired.local_path
                    origin = "reference_https"
                    provenance = AssetProvenance(
                        origin_type="reference_https",
                        source_page=acquired.acquired.original_url,
                        provider=acquired.acquired.provider,
                        provider_asset_id=acquired.acquired.provider_item_id,
                        retrieved_at=acquired.acquired.retrieved_at,
                    )
                else:
                    assert value.local_path is not None
                    path = value.local_path.expanduser().resolve(strict=True)
                    origin = "local_reference"
                    provenance = AssetProvenance(origin_type="local_reference")
                asset = ingest.ingest(
                    LocalMediaSource(
                        path, origin, provenance, AssetUsageRole.REFERENCE_ANALYSIS_ONLY
                    ),
                    created_by="product-flow-reference",
                )
                asset_ref = EntityRevisionRef(asset.envelope.id, asset.envelope.revision)
                shots = workspace.detect(
                    asset_ref,
                    reference_capabilities.shot_detector,
                    reference_capabilities.shot_detection_options,
                )
                analyses = tuple(
                    reference_capabilities.understanding.analyze(
                        EntityRevisionRef(shot.envelope.id, shot.envelope.revision),
                        reference_capabilities.analysis_profile,
                    )
                    for shot in shots
                )
                result = evidence_service.analyze(asset, shots, analyses)
                guidance.append(to_reference_style_guidance(result))
                brief_references.append(
                    BriefReference(
                        value.reference_id, value.kind.value, value.description, asset_ref
                    )
                )
            return PreparedPlanningReferences(tuple(brief_references), tuple(guidance))

        prepare_references = prepare

    return PlanningProductFlow(
        PlanningProductOperations(
            lambda value, created_by: _create_brief(workspace, value, created_by),
            runtime.preproduction.generate_script,
            runtime.preproduction.generate_shooting,
            prepare_references,
            runtime.preproduction.generate_script_with_references,
            runtime.preproduction.generate_shooting_with_references,
        )
    )


def build_editing_product_flow(
    workspace: ProjectWorkspace,
    capabilities: EditingProductCapabilities,
) -> EditingProductFlow:
    editing_runtime = workspace.editing_runtime(director=capabilities.director)
    resolver = GroundedEditPlanResolver(
        shot_index=workspace.shot_index,
        shot_repository=workspace.shots,
        temporal_evidence_repository=workspace.temporal,
    )
    builder = DeterministicEDLBuilder()
    media_resolver = RepositoryLocalAssetMediaResolver(workspace.assets)
    review_runtime = ReviewApplicationRuntime(capabilities.rendered_media_qc)
    ingest = AssetIngestService(capabilities.media_probe, repository=workspace.assets)

    def create_brief(value: ProductBriefInput, created_by: str) -> Brief:
        return _create_brief(workspace, value, created_by)

    def prepare_media(paths: tuple[Path, ...]) -> tuple[EntityRevisionRef, ...]:
        asset_refs: list[EntityRevisionRef] = []
        for path in paths:
            asset = ingest.ingest(
                LocalMediaSource(
                    path,
                    "local",
                    AssetProvenance(origin_type="local"),
                    AssetUsageRole.EDITABLE_VISUAL_FOOTAGE,
                ),
                created_by="product-flow",
            )
            if asset.media_kind.casefold() != "video":
                raise ValueError(f"selected visual footage did not probe as video: {path}")
            if asset.duration is None or asset.duration.as_fraction() <= 0:
                raise ValueError(f"selected visual footage has no positive probed duration: {path}")
            asset_ref = EntityRevisionRef(asset.envelope.id, asset.envelope.revision)
            asset_refs.append(asset_ref)
            shots = workspace.detect(
                asset_ref,
                capabilities.shot_detector,
                capabilities.shot_detection_options,
            )
            for shot in shots:
                shot_ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
                capabilities.understanding.analyze(shot_ref, capabilities.analysis_profile)
        workspace.rebuild_index()
        return tuple(asset_refs)

    def _music_beat_map(
        path: Path,
        asset_ref: EntityRevisionRef,
        duration: MediaTime,
    ) -> BeatMap:
        return WaveEnergyBeatAnalysisService().analyze(
            str(path),
            asset_ref,
            MediaTimeRange(MediaTime(0, 1), duration),
        )

    def _prepared_local_music(
        value: EditingMusicInput,
        report: Callable[[ProductFlowEventLevel, str], None],
    ) -> PreparedEditingMusic:
        path = value.local_path.expanduser().resolve(strict=True)
        report(ProductFlowEventLevel.INFO, "Validating local music rights attestation")
        origin = AssetOrigin.IMPORTED_LOCAL.value
        asset = ingest.ingest(
            LocalMediaSource(
                path,
                origin,
                AssetProvenance(origin_type=origin),
                AssetUsageRole.MUSIC,
            ),
            created_by="product-flow-music",
        )
        if asset.media_kind.casefold() != "audio":
            raise ValueError("selected local music did not probe as audio")
        if asset.duration is None or asset.duration.as_fraction() <= 0:
            raise ValueError("selected local music has no positive probed duration")
        asset_ref = EntityRevisionRef(asset.envelope.id, asset.envelope.revision)
        statement = "I confirm I have the rights needed to use this local music in this output."
        identity = hashlib.sha256(
            f"{asset_ref.entity_id}@{asset_ref.revision}:{asset.content_hash}:{statement}".encode()
        ).hexdigest()
        attestation = RightsAttestation(
            f"att_{identity}",
            asset_ref,
            "product-user",
            capabilities.clock(),
            statement,
        )
        if local_rights_eligibility(asset_ref, attestation) is not RightsEligibility.ELIGIBLE:
            raise ValueError("local music rights gate did not produce an eligible candidate")
        report(ProductFlowEventLevel.INFO, "Local music passed the rights gate")
        analysis_failures: list[str] = []
        beat_map = _analysis_beat_map_for_music(
            path,
            asset_ref,
            asset.duration,
            direct_pcm_wav=(
                path.suffix.casefold() in {".wav", ".wave"}
                and (asset.codec or "").casefold() == "pcm_s16le"
            ),
            failures=analysis_failures,
        )
        if beat_map is None:
            detail = "; ".join(analysis_failures)
            raise ValueError(
                "selected local music could not be decoded for BeatMap analysis"
                + (f": {detail}" if detail else "")
            )
        report(
            ProductFlowEventLevel.INFO,
            f"BeatMap analysis completed with {len(beat_map.beats)} beat point(s)",
        )
        evidence_payload = json.dumps(
            {
                "schema": "local-music-rights-attestation/v1",
                "attestation_id": attestation.attestation_id,
                "asset_ref": {
                    "entity_id": asset_ref.entity_id,
                    "revision": asset_ref.revision,
                },
                "asset_content_hash": asset.content_hash,
                "asserted_by": attestation.asserted_by,
                "asserted_at": attestation.asserted_at.isoformat(),
                "statement": attestation.statement,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        evidence = workspace.artifacts.put(
            ArtifactPayload(
                "application/vnd.video-editing-agent.rights-attestation+json",
                evidence_payload,
            )
        )
        return PreparedEditingMusic(asset_ref, beat_map, (evidence.artifact_id,))

    def _analysis_beat_map_for_music(
        source: Path,
        asset_ref: EntityRevisionRef,
        duration: MediaTime,
        *,
        direct_pcm_wav: bool,
        failures: list[str],
    ) -> BeatMap | None:
        if direct_pcm_wav:
            return _music_beat_map(source, asset_ref, duration)
        if capabilities.ffmpeg_executable is None:
            failures.append("music requires FFmpeg decoding for BeatMap analysis")
            return None
        with tempfile.NamedTemporaryFile(
            prefix="music-analysis-",
            suffix=".wav",
            dir=workspace.root,
            delete=False,
        ) as stream:
            analysis_path = Path(stream.name)
        try:
            try:
                completed = subprocess.run(
                    [
                        str(capabilities.ffmpeg_executable),
                        "-hide_banner",
                        "-loglevel",
                        "error",
                        "-y",
                        "-i",
                        str(source),
                        "-map",
                        "0:a:0",
                        "-vn",
                        "-ac",
                        "1",
                        "-ar",
                        "48000",
                        "-c:a",
                        "pcm_s16le",
                        str(analysis_path),
                    ],
                    check=False,
                    shell=False,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
            except (OSError, subprocess.TimeoutExpired) as error:
                failures.append(f"FFmpeg audio analysis decode failed: {error}")
                return None
            if completed.returncode != 0:
                detail = completed.stderr.strip().splitlines()
                failures.append(
                    "FFmpeg audio analysis decode failed" + (f": {detail[-1]}" if detail else "")
                )
                return None
            return _music_beat_map(analysis_path, asset_ref, duration)
        finally:
            analysis_path.unlink(missing_ok=True)

    def _prepared_public_music(
        brief: ProductBriefInput,
        report: Callable[[ProductFlowEventLevel, str], None],
    ) -> PreparedEditingMusic:
        discovery = OpenverseWikimediaAudioProvider(page_size=20)
        candidates = _discover_public_music_candidates(discovery, brief, report)
        if not candidates:
            raise ValueError("public music discovery returned no candidates")
        verifier = WikimediaAudioRightsVerifier(
            workspace.artifacts,
            clock=capabilities.clock,
        )
        acquirer = WikimediaAudioAcquirer(
            workspace.provider_audio,
            clock=capabilities.clock,
        )
        failures: list[str] = []
        for index, candidate in enumerate(candidates, start=1):
            report(
                ProductFlowEventLevel.INFO,
                f"Rights gate checking public music candidate {index}/{len(candidates)}",
            )
            if candidate.is_generated_audio is True:
                failures.append(f"{candidate.provider_item_id}: generated audio excluded")
                report(ProductFlowEventLevel.WARNING, "Generated audio candidate was excluded")
                continue
            verification = verifier.verify(candidate.provider_item_id)
            if not verification.is_verified or verification.verified is None:
                failures.append(f"{candidate.provider_item_id}: rights verification failed")
                report(ProductFlowEventLevel.WARNING, "Candidate failed rights verification")
                continue
            verified = verification.verified
            if verified.snapshot.eligibility is not RightsEligibility.ELIGIBLE:
                failures.append(
                    f"{candidate.provider_item_id}: automatic mode requires attribution-free "
                    "ELIGIBLE rights"
                )
                report(
                    ProductFlowEventLevel.WARNING,
                    "Candidate did not pass the attribution-free automatic rights gate",
                )
                continue
            report(ProductFlowEventLevel.INFO, "Candidate passed the public music rights gate")
            report(ProductFlowEventLevel.INFO, "Acquiring rights-approved public music")
            acquisition = acquirer.acquire(
                AudioAcquisitionRequest(
                    provider="wikimedia_commons",
                    provider_item_id=verified.provider_item_id,
                    approved_source_url=verified.source_url,
                    source_page=verified.source_page,
                    license_snapshot_ref=verified.rights_artifact_ref,
                    rights_eligibility=verified.snapshot.eligibility,
                    expected_source_sha1=verified.source_sha1,
                    expected_byte_size=verified.byte_size,
                    expected_content_type=verified.mime_type,
                )
            )
            if not acquisition.is_acquired or acquisition.acquired is None:
                failures.append(f"{candidate.provider_item_id}: acquisition failed")
                report(ProductFlowEventLevel.WARNING, "Public music acquisition failed")
                continue
            acquired = acquisition.acquired
            report(ProductFlowEventLevel.INFO, "Public music acquisition completed")
            origin = AssetOrigin.PROVIDER_ACQUIRED_AUDIO.value
            asset = ingest.ingest(
                LocalMediaSource(
                    acquired.local_path,
                    origin,
                    AssetProvenance(
                        origin_type=origin,
                        provider="wikimedia_commons",
                        provider_asset_id=verified.provider_item_id,
                        source_page=verified.source_page,
                        creator=verified.creator,
                        retrieved_at=acquired.acquired_at,
                        license_information=verified.license_identifier,
                        attribution=verified.attribution_text,
                    ),
                    AssetUsageRole.MUSIC,
                ),
                created_by="product-flow-public-music",
            )
            if asset.content_hash != acquired.local_sha256:
                raise RuntimeError("acquired public music hash changed during Asset ingest")
            if asset.media_kind.casefold() != "audio":
                failures.append(
                    f"{candidate.provider_item_id}: acquired file did not probe as audio"
                )
                continue
            if asset.duration is None or asset.duration.as_fraction() <= 0:
                failures.append(f"{candidate.provider_item_id}: acquired file has no duration")
                continue
            asset_ref = EntityRevisionRef(asset.envelope.id, asset.envelope.revision)
            beat_map = _analysis_beat_map_for_music(
                acquired.local_path,
                asset_ref,
                asset.duration,
                direct_pcm_wav=(
                    acquired.local_path.suffix.casefold() in {".wav", ".wave"}
                    and (asset.codec or "").casefold() == "pcm_s16le"
                ),
                failures=failures,
            )
            if beat_map is None:
                report(ProductFlowEventLevel.WARNING, "Acquired music BeatMap analysis failed")
                continue
            report(
                ProductFlowEventLevel.INFO,
                f"BeatMap analysis completed with {len(beat_map.beats)} beat point(s)",
            )
            rights_refs = tuple(
                dict.fromkeys(
                    (
                        *verified.snapshot.evidence_artifact_refs,
                        verified.rights_artifact_ref,
                    )
                )
            )
            return PreparedEditingMusic(asset_ref, beat_map, rights_refs)
        detail = _bounded_failure_summary(failures)
        raise ValueError(
            "no automatically eligible public background music could be prepared"
            + (f": {detail}" if detail else "")
        )

    def prepare_music(
        value: EditingMusicInput | None,
        brief: ProductBriefInput,
        report: Callable[[ProductFlowEventLevel, str], None],
    ) -> PreparedEditingMusic | None:
        if value is not None:
            return _prepared_local_music(value, report)
        if not capabilities.automatic_public_music:
            return None
        return _prepared_public_music(brief, report)

    def generate_edit_plan(
        brief_ref: EntityRevisionRef,
        script_ref: EntityRevisionRef | None,
        shooting_ref: EntityRevisionRef | None,
        created_by: str,
    ) -> EditPlan:
        return editing_runtime.editing.generate_edit_plan(
            GenerateEditPlanRequest(
                capabilities.edit_plan_id_factory(),
                brief_ref,
                script_ref,
                shooting_ref,
                created_by=created_by,
            )
        )

    def resolve_edit_plan(edit_plan: EditPlan) -> tuple[ResolutionDecision, ...]:
        return resolver.resolve(edit_plan)

    def assemble_edl(
        edit_plan: EditPlan,
        decisions: tuple[ResolutionDecision, ...],
        requires_audible_output: bool,
        music: PreparedEditingMusic | None,
    ) -> EDL:
        shot_refs = {
            selection.shot_ref
            for decision in decisions
            if decision.decision_type is ResolutionDecisionType.RESOLVED
            for selection in decision.selections
        }
        shots = tuple(
            workspace.shots.load(ref)
            for ref in sorted(shot_refs, key=lambda item: (item.entity_id, item.revision))
        )
        plan_ref = EntityRevisionRef(edit_plan.envelope.id, edit_plan.envelope.revision)
        source_mix = build_conservative_source_audio_mix(edit_plan, decisions)
        music_selection = None
        audio_mix = source_mix
        if music is not None:
            duration = MediaTime(0, 1)
            for decision in decisions:
                if decision.decision_type is ResolutionDecisionType.RESOLVED:
                    for selection in decision.selections:
                        duration = duration + selection.selected_source_range.duration
            if duration.as_fraction() <= 0:
                raise ValueError("resolved edit has no positive duration for music selection")
            source_duration = music.beat_map.analyzed_source_range.duration
            window_duration = (
                source_duration
                if source_duration.as_fraction() < duration.as_fraction()
                else duration
            )
            windows = generate_music_windows(
                music.beat_map,
                window_duration,
                music.rights_evidence_refs,
                intent=MusicIntent(
                    "rights-approved background music",
                    target_duration=duration,
                ),
            )
            music_selection = select_music(windows, target_duration=duration)
            if music_selection is None:
                raise ValueError("selected music did not produce a rights-approved BeatMap window")
            music_mix = plan_basic_mix(plan_ref, music.asset_ref, duration, ())
            mix_identity = hashlib.sha256(
                (
                    f"{source_mix.decision_id}:{music_mix.decision_id}:"
                    f"{music_selection.decision_id}:product-bgm-v1"
                ).encode()
            ).hexdigest()
            audio_mix = AudioMixDecision(
                f"amx_{mix_identity}",
                plan_ref,
                source_mix.source_audio_policy,
                music_mix.automation_intents,
                music_mix.loudness_intent,
                min(source_mix.confidence, music_mix.confidence),
                tuple(dict.fromkeys((*source_mix.warnings, *music_mix.warnings))),
                source_mix.source_treatments,
            )
        result = builder.build(
            EDLBuildRequest(
                EntityEnvelope(
                    capabilities.edl_id_factory(),
                    1,
                    "0.2",
                    EntityStatus.VALID,
                    capabilities.clock(),
                    "product-flow",
                    derived_from=(plan_ref,),
                ),
                edit_plan,
                decisions,
                shots,
                music_selection=music_selection,
                audio_mix=audio_mix,
                requires_audible_output=requires_audible_output,
            )
        )
        if result.edl is None or result.diagnostics:
            codes = ",".join(item.code.value for item in result.diagnostics)
            raise ValueError(f"canonical EDL assembly failed: {codes}")
        return result.edl

    def build_edl(
        edit_plan: EditPlan,
        decisions: tuple[ResolutionDecision, ...],
        requires_audible_output: bool,
    ) -> EDL:
        return assemble_edl(edit_plan, decisions, requires_audible_output, None)

    def build_edl_with_music(
        edit_plan: EditPlan,
        decisions: tuple[ResolutionDecision, ...],
        requires_audible_output: bool,
        music: PreparedEditingMusic,
    ) -> EDL:
        return assemble_edl(edit_plan, decisions, requires_audible_output, music)

    def save_edl(edl: EDL) -> None:
        workspace.edls.save(edl)

    def validate_audio(
        edl: EDL,
        decisions: tuple[ResolutionDecision, ...],
    ) -> EDL:
        source_by_selection = {
            segment.segment_id.removeprefix("source-audio:"): segment
            for segment in edl.segments
            if segment.segment_id.startswith("source-audio:")
        }
        video_by_selection = {
            segment.segment_id.removeprefix("video:"): segment
            for segment in edl.segments
            if segment.segment_id.startswith("video:")
        }
        for selection_id, video in video_by_selection.items():
            source_audio = source_by_selection.get(selection_id)
            if source_audio is None:
                raise RuntimeError(
                    f"ORIGINAL voice requires canonical SOURCE_AUDIO for selection {selection_id}"
                )
            if (
                source_audio.asset_ref != video.asset_ref
                or source_audio.source_range != video.source_range
                or source_audio.timeline_range != video.timeline_range
            ):
                raise RuntimeError(
                    f"SOURCE_AUDIO mapping disagrees with grounded video selection {selection_id}"
                )
        return edl

    def finalize_voice(
        edl: EDL,
        decisions: tuple[ResolutionDecision, ...],
        voice_mode: VoiceMode,
    ) -> EDL:
        if voice_mode is VoiceMode.ORIGINAL:
            return edl
        if capabilities.speech_synthesis is None:
            raise RuntimeError(
                "Synthetic voice requested but no approved SpeechSynthesisPort capability "
                "is configured"
            )
        raise RuntimeError(
            "Synthetic voice provider is available, but canonical derived voiceover lane "
            "assembly is not approved in this Stage-A boundary"
        )

    def compile_product_subtitles(
        edl: EDL,
        decisions: tuple[ResolutionDecision, ...],
        subtitle_style: SubtitleStyleProfile,
        report: Callable[[ProductFlowEventLevel, str], None],
    ) -> EDL:
        video_by_selection = {
            segment.segment_id.removeprefix("video:"): segment
            for segment in edl.segments
            if segment.segment_id.startswith("video:")
        }
        cues: list[StructuredSubtitleCue] = []
        for decision in decisions:
            if decision.decision_type is not ResolutionDecisionType.RESOLVED:
                continue
            for selection in decision.selections:
                video = video_by_selection.get(selection.selection_id)
                if video is None:
                    raise RuntimeError("canonical video segment is missing for subtitle mapping")
                transcript = workspace.transcripts.latest(selection.shot_ref)
                speech_evidence = tuple(
                    item
                    for item in workspace.temporal.list_evidence(selection.shot_ref)
                    if item.kind == SPEECH_ACTIVITY_KIND
                    and item.source_range is not None
                    and item.source_range.start.as_fraction()
                    < selection.selected_source_range.end.as_fraction()
                    and selection.selected_source_range.start.as_fraction()
                    < item.source_range.end.as_fraction()
                )
                if transcript is None and capabilities.speech_recognition is not None:
                    try:
                        transcript = capabilities.speech_recognition(selection.shot_ref)
                    except SpeechRecognitionCapabilityUnavailable as error:
                        if speech_evidence:
                            raise RuntimeError(
                                "grounded speech requires subtitles, but the approved Stage-A "
                                f"ASR capability is unavailable: {error}"
                            ) from error
                        report(
                            ProductFlowEventLevel.WARNING,
                            "Subtitle stage SKIPPED: ASR capability is unavailable and no "
                            "grounded speech evidence requires transcription; no subtitle cues "
                            "were fabricated",
                        )
                        continue
                if transcript is None:
                    if speech_evidence:
                        raise RuntimeError(
                            "grounded speech requires subtitles, but no approved Stage-A ASR "
                            "capability is configured"
                        )
                    report(
                        ProductFlowEventLevel.INFO,
                        "Subtitle stage SKIPPED: no trusted speech transcript or grounded speech "
                        "requirement; no subtitle cues were fabricated",
                    )
                    continue
                if transcript.shot_ref != selection.shot_ref:
                    raise RuntimeError("speech evidence belongs to a different exact Shot")
                if not transcript.segments:
                    report(
                        ProductFlowEventLevel.INFO,
                        "Subtitle stage NO_SPEECH: trusted speech analysis returned no timed "
                        "speech segments",
                    )
                    continue
                transcript_ref = (
                    f"speech_transcript:{transcript.shot_ref.entity_id}@"
                    f"{transcript.shot_ref.revision}:r{transcript.revision}"
                )
                evidence_refs = tuple(dict.fromkeys((*transcript.artifact_refs, transcript_ref)))
                selected = selection.selected_source_range
                for index, speech in enumerate(transcript.segments):
                    if (
                        speech.source_range.start.as_fraction() < selected.start.as_fraction()
                        or speech.source_range.end.as_fraction() > selected.end.as_fraction()
                    ):
                        continue
                    offset = speech.source_range.start.as_fraction() - selected.start.as_fraction()
                    timeline_start_fraction = video.timeline_range.start.as_fraction() + offset
                    timeline_start = MediaTime(
                        timeline_start_fraction.numerator,
                        timeline_start_fraction.denominator,
                    )
                    identity = hashlib.sha256(
                        (
                            f"{selection.selection_id}:{transcript_ref}:{index}:"
                            f"{speech.source_range.start.as_fraction()}:"
                            f"{speech.source_range.end.as_fraction()}:{speech.text}"
                        ).encode()
                    ).hexdigest()[:24]
                    cues.append(
                        StructuredSubtitleCue(
                            f"subtitle_{identity}",
                            MediaTimeRange(
                                timeline_start,
                                speech.source_range.duration,
                            ),
                            speech.text,
                            transcript.language or "und",
                            layout=SubtitleLayoutRegion.LOWER_SAFE,
                            style_profile=subtitle_style,
                            evidence_refs=evidence_refs,
                        )
                    )
        if not cues:
            return edl
        return compile_subtitle_cues(
            edl,
            tuple(sorted(cues, key=lambda cue: (cue.timeline_range.start, cue.cue_id))),
        )

    def render(edl: EDL, output_path: Path, output_profile: EditingOutputProfile) -> RenderResult:
        asset_refs = sorted(
            {segment.asset_ref for segment in edl.segments},
            key=lambda item: (item.entity_id, item.revision),
        )
        media = tuple(media_resolver.resolve_local(ref) for ref in asset_refs)
        return capabilities.renderer.render(
            RenderRequest(
                edl,
                media,
                _output_spec(output_path, output_profile),
            )
        )

    def review(
        edl_ref: EntityRevisionRef,
        render_result: RenderResult,
        requires_audible_output: bool,
    ) -> ReviewVerdict:
        return review_runtime.review(ReviewRequest(edl_ref, render_result, requires_audible_output))

    return EditingProductFlow(
        EditingProductOperations(
            create_brief,
            prepare_media,
            generate_edit_plan,
            resolve_edit_plan,
            build_edl,
            save_edl,
            render,
            review,
            prepare_music,
            build_edl_with_music,
            validate_audio,
            finalize_voice,
            compile_product_subtitles,
        )
    )

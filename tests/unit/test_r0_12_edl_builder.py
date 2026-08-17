from dataclasses import replace
from datetime import UTC, datetime

from video_editing_agent.application.edl_builder import (
    DeterministicEDLBuilder,
    EDLBuildDiagnosticCode,
    EDLBuildRequest,
)
from video_editing_agent.application.ports.audio_editorial import (
    AudioAutomationIntent,
    AudioAutomationKind,
    AudioMixDecision,
    AudioTrackRole,
    SourceAudioPolicy,
    SourceAudioTreatment,
    VoiceTreatment,
)
from video_editing_agent.application.ports.music_selection import (
    MusicSelectionDecision,
    MusicSourceSegment,
)
from video_editing_agent.application.ports.spatial_composer import (
    OutputCanvas,
    PixelCrop,
    ReframeDecision,
    SourceFrameGeometry,
    SpatialCropKeyframe,
    SpatialInterpolationMode,
    SpatialTransformKeyframe,
    SpatialTransformPlan,
)
from video_editing_agent.domain.common.entity import (
    EntityEnvelope,
    EntityRevisionRef,
    EntityStatus,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.model import EditPlan, EditSlot
from video_editing_agent.domain.edit.resolution import (
    ResolutionDecision,
    ResolutionDecisionType,
    ResolvedSelection,
)
from video_editing_agent.domain.edl import encode_edl, validate_edl
from video_editing_agent.domain.shot.model import Shot

NOW = datetime(2026, 8, 16, tzinfo=UTC)


def _envelope(identity: str, revision: int = 1) -> EntityEnvelope:
    return EntityEnvelope(identity, revision, "0.2", EntityStatus.VALID, NOW, "test")


def _fixture() -> tuple[EditPlan, tuple[ResolutionDecision, ...], tuple[Shot, ...]]:
    plan = EditPlan(
        _envelope("edit-plan"),
        EntityRevisionRef("script", 1),
        EntityRevisionRef("shooting", 1),
        (EditSlot("intro", "open", 0), EditSlot("proof", "show proof", 1)),
    )
    first = ResolvedSelection(
        "selection-a",
        EntityRevisionRef("shot-a", 1),
        MediaTimeRange(MediaTime(5, 24), MediaTime(1, 2)),
        0,
    )
    second = ResolvedSelection(
        "selection-b",
        EntityRevisionRef("shot-b", 1),
        MediaTimeRange(MediaTime(2, 1), MediaTime(3, 4)),
        0,
    )
    decisions = (
        ResolutionDecision(
            "resolution-a",
            EntityRevisionRef("edit-plan", 1),
            ("intro",),
            ResolutionDecisionType.RESOLVED,
            (first,),
        ),
        ResolutionDecision(
            "resolution-b",
            EntityRevisionRef("edit-plan", 1),
            ("proof",),
            ResolutionDecisionType.RESOLVED,
            (second,),
        ),
    )
    shots = (
        Shot(
            _envelope("shot-a"),
            EntityRevisionRef("asset-a", 2),
            boundary_method="fixture",
            source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(3, 1)),
        ),
        Shot(
            _envelope("shot-b"),
            EntityRevisionRef("asset-b", 1),
            boundary_method="fixture",
            source_range=MediaTimeRange(MediaTime(1, 1), MediaTime(3, 1)),
        ),
    )
    return plan, decisions, shots


def _request(
    *,
    spatial_decisions: tuple[ReframeDecision, ...] = (),
    music_selection: MusicSelectionDecision | None = None,
    audio_mix: AudioMixDecision | None = None,
) -> EDLBuildRequest:
    plan, decisions, shots = _fixture()
    return EDLBuildRequest(
        _envelope("edl-built"),
        plan,
        decisions,
        shots,
        spatial_decisions,
        music_selection,
        audio_mix,
    )


def _spatial_decision() -> ReframeDecision:
    plan = SpatialTransformPlan(
        "selection-a",
        EntityRevisionRef("shot-a", 1),
        MediaTimeRange(MediaTime(5, 24), MediaTime(1, 2)),
        SourceFrameGeometry(1920, 1080),
        OutputCanvas(1080, 1920),
        (
            SpatialCropKeyframe(MediaTime(5, 24), PixelCrop(0, 0, 603, 1072)),
            SpatialCropKeyframe(MediaTime(11, 24), PixelCrop(10, 0, 603, 1072)),
        ),
        SpatialInterpolationMode.LINEAR,
    )
    return ReframeDecision(
        "reframe-a",
        "selection-a",
        "track",
        tuple(
            SpatialTransformKeyframe(
                item.source_time,
                (item.crop.left + item.crop.width / 2) / 1920,
                (item.crop.top + item.crop.height / 2) / 1080,
                1920 / item.crop.width,
            )
            for item in plan.keyframes
        ),
        0.9,
        transform_plan=plan,
    )


def test_builder_allocates_exact_timeline_and_translates_spatial_plan() -> None:
    result = DeterministicEDLBuilder().build(_request(spatial_decisions=(_spatial_decision(),)))

    assert result.is_built and result.edl is not None
    assert validate_edl(result.edl).is_valid
    video = result.edl.ordered_segments
    assert tuple(item.timeline_range for item in video) == (
        MediaTimeRange(MediaTime(0, 1), MediaTime(1, 2)),
        MediaTimeRange(MediaTime(1, 2), MediaTime(3, 4)),
    )
    assert tuple(item.asset_ref.entity_id for item in video) == ("asset-a", "asset-b")
    assert video[0].spatial_decision_ref == "reframe-a"
    assert video[0].spatial_automation is not None
    assert tuple(item.timeline_time for item in video[0].spatial_automation.keyframes) == (
        MediaTime(0, 1),
        MediaTime(1, 4),
    )


def test_builder_is_independent_of_incidental_input_collection_order() -> None:
    request = _request(spatial_decisions=(_spatial_decision(),))
    reversed_request = replace(
        request,
        resolution_decisions=tuple(reversed(request.resolution_decisions)),
        shots=tuple(reversed(request.shots)),
    )

    first = DeterministicEDLBuilder().build(request)
    second = DeterministicEDLBuilder().build(reversed_request)

    assert first.is_built and first.edl is not None
    assert second.is_built and second.edl is not None
    assert encode_edl(first.edl) == encode_edl(second.edl)


def test_builder_translates_approved_music_mix_without_rescoring() -> None:
    music = MusicSelectionDecision(
        "music-choice",
        EntityRevisionRef("music", 3),
        (MusicSourceSegment(0, MediaTimeRange(MediaTime(10, 1), MediaTime(5, 4))),),
        ("rights",),
        0.8,
        0.7,
    )
    mix = AudioMixDecision(
        "mix",
        EntityRevisionRef("edit-plan", 1),
        SourceAudioPolicy.MUTE,
        (
            AudioAutomationIntent(
                AudioAutomationKind.GAIN,
                music.selected_asset_ref,
                (),
                -10.0,
                start=MediaTime(0, 1),
                end=MediaTime(5, 4),
                target_role=AudioTrackRole.BGM,
            ),
        ),
    )

    result = DeterministicEDLBuilder().build(_request(music_selection=music, audio_mix=mix))

    assert result.is_built and result.edl is not None
    assert tuple(track.track_id for track in result.edl.effective_tracks) == ("video", "bgm")
    bgm = next(item for item in result.edl.segments if item.track_id == "bgm")
    assert bgm.asset_ref == music.selected_asset_ref
    assert bgm.source_range == music.source_segments[0].source_range
    assert bgm.audio_mix_decision_ref == mix.decision_id
    assert bgm.audio_automations[0].keyframes[0].gain_millibels == -1000


def test_source_audio_policy_changes_assembled_tracks_without_mutating_assets() -> None:
    plan_ref = EntityRevisionRef("edit-plan", 1)
    mute_mix = AudioMixDecision("mute", plan_ref, SourceAudioPolicy.MUTE)
    preserve_mix = AudioMixDecision("preserve", plan_ref, SourceAudioPolicy.PRESERVE)

    muted = DeterministicEDLBuilder().build(_request(audio_mix=mute_mix))
    preserved = DeterministicEDLBuilder().build(_request(audio_mix=preserve_mix))

    assert muted.edl is not None and preserved.edl is not None
    assert {item.track_id for item in muted.edl.segments} == {"video"}
    assert {item.track_id for item in preserved.edl.segments} == {
        "video",
        "source_audio",
    }
    source = tuple(item for item in preserved.edl.segments if item.track_id == "source_audio")
    video = tuple(item for item in preserved.edl.segments if item.track_id == "video")
    assert tuple((item.asset_ref, item.source_range) for item in source) == tuple(
        (item.asset_ref, item.source_range) for item in video
    )
    assert all(item.audio_mix_decision_ref == "mute" for item in muted.edl.segments)


def test_explicit_mixed_source_treatments_override_legacy_default() -> None:
    request = _request()
    plan, decisions, shots = request.edit_plan, request.resolution_decisions, request.shots
    third_slot = EditSlot("detail", "show detail", 2)
    third_selection = ResolvedSelection(
        "selection-c",
        EntityRevisionRef("shot-c", 1),
        MediaTimeRange(MediaTime(4, 1), MediaTime(1, 1)),
        0,
    )
    third_decision = ResolutionDecision(
        "resolution-c",
        EntityRevisionRef("edit-plan", 1),
        ("detail",),
        ResolutionDecisionType.RESOLVED,
        (third_selection,),
    )
    third_shot = Shot(
        _envelope("shot-c"),
        EntityRevisionRef("asset-c", 1),
        boundary_method="fixture",
        source_range=MediaTimeRange(MediaTime(3, 1), MediaTime(3, 1)),
    )
    mix = AudioMixDecision(
        "mixed",
        EntityRevisionRef("edit-plan", 1),
        SourceAudioPolicy.MUTE,
        source_treatments=(
            SourceAudioTreatment(
                "selection-a",
                decisions[0].selections[0].selected_source_range,
                SourceAudioPolicy.PRESERVE,
                VoiceTreatment.CLEAN,
                required_speech=True,
            ),
            SourceAudioTreatment(
                "selection-b",
                decisions[1].selections[0].selected_source_range,
                SourceAudioPolicy.DUCK,
                duck_gain_db=-12.0,
            ),
            SourceAudioTreatment(
                "selection-c",
                third_selection.selected_source_range,
                SourceAudioPolicy.MUTE,
                VoiceTreatment.DO_NOT_USE_ORIGINAL,
                required_speech=True,
            ),
        ),
    )
    result = DeterministicEDLBuilder().build(
        replace(
            request,
            edit_plan=replace(plan, slots=(*plan.slots, third_slot)),
            resolution_decisions=(*decisions, third_decision),
            shots=(*shots, third_shot),
            audio_mix=mix,
        )
    )

    assert result.is_built and result.edl is not None
    source = tuple(item for item in result.edl.segments if item.track_id == "source_audio")
    assert tuple(item.segment_id for item in source) == (
        "source-audio:selection-a",
        "source-audio:selection-b",
    )
    assert source[0].audio_automations == ()
    assert tuple(item.kind.value for item in source[1].audio_automations) == ("gain", "duck")
    assert tuple(item.gain_millibels for item in source[1].audio_automations[1].keyframes) == (
        -1200,
        -1200,
    )
    assert source[1].source_range == decisions[1].selections[0].selected_source_range


def test_source_treatment_targets_and_speech_protection_fail_closed() -> None:
    request = _request()
    first_range = request.resolution_decisions[0].selections[0].selected_source_range
    cases = (
        SourceAudioTreatment("unknown", first_range, SourceAudioPolicy.PRESERVE),
        SourceAudioTreatment(
            "selection-a",
            MediaTimeRange(first_range.start, first_range.duration + MediaTime(1, 24)),
            SourceAudioPolicy.PRESERVE,
        ),
        SourceAudioTreatment(
            "selection-a",
            first_range,
            SourceAudioPolicy.MUTE,
            VoiceTreatment.PRESERVE,
            required_speech=True,
        ),
    )
    expected = (
        EDLBuildDiagnosticCode.AUDIO_TREATMENT_INVALID,
        EDLBuildDiagnosticCode.AUDIO_TREATMENT_INVALID,
        EDLBuildDiagnosticCode.SPEECH_PROTECTION_VIOLATION,
    )
    for treatment, code in zip(cases, expected, strict=True):
        result = DeterministicEDLBuilder().build(
            replace(
                request,
                audio_mix=AudioMixDecision(
                    "mix",
                    EntityRevisionRef("edit-plan", 1),
                    SourceAudioPolicy.MUTE,
                    source_treatments=(treatment,),
                ),
            )
        )
        assert code in {item.code for item in result.diagnostics}


def test_duplicate_treatment_and_revoice_permission_do_not_fabricate_audio() -> None:
    request = _request()
    first_range = request.resolution_decisions[0].selections[0].selected_source_range
    treatment = SourceAudioTreatment(
        "selection-a",
        first_range,
        SourceAudioPolicy.MUTE,
        VoiceTreatment.ALLOW_REVOICE,
    )
    duplicate = DeterministicEDLBuilder().build(
        replace(
            request,
            audio_mix=AudioMixDecision(
                "duplicate",
                EntityRevisionRef("edit-plan", 1),
                SourceAudioPolicy.MUTE,
                source_treatments=(treatment, treatment),
            ),
        )
    )
    permitted = DeterministicEDLBuilder().build(
        replace(
            request,
            audio_mix=AudioMixDecision(
                "revoice-permission",
                EntityRevisionRef("edit-plan", 1),
                SourceAudioPolicy.MUTE,
                source_treatments=(treatment,),
            ),
        )
    )

    assert EDLBuildDiagnosticCode.AUDIO_TREATMENT_INVALID in {
        item.code for item in duplicate.diagnostics
    }
    assert permitted.is_built and permitted.edl is not None
    assert all(item.track_id != "voiceover" for item in permitted.edl.segments)


def test_builder_applies_declared_audible_intent_qc_without_guessing_intent() -> None:
    request = _request(
        audio_mix=AudioMixDecision(
            "silent", EntityRevisionRef("edit-plan", 1), SourceAudioPolicy.MUTE
        )
    )

    required = DeterministicEDLBuilder().build(replace(request, requires_audible_output=True))
    intentional = DeterministicEDLBuilder().build(replace(request, requires_audible_output=False))

    assert EDLBuildDiagnosticCode.AUDIBLE_LANE_QC_FAILED in {
        item.code for item in required.diagnostics
    }
    assert intentional.is_built and intentional.edl is not None


def test_builder_failures_are_structured_for_incomplete_and_ambiguous_coverage() -> None:
    plan, decisions, shots = _fixture()
    unresolved = ResolutionDecision(
        "unresolved",
        EntityRevisionRef("edit-plan", 1),
        ("proof",),
        ResolutionDecisionType.UNRESOLVED,
    )
    duplicate = replace(decisions[0], decision_id="duplicate")
    result = DeterministicEDLBuilder().build(
        EDLBuildRequest(
            _envelope("edl"),
            plan,
            (decisions[0], duplicate, unresolved),
            shots,
        )
    )

    assert not result.is_built and result.edl is None
    assert {item.code for item in result.diagnostics} == {
        EDLBuildDiagnosticCode.AMBIGUOUS_SLOT_COVERAGE,
        EDLBuildDiagnosticCode.UNRESOLVED_SLOT,
    }


def test_builder_fails_closed_for_missing_shot_and_illegal_selected_range() -> None:
    plan, decisions, shots = _fixture()
    missing = DeterministicEDLBuilder().build(
        EDLBuildRequest(_envelope("edl"), plan, decisions, shots[:1])
    )
    escaped_selection = replace(
        decisions[0].selections[0],
        selected_source_range=MediaTimeRange(MediaTime(11, 4), MediaTime(1, 2)),
    )
    escaped_decision = replace(decisions[0], selections=(escaped_selection,))
    illegal = DeterministicEDLBuilder().build(
        EDLBuildRequest(_envelope("edl"), plan, (escaped_decision, decisions[1]), shots)
    )

    assert EDLBuildDiagnosticCode.MISSING_SHOT in {item.code for item in missing.diagnostics}
    assert EDLBuildDiagnosticCode.ILLEGAL_SOURCE_RANGE in {
        item.code for item in illegal.diagnostics
    }


def test_builder_refuses_unmappable_spatial_and_audio_decisions() -> None:
    spatial = replace(_spatial_decision(), transform_plan=None)
    mix = AudioMixDecision(
        "mix",
        EntityRevisionRef("edit-plan", 1),
        SourceAudioPolicy.DUCK,
    )

    result = DeterministicEDLBuilder().build(_request(spatial_decisions=(spatial,), audio_mix=mix))

    assert {item.code for item in result.diagnostics} == {
        EDLBuildDiagnosticCode.AUDIO_MAPPING_UNSUPPORTED,
        EDLBuildDiagnosticCode.SPATIAL_DECISION_INVALID,
    }


def test_builder_timeline_is_independent_of_planning_provenance() -> None:
    legacy_plan, decisions, shots = _fixture()
    brief_ref = EntityRevisionRef("brief", 1)
    editing_only_plan = replace(
        legacy_plan,
        script_plan_ref=None,
        shooting_plan_ref=None,
        brief_ref=brief_ref,
    )
    combined_plan = replace(
        legacy_plan,
        brief_ref=brief_ref,
    )
    builder = DeterministicEDLBuilder()

    editing_only = builder.build(
        EDLBuildRequest(
            _envelope("edl-provenance"),
            editing_only_plan,
            decisions,
            shots,
        )
    )
    combined = builder.build(
        EDLBuildRequest(
            _envelope("edl-provenance"),
            combined_plan,
            decisions,
            shots,
        )
    )

    assert editing_only.is_built and editing_only.edl is not None
    assert combined.is_built and combined.edl is not None
    assert encode_edl(editing_only.edl) == encode_edl(combined.edl)

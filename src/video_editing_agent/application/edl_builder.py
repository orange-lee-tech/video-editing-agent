from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from video_editing_agent.application.ports.audio_editorial import (
    AudioAutomationIntent,
    AudioAutomationKind,
    AudioMixDecision,
    AudioTrackRole,
    SourceAudioPolicy,
)
from video_editing_agent.application.ports.music_selection import MusicSelectionDecision
from video_editing_agent.application.ports.spatial_composer import (
    ReframeDecision,
    SpatialInterpolationMode,
)
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.model import EditPlan
from video_editing_agent.domain.edit.resolution import (
    ResolutionDecision,
    ResolutionDecisionType,
    ResolvedSelection,
)
from video_editing_agent.domain.edl import (
    EDL,
    EDLAudioAutomation,
    EDLAudioAutomationKind,
    EDLAudioKeyframe,
    EDLInterpolation,
    EDLSegment,
    EDLSpatialAutomation,
    EDLSpatialKeyframe,
    EDLTrack,
    EDLTrackFamily,
    ExactRational,
    decode_edl,
    encode_edl,
    validate_edl,
)
from video_editing_agent.domain.shot.model import Shot


class EDLBuildDiagnosticCode(StrEnum):
    EDIT_PLAN_REF_MISMATCH = "edit_plan_ref_mismatch"
    AMBIGUOUS_SLOT_ORDER = "ambiguous_slot_order"
    UNKNOWN_SLOT_COVERAGE = "unknown_slot_coverage"
    MISSING_SLOT_COVERAGE = "missing_slot_coverage"
    AMBIGUOUS_SLOT_COVERAGE = "ambiguous_slot_coverage"
    UNRESOLVED_SLOT = "unresolved_slot"
    DUPLICATE_SELECTION_ID = "duplicate_selection_id"
    DUPLICATE_SHOT = "duplicate_shot"
    MISSING_SHOT = "missing_shot"
    ILLEGAL_SOURCE_RANGE = "illegal_source_range"
    SPATIAL_DECISION_CONFLICT = "spatial_decision_conflict"
    SPATIAL_DECISION_INVALID = "spatial_decision_invalid"
    AUDIO_DECISION_INCOMPLETE = "audio_decision_incomplete"
    AUDIO_MAPPING_UNSUPPORTED = "audio_mapping_unsupported"
    CANONICAL_EDL_INVALID = "canonical_edl_invalid"


@dataclass(frozen=True, slots=True)
class EDLBuildDiagnostic:
    code: EDLBuildDiagnosticCode
    message: str
    slot_ids: tuple[str, ...] = ()
    selection_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EDLBuildRequest:
    envelope: EntityEnvelope
    edit_plan: EditPlan
    resolution_decisions: tuple[ResolutionDecision, ...]
    shots: tuple[Shot, ...]
    spatial_decisions: tuple[ReframeDecision, ...] = ()
    music_selection: MusicSelectionDecision | None = None
    audio_mix: AudioMixDecision | None = None


@dataclass(frozen=True, slots=True)
class EDLBuildResult:
    edl: EDL | None
    diagnostics: tuple[EDLBuildDiagnostic, ...]

    @property
    def is_built(self) -> bool:
        return self.edl is not None and not self.diagnostics


def _ref(envelope: EntityEnvelope) -> EntityRevisionRef:
    return EntityRevisionRef(envelope.id, envelope.revision)


def _inside(inner: MediaTimeRange, outer: MediaTimeRange) -> bool:
    return (
        inner.start.as_fraction() >= outer.start.as_fraction()
        and inner.end.as_fraction() <= outer.end.as_fraction()
    )


def _timeline_time(
    source_time: MediaTime, selection: ResolvedSelection, timeline_range: MediaTimeRange
) -> MediaTime:
    return timeline_range.start + (source_time - selection.selected_source_range.start)


def _spatial_automation(
    decision: ReframeDecision,
    selection: ResolvedSelection,
    timeline_range: MediaTimeRange,
) -> EDLSpatialAutomation | None:
    plan = decision.transform_plan
    if plan is None:
        return None
    interpolation = (
        EDLInterpolation.HOLD
        if plan.interpolation is SpatialInterpolationMode.HOLD
        else EDLInterpolation.LINEAR
    )
    return EDLSpatialAutomation(
        interpolation,
        tuple(
            EDLSpatialKeyframe(
                _timeline_time(item.source_time, selection, timeline_range),
                item.source_time,
                item.crop.left,
                item.crop.top,
                item.crop.width,
                item.crop.height,
                ExactRational(1),
                ExactRational(0),
                ExactRational(0),
            )
            for item in plan.keyframes
        ),
    )


def _gain_millibels(intent: AudioAutomationIntent) -> int | None:
    if intent.gain_db is None:
        return None
    value = Decimal(str(intent.gain_db)) * 100
    if value != value.to_integral_value():
        return None
    return int(value)


def _audio_automation(intent: AudioAutomationIntent) -> EDLAudioAutomation | None:
    if intent.start is None or intent.end is None:
        return None
    gain = _gain_millibels(intent)
    if gain is None:
        return None
    if intent.kind is AudioAutomationKind.GAIN:
        kind = EDLAudioAutomationKind.GAIN
        keyframes = (
            EDLAudioKeyframe(intent.start, gain),
            EDLAudioKeyframe(intent.end, gain),
        )
    elif intent.kind is AudioAutomationKind.DUCK:
        kind = EDLAudioAutomationKind.DUCK
        keyframes = (
            EDLAudioKeyframe(intent.start, gain),
            EDLAudioKeyframe(intent.end, gain),
        )
    elif intent.kind is AudioAutomationKind.FADE_IN:
        kind = EDLAudioAutomationKind.FADE
        keyframes = (
            EDLAudioKeyframe(intent.start, gain, muted=True),
            EDLAudioKeyframe(intent.end, gain),
        )
    elif intent.kind is AudioAutomationKind.FADE_OUT:
        kind = EDLAudioAutomationKind.FADE
        keyframes = (
            EDLAudioKeyframe(intent.start, gain),
            EDLAudioKeyframe(intent.end, gain, muted=True),
        )
    else:
        return None
    return EDLAudioAutomation(kind, EDLInterpolation.LINEAR, keyframes)


class DeterministicEDLBuilder:
    """Assemble approved decisions; never select, reframe, remix, or repair them."""

    def build(self, request: EDLBuildRequest) -> EDLBuildResult:
        diagnostics: list[EDLBuildDiagnostic] = []

        def add(
            code: EDLBuildDiagnosticCode,
            message: str,
            *,
            slots: tuple[str, ...] = (),
            selections: tuple[str, ...] = (),
        ) -> None:
            diagnostics.append(EDLBuildDiagnostic(code, message, slots, selections))

        plan_ref = _ref(request.edit_plan.envelope)
        slot_ids = {slot.slot_id for slot in request.edit_plan.slots}
        orders = tuple(slot.order for slot in request.edit_plan.slots)
        if len(set(orders)) != len(orders):
            add(
                EDLBuildDiagnosticCode.AMBIGUOUS_SLOT_ORDER,
                "EditPlan slot order must be unique for exact timeline assembly",
            )

        coverage: dict[str, list[ResolutionDecision]] = {slot_id: [] for slot_id in slot_ids}
        for resolution_decision in request.resolution_decisions:
            if resolution_decision.edit_plan_ref != plan_ref:
                add(
                    EDLBuildDiagnosticCode.EDIT_PLAN_REF_MISMATCH,
                    "resolution decision references a different EditPlan revision",
                    slots=resolution_decision.target_slot_ids,
                )
            unknown = tuple(sorted(set(resolution_decision.target_slot_ids) - slot_ids))
            if unknown:
                add(
                    EDLBuildDiagnosticCode.UNKNOWN_SLOT_COVERAGE,
                    "resolution decision targets unknown EditSlot IDs",
                    slots=unknown,
                )
            for slot_id in resolution_decision.target_slot_ids:
                if slot_id in coverage:
                    coverage[slot_id].append(resolution_decision)

        ordered_decisions: list[ResolutionDecision] = []
        for slot in sorted(request.edit_plan.slots, key=lambda item: (item.order, item.slot_id)):
            coverage_matches = coverage[slot.slot_id]
            if not coverage_matches:
                add(
                    EDLBuildDiagnosticCode.MISSING_SLOT_COVERAGE,
                    "EditSlot has no ResolutionDecision",
                    slots=(slot.slot_id,),
                )
            elif len(coverage_matches) > 1 or len(coverage_matches[0].target_slot_ids) != 1:
                add(
                    EDLBuildDiagnosticCode.AMBIGUOUS_SLOT_COVERAGE,
                    "EditSlot coverage cannot be mapped to one ordered decision",
                    slots=(slot.slot_id,),
                )
            elif coverage_matches[0].decision_type is not ResolutionDecisionType.RESOLVED:
                add(
                    EDLBuildDiagnosticCode.UNRESOLVED_SLOT,
                    "EditSlot resolution is unresolved",
                    slots=(slot.slot_id,),
                )
            else:
                ordered_decisions.append(coverage_matches[0])

        shot_lookup: dict[EntityRevisionRef, Shot] = {}
        for indexed_shot in request.shots:
            shot_ref = _ref(indexed_shot.envelope)
            if shot_ref in shot_lookup:
                add(
                    EDLBuildDiagnosticCode.DUPLICATE_SHOT,
                    "Shot lookup contains duplicate exact revision refs",
                )
            shot_lookup[shot_ref] = indexed_shot

        spatial_lookup: dict[str, list[ReframeDecision]] = {}
        for spatial_decision in request.spatial_decisions:
            spatial_lookup.setdefault(spatial_decision.selection_id, []).append(spatial_decision)

        seen_selections: set[str] = set()
        timeline_cursor = MediaTime(0, 1)
        video_segments: list[EDLSegment] = []
        for decision in ordered_decisions:
            slot_id = decision.target_slot_ids[0]
            for selection in decision.selections:
                if selection.selection_id in seen_selections:
                    add(
                        EDLBuildDiagnosticCode.DUPLICATE_SELECTION_ID,
                        "selection_id values must be unique across assembled decisions",
                        slots=(slot_id,),
                        selections=(selection.selection_id,),
                    )
                    continue
                seen_selections.add(selection.selection_id)
                selected_shot = shot_lookup.get(selection.shot_ref)
                if selected_shot is None:
                    add(
                        EDLBuildDiagnosticCode.MISSING_SHOT,
                        "selection Shot revision is absent from authoritative lookup",
                        slots=(slot_id,),
                        selections=(selection.selection_id,),
                    )
                    continue
                if not _inside(selection.selected_source_range, selected_shot.source_range):
                    add(
                        EDLBuildDiagnosticCode.ILLEGAL_SOURCE_RANGE,
                        "selected source range escapes its authoritative Shot",
                        slots=(slot_id,),
                        selections=(selection.selection_id,),
                    )
                    continue
                timeline_range = MediaTimeRange(
                    timeline_cursor, selection.selected_source_range.duration
                )
                timeline_cursor = timeline_range.end
                spatial_matches = spatial_lookup.get(selection.selection_id, [])
                if len(spatial_matches) > 1:
                    add(
                        EDLBuildDiagnosticCode.SPATIAL_DECISION_CONFLICT,
                        "selection has multiple spatial decisions",
                        selections=(selection.selection_id,),
                    )
                    continue
                spatial = None
                spatial_ref = None
                if spatial_matches:
                    spatial_decision = spatial_matches[0]
                    plan = spatial_decision.transform_plan
                    if (
                        plan is None
                        or plan.selection_id != selection.selection_id
                        or plan.shot_ref != selection.shot_ref
                        or plan.source_range != selection.selected_source_range
                    ):
                        add(
                            EDLBuildDiagnosticCode.SPATIAL_DECISION_INVALID,
                            "spatial decision has no matching canonical transform plan",
                            selections=(selection.selection_id,),
                        )
                        continue
                    spatial = _spatial_automation(spatial_decision, selection, timeline_range)
                    spatial_ref = spatial_decision.decision_id
                video_segments.append(
                    EDLSegment(
                        f"video:{selection.selection_id}",
                        selected_shot.asset_ref,
                        source_range=selection.selected_source_range,
                        timeline_range=timeline_range,
                        track_id="video",
                        shot_ref=selection.shot_ref,
                        spatial_decision_ref=spatial_ref,
                        audio_mix_decision_ref=(
                            None if request.audio_mix is None else request.audio_mix.decision_id
                        ),
                        spatial_automation=spatial,
                    )
                )

        if set(spatial_lookup) - seen_selections:
            add(
                EDLBuildDiagnosticCode.SPATIAL_DECISION_INVALID,
                "spatial decision targets a selection outside the assembled EditPlan",
                selections=tuple(sorted(set(spatial_lookup) - seen_selections)),
            )

        tracks = [EDLTrack("video", EDLTrackFamily.VIDEO)]
        segments: list[EDLSegment] = list(video_segments)
        mix = request.audio_mix
        music = request.music_selection
        if mix is not None and mix.edit_plan_ref != plan_ref:
            add(
                EDLBuildDiagnosticCode.EDIT_PLAN_REF_MISMATCH,
                "audio mix references a different EditPlan revision",
            )
        if music is not None and mix is None:
            add(
                EDLBuildDiagnosticCode.AUDIO_DECISION_INCOMPLETE,
                "music selection requires an approved AudioMixDecision",
            )
        if music is None and mix is not None and mix.automation_intents:
            add(
                EDLBuildDiagnosticCode.AUDIO_DECISION_INCOMPLETE,
                "audio automation intents require their selected music decision",
            )
        if mix is not None and mix.source_audio_policy is SourceAudioPolicy.DUCK:
            add(
                EDLBuildDiagnosticCode.AUDIO_MAPPING_UNSUPPORTED,
                "source-audio DUCK lacks a deterministic EDL mapping in current contracts",
            )
        elif mix is not None and mix.source_audio_policy is SourceAudioPolicy.PRESERVE:
            tracks.append(EDLTrack("source_audio", EDLTrackFamily.SOURCE_AUDIO))
            segments.extend(
                EDLSegment(
                    f"source-audio:{segment.segment_id.removeprefix('video:')}",
                    segment.asset_ref,
                    source_range=segment.source_range,
                    timeline_range=segment.timeline_range,
                    track_id="source_audio",
                    shot_ref=segment.shot_ref,
                    audio_mix_decision_ref=mix.decision_id,
                )
                for segment in video_segments
            )

        if music is not None and mix is not None:
            tracks.append(EDLTrack("bgm", EDLTrackFamily.BGM))
            bgm_cursor = MediaTime(0, 1)
            bgm_segments: list[EDLSegment] = []
            for item in music.source_segments:
                timeline_range = MediaTimeRange(bgm_cursor, item.source_range.duration)
                bgm_cursor = timeline_range.end
                bgm_segments.append(
                    EDLSegment(
                        f"bgm:{music.decision_id}:{item.order}",
                        music.selected_asset_ref,
                        source_range=item.source_range,
                        timeline_range=timeline_range,
                        track_id="bgm",
                        audio_mix_decision_ref=mix.decision_id,
                    )
                )
            for intent in mix.automation_intents:
                if (
                    intent.target_asset_ref != music.selected_asset_ref
                    or intent.target_role is not AudioTrackRole.BGM
                    or intent.target_slot_ids
                ):
                    add(
                        EDLBuildDiagnosticCode.AUDIO_MAPPING_UNSUPPORTED,
                        "audio intent target cannot be mapped to the selected BGM track",
                    )
                    continue
                translated = _audio_automation(intent)
                if translated is None:
                    add(
                        EDLBuildDiagnosticCode.AUDIO_MAPPING_UNSUPPORTED,
                        "audio intent timing, kind, or gain precision is unsupported",
                    )
                    continue
                containing = [
                    index
                    for index, segment in enumerate(bgm_segments)
                    if all(
                        segment.timeline_range.start.as_fraction()
                        <= keyframe.timeline_time.as_fraction()
                        <= segment.timeline_range.end.as_fraction()
                        for keyframe in translated.keyframes
                    )
                ]
                if len(containing) != 1:
                    add(
                        EDLBuildDiagnosticCode.AUDIO_MAPPING_UNSUPPORTED,
                        "audio intent must fit wholly inside one selected music segment",
                    )
                    continue
                index = containing[0]
                current = bgm_segments[index]
                bgm_segments[index] = EDLSegment(
                    current.segment_id,
                    current.asset_ref,
                    source_range=current.source_range,
                    timeline_range=current.timeline_range,
                    track_id=current.track_id,
                    audio_mix_decision_ref=current.audio_mix_decision_ref,
                    audio_automations=(*current.audio_automations, translated),
                )
            segments.extend(bgm_segments)

        if diagnostics:
            return EDLBuildResult(None, _ordered_diagnostics(diagnostics))
        edl = EDL(
            request.envelope,
            plan_ref,
            tuple(segments),
            tuple(tracks),
        )
        validation = validate_edl(edl)
        if not validation.is_valid:
            add(
                EDLBuildDiagnosticCode.CANONICAL_EDL_INVALID,
                "assembled EDL failed canonical validation: "
                + ",".join(item.code.value for item in validation.diagnostics),
            )
            return EDLBuildResult(None, _ordered_diagnostics(diagnostics))
        if decode_edl(encode_edl(edl)) != EDL(
            edl.envelope, edl.edit_plan_ref, edl.ordered_segments, edl.effective_tracks
        ):
            add(
                EDLBuildDiagnosticCode.CANONICAL_EDL_INVALID,
                "assembled EDL failed deterministic codec round-trip",
            )
            return EDLBuildResult(None, _ordered_diagnostics(diagnostics))
        return EDLBuildResult(edl, ())


def _ordered_diagnostics(
    diagnostics: list[EDLBuildDiagnostic],
) -> tuple[EDLBuildDiagnostic, ...]:
    return tuple(
        sorted(
            diagnostics,
            key=lambda item: (item.code.value, item.slot_ids, item.selection_ids, item.message),
        )
    )

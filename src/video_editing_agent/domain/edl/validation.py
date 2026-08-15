from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from video_editing_agent.domain.edl.automation import (
    EDLAudioAutomationKind,
    EDLInterpolation,
    ExactRational,
)
from video_editing_agent.domain.edl.model import EDL, EDLSegment, EDLTrackFamily
from video_editing_agent.domain.edl.subtitle import (
    EDLSubtitleCue,
    SubtitleEmphasisStyle,
    SubtitleLayoutRegion,
)


class EDLDiagnosticCode(StrEnum):
    DUPLICATE_SEGMENT_ID = "duplicate_segment_id"
    DUPLICATE_TRACK_ID = "duplicate_track_id"
    UNKNOWN_TRACK = "unknown_track"
    DURATION_MISMATCH = "duration_mismatch"
    SAME_TRACK_OVERLAP = "same_track_overlap"
    AUTOMATION_TRACK_INCOMPATIBLE = "automation_track_incompatible"
    AUTOMATION_KEYFRAME_ORDER = "automation_keyframe_order"
    AUTOMATION_KEYFRAME_RANGE = "automation_keyframe_range"
    AUTOMATION_VALUE_INVALID = "automation_value_invalid"
    AUTOMATION_INTERPOLATION_UNSUPPORTED = "automation_interpolation_unsupported"
    AUDIO_LOOP_INVALID = "audio_loop_invalid"
    AUTOMATION_TIME_MAPPING_INVALID = "automation_time_mapping_invalid"
    AUDIO_KIND_UNSUPPORTED = "audio_kind_unsupported"
    DUPLICATE_SUBTITLE_CUE_ID = "duplicate_subtitle_cue_id"
    SUBTITLE_IDENTITY_INVALID = "subtitle_identity_invalid"
    SUBTITLE_TRACK_INVALID = "subtitle_track_invalid"
    SUBTITLE_RANGE_INVALID = "subtitle_range_invalid"
    SUBTITLE_TEXT_INVALID = "subtitle_text_invalid"
    SUBTITLE_LANGUAGE_INVALID = "subtitle_language_invalid"
    SUBTITLE_LAYOUT_INVALID = "subtitle_layout_invalid"
    SUBTITLE_EMPHASIS_INVALID = "subtitle_emphasis_invalid"
    SUBTITLE_OVERLAP_UNSUPPORTED = "subtitle_overlap_unsupported"


@dataclass(frozen=True, slots=True)
class EDLDiagnostic:
    code: EDLDiagnosticCode
    message: str
    segment_ids: tuple[str, ...] = ()
    track_id: str | None = None


@dataclass(frozen=True, slots=True)
class EDLValidationResult:
    diagnostics: tuple[EDLDiagnostic, ...]

    @property
    def is_valid(self) -> bool:
        return not self.diagnostics


def _overlap_findings(segments: tuple[EDLSegment, ...]) -> list[EDLDiagnostic]:
    findings: list[EDLDiagnostic] = []
    by_track: dict[str, list[EDLSegment]] = {}
    for segment in segments:
        by_track.setdefault(segment.track_id, []).append(segment)
    for track_id in sorted(by_track):
        ordered = sorted(
            by_track[track_id],
            key=lambda item: (
                item.timeline_range.start.as_fraction(),
                item.timeline_range.end.as_fraction(),
                item.segment_id,
            ),
        )
        for previous, current in zip(ordered, ordered[1:], strict=False):
            if (
                current.timeline_range.start.as_fraction()
                < previous.timeline_range.end.as_fraction()
            ):
                findings.append(
                    EDLDiagnostic(
                        code=EDLDiagnosticCode.SAME_TRACK_OVERLAP,
                        message="segments on the same track must not overlap",
                        segment_ids=(previous.segment_id, current.segment_id),
                        track_id=track_id,
                    )
                )
    return findings


def validate_edl(edl: EDL) -> EDLValidationResult:
    """Validate locally provable timeline invariants without repairing the EDL."""

    diagnostics: list[EDLDiagnostic] = []
    seen_segments: set[str] = set()
    for segment in edl.segments:
        if segment.segment_id in seen_segments:
            diagnostics.append(
                EDLDiagnostic(
                    code=EDLDiagnosticCode.DUPLICATE_SEGMENT_ID,
                    message="segment_id values must be unique",
                    segment_ids=(segment.segment_id,),
                )
            )
        seen_segments.add(segment.segment_id)

    seen_tracks: set[str] = set()
    for track in edl.effective_tracks:
        if track.track_id in seen_tracks:
            diagnostics.append(
                EDLDiagnostic(
                    code=EDLDiagnosticCode.DUPLICATE_TRACK_ID,
                    message="track_id values must be unique",
                    track_id=track.track_id,
                )
            )
        seen_tracks.add(track.track_id)

    known_tracks = {track.track_id for track in edl.effective_tracks}
    track_families = {track.track_id: track.family for track in edl.effective_tracks}
    for segment in edl.segments:
        if segment.track_id not in known_tracks:
            diagnostics.append(
                EDLDiagnostic(
                    code=EDLDiagnosticCode.UNKNOWN_TRACK,
                    message="segment references an undefined or unsupported track",
                    segment_ids=(segment.segment_id,),
                    track_id=segment.track_id,
                )
            )
        if segment.source_range.duration != segment.timeline_range.duration:
            diagnostics.append(
                EDLDiagnostic(
                    code=EDLDiagnosticCode.DURATION_MISMATCH,
                    message="source and timeline duration must match until rate mapping is typed",
                    segment_ids=(segment.segment_id,),
                    track_id=segment.track_id,
                )
            )
        diagnostics.extend(_automation_findings(segment, track_families.get(segment.track_id)))

    diagnostics.extend(_overlap_findings(edl.segments))
    diagnostics.extend(_subtitle_findings(edl, track_families))
    diagnostics.sort(key=lambda item: (item.code.value, item.track_id or "", item.segment_ids))
    return EDLValidationResult(diagnostics=tuple(diagnostics))


_LANGUAGE = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")


def _cue_diagnostic(cue: EDLSubtitleCue, code: EDLDiagnosticCode, message: str) -> EDLDiagnostic:
    return EDLDiagnostic(code, message, (cue.cue_id,), cue.track_id)


def _subtitle_findings(edl: EDL, track_families: dict[str, EDLTrackFamily]) -> list[EDLDiagnostic]:
    findings: list[EDLDiagnostic] = []
    seen: set[str] = set()
    video_end = max(
        (
            segment.timeline_range.end.as_fraction()
            for segment in edl.segments
            if track_families.get(segment.track_id) is EDLTrackFamily.VIDEO
        ),
        default=None,
    )
    by_track: dict[str, list[EDLSubtitleCue]] = {}
    for cue in edl.subtitle_cues:
        if not cue.cue_id.strip() or (cue.speaker_ref is not None and not cue.speaker_ref.strip()):
            findings.append(
                _cue_diagnostic(
                    cue,
                    EDLDiagnosticCode.SUBTITLE_IDENTITY_INVALID,
                    "cue identity and optional speaker reference must not be empty",
                )
            )
        if cue.cue_id in seen:
            findings.append(
                _cue_diagnostic(
                    cue,
                    EDLDiagnosticCode.DUPLICATE_SUBTITLE_CUE_ID,
                    "subtitle cue IDs must be unique",
                )
            )
        seen.add(cue.cue_id)
        if track_families.get(cue.track_id) is not EDLTrackFamily.SUBTITLE:
            findings.append(
                _cue_diagnostic(
                    cue,
                    EDLDiagnosticCode.SUBTITLE_TRACK_INVALID,
                    "subtitle cues require a defined SUBTITLE track",
                )
            )
        start = cue.timeline_range.start.as_fraction()
        end = cue.timeline_range.end.as_fraction()
        if start < 0 or video_end is None or end > video_end:
            findings.append(
                _cue_diagnostic(
                    cue,
                    EDLDiagnosticCode.SUBTITLE_RANGE_INVALID,
                    "subtitle cue must remain inside the executable VIDEO timeline",
                )
            )
        if not cue.text.strip() or "\x00" in cue.text:
            findings.append(
                _cue_diagnostic(
                    cue,
                    EDLDiagnosticCode.SUBTITLE_TEXT_INVALID,
                    "subtitle text must be non-empty and safe",
                )
            )
        if not _LANGUAGE.fullmatch(cue.language):
            findings.append(
                _cue_diagnostic(
                    cue,
                    EDLDiagnosticCode.SUBTITLE_LANGUAGE_INVALID,
                    "subtitle language must be a bounded BCP-47-style tag",
                )
            )
        if not isinstance(cue.layout, SubtitleLayoutRegion):
            findings.append(
                _cue_diagnostic(
                    cue,
                    EDLDiagnosticCode.SUBTITLE_LAYOUT_INVALID,
                    "subtitle layout intent is unsupported",
                )
            )
        previous_end = -1
        for span in cue.emphasis:
            if (
                not isinstance(span.style, SubtitleEmphasisStyle)
                or span.start < 0
                or span.start >= span.end
                or span.end > len(cue.text)
                or span.start < previous_end
            ):
                findings.append(
                    _cue_diagnostic(
                        cue,
                        EDLDiagnosticCode.SUBTITLE_EMPHASIS_INVALID,
                        "emphasis spans must be ordered, non-overlapping character ranges",
                    )
                )
                break
            previous_end = span.end
        by_track.setdefault(cue.track_id, []).append(cue)
    for track_id, values in by_track.items():
        ordered = sorted(
            values,
            key=lambda cue: (
                cue.timeline_range.start.as_fraction(),
                cue.timeline_range.end.as_fraction(),
                cue.cue_id,
            ),
        )
        for previous, current in zip(ordered, ordered[1:], strict=False):
            if (
                current.timeline_range.start.as_fraction()
                < previous.timeline_range.end.as_fraction()
            ):
                findings.append(
                    EDLDiagnostic(
                        EDLDiagnosticCode.SUBTITLE_OVERLAP_UNSUPPORTED,
                        "overlapping subtitle cues are unsupported by the baseline",
                        (previous.cue_id, current.cue_id),
                        track_id,
                    )
                )
    return findings


def _automation_findings(
    segment: EDLSegment, track_family: EDLTrackFamily | None
) -> list[EDLDiagnostic]:
    findings: list[EDLDiagnostic] = []

    def add(code: EDLDiagnosticCode, message: str) -> None:
        findings.append(
            EDLDiagnostic(
                code=code,
                message=message,
                segment_ids=(segment.segment_id,),
                track_id=segment.track_id,
            )
        )

    spatial = segment.spatial_automation
    if spatial is not None:
        if track_family not in (EDLTrackFamily.VIDEO, EDLTrackFamily.GRAPHICS):
            add(
                EDLDiagnosticCode.AUTOMATION_TRACK_INCOMPATIBLE,
                "spatial automation requires a video or graphics track",
            )
        if not isinstance(spatial.interpolation, EDLInterpolation):
            add(
                EDLDiagnosticCode.AUTOMATION_INTERPOLATION_UNSUPPORTED,
                "spatial automation interpolation is unsupported",
            )
        timeline_times = tuple(item.timeline_time.as_fraction() for item in spatial.keyframes)
        source_times = tuple(item.source_time.as_fraction() for item in spatial.keyframes)
        if not spatial.keyframes or timeline_times != tuple(sorted(set(timeline_times))):
            add(
                EDLDiagnosticCode.AUTOMATION_KEYFRAME_ORDER,
                "spatial keyframes must be non-empty, unique, and timeline ordered",
            )
        if source_times != tuple(sorted(set(source_times))):
            add(
                EDLDiagnosticCode.AUTOMATION_KEYFRAME_ORDER,
                "spatial source times must be unique and ordered",
            )
        if any(
            item.timeline_time.as_fraction() < segment.timeline_range.start.as_fraction()
            or item.timeline_time.as_fraction() >= segment.timeline_range.end.as_fraction()
            or item.source_time.as_fraction() < segment.source_range.start.as_fraction()
            or item.source_time.as_fraction() >= segment.source_range.end.as_fraction()
            for item in spatial.keyframes
        ):
            add(
                EDLDiagnosticCode.AUTOMATION_KEYFRAME_RANGE,
                "spatial keyframes must stay inside half-open segment mappings",
            )
        if any(
            item.timeline_time.as_fraction() - segment.timeline_range.start.as_fraction()
            != item.source_time.as_fraction() - segment.source_range.start.as_fraction()
            for item in spatial.keyframes
        ):
            add(
                EDLDiagnosticCode.AUTOMATION_TIME_MAPPING_INVALID,
                "spatial source/timeline keyframes must follow the segment mapping",
            )
        if any(
            any(
                isinstance(value, bool) or not isinstance(value, int)
                for value in (
                    item.crop_left,
                    item.crop_top,
                    item.crop_width,
                    item.crop_height,
                )
            )
            or not isinstance(item.scale, ExactRational)
            or not isinstance(item.position_x, ExactRational)
            or not isinstance(item.position_y, ExactRational)
            or item.crop_left < 0
            or item.crop_top < 0
            or item.crop_width <= 0
            or item.crop_height <= 0
            or item.scale.value <= 0
            for item in spatial.keyframes
        ):
            add(
                EDLDiagnosticCode.AUTOMATION_VALUE_INVALID,
                "spatial crop and scale values must be legal",
            )

    audio_families = {
        EDLTrackFamily.SOURCE_AUDIO,
        EDLTrackFamily.BGM,
        EDLTrackFamily.VOICEOVER,
        EDLTrackFamily.SFX,
    }
    for automation in segment.audio_automations:
        if track_family not in audio_families:
            add(
                EDLDiagnosticCode.AUTOMATION_TRACK_INCOMPATIBLE,
                "audio automation requires an audio track",
            )
        if not isinstance(automation.interpolation, EDLInterpolation):
            add(
                EDLDiagnosticCode.AUTOMATION_INTERPOLATION_UNSUPPORTED,
                "audio automation interpolation is unsupported",
            )
        if not isinstance(automation.kind, EDLAudioAutomationKind):
            add(
                EDLDiagnosticCode.AUDIO_KIND_UNSUPPORTED,
                "audio automation kind is unsupported",
            )
        times = tuple(item.timeline_time.as_fraction() for item in automation.keyframes)
        if times != tuple(sorted(set(times))):
            add(
                EDLDiagnosticCode.AUTOMATION_KEYFRAME_ORDER,
                "audio keyframes must be unique and timeline ordered",
            )
        if any(
            item.timeline_time.as_fraction() < segment.timeline_range.start.as_fraction()
            or item.timeline_time.as_fraction() > segment.timeline_range.end.as_fraction()
            for item in automation.keyframes
        ):
            add(
                EDLDiagnosticCode.AUTOMATION_KEYFRAME_RANGE,
                "audio envelope points must stay inside the closed segment envelope",
            )
        if automation.kind is EDLAudioAutomationKind.LOOP:
            loop_range = automation.loop_source_range
            if (
                loop_range is None
                or loop_range.start.as_fraction() < segment.source_range.start.as_fraction()
                or loop_range.end.as_fraction() > segment.source_range.end.as_fraction()
            ):
                add(
                    EDLDiagnosticCode.AUDIO_LOOP_INVALID,
                    "loop automation requires a source range inside the segment mapping",
                )
        elif automation.loop_source_range is not None:
            add(
                EDLDiagnosticCode.AUDIO_LOOP_INVALID,
                "only loop automation may define loop_source_range",
            )
        if automation.kind is not EDLAudioAutomationKind.LOOP and not automation.keyframes:
            add(
                EDLDiagnosticCode.AUTOMATION_KEYFRAME_ORDER,
                "non-loop audio automation requires envelope keyframes",
            )
    return findings

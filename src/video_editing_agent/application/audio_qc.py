from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from video_editing_agent.domain.edl import EDL, EDLAudioAutomationKind, EDLTrackFamily


class AudibleLaneQcCode(StrEnum):
    PASS = "pass"
    INTENTIONAL_SILENCE = "intentional_silence"
    REQUIRED_AUDIBLE_LANE_MISSING = "required_audible_lane_missing"


@dataclass(frozen=True, slots=True)
class AudibleLaneQcResult:
    passed: bool
    code: AudibleLaneQcCode
    audible_segment_ids: tuple[str, ...]
    message: str


def check_audible_lanes(edl: EDL, *, requires_audible_output: bool) -> AudibleLaneQcResult:
    """Check approved canonical structure; PCM inspection remains separate evidence."""

    audible_track_ids = {
        track.track_id
        for track in edl.effective_tracks
        if track.family
        in {
            EDLTrackFamily.SOURCE_AUDIO,
            EDLTrackFamily.BGM,
            EDLTrackFamily.VOICEOVER,
            EDLTrackFamily.SFX,
        }
    }
    segment_ids = tuple(
        segment.segment_id
        for segment in edl.ordered_segments
        if segment.track_id in audible_track_ids
        and not any(
            automation.kind is EDLAudioAutomationKind.MUTE
            and len(automation.keyframes) == 2
            and automation.keyframes[0].timeline_time.as_fraction()
            <= segment.timeline_range.start.as_fraction()
            and automation.keyframes[1].timeline_time.as_fraction()
            >= segment.timeline_range.end.as_fraction()
            for automation in segment.audio_automations
        )
    )
    if segment_ids:
        return AudibleLaneQcResult(
            True, AudibleLaneQcCode.PASS, segment_ids, "canonical EDL has approved audible content"
        )
    if not requires_audible_output:
        return AudibleLaneQcResult(
            True,
            AudibleLaneQcCode.INTENTIONAL_SILENCE,
            (),
            "silent output is explicitly permitted by intent",
        )
    return AudibleLaneQcResult(
        False,
        AudibleLaneQcCode.REQUIRED_AUDIBLE_LANE_MISSING,
        (),
        "non-silent intent has no approved audible lane in the canonical EDL",
    )

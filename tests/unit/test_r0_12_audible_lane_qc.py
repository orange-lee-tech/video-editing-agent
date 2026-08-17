from dataclasses import replace
from datetime import UTC, datetime

from video_editing_agent.application.audio_qc import AudibleLaneQcCode, check_audible_lanes
from video_editing_agent.domain.common.entity import (
    EntityEnvelope,
    EntityRevisionRef,
    EntityStatus,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edl import (
    EDL,
    EDLAudioAutomation,
    EDLAudioAutomationKind,
    EDLAudioKeyframe,
    EDLInterpolation,
    EDLSegment,
    EDLTrack,
    EDLTrackFamily,
)


def _edl(*, audible: bool) -> EDL:
    envelope = EntityEnvelope(
        "edl", 1, "0.2", EntityStatus.VALID, datetime(2026, 8, 17, tzinfo=UTC), "test"
    )
    selected = MediaTimeRange(MediaTime(0, 1), MediaTime(1, 1))
    video = EDLSegment(
        "video:selection",
        EntityRevisionRef("asset", 1),
        source_range=selected,
        timeline_range=selected,
    )
    source = EDLSegment(
        "source-audio:selection",
        EntityRevisionRef("asset", 1),
        source_range=selected,
        timeline_range=selected,
        track_id="source_audio",
    )
    return EDL(
        envelope,
        EntityRevisionRef("plan", 1),
        (video, *((source,) if audible else ())),
        (
            EDLTrack("video", EDLTrackFamily.VIDEO),
            *((EDLTrack("source_audio", EDLTrackFamily.SOURCE_AUDIO),) if audible else ()),
        ),
    )


def test_non_silent_intent_requires_approved_audible_segment() -> None:
    result = check_audible_lanes(_edl(audible=False), requires_audible_output=True)

    assert not result.passed
    assert result.code is AudibleLaneQcCode.REQUIRED_AUDIBLE_LANE_MISSING
    assert result.audible_segment_ids == ()


def test_intentional_silence_and_present_audible_lane_pass() -> None:
    silent = check_audible_lanes(_edl(audible=False), requires_audible_output=False)
    audible = check_audible_lanes(_edl(audible=True), requires_audible_output=True)

    assert silent.passed and silent.code is AudibleLaneQcCode.INTENTIONAL_SILENCE
    assert audible.passed and audible.code is AudibleLaneQcCode.PASS
    assert audible.audible_segment_ids == ("source-audio:selection",)


def test_fully_muted_segment_does_not_satisfy_non_silent_intent() -> None:
    edl = _edl(audible=True)
    mute = EDLAudioAutomation(
        EDLAudioAutomationKind.MUTE,
        EDLInterpolation.LINEAR,
        (
            EDLAudioKeyframe(MediaTime(0, 1), 0, muted=True),
            EDLAudioKeyframe(MediaTime(1, 1), 0, muted=True),
        ),
    )
    segments = tuple(
        replace(item, audio_automations=(mute,)) if item.track_id == "source_audio" else item
        for item in edl.segments
    )

    result = check_audible_lanes(replace(edl, segments=segments), requires_audible_output=True)

    assert not result.passed
    assert result.code is AudibleLaneQcCode.REQUIRED_AUDIBLE_LANE_MISSING

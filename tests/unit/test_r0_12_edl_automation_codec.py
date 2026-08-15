import json
from datetime import UTC, datetime

import pytest

from video_editing_agent.domain.common.entity import (
    EntityEnvelope,
    EntityRevisionRef,
    EntityStatus,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edl import (
    EDL,
    EDL_SCHEMA_VERSION,
    EDLAudioAutomation,
    EDLAudioAutomationKind,
    EDLAudioKeyframe,
    EDLDiagnosticCode,
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


def _envelope() -> EntityEnvelope:
    return EntityEnvelope(
        "edl-automation",
        2,
        "0.2",
        EntityStatus.VALID,
        datetime(2026, 8, 15, 9, 30, tzinfo=UTC),
        "test",
        (EntityRevisionRef("edl-parent", 1),),
    )


def _automated_edl() -> EDL:
    spatial = EDLSpatialAutomation(
        EDLInterpolation.LINEAR,
        (
            EDLSpatialKeyframe(
                MediaTime(5, 24),
                MediaTime(1, 24),
                0,
                0,
                1080,
                1920,
                ExactRational(4, 3),
                ExactRational(1, 3),
                ExactRational(2, 3),
            ),
            EDLSpatialKeyframe(
                MediaTime(11, 24),
                MediaTime(7, 24),
                20,
                0,
                1080,
                1920,
                ExactRational(3, 2),
                ExactRational(2, 3),
                ExactRational(2, 3),
            ),
        ),
    )
    fade = EDLAudioAutomation(
        EDLAudioAutomationKind.FADE,
        EDLInterpolation.LINEAR,
        (
            EDLAudioKeyframe(MediaTime(0, 1), -6000, muted=True),
            EDLAudioKeyframe(MediaTime(2, 1), -1200),
        ),
    )
    loop = EDLAudioAutomation(
        EDLAudioAutomationKind.LOOP,
        EDLInterpolation.HOLD,
        loop_source_range=MediaTimeRange(MediaTime(10, 1), MediaTime(1, 2)),
    )
    return EDL(
        _envelope(),
        EntityRevisionRef("edit-plan", 3),
        (
            EDLSegment(
                "music",
                EntityRevisionRef("asset-music", 1),
                source_range=MediaTimeRange(MediaTime(10, 1), MediaTime(2, 1)),
                timeline_range=MediaTimeRange(MediaTime(0, 1), MediaTime(2, 1)),
                track_id="music",
                audio_mix_decision_ref="mix-7",
                audio_automations=(fade, loop),
            ),
            EDLSegment(
                "picture",
                EntityRevisionRef("asset-video", 4),
                source_range=MediaTimeRange(MediaTime(1, 24), MediaTime(1, 2)),
                timeline_range=MediaTimeRange(MediaTime(5, 24), MediaTime(1, 2)),
                track_id="picture",
                shot_ref=EntityRevisionRef("shot-3", 2),
                spatial_decision_ref="reframe-9",
                spatial_automation=spatial,
            ),
        ),
        (
            EDLTrack("music", EDLTrackFamily.BGM),
            EDLTrack("picture", EDLTrackFamily.VIDEO),
        ),
    )


def test_v2_round_trip_preserves_exact_rational_automation_and_provenance() -> None:
    original = _automated_edl()

    encoded = encode_edl(original)
    decoded = decode_edl(encoded)

    assert decoded == EDL(
        original.envelope,
        original.edit_plan_ref,
        original.ordered_segments,
        original.effective_tracks,
    )
    assert encode_edl(decoded) == encoded
    assert b'"value":1' in encoded and b'"scale":24' in encoded
    picture = decoded.segments[0]
    assert picture.spatial_decision_ref == "reframe-9"
    assert picture.spatial_automation is not None
    assert picture.spatial_automation.keyframes[0].position_x == ExactRational(1, 3)
    assert decoded.segments[1].audio_mix_decision_ref == "mix-7"


def test_serialization_is_independent_of_input_track_and_segment_order() -> None:
    original = _automated_edl()
    reversed_edl = EDL(
        original.envelope,
        original.edit_plan_ref,
        tuple(reversed(original.segments)),
        tuple(reversed(original.tracks)),
    )

    assert encode_edl(reversed_edl) == encode_edl(original)


def test_invalid_spatial_and_audio_automation_return_structured_findings() -> None:
    invalid_spatial = EDLSpatialAutomation(
        EDLInterpolation.HOLD,
        (
            EDLSpatialKeyframe(MediaTime(3, 1), MediaTime(3, 1), -1, 0, 0, 10),
            EDLSpatialKeyframe(MediaTime(1, 1), MediaTime(1, 1), 0, 0, 10, 10),
        ),
    )
    invalid_audio = EDLAudioAutomation(
        EDLAudioAutomationKind.GAIN,
        EDLInterpolation.LINEAR,
        (EDLAudioKeyframe(MediaTime(3, 1), -100),),
    )
    segment = EDLSegment(
        "bad",
        EntityRevisionRef("asset", 1),
        source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(2, 1)),
        timeline_range=MediaTimeRange(MediaTime(0, 1), MediaTime(2, 1)),
        spatial_automation=invalid_spatial,
        audio_automations=(invalid_audio,),
    )
    edl = EDL(
        _envelope(),
        EntityRevisionRef("edit-plan", 1),
        (segment,),
        (EDLTrack("video", EDLTrackFamily.VIDEO),),
    )

    result = validate_edl(edl)

    assert {item.code for item in result.diagnostics} == {
        EDLDiagnosticCode.AUTOMATION_KEYFRAME_ORDER,
        EDLDiagnosticCode.AUTOMATION_KEYFRAME_RANGE,
        EDLDiagnosticCode.AUTOMATION_TRACK_INCOMPATIBLE,
        EDLDiagnosticCode.AUTOMATION_VALUE_INVALID,
    }
    with pytest.raises(ValueError, match="cannot serialize invalid EDL"):
        encode_edl(edl)


def test_codec_fails_closed_for_unknown_or_ambiguous_schema() -> None:
    payload = json.loads(encode_edl(_automated_edl()))
    payload["schema_version"] = "future-edl-v99"

    with pytest.raises(ValueError, match="unsupported EDL artifact schema"):
        decode_edl(json.dumps(payload).encode())

    del payload["schema_version"]
    with pytest.raises(ValueError, match="unsupported EDL artifact schema"):
        decode_edl(json.dumps(payload).encode())


def test_spatial_source_and_timeline_times_must_follow_segment_mapping() -> None:
    segment = EDLSegment(
        "bad-mapping",
        EntityRevisionRef("asset", 1),
        source_range=MediaTimeRange(MediaTime(10, 1), MediaTime(2, 1)),
        timeline_range=MediaTimeRange(MediaTime(4, 1), MediaTime(2, 1)),
        spatial_automation=EDLSpatialAutomation(
            EDLInterpolation.HOLD,
            (EDLSpatialKeyframe(MediaTime(5, 1), MediaTime(10, 1), 0, 0, 10, 10),),
        ),
    )
    edl = EDL(
        _envelope(),
        EntityRevisionRef("edit-plan", 1),
        (segment,),
        (EDLTrack("video", EDLTrackFamily.VIDEO),),
    )

    assert EDLDiagnosticCode.AUTOMATION_TIME_MAPPING_INVALID in {
        item.code for item in validate_edl(edl).diagnostics
    }


def test_codec_declares_explicit_v2_schema() -> None:
    assert json.loads(encode_edl(_automated_edl()))["schema_version"] == EDL_SCHEMA_VERSION

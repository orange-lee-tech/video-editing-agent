from __future__ import annotations

import json
from datetime import UTC, datetime

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
        "edl-automation-probe",
        1,
        "0.2",
        EntityStatus.VALID,
        datetime(2026, 8, 15, tzinfo=UTC),
        "r0.12-engineering-probe",
    )


def main() -> int:
    spatial = EDLSpatialAutomation(
        EDLInterpolation.LINEAR,
        (
            EDLSpatialKeyframe(
                MediaTime(1, 24),
                MediaTime(5, 24),
                0,
                0,
                1080,
                1920,
                position_x=ExactRational(1, 3),
            ),
            EDLSpatialKeyframe(
                MediaTime(12, 24),
                MediaTime(16, 24),
                24,
                0,
                1080,
                1920,
                position_x=ExactRational(2, 3),
            ),
        ),
    )
    audio = EDLAudioAutomation(
        EDLAudioAutomationKind.FADE,
        EDLInterpolation.LINEAR,
        (
            EDLAudioKeyframe(MediaTime(0, 1), -6000, True),
            EDLAudioKeyframe(MediaTime(1, 1), -1200),
        ),
    )
    edl = EDL(
        _envelope(),
        EntityRevisionRef("edit-plan", 1),
        (
            EDLSegment(
                "music",
                EntityRevisionRef("asset-music", 1),
                source_range=MediaTimeRange(MediaTime(2, 1), MediaTime(1, 1)),
                timeline_range=MediaTimeRange(MediaTime(0, 1), MediaTime(1, 1)),
                track_id="music",
                audio_mix_decision_ref="mix-1",
                audio_automations=(audio,),
            ),
            EDLSegment(
                "picture",
                EntityRevisionRef("asset-video", 1),
                source_range=MediaTimeRange(MediaTime(5, 24), MediaTime(1, 2)),
                timeline_range=MediaTimeRange(MediaTime(1, 24), MediaTime(1, 2)),
                track_id="picture",
                spatial_decision_ref="reframe-1",
                spatial_automation=spatial,
            ),
        ),
        (
            EDLTrack("music", EDLTrackFamily.BGM),
            EDLTrack("picture", EDLTrackFamily.VIDEO),
        ),
    )
    encoded = encode_edl(edl)
    decoded = decode_edl(encoded)
    invalid = EDL(
        _envelope(),
        EntityRevisionRef("edit-plan", 1),
        (
            EDLSegment(
                "bad",
                EntityRevisionRef("asset", 1),
                source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(1, 1)),
                timeline_range=MediaTimeRange(MediaTime(0, 1), MediaTime(1, 1)),
                track_id="music",
                spatial_automation=spatial,
            ),
        ),
        (EDLTrack("music", EDLTrackFamily.BGM),),
    )
    invalid_result = validate_edl(invalid)
    gates = {
        "EXACT_V2_ROUND_TRIP": encode_edl(decoded) == encoded,
        "RATIONAL_TIME_PRESERVED": decoded.segments[0].spatial_automation is not None
        and decoded.segments[0].spatial_automation.keyframes[0].timeline_time == MediaTime(1, 24),
        "SPATIAL_PROVENANCE_PRESERVED": decoded.segments[0].spatial_decision_ref == "reframe-1",
        "AUDIO_PROVENANCE_PRESERVED": decoded.segments[1].audio_mix_decision_ref == "mix-1",
        "INVALID_AUTOMATION_STRUCTURED": not invalid_result.is_valid
        and "automation_track_incompatible"
        in {item.code.value for item in invalid_result.diagnostics},
    }
    report = {
        "classification": "ENGINEERING_FOUNDATION_ONLY",
        "gates": {name: "PASS" if passed else "FAIL" for name, passed in gates.items()},
        "serialized_bytes": len(encoded),
        "pass": all(gates.values()),
    }
    print(json.dumps(report, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

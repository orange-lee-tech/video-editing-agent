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
    EDLSegment,
    EDLTrack,
    EDLTrackFamily,
    validate_edl,
)


def _segment(identity: str, track_id: str, start: int) -> EDLSegment:
    return EDLSegment(
        identity,
        EntityRevisionRef(f"asset-{identity}", 1),
        source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(2, 1)),
        timeline_range=MediaTimeRange(MediaTime(start, 1), MediaTime(2, 1)),
        track_id=track_id,
    )


def _edl(segments: tuple[EDLSegment, ...], tracks: tuple[EDLTrack, ...]) -> EDL:
    return EDL(
        EntityEnvelope(
            id="edl-probe",
            revision=1,
            schema_version="0.2",
            status=EntityStatus.VALID,
            created_at=datetime(2026, 8, 15, tzinfo=UTC),
            created_by="r0.12-engineering-probe",
        ),
        EntityRevisionRef("edit-plan-probe", 1),
        segments,
        tracks,
    )


def main() -> int:
    tracks = (
        EDLTrack("captions", EDLTrackFamily.SUBTITLE),
        EDLTrack("music", EDLTrackFamily.BGM),
        EDLTrack("picture", EDLTrackFamily.VIDEO),
    )
    valid = _edl(
        (
            _segment("caption", "captions", 0),
            _segment("music", "music", 0),
            _segment("picture", "picture", 0),
        ),
        tracks,
    )
    invalid = _edl(
        (
            _segment("picture-a", "picture", 0),
            _segment("picture-b", "picture", 1),
            _segment("orphan", "unknown", 0),
        ),
        tracks,
    )
    valid_result = validate_edl(valid)
    invalid_result = validate_edl(invalid)
    gates = {
        "KNOWN_MULTITRACK_VALID": valid_result.is_valid,
        "DETERMINISTIC_TRACK_ORDER": tuple(track.track_id for track in valid.effective_tracks)
        == ("picture", "music", "captions"),
        "DETERMINISTIC_SEGMENT_ORDER": tuple(
            segment.segment_id for segment in valid.ordered_segments
        )
        == ("picture", "music", "caption"),
        "INVALID_TIMELINE_REFUSED": not invalid_result.is_valid,
        "STRUCTURED_FINDINGS": {item.code.value for item in invalid_result.diagnostics}
        == {"same_track_overlap", "unknown_track"},
    }
    report = {
        "classification": "ENGINEERING_FOUNDATION_ONLY",
        "gates": {name: "PASS" if passed else "FAIL" for name, passed in gates.items()},
        "invalid_diagnostics": [
            {
                "code": item.code.value,
                "track_id": item.track_id,
                "segment_ids": item.segment_ids,
            }
            for item in invalid_result.diagnostics
        ],
        "pass": all(gates.values()),
    }
    print(json.dumps(report, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

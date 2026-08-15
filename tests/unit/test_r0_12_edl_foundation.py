from datetime import UTC, datetime

from video_editing_agent.domain.common.entity import (
    EntityEnvelope,
    EntityRevisionRef,
    EntityStatus,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edl import (
    EDL,
    EDLDiagnosticCode,
    EDLSegment,
    EDLTrack,
    EDLTrackFamily,
    validate_edl,
)


def _envelope() -> EntityEnvelope:
    return EntityEnvelope(
        id="edl-test",
        revision=1,
        schema_version="0.2",
        status=EntityStatus.VALID,
        created_at=datetime(2026, 8, 15, tzinfo=UTC),
        created_by="test",
    )


def _segment(
    identity: str,
    track_id: str,
    timeline_start: int,
    *,
    duration: int = 2,
    source_duration: int | None = None,
) -> EDLSegment:
    return EDLSegment(
        identity,
        EntityRevisionRef(f"asset-{identity}", 1),
        source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(source_duration or duration, 1)),
        timeline_range=MediaTimeRange(MediaTime(timeline_start, 1), MediaTime(duration, 1)),
        track_id=track_id,
    )


def _edl(segments: tuple[EDLSegment, ...], *, tracks: tuple[EDLTrack, ...] = ()) -> EDL:
    return EDL(_envelope(), EntityRevisionRef("edit-plan", 1), segments, tracks)


def test_known_multitrack_edl_has_explicit_deterministic_composition_order() -> None:
    tracks = (
        EDLTrack("captions", EDLTrackFamily.SUBTITLE),
        EDLTrack("picture", EDLTrackFamily.VIDEO),
        EDLTrack("music", EDLTrackFamily.BGM),
    )
    edl = _edl(
        (
            _segment("caption", "captions", 0),
            _segment("music", "music", 0),
            _segment("picture", "picture", 0),
        ),
        tracks=tracks,
    )

    assert validate_edl(edl).is_valid
    assert tuple(track.track_id for track in edl.effective_tracks) == (
        "picture",
        "music",
        "captions",
    )
    assert tuple(segment.segment_id for segment in edl.ordered_segments) == (
        "picture",
        "music",
        "caption",
    )


def test_input_order_does_not_change_track_or_segment_order() -> None:
    tracks = (
        EDLTrack("video-high", EDLTrackFamily.VIDEO, layer=1),
        EDLTrack("video-base", EDLTrackFamily.VIDEO),
    )
    segments = (_segment("later", "video-base", 2), _segment("first", "video-base", 0))

    forward = _edl(segments, tracks=tracks)
    reverse = _edl(tuple(reversed(segments)), tracks=tuple(reversed(tracks)))

    assert forward.effective_tracks == reverse.effective_tracks
    assert forward.ordered_segments == reverse.ordered_segments


def test_v01_builtin_track_id_migrates_without_losing_rational_time() -> None:
    segment = EDLSegment(
        "legacy",
        EntityRevisionRef("asset", 1),
        source_range=MediaTimeRange(MediaTime(1, 24), MediaTime(1, 2)),
        timeline_range=MediaTimeRange(MediaTime(7, 24), MediaTime(1, 2)),
    )
    edl = _edl((segment,))

    assert edl.effective_tracks == (EDLTrack("video", EDLTrackFamily.VIDEO),)
    assert validate_edl(edl).is_valid
    assert edl.segments[0].source_range.start == MediaTime(1, 24)


def test_invalid_timeline_returns_stable_structured_diagnostics() -> None:
    duplicate = _segment("duplicate", "picture", 0)
    edl = _edl(
        (
            duplicate,
            duplicate,
            _segment("overlap", "picture", 1),
            _segment("unknown", "mystery", 0, source_duration=3),
        ),
        tracks=(
            EDLTrack("picture", EDLTrackFamily.VIDEO),
            EDLTrack("picture", EDLTrackFamily.VIDEO),
        ),
    )

    result = validate_edl(edl)

    assert not result.is_valid
    assert {item.code for item in result.diagnostics} == {
        EDLDiagnosticCode.DUPLICATE_SEGMENT_ID,
        EDLDiagnosticCode.DUPLICATE_TRACK_ID,
        EDLDiagnosticCode.UNKNOWN_TRACK,
        EDLDiagnosticCode.DURATION_MISMATCH,
        EDLDiagnosticCode.SAME_TRACK_OVERLAP,
    }
    assert result == validate_edl(edl)


def test_half_open_adjacent_segments_do_not_overlap() -> None:
    edl = _edl((_segment("first", "video", 0), _segment("second", "video", 2)))

    assert validate_edl(edl).is_valid

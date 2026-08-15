from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTimeRange


class EDLTrackFamily(StrEnum):
    VIDEO = "video"
    SOURCE_AUDIO = "source_audio"
    BGM = "bgm"
    VOICEOVER = "voiceover"
    SFX = "sfx"
    SUBTITLE = "subtitle"
    GRAPHICS = "graphics"


_TRACK_FAMILY_ORDER = {
    EDLTrackFamily.VIDEO: 0,
    EDLTrackFamily.SOURCE_AUDIO: 1,
    EDLTrackFamily.BGM: 2,
    EDLTrackFamily.VOICEOVER: 3,
    EDLTrackFamily.SFX: 4,
    EDLTrackFamily.SUBTITLE: 5,
    EDLTrackFamily.GRAPHICS: 6,
}


@dataclass(frozen=True, slots=True)
class EDLTrack:
    """A typed composition lane; lower family/layer values compose first."""

    track_id: str
    family: EDLTrackFamily
    layer: int = 0

    def __post_init__(self) -> None:
        if not self.track_id.strip():
            raise ValueError("track_id must not be empty")
        if not isinstance(self.family, EDLTrackFamily):
            raise TypeError("family must be an EDLTrackFamily")
        if self.layer < 0:
            raise ValueError("track layer must be >= 0")

    @property
    def composition_key(self) -> tuple[int, int, str]:
        return (_TRACK_FAMILY_ORDER[self.family], self.layer, self.track_id)


def legacy_track(track_id: str) -> EDLTrack | None:
    """Map the v0.1 built-in track identifiers without guessing custom semantics."""

    normalized = track_id.casefold()
    aliases = {
        "video": EDLTrackFamily.VIDEO,
        "source_audio": EDLTrackFamily.SOURCE_AUDIO,
        "bgm": EDLTrackFamily.BGM,
        "voiceover": EDLTrackFamily.VOICEOVER,
        "sfx": EDLTrackFamily.SFX,
        "subtitle": EDLTrackFamily.SUBTITLE,
        "title": EDLTrackFamily.GRAPHICS,
        "overlay": EDLTrackFamily.GRAPHICS,
        "graphics": EDLTrackFamily.GRAPHICS,
    }
    family = aliases.get(normalized)
    if family is None:
        return None
    return EDLTrack(track_id=track_id, family=family)


def _resolve_range(
    *,
    explicit: MediaTimeRange | None,
    start_ms: int | None,
    end_ms: int | None,
    name: str,
) -> MediaTimeRange:
    if explicit is not None:
        if start_ms is not None or end_ms is not None:
            raise ValueError(f"provide {name} or legacy millisecond bounds, not both")
        return explicit
    if start_ms is None or end_ms is None:
        raise ValueError(f"{name} or both legacy millisecond bounds are required")
    return MediaTimeRange.from_milliseconds(start_ms, end_ms)


@dataclass(frozen=True, slots=True, init=False)
class EDLSegment:
    segment_id: str
    asset_ref: EntityRevisionRef
    source_range: MediaTimeRange
    timeline_range: MediaTimeRange
    track_id: str
    shot_ref: EntityRevisionRef | None
    spatial_decision_ref: str | None
    audio_mix_decision_ref: str | None

    def __init__(
        self,
        segment_id: str,
        asset_ref: EntityRevisionRef,
        source_in_ms: int | None = None,
        source_out_ms: int | None = None,
        timeline_in_ms: int | None = None,
        timeline_out_ms: int | None = None,
        *,
        source_range: MediaTimeRange | None = None,
        timeline_range: MediaTimeRange | None = None,
        track_id: str = "video",
        shot_ref: EntityRevisionRef | None = None,
        spatial_decision_ref: str | None = None,
        audio_mix_decision_ref: str | None = None,
    ) -> None:
        if not segment_id.strip():
            raise ValueError("segment_id must not be empty")
        if not track_id.strip():
            raise ValueError("track_id must not be empty")
        resolved_source = _resolve_range(
            explicit=source_range,
            start_ms=source_in_ms,
            end_ms=source_out_ms,
            name="source_range",
        )
        resolved_timeline = _resolve_range(
            explicit=timeline_range,
            start_ms=timeline_in_ms,
            end_ms=timeline_out_ms,
            name="timeline_range",
        )
        if resolved_source.start.as_fraction() < 0:
            raise ValueError("source_range must start at >= 0")
        if resolved_timeline.start.as_fraction() < 0:
            raise ValueError("timeline_range must start at >= 0")

        object.__setattr__(self, "segment_id", segment_id)
        object.__setattr__(self, "asset_ref", asset_ref)
        object.__setattr__(self, "source_range", resolved_source)
        object.__setattr__(self, "timeline_range", resolved_timeline)
        object.__setattr__(self, "track_id", track_id)
        object.__setattr__(self, "shot_ref", shot_ref)
        object.__setattr__(self, "spatial_decision_ref", spatial_decision_ref)
        object.__setattr__(self, "audio_mix_decision_ref", audio_mix_decision_ref)

    @property
    def source_in_ms(self) -> int:
        return self.source_range.start.to_milliseconds_exact()

    @property
    def source_out_ms(self) -> int:
        return self.source_range.end.to_milliseconds_exact()

    @property
    def timeline_in_ms(self) -> int:
        return self.timeline_range.start.to_milliseconds_exact()

    @property
    def timeline_out_ms(self) -> int:
        return self.timeline_range.end.to_milliseconds_exact()


@dataclass(frozen=True, slots=True)
class EDL:
    envelope: EntityEnvelope
    edit_plan_ref: EntityRevisionRef
    segments: tuple[EDLSegment, ...]
    tracks: tuple[EDLTrack, ...] = ()

    @property
    def effective_tracks(self) -> tuple[EDLTrack, ...]:
        """Return explicit v0.2 tracks or the safe built-in v0.1 migration view."""

        if self.tracks:
            return tuple(sorted(self.tracks, key=lambda track: track.composition_key))
        migrated = {
            track.track_id: track
            for segment in self.segments
            if (track := legacy_track(segment.track_id)) is not None
        }
        return tuple(sorted(migrated.values(), key=lambda track: track.composition_key))

    @property
    def ordered_segments(self) -> tuple[EDLSegment, ...]:
        track_order = {track.track_id: index for index, track in enumerate(self.effective_tracks)}
        return tuple(
            sorted(
                self.segments,
                key=lambda segment: (
                    track_order.get(segment.track_id, len(track_order)),
                    segment.timeline_range.start.as_fraction(),
                    segment.timeline_range.end.as_fraction(),
                    segment.segment_id,
                ),
            )
        )

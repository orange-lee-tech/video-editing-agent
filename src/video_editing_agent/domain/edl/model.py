from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTimeRange


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

    def __post_init__(self) -> None:
        segment_ids = tuple(segment.segment_id for segment in self.segments)
        if len(segment_ids) != len(set(segment_ids)):
            raise ValueError("EDL segment_id values must be unique")

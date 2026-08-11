from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTimeRange


def _resolve_source_range(
    *,
    source_range: MediaTimeRange | None,
    source_start_ms: int | None,
    source_end_ms: int | None,
) -> MediaTimeRange:
    if source_range is not None:
        if source_start_ms is not None or source_end_ms is not None:
            raise ValueError("provide source_range or legacy millisecond bounds, not both")
        return source_range
    if source_start_ms is None or source_end_ms is None:
        raise ValueError("source_range or both legacy millisecond bounds are required")
    return MediaTimeRange.from_milliseconds(source_start_ms, source_end_ms)


@dataclass(frozen=True, slots=True, init=False)
class Shot:
    envelope: EntityEnvelope
    asset_ref: EntityRevisionRef
    source_range: MediaTimeRange
    boundary_method: str
    previous_shot_ref: EntityRevisionRef | None
    next_shot_ref: EntityRevisionRef | None
    scene_ref: EntityRevisionRef | None

    def __init__(
        self,
        envelope: EntityEnvelope,
        asset_ref: EntityRevisionRef,
        source_start_ms: int | None = None,
        source_end_ms: int | None = None,
        boundary_method: str = "",
        previous_shot_ref: EntityRevisionRef | None = None,
        next_shot_ref: EntityRevisionRef | None = None,
        scene_ref: EntityRevisionRef | None = None,
        *,
        source_range: MediaTimeRange | None = None,
    ) -> None:
        resolved_range = _resolve_source_range(
            source_range=source_range,
            source_start_ms=source_start_ms,
            source_end_ms=source_end_ms,
        )
        if resolved_range.start.as_fraction() < 0:
            raise ValueError("source range start must be >= 0")
        if not boundary_method.strip():
            raise ValueError("boundary_method must not be empty")

        object.__setattr__(self, "envelope", envelope)
        object.__setattr__(self, "asset_ref", asset_ref)
        object.__setattr__(self, "source_range", resolved_range)
        object.__setattr__(self, "boundary_method", boundary_method)
        object.__setattr__(self, "previous_shot_ref", previous_shot_ref)
        object.__setattr__(self, "next_shot_ref", next_shot_ref)
        object.__setattr__(self, "scene_ref", scene_ref)

    @property
    def source_start_ms(self) -> int:
        """Legacy exact-ms adapter. Raises when the canonical time is sub-millisecond."""

        return self.source_range.start.to_milliseconds_exact()

    @property
    def source_end_ms(self) -> int:
        """Legacy exact-ms adapter. Raises when the canonical time is sub-millisecond."""

        return self.source_range.end.to_milliseconds_exact()

    @property
    def duration_ms(self) -> int:
        """Legacy exact-ms adapter. Raises when the canonical duration is sub-millisecond."""

        return self.source_range.duration.to_milliseconds_exact()

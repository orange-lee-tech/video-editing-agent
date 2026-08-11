from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTimeRange


def _validate_optional_duration(name: str, value: int | None) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int or None")
    if value < 0:
        raise ValueError(f"{name} must be >= 0")


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


@dataclass(frozen=True, slots=True)
class ShotDetectionOptions:
    """Model-agnostic shot-duration policy supplied by the application layer."""

    min_shot_duration_ms: int | None = None
    max_shot_duration_ms: int | None = None

    def __post_init__(self) -> None:
        _validate_optional_duration("min_shot_duration_ms", self.min_shot_duration_ms)
        _validate_optional_duration("max_shot_duration_ms", self.max_shot_duration_ms)

        min_ms = self.min_shot_duration_ms or None
        max_ms = self.max_shot_duration_ms or None
        if min_ms is not None and max_ms is not None and min_ms > max_ms:
            raise ValueError("min_shot_duration_ms cannot exceed max_shot_duration_ms")


@dataclass(frozen=True, slots=True, init=False)
class ShotBoundaryProposal:
    """Detector proposal with canonical exact source time; it is not Shot identity."""

    asset_ref: EntityRevisionRef
    source_range: MediaTimeRange
    detection_method: str
    confidence: float | None

    def __init__(
        self,
        asset_ref: EntityRevisionRef,
        source_start_ms: int | None = None,
        source_end_ms: int | None = None,
        detection_method: str = "",
        confidence: float | None = None,
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
        if not detection_method.strip():
            raise ValueError("detection_method must not be empty")
        if confidence is not None:
            if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
                raise TypeError("confidence must be a number or None")
            if not 0.0 <= float(confidence) <= 1.0:
                raise ValueError("confidence must be between 0 and 1")

        object.__setattr__(self, "asset_ref", asset_ref)
        object.__setattr__(self, "source_range", resolved_range)
        object.__setattr__(self, "detection_method", detection_method)
        object.__setattr__(self, "confidence", None if confidence is None else float(confidence))

    @property
    def source_start_ms(self) -> int:
        return self.source_range.start.to_milliseconds_exact()

    @property
    def source_end_ms(self) -> int:
        return self.source_range.end.to_milliseconds_exact()


class ShotDetector(Protocol):
    """Capability port for proposing shot boundaries from an existing Asset revision."""

    def detect(
        self,
        asset_ref: EntityRevisionRef,
        options: ShotDetectionOptions,
    ) -> tuple[ShotBoundaryProposal, ...]: ...

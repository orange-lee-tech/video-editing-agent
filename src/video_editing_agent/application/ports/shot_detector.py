from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef


def _validate_optional_duration(name: str, value: int | None) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int or None")
    if value < 0:
        raise ValueError(f"{name} must be >= 0")


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


@dataclass(frozen=True, slots=True)
class ShotBoundaryProposal:
    """A detector-owned boundary proposal that has not yet become Shot identity."""

    asset_ref: EntityRevisionRef
    source_start_ms: int
    source_end_ms: int
    detection_method: str
    confidence: float | None = None

    def __post_init__(self) -> None:
        if isinstance(self.source_start_ms, bool) or not isinstance(self.source_start_ms, int):
            raise TypeError("source_start_ms must be an int")
        if isinstance(self.source_end_ms, bool) or not isinstance(self.source_end_ms, int):
            raise TypeError("source_end_ms must be an int")
        if self.source_start_ms < 0:
            raise ValueError("source_start_ms must be >= 0")
        if self.source_end_ms <= self.source_start_ms:
            raise ValueError("source_end_ms must be greater than source_start_ms")
        if not self.detection_method.strip():
            raise ValueError("detection_method must not be empty")

        if self.confidence is not None:
            if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
                raise TypeError("confidence must be a number or None")
            if not 0.0 <= float(self.confidence) <= 1.0:
                raise ValueError("confidence must be between 0 and 1")


class ShotDetector(Protocol):
    """Capability port for proposing shot boundaries from an existing Asset revision."""

    def detect(
        self,
        asset_ref: EntityRevisionRef,
        options: ShotDetectionOptions,
    ) -> tuple[ShotBoundaryProposal, ...]: ...

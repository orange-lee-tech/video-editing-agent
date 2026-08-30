from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.application.ports.artifact_store import StoredArtifactRef
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.shot.analysis import AnalysisProfile


class VisualProviderError(RuntimeError):
    """Base error for a visual-understanding provider adapter."""


class VisualProviderTransientError(VisualProviderError):
    """A provider failure that may succeed when the same request is retried."""

    def __init__(self, message: str, *, retry_after_seconds: float | None = None) -> None:
        super().__init__(message)
        if retry_after_seconds is not None:
            if isinstance(retry_after_seconds, bool) or not isinstance(
                retry_after_seconds, (int, float)
            ):
                raise TypeError("retry_after_seconds must be a number or null")
            delay = float(retry_after_seconds)
            if not math.isfinite(delay) or delay < 0:
                raise ValueError("retry_after_seconds must be finite and >= 0")
            retry_after_seconds = delay
        self.retry_after_seconds = retry_after_seconds


class VisualProviderResponseError(VisualProviderError):
    """A non-retryable provider response/schema failure."""


class VisualProviderQuotaError(VisualProviderError):
    """A provider quota that automatic short-term retries cannot safely resolve."""

    def __init__(
        self,
        message: str,
        *,
        quota_ids: tuple[str, ...] = (),
        retry_after_seconds: float | None = None,
    ) -> None:
        super().__init__(message)
        self.quota_ids = quota_ids
        self.retry_after_seconds = retry_after_seconds


@dataclass(frozen=True, slots=True, init=False)
class VisualFrameReference:
    artifact_ref: StoredArtifactRef
    ordinal: int
    source_timestamp: MediaTime

    def __init__(
        self,
        artifact_ref: StoredArtifactRef,
        ordinal: int,
        source_timestamp_ms: int | None = None,
        *,
        source_timestamp: MediaTime | None = None,
    ) -> None:
        if source_timestamp is not None:
            if source_timestamp_ms is not None:
                raise ValueError("provide source_timestamp or source_timestamp_ms, not both")
            resolved_timestamp = source_timestamp
        else:
            if source_timestamp_ms is None:
                raise ValueError("source_timestamp or source_timestamp_ms is required")
            resolved_timestamp = MediaTime.from_milliseconds(source_timestamp_ms)

        if not artifact_ref.media_type.startswith("image/"):
            raise ValueError("visual frame artifact must use an image/* media type")
        if isinstance(ordinal, bool) or not isinstance(ordinal, int):
            raise TypeError("ordinal must be an int")
        if ordinal < 0:
            raise ValueError("ordinal must be >= 0")
        if resolved_timestamp.as_fraction() < 0:
            raise ValueError("source_timestamp must be >= 0")

        object.__setattr__(self, "artifact_ref", artifact_ref)
        object.__setattr__(self, "ordinal", ordinal)
        object.__setattr__(self, "source_timestamp", resolved_timestamp)

    @property
    def source_timestamp_ms(self) -> int:
        return self.source_timestamp.to_milliseconds_exact()


@dataclass(frozen=True, slots=True)
class VisualUnderstandingRequest:
    shot_ref: EntityRevisionRef
    profile: AnalysisProfile
    frames: tuple[VisualFrameReference, ...]

    def __post_init__(self) -> None:
        if not self.frames:
            raise ValueError("visual understanding requires at least one frame")
        if tuple(frame.ordinal for frame in self.frames) != tuple(range(len(self.frames))):
            raise ValueError("visual frame ordinals must be contiguous from zero")
        timestamps = tuple(frame.source_timestamp.as_fraction() for frame in self.frames)
        if timestamps != tuple(sorted(set(timestamps))):
            raise ValueError("visual frame timestamps must be unique and increasing")


@dataclass(frozen=True, slots=True)
class VisualQualityScoreProposal:
    """Provider-proposed normalized visual-quality dimension."""

    name: str
    value: float

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("visual quality score name must not be empty")
        if isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
            raise TypeError("visual quality score value must be a number")
        value = float(self.value)
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError("visual quality score value must be finite and between 0 and 1")


@dataclass(frozen=True, slots=True)
class VisualSemanticsProposal:
    """Provider output only. It is not Domain state until deterministically validated."""

    summary: str | None = None
    tags: tuple[str, ...] = ()
    subjects: tuple[str, ...] = ()
    actions: tuple[str, ...] = ()
    environment: str | None = None
    framing: str | None = None
    camera_motion: str | None = None
    quality_scores: tuple[VisualQualityScoreProposal, ...] = ()


class VisualUnderstandingPort(Protocol):
    def analyze(self, request: VisualUnderstandingRequest) -> VisualSemanticsProposal: ...

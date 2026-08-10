from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.application.ports.artifact_store import StoredArtifactRef
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shot.analysis import AnalysisProfile


class VisualProviderError(RuntimeError):
    """Base error for a visual-understanding provider adapter."""


class VisualProviderTransientError(VisualProviderError):
    """A provider failure that may succeed when the same request is retried."""


class VisualProviderResponseError(VisualProviderError):
    """A non-retryable provider response/schema failure."""


@dataclass(frozen=True, slots=True)
class VisualFrameReference:
    artifact_ref: StoredArtifactRef
    ordinal: int
    source_timestamp_ms: int

    def __post_init__(self) -> None:
        if not self.artifact_ref.media_type.startswith("image/"):
            raise ValueError("visual frame artifact must use an image/* media type")
        if isinstance(self.ordinal, bool) or not isinstance(self.ordinal, int):
            raise TypeError("ordinal must be an int")
        if self.ordinal < 0:
            raise ValueError("ordinal must be >= 0")
        if isinstance(self.source_timestamp_ms, bool) or not isinstance(
            self.source_timestamp_ms, int
        ):
            raise TypeError("source_timestamp_ms must be an int")
        if self.source_timestamp_ms < 0:
            raise ValueError("source_timestamp_ms must be >= 0")


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
        timestamps = tuple(frame.source_timestamp_ms for frame in self.frames)
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

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from video_editing_agent.domain.common.entity import EntityRevisionRef


class AnalysisProfile(StrEnum):
    """Reviewed understanding depth names from Architecture Contract v0.1.2."""

    BASIC = "basic"
    SEMANTIC = "semantic"
    SPEECH = "speech"
    DEEP_VISUAL = "deep_visual"
    EDITORIAL = "editorial"


@dataclass(frozen=True, slots=True)
class NamedQualityScore:
    name: str
    value: float

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("quality score name must not be empty")
        if isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
            raise TypeError("quality score value must be a number")
        normalized = float(self.value)
        if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
            raise ValueError("quality score value must be finite and between 0 and 1")


@dataclass(frozen=True, slots=True)
class VisualSemantics:
    summary: str | None = None
    tags: tuple[str, ...] = ()
    subjects: tuple[str, ...] = ()
    actions: tuple[str, ...] = ()
    environment: str | None = None
    framing: str | None = None
    camera_motion: str | None = None


@dataclass(frozen=True, slots=True)
class SpeechContent:
    transcript: str | None = None
    language: str | None = None


@dataclass(frozen=True, slots=True)
class ShotAnalysisRef:
    shot_ref: EntityRevisionRef
    revision: int

    def __post_init__(self) -> None:
        if isinstance(self.revision, bool) or not isinstance(self.revision, int):
            raise TypeError("analysis revision must be an int")
        if self.revision < 1:
            raise ValueError("analysis revision must be >= 1")


@dataclass(frozen=True, slots=True)
class ShotAnalysis:
    """Derived, revisioned understanding attached to immutable Shot identity."""

    shot_ref: EntityRevisionRef
    revision: int
    profile: AnalysisProfile
    analyzed_at: datetime
    technical_quality: tuple[NamedQualityScore, ...] = ()
    visual: VisualSemantics | None = None
    speech: SpeechContent | None = None
    embedding_ref: str | None = None
    artifact_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        ShotAnalysisRef(self.shot_ref, self.revision)
        if self.embedding_ref is not None and not self.embedding_ref.strip():
            raise ValueError("embedding_ref must not be blank")
        if any(not artifact_ref.strip() for artifact_ref in self.artifact_refs):
            raise ValueError("artifact_refs must not contain blank values")

    @property
    def ref(self) -> ShotAnalysisRef:
        return ShotAnalysisRef(self.shot_ref, self.revision)

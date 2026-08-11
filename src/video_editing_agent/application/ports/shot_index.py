from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.shot.analysis import AnalysisProfile, ShotAnalysis
from video_editing_agent.domain.shot.model import Shot


def _resolve_optional_duration(
    *,
    duration: MediaTime | None,
    duration_ms: int | None,
    name: str,
) -> MediaTime | None:
    if duration is not None:
        if duration_ms is not None:
            raise ValueError(f"provide {name} or legacy {name}_ms, not both")
        resolved = duration
    elif duration_ms is not None:
        if isinstance(duration_ms, bool) or not isinstance(duration_ms, int):
            raise TypeError(f"{name}_ms must be an int or None")
        resolved = MediaTime.from_milliseconds(duration_ms)
    else:
        return None

    if resolved.as_fraction() < 0:
        raise ValueError(f"{name} must be >= 0")
    return resolved


class EmbeddingNormalization(StrEnum):
    NONE = "none"
    L2 = "l2"


@dataclass(frozen=True, slots=True)
class ShotIndexRepresentationDescriptor:
    """Rebuildable retrieval representation provenance, never Shot semantic truth."""

    shot_ref: EntityRevisionRef
    analysis_revision: int
    representation: str
    model_id: str
    model_revision: str
    dimension: int
    normalization: EmbeddingNormalization

    def __post_init__(self) -> None:
        if self.analysis_revision < 1:
            raise ValueError("analysis_revision must be >= 1")
        for name, value in (
            ("representation", self.representation),
            ("model_id", self.model_id),
            ("model_revision", self.model_revision),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        if isinstance(self.dimension, bool) or not isinstance(self.dimension, int):
            raise TypeError("dimension must be an int")
        if self.dimension < 1:
            raise ValueError("dimension must be >= 1")


@dataclass(frozen=True, slots=True)
class ShotIndexSource:
    """Factual Shot + derived analysis pair supplied to non-authoritative retrieval."""

    shot: Shot
    analysis: ShotAnalysis

    def __post_init__(self) -> None:
        shot_ref = EntityRevisionRef(self.shot.envelope.id, self.shot.envelope.revision)
        if self.analysis.shot_ref != shot_ref:
            raise ValueError("ShotAnalysis must reference the exact Shot revision being indexed")


@dataclass(frozen=True, slots=True, init=False)
class ShotSearchConstraints:
    """Retrieval prefilters only; Resolver still owns final eligibility validation."""

    asset_refs: tuple[EntityRevisionRef, ...]
    profiles: tuple[AnalysisProfile, ...]
    min_duration: MediaTime | None
    max_duration: MediaTime | None

    def __init__(
        self,
        asset_refs: tuple[EntityRevisionRef, ...] = (),
        profiles: tuple[AnalysisProfile, ...] = (),
        min_duration_ms: int | None = None,
        max_duration_ms: int | None = None,
        *,
        min_duration: MediaTime | None = None,
        max_duration: MediaTime | None = None,
    ) -> None:
        resolved_min = _resolve_optional_duration(
            duration=min_duration,
            duration_ms=min_duration_ms,
            name="min_duration",
        )
        resolved_max = _resolve_optional_duration(
            duration=max_duration,
            duration_ms=max_duration_ms,
            name="max_duration",
        )
        if (
            resolved_min is not None
            and resolved_max is not None
            and resolved_min.as_fraction() > resolved_max.as_fraction()
        ):
            raise ValueError("min_duration cannot exceed max_duration")

        object.__setattr__(self, "asset_refs", asset_refs)
        object.__setattr__(self, "profiles", profiles)
        object.__setattr__(self, "min_duration", resolved_min)
        object.__setattr__(self, "max_duration", resolved_max)

    @property
    def min_duration_ms(self) -> int | None:
        if self.min_duration is None:
            return None
        return self.min_duration.to_milliseconds_exact()

    @property
    def max_duration_ms(self) -> int | None:
        if self.max_duration is None:
            return None
        return self.max_duration.to_milliseconds_exact()


@dataclass(frozen=True, slots=True)
class ShotCandidate:
    """Derived retrieval result; never a ResolutionDecision or eligibility fact."""

    shot_ref: EntityRevisionRef
    analysis_revision: int
    retrieval_score: float
    matched_terms: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.analysis_revision < 1:
            raise ValueError("analysis_revision must be >= 1")
        if not 0.0 <= self.retrieval_score <= 1.0:
            raise ValueError("retrieval_score must be between 0 and 1")


class ShotIndex(Protocol):
    """Rebuildable retrieval infrastructure over Shot and ShotAnalysis facts."""

    def upsert(self, source: ShotIndexSource) -> None: ...

    def rebuild(self, sources: Iterable[ShotIndexSource]) -> None: ...

    def remove(self, shot_ref: EntityRevisionRef) -> None: ...

    def search(
        self,
        query: str,
        *,
        constraints: ShotSearchConstraints | None = None,
        limit: int = 20,
    ) -> tuple[ShotCandidate, ...]: ...

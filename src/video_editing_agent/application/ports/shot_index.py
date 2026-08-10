from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shot.analysis import AnalysisProfile, ShotAnalysis
from video_editing_agent.domain.shot.model import Shot


def _validate_optional_duration(name: str, value: int | None) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int or None")
    if value < 0:
        raise ValueError(f"{name} must be >= 0")


@dataclass(frozen=True, slots=True)
class ShotIndexSource:
    """Factual Shot + derived analysis pair supplied to non-authoritative retrieval."""

    shot: Shot
    analysis: ShotAnalysis

    def __post_init__(self) -> None:
        shot_ref = EntityRevisionRef(self.shot.envelope.id, self.shot.envelope.revision)
        if self.analysis.shot_ref != shot_ref:
            raise ValueError("ShotAnalysis must reference the exact Shot revision being indexed")


@dataclass(frozen=True, slots=True)
class ShotSearchConstraints:
    """Retrieval prefilters only; Resolver still owns final eligibility validation."""

    asset_refs: tuple[EntityRevisionRef, ...] = ()
    profiles: tuple[AnalysisProfile, ...] = ()
    min_duration_ms: int | None = None
    max_duration_ms: int | None = None

    def __post_init__(self) -> None:
        _validate_optional_duration("min_duration_ms", self.min_duration_ms)
        _validate_optional_duration("max_duration_ms", self.max_duration_ms)
        if (
            self.min_duration_ms is not None
            and self.max_duration_ms is not None
            and self.min_duration_ms > self.max_duration_ms
        ):
            raise ValueError("min_duration_ms cannot exceed max_duration_ms")


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

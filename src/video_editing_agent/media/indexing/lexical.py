from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass

from video_editing_agent.application.ports.shot_index import (
    ShotCandidate,
    ShotIndex,
    ShotIndexSource,
    ShotSearchConstraints,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.shot.analysis import AnalysisProfile

_TOKEN_RUN_PATTERN = re.compile(r"[a-z0-9_]+|[\u3400-\u4dbf\u4e00-\u9fff]+")
MAX_TERM_WEIGHT = 5.0


@dataclass(frozen=True, slots=True)
class _IndexedShot:
    shot_ref: EntityRevisionRef
    asset_ref: EntityRevisionRef
    duration: MediaTime
    analysis_revision: int
    profile: AnalysisProfile
    term_weights: dict[str, float]


def _is_cjk(character: str) -> bool:
    return "\u3400" <= character <= "\u4dbf" or "\u4e00" <= character <= "\u9fff"


def _ordered_unique(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return tuple(result)


def _tokenize(text: str) -> tuple[str, ...]:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    tokens: list[str] = []
    for match in _TOKEN_RUN_PATTERN.finditer(normalized):
        run = match.group(0)
        if not run or not _is_cjk(run[0]):
            tokens.append(run)
            continue

        tokens.append(run)
        tokens.extend(run)
        if len(run) > 1:
            tokens.extend(run[index : index + 2] for index in range(len(run) - 1))
    return _ordered_unique(tokens)


def _add_weighted_text(
    term_weights: dict[str, float],
    text: str | None,
    *,
    weight: float,
) -> None:
    if text is None:
        return
    for term in _tokenize(text):
        term_weights[term] = max(term_weights.get(term, 0.0), weight)


def _build_record(source: ShotIndexSource) -> _IndexedShot:
    term_weights: dict[str, float] = {}
    visual = source.analysis.visual
    if visual is not None:
        _add_weighted_text(term_weights, visual.summary, weight=3.0)
        for value in visual.tags:
            _add_weighted_text(term_weights, value, weight=5.0)
        for value in visual.subjects:
            _add_weighted_text(term_weights, value, weight=5.0)
        for value in visual.actions:
            _add_weighted_text(term_weights, value, weight=5.0)
        _add_weighted_text(term_weights, visual.environment, weight=2.0)
        _add_weighted_text(term_weights, visual.framing, weight=2.0)
        _add_weighted_text(term_weights, visual.camera_motion, weight=2.0)

    speech = source.analysis.speech
    if speech is not None:
        _add_weighted_text(term_weights, speech.transcript, weight=4.0)

    shot_ref = EntityRevisionRef(source.shot.envelope.id, source.shot.envelope.revision)
    return _IndexedShot(
        shot_ref=shot_ref,
        asset_ref=source.shot.asset_ref,
        duration=source.shot.source_range.duration,
        analysis_revision=source.analysis.revision,
        profile=source.analysis.profile,
        term_weights=term_weights,
    )


def _passes_constraints(record: _IndexedShot, constraints: ShotSearchConstraints) -> bool:
    if constraints.asset_refs and record.asset_ref not in constraints.asset_refs:
        return False
    if constraints.profiles and record.profile not in constraints.profiles:
        return False
    duration = record.duration.as_fraction()
    if (
        constraints.min_duration is not None
        and duration < constraints.min_duration.as_fraction()
    ):
        return False
    if (
        constraints.max_duration is not None
        and duration > constraints.max_duration.as_fraction()
    ):
        return False
    return True


class LexicalShotIndex(ShotIndex):
    """Deterministic rebuildable lexical retrieval with no Domain or Resolver authority."""

    def __init__(self) -> None:
        self._records: dict[EntityRevisionRef, _IndexedShot] = {}

    def upsert(self, source: ShotIndexSource) -> None:
        record = _build_record(source)
        existing = self._records.get(record.shot_ref)
        if existing is not None and record.analysis_revision < existing.analysis_revision:
            raise ValueError("cannot replace a newer indexed ShotAnalysis with an older revision")
        self._records[record.shot_ref] = record

    def rebuild(self, sources: Iterable[ShotIndexSource]) -> None:
        rebuilt: dict[EntityRevisionRef, _IndexedShot] = {}
        for source in sources:
            record = _build_record(source)
            existing = rebuilt.get(record.shot_ref)
            if existing is None or record.analysis_revision >= existing.analysis_revision:
                rebuilt[record.shot_ref] = record
        self._records = rebuilt

    def remove(self, shot_ref: EntityRevisionRef) -> None:
        self._records.pop(shot_ref, None)

    def search(
        self,
        query: str,
        *,
        constraints: ShotSearchConstraints | None = None,
        limit: int = 20,
    ) -> tuple[ShotCandidate, ...]:
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError("limit must be an int")
        if limit < 1:
            raise ValueError("limit must be >= 1")

        query_terms = _tokenize(query)
        if not query_terms:
            raise ValueError("query must contain at least one searchable term")
        active_constraints = constraints or ShotSearchConstraints()

        candidates: list[ShotCandidate] = []
        for record in self._records.values():
            if not _passes_constraints(record, active_constraints):
                continue

            matched_terms = tuple(
                term for term in query_terms if record.term_weights.get(term, 0.0) > 0.0
            )
            if not matched_terms:
                continue

            weighted_sum = sum(record.term_weights[term] for term in matched_terms)
            score = min(1.0, weighted_sum / (MAX_TERM_WEIGHT * len(query_terms)))
            candidates.append(
                ShotCandidate(
                    shot_ref=record.shot_ref,
                    analysis_revision=record.analysis_revision,
                    retrieval_score=score,
                    matched_terms=matched_terms,
                )
            )

        candidates.sort(
            key=lambda candidate: (
                -candidate.retrieval_score,
                candidate.shot_ref.entity_id,
                candidate.shot_ref.revision,
            )
        )
        return tuple(candidates[:limit])

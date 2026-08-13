from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.application.ports.shot_index import ShotCandidate
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.shot.model import Shot


@dataclass(frozen=True, slots=True)
class EligibilityDecision:
    shot_ref: EntityRevisionRef
    eligible: bool
    reasons: tuple[str, ...]


def eligible_shots(
    shots: tuple[Shot, ...],
    *,
    minimum_duration: MediaTime,
    excluded: frozenset[EntityRevisionRef] = frozenset(),
) -> tuple[tuple[Shot, ...], tuple[EligibilityDecision, ...]]:
    accepted = []
    decisions = []
    for shot in shots:
        ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
        reasons = []
        if shot.envelope.status.value != "valid":
            reasons.append("not_current_valid")
        if shot.source_range.duration.as_fraction() < minimum_duration.as_fraction():
            reasons.append("insufficient_duration")
        if ref in excluded:
            reasons.append("usage_or_lock_excluded")
        decisions.append(EligibilityDecision(ref, not reasons, tuple(reasons)))
        if not reasons:
            accepted.append(shot)
    return tuple(accepted), tuple(decisions)


@dataclass(frozen=True, slots=True)
class HybridCandidate:
    shot_ref: EntityRevisionRef
    analysis_revision: int
    fused_score: float
    channel_ranks: tuple[tuple[str, int], ...]


def reciprocal_rank_fusion(
    lexical: tuple[ShotCandidate, ...], dense: tuple[ShotCandidate, ...], *, k: int = 60
) -> tuple[HybridCandidate, ...]:
    if k < 1:
        raise ValueError("RRF k must be positive")
    values: dict[EntityRevisionRef, tuple[int, float, list[tuple[str, int]]]] = {}
    for channel, candidates in (("lexical", lexical), ("dense", dense)):
        for rank, candidate in enumerate(candidates, 1):
            revision, score, ranks = values.get(
                candidate.shot_ref, (candidate.analysis_revision, 0.0, [])
            )
            if revision != candidate.analysis_revision:
                raise ValueError("retrieval channels disagree on analysis revision")
            ranks.append((channel, rank))
            values[candidate.shot_ref] = (revision, score + 1 / (k + rank), ranks)
    result = [
        HybridCandidate(ref, revision, score, tuple(ranks))
        for ref, (revision, score, ranks) in values.items()
    ]
    result.sort(key=lambda x: (-x.fused_score, x.shot_ref.entity_id, x.shot_ref.revision))
    return tuple(result)

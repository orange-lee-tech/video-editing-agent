from __future__ import annotations

import hashlib
from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.edit.model import EditPlan
from video_editing_agent.domain.edit.resolution import (
    CandidateWindow,
    ResolutionDecision,
    ResolutionDecisionType,
    ResolvedSelection,
)


@dataclass(frozen=True, slots=True)
class ResolverCandidate:
    window: CandidateWindow
    retrieval_fit: float
    editorial_fit: float
    evidence_quality: float


@dataclass(frozen=True, slots=True)
class ResolverStrategy:
    strategy_version: str = "r0.9b-beam-v1"
    beam_width: int = 8
    top_k_per_slot: int = 5


@dataclass(frozen=True, slots=True)
class _State:
    candidates: tuple[ResolverCandidate, ...]
    score: float
    contributions: tuple[tuple[str, float], ...]
    used: frozenset[EntityRevisionRef]


def _unary(candidate: ResolverCandidate) -> tuple[float, tuple[tuple[str, float], ...]]:
    contributions = (
        ("retrieval_fit", candidate.retrieval_fit * 0.25),
        ("editorial_fit", candidate.editorial_fit * 0.5),
        ("evidence_quality", candidate.evidence_quality * 0.25),
    )
    return sum(x[1] for x in contributions), contributions


def resolve_multiple_selections(
    slot_id: str,
    candidates: tuple[ResolverCandidate, ...],
    *,
    count: int,
    plan_ref: EntityRevisionRef,
) -> ResolutionDecision:
    if count < 1:
        raise ValueError("selection count must be positive")
    ordered = sorted(
        candidates,
        key=lambda x: (-_unary(x)[0], x.window.candidate_id),
    )
    selected = ordered[:count]
    if len(selected) != count:
        return ResolutionDecision(
            f"rdec_{slot_id}",
            plan_ref,
            (slot_id,),
            ResolutionDecisionType.UNRESOLVED,
            reasons=("insufficient legal grounded candidates",),
        )
    selections = tuple(
        ResolvedSelection(
            f"rsel_{slot_id}_{index}",
            item.window.shot_ref,
            item.window.source_range,
            index,
            role="component",
            anchor_refs=tuple(
                x for x in (item.window.in_anchor_ref, item.window.out_anchor_ref) if x
            ),
            evidence_refs=item.window.evidence_refs,
        )
        for index, item in enumerate(selected)
    )
    return ResolutionDecision(
        f"rdec_{slot_id}_multi",
        plan_ref,
        (slot_id,),
        ResolutionDecisionType.RESOLVED,
        selections,
        sum(_unary(x)[0] for x in selected) / count,
        min(x.evidence_quality for x in selected),
        ("explicit multi-selection slot requirement",),
        evidence_refs=tuple(sorted({ref for x in selected for ref in x.window.evidence_refs})),
    )


def optimize_sequence(
    plan: EditPlan,
    candidates_by_slot: dict[str, tuple[ResolverCandidate, ...]],
    *,
    plan_ref: EntityRevisionRef,
    strategy: ResolverStrategy | None = None,
) -> tuple[ResolutionDecision, ...]:
    active_strategy = strategy or ResolverStrategy()
    states: tuple[_State, ...] = (_State((), 0.0, (), frozenset()),)
    unresolved: set[str] = set()
    for slot in plan.slots:
        candidates = candidates_by_slot.get(slot.slot_id, ())[: active_strategy.top_k_per_slot]
        expanded = []
        for state in states:
            for candidate in candidates:
                if not slot.allow_reuse and candidate.window.shot_ref in state.used:
                    continue
                unary, features = _unary(candidate)
                reuse_penalty = -0.2 if candidate.window.shot_ref in state.used else 0.0
                expanded.append(
                    _State(
                        (*state.candidates, candidate),
                        state.score + unary + reuse_penalty,
                        (*state.contributions, *features, ("reuse", reuse_penalty)),
                        state.used | {candidate.window.shot_ref},
                    )
                )
        if not expanded:
            unresolved.add(slot.slot_id)
            continue
        expanded.sort(
            key=lambda x: (
                -x.score,
                tuple(item.window.candidate_id for item in x.candidates),
            )
        )
        states = tuple(expanded[: active_strategy.beam_width])
    best = states[0]
    decisions = []
    selected_by_slot = dict(
        zip(
            (x.slot_id for x in plan.slots if x.slot_id not in unresolved),
            best.candidates,
            strict=True,
        )
    )
    for slot in plan.slots:
        selected: ResolverCandidate | None = selected_by_slot.get(slot.slot_id)
        if selected is None:
            decisions.append(
                ResolutionDecision(
                    f"rdec_{slot.slot_id}",
                    plan_ref,
                    (slot.slot_id,),
                    ResolutionDecisionType.UNRESOLVED,
                    reasons=("no legal grounded candidate",),
                    warnings=("missing evidence or eligibility",),
                )
            )
            continue
        alternatives = tuple(
            x.window.candidate_id
            for x in candidates_by_slot.get(slot.slot_id, ())
            if x.window != selected.window
        )
        score, features = _unary(selected)
        digest = hashlib.sha256(
            f"{plan_ref}:{slot.slot_id}:{selected.window.candidate_id}:{active_strategy.strategy_version}".encode()
        ).hexdigest()
        selection = ResolvedSelection(
            f"rsel_{digest}",
            selected.window.shot_ref,
            selected.window.source_range,
            0,
            anchor_refs=tuple(
                x for x in (selected.window.in_anchor_ref, selected.window.out_anchor_ref) if x
            ),
            evidence_refs=selected.window.evidence_refs,
        )
        decisions.append(
            ResolutionDecision(
                f"rdec_{digest}",
                plan_ref,
                (slot.slot_id,),
                ResolutionDecisionType.RESOLVED,
                (selection,),
                min(1.0, score),
                selected.evidence_quality,
                ("highest deterministic feasible sequence utility",),
                (),
                selected.window.evidence_refs,
                features,
                alternatives,
            )
        )
    return tuple(decisions)

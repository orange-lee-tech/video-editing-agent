from __future__ import annotations

from datetime import UTC, datetime

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.model import DurationConstraint, EditPlan, EditSlot
from video_editing_agent.domain.edit.resolution import CandidateWindow, ResolutionDecisionType
from video_editing_agent.editing.resolver.optimizer import (
    ResolverCandidate,
    optimize_sequence,
    resolve_multiple_selections,
)


def _plan(*slots):
    return EditPlan(
        EntityEnvelope("plan", 1, "0.2", EntityStatus.VALID, datetime.now(UTC), "test"),
        EntityRevisionRef("script", 1),
        EntityRevisionRef("shoot", 1),
        slots,
    )


def _slot(identity, order, reuse=False):
    return EditSlot(
        identity,
        "purpose",
        order,
        "proof",
        "query",
        DurationConstraint(MediaTime(1, 1), MediaTime(2, 1)),
        allow_reuse=reuse,
    )


def _candidate(identity, shot, start, retrieval, editorial):
    window = CandidateWindow(
        identity,
        EntityRevisionRef(shot, 1),
        MediaTimeRange(MediaTime(start, 1), MediaTime(2, 1)),
        0.8,
        "anchor",
        None,
        (),
        ("evidence",),
    )
    return ResolverCandidate(window, retrieval, editorial, 0.8)


def test_editorial_fit_can_beat_retrieval_and_decision_is_inspectable() -> None:
    slot = _slot("one", 0)
    high_rank = _candidate("rank", "a", 0, 1.0, 0.2)
    editorial = _candidate("edit", "b", 2, 0.5, 1.0)
    decision = optimize_sequence(
        _plan(slot), {"one": (high_rank, editorial)}, plan_ref=EntityRevisionRef("plan", 1)
    )[0]
    assert decision.selections[0].shot_ref.entity_id == "b"
    assert decision.score != decision.confidence and decision.feature_contributions
    assert decision.alternative_candidate_ids == ("rank",)


def test_reuse_policy_unresolved_and_determinism() -> None:
    slots = (_slot("one", 0), _slot("two", 1))
    candidate = _candidate("same", "a", 0, 1, 1)
    args = (_plan(*slots), {"one": (candidate,), "two": (candidate,)})
    first = optimize_sequence(*args, plan_ref=EntityRevisionRef("plan", 1))
    assert first == optimize_sequence(*args, plan_ref=EntityRevisionRef("plan", 1))
    assert first[1].decision_type is ResolutionDecisionType.UNRESOLVED


def test_explicit_slot_can_resolve_to_multiple_grounded_selections() -> None:
    decision = resolve_multiple_selections(
        "montage",
        (_candidate("a", "a", 0, 1, 1), _candidate("b", "b", 3, 0.9, 0.9)),
        count=2,
        plan_ref=EntityRevisionRef("plan", 1),
    )
    assert len(decision.selections) == 2
    assert tuple(x.order for x in decision.selections) == (0, 1)


def test_planning_context_does_not_change_resolution_authority() -> None:
    slot = _slot("one", 0)
    envelope = EntityEnvelope(
        "plan",
        1,
        "0.2",
        EntityStatus.VALID,
        datetime.now(UTC),
        "test",
    )
    brief_ref = EntityRevisionRef("brief", 1)
    editing_only = EditPlan(
        envelope,
        None,
        None,
        (slot,),
        brief_ref=brief_ref,
    )
    combined = EditPlan(
        envelope,
        EntityRevisionRef("script", 1),
        EntityRevisionRef("shoot", 1),
        (slot,),
        brief_ref=brief_ref,
    )
    candidates = {"one": (_candidate("winner", "a", 0, 0.9, 0.9),)}
    plan_ref = EntityRevisionRef("plan", 1)

    assert optimize_sequence(editing_only, candidates, plan_ref=plan_ref) == optimize_sequence(
        combined, candidates, plan_ref=plan_ref
    )

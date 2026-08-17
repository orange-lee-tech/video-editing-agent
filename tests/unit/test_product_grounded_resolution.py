from __future__ import annotations

from datetime import UTC, datetime

from video_editing_agent.application.ports.shot_index import ShotCandidate
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.model import DurationConstraint, EditPlan, EditSlot
from video_editing_agent.domain.edit.resolution import ResolutionDecisionType
from video_editing_agent.domain.evidence.temporal import TemporalAnchor, TemporalEvidence
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.editing.resolver.product_resolution import GroundedEditPlanResolver


def _envelope(identity: str) -> EntityEnvelope:
    return EntityEnvelope(identity, 1, "test", EntityStatus.VALID, datetime.now(UTC), "test")


def _plan(slot: EditSlot) -> EditPlan:
    return EditPlan(
        _envelope("epl_product"),
        None,
        None,
        (slot,),
        EntityRevisionRef("brf_product", 1),
    )


def _shot(identity: str = "sht_product") -> Shot:
    return Shot(
        _envelope(identity),
        EntityRevisionRef("ast_product", 1),
        boundary_method="fixture",
        source_range=MediaTimeRange(MediaTime(10, 1), MediaTime(10, 1)),
    )


class FakeIndex:
    def __init__(self, candidates: tuple[ShotCandidate, ...]) -> None:
        self.candidates = candidates
        self.queries: list[str] = []

    def upsert(self, source) -> None:
        raise AssertionError("resolver must not mutate index")

    def rebuild(self, sources) -> None:
        raise AssertionError("resolver must not rebuild index")

    def remove(self, shot_ref: EntityRevisionRef) -> None:
        raise AssertionError("resolver must not remove index records")

    def search(self, query: str, *, constraints=None, limit: int = 20):
        self.queries.append(query)
        return self.candidates[:limit]


class FakeShots:
    def __init__(self, shot: Shot) -> None:
        self.shot = shot

    def load(self, shot_ref: EntityRevisionRef) -> Shot:
        assert shot_ref == EntityRevisionRef(self.shot.envelope.id, self.shot.envelope.revision)
        return self.shot


class FakeTemporal:
    def __init__(
        self,
        evidence: tuple[TemporalEvidence, ...] = (),
        anchors: tuple[TemporalAnchor, ...] = (),
    ) -> None:
        self.evidence = evidence
        self.anchors = anchors

    def save_evidence(self, evidence: TemporalEvidence) -> None:
        raise AssertionError("resolver must not persist evidence")

    def save_evidence_batch(self, evidence: tuple[TemporalEvidence, ...]) -> None:
        raise AssertionError("resolver must not persist evidence")

    def save_anchor(self, anchor: TemporalAnchor) -> None:
        raise AssertionError("resolver must not persist anchors")

    def save_evidence_and_anchors(self, evidence, anchors) -> None:
        raise AssertionError("resolver must not persist evidence")

    def list_evidence(self, shot_ref: EntityRevisionRef) -> tuple[TemporalEvidence, ...]:
        return self.evidence

    def list_anchors(self, shot_ref: EntityRevisionRef) -> tuple[TemporalAnchor, ...]:
        return self.anchors


def _resolver(index: FakeIndex, shot: Shot, temporal: FakeTemporal) -> GroundedEditPlanResolver:
    return GroundedEditPlanResolver(
        shot_index=index,
        shot_repository=FakeShots(shot),
        temporal_evidence_repository=temporal,
    )


def test_resolver_derives_query_from_edit_slot_and_prefers_persisted_anchor() -> None:
    shot = _shot()
    shot_ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
    evidence = TemporalEvidence(
        "ev_action",
        shot_ref,
        "action",
        "fixture",
        "1",
        0.9,
        source_range=MediaTimeRange(MediaTime(14, 1), MediaTime(2, 1)),
    )
    anchor = TemporalAnchor(
        "anchor_action",
        shot_ref,
        "action_peak",
        MediaTime(15, 1),
        0.9,
        ("ev_action",),
        "fixture",
    )
    index = FakeIndex((ShotCandidate(shot_ref, 1, 0.8, ("product",)),))
    slot = EditSlot(
        "slot_product",
        "show product",
        semantic_query="product action",
        target_duration=DurationConstraint(MediaTime(2, 1), MediaTime(3, 1)),
    )

    decisions = _resolver(index, shot, FakeTemporal((evidence,), (anchor,))).resolve(_plan(slot))

    assert index.queries == ["product action"]
    assert len(decisions) == 1
    decision = decisions[0]
    assert decision.decision_type is ResolutionDecisionType.RESOLVED
    selection = decision.selections[0]
    assert selection.shot_ref == shot_ref
    assert selection.selected_source_range == MediaTimeRange(MediaTime(15, 1), MediaTime(3, 1))
    assert "anchor_action" in selection.anchor_refs
    assert "ev_action" in selection.evidence_refs


def test_resolver_uses_deterministic_shot_boundary_fallback_when_no_anchor_exists() -> None:
    shot = _shot()
    shot_ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
    index = FakeIndex((ShotCandidate(shot_ref, 1, 0.7, ("product",)),))
    slot = EditSlot(
        "slot_boundary",
        "show product",
        semantic_query="product",
        target_duration=DurationConstraint(MediaTime(2, 1), MediaTime(3, 1)),
    )
    resolver = _resolver(index, shot, FakeTemporal())

    first = resolver.resolve(_plan(slot))
    second = resolver.resolve(_plan(slot))

    assert first == second
    selection = first[0].selections[0]
    assert selection.selected_source_range == MediaTimeRange(MediaTime(10, 1), MediaTime(3, 1))
    assert (
        selection.selected_source_range.start.as_fraction() >= shot.source_range.start.as_fraction()
    )
    assert selection.selected_source_range.end.as_fraction() <= shot.source_range.end.as_fraction()
    assert selection.evidence_refs == ("shot-boundary:sht_product@1",)


def test_resolver_full_shot_fallback_is_grounded_when_slot_has_no_duration() -> None:
    shot = _shot()
    shot_ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
    index = FakeIndex((ShotCandidate(shot_ref, 1, 0.6, ("product",)),))
    slot = EditSlot("slot_full", "show product", semantic_query="product")

    decision = _resolver(index, shot, FakeTemporal()).resolve(_plan(slot))[0]

    assert decision.decision_type is ResolutionDecisionType.RESOLVED
    assert decision.selections[0].selected_source_range == shot.source_range
    assert decision.selections[0].evidence_refs == ("shot-boundary:sht_product@1",)


def test_no_retrieval_candidate_remains_explicitly_unresolved() -> None:
    shot = _shot()
    slot = EditSlot(
        "slot_missing",
        "missing thing",
        semantic_query="not present",
        target_duration=DurationConstraint(MediaTime(1, 1), MediaTime(2, 1)),
    )

    decision = _resolver(FakeIndex(()), shot, FakeTemporal()).resolve(_plan(slot))[0]

    assert decision.decision_type is ResolutionDecisionType.UNRESOLVED
    assert decision.selections == ()

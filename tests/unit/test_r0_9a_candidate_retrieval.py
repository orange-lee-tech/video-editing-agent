from __future__ import annotations

from datetime import UTC, datetime

import pytest

from video_editing_agent.application.ports.shot_index import ShotCandidate
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.model import DurationConstraint
from video_editing_agent.domain.evidence.temporal import TemporalAnchor, TemporalEvidence
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.editing.director.candidate_windows import generate_candidate_windows
from video_editing_agent.editing.director.model import EditSlot
from video_editing_agent.editing.director.retrieval import eligible_shots, reciprocal_rank_fusion


def _shot(identity="sht", duration=10):
    return Shot(
        EntityEnvelope(identity, 1, "0.2", EntityStatus.VALID, datetime.now(UTC), "test"),
        EntityRevisionRef("ast", 1),
        boundary_method="test",
        source_range=MediaTimeRange(MediaTime(2, 1), MediaTime(duration, 1)),
    )


def _slot():
    return EditSlot(
        "slot",
        "show action",
        0,
        "proof",
        "pick up bottle",
        DurationConstraint(MediaTime(1, 1), MediaTime(2, 1)),
    )


def test_slot_has_no_source_authority_and_eligibility_dominates() -> None:
    assert not hasattr(_slot(), "shot_ref") and not hasattr(_slot(), "source_range")
    accepted, decisions = eligible_shots(
        (_shot("legal", 3), _shot("short", 1)), minimum_duration=MediaTime(2, 1)
    )
    assert [x.envelope.id for x in accepted] == ["legal"]
    assert not decisions[1].eligible


def test_rrf_is_stable_and_does_not_compare_raw_scores() -> None:
    a, b = EntityRevisionRef("a", 1), EntityRevisionRef("b", 1)
    lexical = (ShotCandidate(b, 1, 0.99, ()), ShotCandidate(a, 1, 0.1, ()))
    dense = (ShotCandidate(a, 1, 0.51, ()), ShotCandidate(b, 1, 0.5, ()))
    assert [x.shot_ref for x in reciprocal_rank_fusion(lexical, dense)] == [a, b]


def test_grounded_windows_are_bounded_deterministic_and_exact_shot() -> None:
    shot = _shot()
    ref = EntityRevisionRef("sht", 1)
    evidence = TemporalEvidence(
        "ev",
        ref,
        "residual_motion_region",
        "test",
        "v1",
        0.8,
        MediaTimeRange(MediaTime(5, 1), MediaTime(1, 1)),
    )
    anchor = TemporalAnchor(
        "an", ref, "residual_motion_onset", MediaTime(5, 1), 0.8, ("ev",), "test"
    )
    first = generate_candidate_windows(_slot(), shot, (anchor,), (evidence,))
    assert first == generate_candidate_windows(_slot(), shot, (anchor,), (evidence,))
    assert (
        first[0].window.source_range.start == MediaTime(5, 1)
        and first[0].window.source_range.end.as_fraction() <= shot.source_range.end.as_fraction()
    )
    with pytest.raises(ValueError, match="exact Shot"):
        generate_candidate_windows(
            _slot(),
            shot,
            (
                TemporalAnchor(
                    "bad", EntityRevisionRef("other", 1), "x", MediaTime(5, 1), 1, ("ev",), "x"
                ),
            ),
            (evidence,),
        )


def test_missing_evidence_yields_no_guessed_windows() -> None:
    assert generate_candidate_windows(_slot(), _shot(), (), ()) == ()

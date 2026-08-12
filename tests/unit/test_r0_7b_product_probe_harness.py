from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

from video_editing_agent.application.ports.preproduction_review import (
    ScriptProposalReview,
    ScriptProposalViolation,
    ShootingProposalReview,
    ShootingProposalViolation,
)

sys.path.insert(0, str(Path(__file__).parents[2]))
_final_accepted_review = importlib.import_module(
    "tools.probes.r0_7b_product_probe_candidates"
)._final_accepted_review


def test_probe_harness_accepts_direct_and_bounded_script_review_paths() -> None:
    accepted = ScriptProposalReview(True)
    rejected = ScriptProposalReview(
        False,
        (ScriptProposalViolation("unsupported_claim", "Unsupported claim."),),
    )

    assert _final_accepted_review([accepted], label="script") is accepted
    assert _final_accepted_review([rejected, accepted], label="script") is accepted


def test_probe_harness_accepts_bounded_shooting_review_path() -> None:
    accepted = ShootingProposalReview(True)
    rejected = ShootingProposalReview(
        False,
        (ShootingProposalViolation("location_mismatch", "Wrong location."),),
    )

    assert _final_accepted_review([rejected, accepted], label="shooting") is accepted


@pytest.mark.parametrize(
    "reviews",
    [
        [],
        [ScriptProposalReview(False, (ScriptProposalViolation("veto", "Veto."),))],
        [ScriptProposalReview(True), ScriptProposalReview(True)],
        [ScriptProposalReview(True), ScriptProposalReview(True), ScriptProposalReview(True)],
    ],
)
def test_probe_harness_rejects_invalid_review_sequences(
    reviews: list[ScriptProposalReview],
) -> None:
    with pytest.raises(AssertionError):
        _final_accepted_review(reviews, label="script")

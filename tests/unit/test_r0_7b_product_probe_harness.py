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
from video_editing_agent.providers.llm.deepseek_preproduction_review import (
    DeepSeekReviewCapacityError,
    DeepSeekReviewDiagnostics,
)

sys.path.insert(0, str(Path(__file__).parents[2]))
_probe = importlib.import_module("tools.probes.r0_7b_product_probe_candidates")
_final_accepted_review = _probe._final_accepted_review


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


def test_product_probe_reports_safe_review_capacity_diagnostics() -> None:
    error = DeepSeekReviewCapacityError(
        DeepSeekReviewDiagnostics(
            finish_reason="length",
            configured_max_tokens=32_000,
            prompt_tokens=100,
            completion_tokens=32_000,
            reasoning_tokens=31_990,
            capacity_recovery_attempted=True,
        )
    )
    case = _probe._product_ad_case()
    config = _probe.DeepSeekChatConfig(model="test-model", thinking_enabled=False, max_tokens=5_000)

    result = _probe._engineering_failure_result(
        case=case, config=config, stage="script_generation_or_review", error=error
    )

    assert result["review_capacity"] == {
        "finish_reason": "length",
        "configured_max_tokens": 32_000,
        "prompt_tokens": 100,
        "completion_tokens": 32_000,
        "reasoning_tokens": 31_990,
        "capacity_recovery_attempted": True,
    }
    assert "reasoning_content" not in str(result)

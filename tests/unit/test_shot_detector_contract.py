import pytest

from video_editing_agent.application.ports.shot_detector import (
    ShotBoundaryProposal,
    ShotDetectionOptions,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef


def test_shot_detection_options_accept_model_agnostic_duration_policy() -> None:
    options = ShotDetectionOptions(
        min_shot_duration_ms=1_000,
        max_shot_duration_ms=30_000,
    )

    assert options.min_shot_duration_ms == 1_000
    assert options.max_shot_duration_ms == 30_000


def test_zero_duration_constraint_is_allowed_as_disabled_policy() -> None:
    options = ShotDetectionOptions(min_shot_duration_ms=0, max_shot_duration_ms=0)

    assert options.min_shot_duration_ms == 0
    assert options.max_shot_duration_ms == 0


def test_minimum_duration_cannot_exceed_maximum() -> None:
    with pytest.raises(ValueError, match="cannot exceed"):
        ShotDetectionOptions(
            min_shot_duration_ms=2_000,
            max_shot_duration_ms=1_000,
        )


def test_shot_boundary_proposal_keeps_asset_revision_and_source_range() -> None:
    proposal = ShotBoundaryProposal(
        asset_ref=EntityRevisionRef("ast_test", 2),
        source_start_ms=1_000,
        source_end_ms=2_500,
        detection_method="transnetv2",
        confidence=0.87,
    )

    assert proposal.asset_ref == EntityRevisionRef("ast_test", 2)
    assert proposal.source_start_ms == 1_000
    assert proposal.source_end_ms == 2_500
    assert proposal.detection_method == "transnetv2"
    assert proposal.confidence == 0.87


def test_shot_boundary_proposal_rejects_empty_or_reversed_range() -> None:
    with pytest.raises(ValueError, match="greater than"):
        ShotBoundaryProposal(
            asset_ref=EntityRevisionRef("ast_test", 1),
            source_start_ms=1_000,
            source_end_ms=1_000,
            detection_method="manual-test",
        )


def test_shot_boundary_proposal_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        ShotBoundaryProposal(
            asset_ref=EntityRevisionRef("ast_test", 1),
            source_start_ms=0,
            source_end_ms=1_000,
            detection_method="manual-test",
            confidence=1.1,
        )

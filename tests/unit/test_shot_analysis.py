from datetime import UTC, datetime

import pytest

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shot.analysis import (
    AnalysisProfile,
    NamedQualityScore,
    ShotAnalysis,
    ShotAnalysisRef,
    VisualSemantics,
)


def test_analysis_profiles_match_reviewed_contract_names() -> None:
    assert [profile.value for profile in AnalysisProfile] == [
        "basic",
        "semantic",
        "speech",
        "deep_visual",
        "editorial",
    ]


def test_shot_analysis_is_revisioned_against_exact_shot_revision() -> None:
    shot_ref = EntityRevisionRef("sht_1", 3)
    analysis = ShotAnalysis(
        shot_ref=shot_ref,
        revision=2,
        profile=AnalysisProfile.SEMANTIC,
        analyzed_at=datetime(2026, 8, 10, 8, 0, tzinfo=UTC),
        visual=VisualSemantics(summary="A person walks into a room", tags=("person", "room")),
        artifact_refs=("art_frame_1",),
    )

    assert analysis.ref == ShotAnalysisRef(shot_ref, 2)
    assert analysis.shot_ref.revision == 3
    assert analysis.profile is AnalysisProfile.SEMANTIC


def test_analysis_revision_must_be_positive() -> None:
    with pytest.raises(ValueError, match="revision"):
        ShotAnalysisRef(EntityRevisionRef("sht_1", 1), 0)


def test_quality_score_is_normalized() -> None:
    assert NamedQualityScore("sharpness", 0.75).value == 0.75

    with pytest.raises(ValueError, match="between 0 and 1"):
        NamedQualityScore("sharpness", 1.1)


def test_blank_artifact_reference_is_rejected() -> None:
    with pytest.raises(ValueError, match="artifact_refs"):
        ShotAnalysis(
            shot_ref=EntityRevisionRef("sht_1", 1),
            revision=1,
            profile=AnalysisProfile.BASIC,
            analyzed_at=datetime.now(UTC),
            artifact_refs=("",),
        )

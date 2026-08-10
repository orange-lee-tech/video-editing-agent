import pytest

from video_editing_agent.application.ports.artifact_store import StoredArtifactRef
from video_editing_agent.application.ports.visual_understanding import (
    VisualFrameReference,
    VisualQualityScoreProposal,
    VisualSemanticsProposal,
    VisualUnderstandingRequest,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shot.analysis import AnalysisProfile
from video_editing_agent.media.understanding.visual_validation import (
    normalize_visual_understanding_proposal,
)


def frame(ordinal: int, timestamp_ms: int) -> VisualFrameReference:
    digest = f"{ordinal + 1:064x}"
    return VisualFrameReference(
        artifact_ref=StoredArtifactRef(
            artifact_id=f"art_sha256_{digest}",
            content_hash=f"sha256:{digest}",
            media_type="image/png",
            byte_size=10,
        ),
        ordinal=ordinal,
        source_timestamp_ms=timestamp_ms,
    )


def test_visual_request_preserves_exact_shot_revision_and_frame_order() -> None:
    request = VisualUnderstandingRequest(
        shot_ref=EntityRevisionRef("sht_1", 4),
        profile=AnalysisProfile.SEMANTIC,
        frames=(frame(0, 333), frame(1, 1_000)),
    )

    assert request.shot_ref == EntityRevisionRef("sht_1", 4)
    assert [item.source_timestamp_ms for item in request.frames] == [333, 1_000]


def test_provider_proposal_is_normalized_before_domain_use() -> None:
    validated = normalize_visual_understanding_proposal(
        VisualSemanticsProposal(
            summary="  Person enters a room.  ",
            tags=("person", " room ", "person", ""),
            subjects=(" person ",),
            actions=(" walking ", "walking"),
            environment=" indoors ",
            framing=" medium shot ",
            camera_motion=" static ",
            quality_scores=(
                VisualQualityScoreProposal(" aesthetic ", 0.82),
                VisualQualityScoreProposal("aesthetic", 0.71),
            ),
        )
    )

    assert validated.visual.summary == "Person enters a room."
    assert validated.visual.tags == ("person", "room")
    assert validated.visual.subjects == ("person",)
    assert validated.visual.actions == ("walking",)
    assert validated.visual.environment == "indoors"
    assert validated.visual.framing == "medium shot"
    assert validated.visual.camera_motion == "static"
    assert [(score.name, score.value) for score in validated.quality_scores] == [
        ("aesthetic", 0.82)
    ]


def test_invalid_visual_quality_score_is_rejected_without_sentinel() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        VisualQualityScoreProposal("aesthetic", -1.0)

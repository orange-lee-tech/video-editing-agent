from datetime import UTC, datetime

from video_editing_agent.application.ports.shot_index import (
    ShotIndexSource,
    ShotSearchConstraints,
)
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.shot.analysis import AnalysisProfile, ShotAnalysis, VisualSemantics
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.indexing.lexical import LexicalShotIndex

NOW = datetime(2026, 8, 11, 2, 45, tzinfo=UTC)


def make_source(shot_id: str, duration: MediaTime) -> ShotIndexSource:
    shot = Shot(
        envelope=EntityEnvelope(
            id=shot_id,
            revision=1,
            schema_version="0.2",
            status=EntityStatus.VALID,
            created_at=NOW,
            created_by="test",
        ),
        asset_ref=EntityRevisionRef("ast_exact", 1),
        source_range=MediaTimeRange(start=MediaTime(0, 1), duration=duration),
        boundary_method="test",
    )
    analysis = ShotAnalysis(
        shot_ref=EntityRevisionRef(shot_id, 1),
        revision=1,
        profile=AnalysisProfile.SEMANTIC,
        analyzed_at=NOW,
        visual=VisualSemantics(tags=("candidate",)),
    )
    return ShotIndexSource(shot=shot, analysis=analysis)


def test_duration_prefilter_uses_canonical_rational_time() -> None:
    index = LexicalShotIndex()
    index.rebuild(
        (
            make_source("sht_short", MediaTime(1, 24)),
            make_source("sht_long", MediaTime(1, 12)),
        )
    )

    result = index.search(
        "candidate",
        constraints=ShotSearchConstraints(min_duration=MediaTime(1, 20)),
    )

    assert [candidate.shot_ref.entity_id for candidate in result] == ["sht_long"]


def test_legacy_millisecond_constraint_remains_supported() -> None:
    constraints = ShotSearchConstraints(min_duration_ms=250, max_duration_ms=1_500)

    assert constraints.min_duration == MediaTime(1, 4)
    assert constraints.max_duration == MediaTime(3, 2)
    assert constraints.min_duration_ms == 250
    assert constraints.max_duration_ms == 1_500

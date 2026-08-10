from datetime import UTC, datetime

import pytest

from video_editing_agent.application.ports.shot_index import (
    ShotIndexSource,
    ShotSearchConstraints,
)
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.shot.analysis import (
    AnalysisProfile,
    ShotAnalysis,
    SpeechContent,
    VisualSemantics,
)
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.indexing.lexical import LexicalShotIndex

NOW = datetime(2026, 8, 10, 10, 30, tzinfo=UTC)


def make_shot(
    shot_id: str,
    *,
    asset_id: str = "ast_1",
    duration_ms: int = 1_000,
    revision: int = 1,
) -> Shot:
    return Shot(
        envelope=EntityEnvelope(
            id=shot_id,
            revision=revision,
            schema_version="0.1.1",
            status=EntityStatus.VALID,
            created_at=NOW,
            created_by="test",
        ),
        asset_ref=EntityRevisionRef(asset_id, 1),
        source_start_ms=0,
        source_end_ms=duration_ms,
        boundary_method="test",
    )


def make_analysis(
    shot: Shot,
    *,
    revision: int = 1,
    profile: AnalysisProfile = AnalysisProfile.SEMANTIC,
    summary: str | None = None,
    tags: tuple[str, ...] = (),
    subjects: tuple[str, ...] = (),
    actions: tuple[str, ...] = (),
    transcript: str | None = None,
) -> ShotAnalysis:
    shot_ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
    visual = VisualSemantics(
        summary=summary,
        tags=tags,
        subjects=subjects,
        actions=actions,
    )
    speech = None if transcript is None else SpeechContent(transcript=transcript, language="en")
    return ShotAnalysis(
        shot_ref=shot_ref,
        revision=revision,
        profile=profile,
        analyzed_at=NOW,
        visual=visual,
        speech=speech,
    )


def source(shot: Shot, **analysis_kwargs: object) -> ShotIndexSource:
    return ShotIndexSource(shot=shot, analysis=make_analysis(shot, **analysis_kwargs))


def test_lexical_search_ranks_subject_and_action_matches() -> None:
    sanding = make_shot("sht_sanding")
    walking = make_shot("sht_walking")
    index = LexicalShotIndex()
    index.rebuild(
        (
            source(
                sanding,
                summary="A craftsperson works at a bench.",
                subjects=("woodworker",),
                actions=("sanding",),
            ),
            source(
                walking,
                summary="A person walks outside.",
                subjects=("person",),
                actions=("walking",),
            ),
        )
    )

    candidates = index.search("woodworker sanding")

    assert len(candidates) == 1
    assert candidates[0].shot_ref == EntityRevisionRef("sht_sanding", 1)
    assert candidates[0].retrieval_score == 1.0
    assert candidates[0].matched_terms == ("woodworker", "sanding")


def test_lexical_search_supports_cjk_character_and_bigram_matching() -> None:
    shot = make_shot("sht_chinese")
    index = LexicalShotIndex()
    index.upsert(source(shot, summary="木工师傅正在打磨木材"))

    candidates = index.search("木工打磨")

    assert len(candidates) == 1
    assert candidates[0].shot_ref == EntityRevisionRef("sht_chinese", 1)
    assert "木工" in candidates[0].matched_terms
    assert "打磨" in candidates[0].matched_terms


def test_search_constraints_prefilter_without_claiming_eligibility() -> None:
    short = make_shot("sht_short", asset_id="ast_a", duration_ms=500)
    long = make_shot("sht_long", asset_id="ast_b", duration_ms=2_000)
    index = LexicalShotIndex()
    index.rebuild(
        (
            source(short, tags=("common",), profile=AnalysisProfile.SEMANTIC),
            source(long, tags=("common",), profile=AnalysisProfile.EDITORIAL),
        )
    )
    constraints = ShotSearchConstraints(
        asset_refs=(EntityRevisionRef("ast_b", 1),),
        profiles=(AnalysisProfile.EDITORIAL,),
        min_duration_ms=1_000,
    )

    candidates = index.search("common", constraints=constraints)

    assert [candidate.shot_ref.entity_id for candidate in candidates] == ["sht_long"]


def test_upsert_replaces_with_newer_analysis_revision() -> None:
    shot = make_shot("sht_revision")
    index = LexicalShotIndex()
    index.upsert(source(shot, revision=1, tags=("old",)))
    index.upsert(source(shot, revision=2, tags=("new",)))

    assert index.search("old") == ()
    candidate = index.search("new")[0]
    assert candidate.analysis_revision == 2


def test_upsert_rejects_stale_analysis_regression() -> None:
    shot = make_shot("sht_stale")
    index = LexicalShotIndex()
    index.upsert(source(shot, revision=2, tags=("new",)))

    with pytest.raises(ValueError, match="older revision"):
        index.upsert(source(shot, revision=1, tags=("old",)))


def test_rebuild_replaces_previous_derived_index_contents() -> None:
    first = make_shot("sht_first")
    second = make_shot("sht_second")
    index = LexicalShotIndex()
    index.upsert(source(first, tags=("first",)))

    index.rebuild((source(second, tags=("second",)),))

    assert index.search("first") == ()
    assert index.search("second")[0].shot_ref == EntityRevisionRef("sht_second", 1)


def test_index_source_requires_exact_shot_revision() -> None:
    shot = make_shot("sht_mismatch", revision=2)
    analysis = ShotAnalysis(
        shot_ref=EntityRevisionRef("sht_mismatch", 1),
        revision=1,
        profile=AnalysisProfile.SEMANTIC,
        analyzed_at=NOW,
    )

    with pytest.raises(ValueError, match="exact Shot revision"):
        ShotIndexSource(shot=shot, analysis=analysis)


def test_search_rejects_empty_query_and_invalid_limit() -> None:
    index = LexicalShotIndex()

    with pytest.raises(ValueError, match="searchable term"):
        index.search("---")
    with pytest.raises(ValueError, match="limit"):
        index.search("term", limit=0)

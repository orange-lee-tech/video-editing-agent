from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.application.use_cases.shot_index import MaintainShotIndex
from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.shot.analysis import AnalysisProfile, ShotAnalysis, VisualSemantics
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.indexing.lexical import LexicalShotIndex
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase
from video_editing_agent.storage.repositories.sqlite_repositories import (
    SqliteAssetRepository,
    SqliteShotAnalysisRepository,
    SqliteShotRepository,
)

NOW = datetime(2026, 8, 10, 11, 0, tzinfo=UTC)


def envelope(entity_id: str) -> EntityEnvelope:
    return EntityEnvelope(
        id=entity_id,
        revision=1,
        schema_version="0.1.1",
        status=EntityStatus.VALID,
        created_at=NOW,
        created_by="test",
    )


def make_asset() -> Asset:
    return Asset(
        envelope=envelope("ast_index"),
        media_kind="video",
        origin="local",
        storage_ref="file:///tmp/index.mp4",
        content_hash="sha256:" + "2" * 64,
        byte_size=100,
        provenance=AssetProvenance(origin_type="local"),
        imported_at=NOW,
        duration_ms=2_000,
    )


def make_shot(shot_id: str, start_ms: int, end_ms: int) -> Shot:
    return Shot(
        envelope=envelope(shot_id),
        asset_ref=EntityRevisionRef("ast_index", 1),
        source_start_ms=start_ms,
        source_end_ms=end_ms,
        boundary_method="test",
    )


def make_analysis(shot_id: str, revision: int, tag: str) -> ShotAnalysis:
    return ShotAnalysis(
        shot_ref=EntityRevisionRef(shot_id, 1),
        revision=revision,
        profile=AnalysisProfile.SEMANTIC,
        analyzed_at=NOW,
        visual=VisualSemantics(summary=f"Scene about {tag}.", tags=(tag,)),
    )


def repositories(path: Path):
    database = SqliteProjectDatabase(path)
    database.initialize()
    return (
        SqliteAssetRepository(database),
        SqliteShotRepository(database),
        SqliteShotAnalysisRepository(database),
    )


def test_rebuild_uses_persisted_latest_analysis_and_skips_missing(tmp_path: Path) -> None:
    path = tmp_path / "project.sqlite3"
    assets, shots, analyses = repositories(path)
    assets.save(make_asset())
    shots.save_many(
        (
            make_shot("sht_index_a", 0, 1_000),
            make_shot("sht_index_b", 1_000, 2_000),
        )
    )
    analyses.save(make_analysis("sht_index_a", 1, "woodworking"))

    _, reopened_shots, reopened_analyses = repositories(path)
    index = LexicalShotIndex()
    use_case = MaintainShotIndex(
        shot_repository=reopened_shots,
        analysis_repository=reopened_analyses,
        shot_index=index,
    )
    first_ref = EntityRevisionRef("sht_index_a", 1)
    second_ref = EntityRevisionRef("sht_index_b", 1)

    result = use_case.rebuild((first_ref, second_ref))

    assert result.requested_count == 2
    assert result.indexed_count == 1
    assert result.skipped_without_analysis == (second_ref,)
    assert index.search("woodworking")[0].shot_ref == first_ref


def test_refresh_promotes_new_persisted_analysis_revision(tmp_path: Path) -> None:
    path = tmp_path / "project.sqlite3"
    assets, shots, analyses = repositories(path)
    assets.save(make_asset())
    shots.save(make_shot("sht_refresh", 0, 1_000))
    analyses.save(make_analysis("sht_refresh", 1, "oldterm"))

    index = LexicalShotIndex()
    use_case = MaintainShotIndex(
        shot_repository=shots,
        analysis_repository=analyses,
        shot_index=index,
    )
    shot_ref = EntityRevisionRef("sht_refresh", 1)
    assert use_case.refresh(shot_ref) is True
    assert index.search("oldterm")[0].analysis_revision == 1

    analyses.save(make_analysis("sht_refresh", 2, "newterm"))
    assert use_case.refresh(shot_ref) is True

    assert index.search("oldterm") == ()
    candidate = index.search("newterm")[0]
    assert candidate.shot_ref == shot_ref
    assert candidate.analysis_revision == 2


def test_rebuild_rejects_duplicate_exact_shot_refs(tmp_path: Path) -> None:
    path = tmp_path / "project.sqlite3"
    assets, shots, analyses = repositories(path)
    assets.save(make_asset())
    shots.save(make_shot("sht_duplicate", 0, 1_000))
    shot_ref = EntityRevisionRef("sht_duplicate", 1)
    use_case = MaintainShotIndex(
        shot_repository=shots,
        analysis_repository=analyses,
        shot_index=LexicalShotIndex(),
    )

    with pytest.raises(ValueError, match="duplicate exact revisions"):
        use_case.rebuild((shot_ref, shot_ref))

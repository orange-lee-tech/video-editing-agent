from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.domain.brief.model import Brief
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.model import EditPlan, EditSlot
from video_editing_agent.domain.edl.model import EDL, EDLSegment, EDLTrack, EDLTrackFamily
from video_editing_agent.storage.project.workspace import ProjectWorkspace
from video_editing_agent.storage.repositories.edl_repository import SqliteEDLRepository
from video_editing_agent.storage.repositories.preproduction_repositories import (
    SqliteBriefRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase
from video_editing_agent.storage.repositories.sqlite_repositories import (
    RevisionConflictError,
    SqliteEditPlanRepository,
)

NOW = datetime(2026, 8, 17, 13, 0, tzinfo=UTC)


def _envelope(identity: str, revision: int = 1) -> EntityEnvelope:
    return EntityEnvelope(identity, revision, "0.2", EntityStatus.VALID, NOW, "test")


def _brief() -> Brief:
    return Brief(
        _envelope("brf_edl_store"), "Title", "Objective", "Audience", "Platform", "Message"
    )


def _edit_plan() -> EditPlan:
    return EditPlan(
        _envelope("epl_edl_store"),
        None,
        None,
        (EditSlot("slot_1", "show value", semantic_query="value"),),
        EntityRevisionRef("brf_edl_store", 1),
    )


def _edl(*, asset_id: str = "ast_edl_store") -> EDL:
    source = MediaTimeRange(MediaTime(1, 24), MediaTime(3, 1))
    return EDL(
        _envelope("edl_store"),
        EntityRevisionRef("epl_edl_store", 1),
        (
            EDLSegment(
                "seg_1",
                EntityRevisionRef(asset_id, 1),
                source_range=source,
                timeline_range=MediaTimeRange(MediaTime(0, 1), source.duration),
                track_id="video",
            ),
        ),
        (EDLTrack("video", EDLTrackFamily.VIDEO),),
    )


def _repositories(path: Path) -> tuple[SqliteProjectDatabase, SqliteEDLRepository]:
    database = SqliteProjectDatabase(path)
    database.initialize()
    SqliteBriefRepository(database).save(_brief())
    SqliteEditPlanRepository(database).save(_edit_plan())
    return database, SqliteEDLRepository(database)


def test_edl_repository_round_trip_preserves_exact_canonical_payload(tmp_path: Path) -> None:
    database, repository = _repositories(tmp_path / "project.sqlite3")
    edl = _edl()

    repository.save(edl)

    reopened = SqliteProjectDatabase(database.path)
    reopened.initialize()
    loaded = SqliteEDLRepository(reopened).load(EntityRevisionRef("edl_store", 1))

    assert loaded == edl
    assert loaded.segments[0].source_range.start == MediaTime(1, 24)
    assert SqliteEDLRepository(reopened).latest_revision("edl_store") == 1
    assert SqliteEDLRepository(reopened).count() == 1


def test_edl_repository_exact_revision_is_idempotent_but_conflict_fails(tmp_path: Path) -> None:
    _, repository = _repositories(tmp_path / "project.sqlite3")
    original = _edl()

    repository.save(original)
    repository.save(original)

    with pytest.raises(RevisionConflictError):
        repository.save(_edl(asset_id="ast_different"))
    assert repository.count() == 1


def test_workspace_exposes_durable_edl_repository_and_schema_v7(tmp_path: Path) -> None:
    workspace = ProjectWorkspace.open(tmp_path / "workspace")

    assert workspace.database.schema_version() == 7
    assert workspace.edls.count() == 0
    assert workspace.status()["counts"]["edls"] == 0

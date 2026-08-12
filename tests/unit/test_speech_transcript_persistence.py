import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.evidence.speech import SpeechSegment, SpeechTranscript, SpeechWord
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.storage.repositories.speech_transcript_repository import (
    SpeechTranscriptConflictError,
    SqliteSpeechTranscriptRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase
from video_editing_agent.storage.repositories.sqlite_repositories import (
    SqliteAssetRepository,
    SqliteShotRepository,
)

NOW = datetime(2026, 8, 12, 16, 50, tzinfo=UTC)


def _envelope(entity_id: str) -> EntityEnvelope:
    return EntityEnvelope(
        id=entity_id,
        revision=1,
        schema_version="0.2",
        status=EntityStatus.VALID,
        created_at=NOW,
        created_by="test",
    )


def _prepare_database(path: Path) -> tuple[SqliteProjectDatabase, EntityRevisionRef]:
    database = SqliteProjectDatabase(path)
    database.initialize()
    asset = Asset(
        envelope=_envelope("ast_speech"),
        media_kind="video",
        origin="local",
        storage_ref="file:///tmp/speech.mp4",
        content_hash="sha256:" + "7" * 64,
        byte_size=100,
        provenance=AssetProvenance(origin_type="local"),
        imported_at=NOW,
        duration=MediaTime(20, 1),
    )
    shot = Shot(
        envelope=_envelope("sht_speech"),
        asset_ref=EntityRevisionRef("ast_speech", 1),
        source_range=MediaTimeRange(MediaTime(5, 1), MediaTime(4, 1)),
        boundary_method="test",
    )
    SqliteAssetRepository(database).save(asset)
    SqliteShotRepository(database).save(shot)
    return database, EntityRevisionRef("sht_speech", 1)


def _transcript(shot_ref: EntityRevisionRef, *, revision: int = 1) -> SpeechTranscript:
    word = SpeechWord(
        "hello",
        MediaTimeRange(MediaTime(11, 2), MediaTime(1, 2)),
        confidence=0.9,
    )
    segment = SpeechSegment(
        "hello",
        MediaTimeRange(MediaTime(11, 2), MediaTime(1, 1)),
        (word,),
        confidence=0.8,
    )
    return SpeechTranscript(
        shot_ref=shot_ref,
        revision=revision,
        recognized_at=NOW,
        provider_id="fake-asr",
        provider_revision="r1",
        text="hello",
        language="en",
        segments=(segment,),
    )


def test_transcript_survives_reopen_with_exact_rational_time(tmp_path: Path) -> None:
    path = tmp_path / "project.sqlite3"
    database, shot_ref = _prepare_database(path)
    repository = SqliteSpeechTranscriptRepository(database)
    transcript = _transcript(shot_ref)
    repository.save(transcript)

    reopened = SqliteProjectDatabase(path)
    reopened.initialize()
    loaded = SqliteSpeechTranscriptRepository(reopened).load(shot_ref, 1)

    assert loaded == transcript
    assert loaded.segments[0].source_range.start == MediaTime(11, 2)
    assert SqliteSpeechTranscriptRepository(reopened).latest(shot_ref) == transcript


def test_transcript_save_is_idempotent_but_conflict_is_rejected(tmp_path: Path) -> None:
    database, shot_ref = _prepare_database(tmp_path / "project.sqlite3")
    repository = SqliteSpeechTranscriptRepository(database)
    transcript = _transcript(shot_ref)

    repository.save(transcript)
    repository.save(transcript)

    changed = SpeechTranscript(
        shot_ref=shot_ref,
        revision=1,
        recognized_at=NOW,
        provider_id="fake-asr",
        provider_revision="r2",
        text="hello",
        language="en",
        segments=transcript.segments,
    )
    with pytest.raises(SpeechTranscriptConflictError, match="different content"):
        repository.save(changed)


def test_transcript_requires_existing_exact_shot_revision(tmp_path: Path) -> None:
    database = SqliteProjectDatabase(tmp_path / "project.sqlite3")
    database.initialize()
    repository = SqliteSpeechTranscriptRepository(database)

    with pytest.raises(sqlite3.IntegrityError):
        repository.save(_transcript(EntityRevisionRef("sht_missing", 1)))

from __future__ import annotations

import sqlite3

from video_editing_agent.application.ports.speech_transcript_repository import (
    SpeechTranscriptRepository,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.evidence.speech import SpeechTranscript
from video_editing_agent.storage.repositories.record_codec import PersistenceIntegrityError
from video_editing_agent.storage.repositories.speech_transcript_codec import (
    decode_speech_transcript,
    encode_speech_transcript,
)
from video_editing_agent.storage.repositories.sqlite_database import (
    PersistenceError,
    SqliteProjectDatabase,
)


class SpeechTranscriptConflictError(PersistenceError):
    """An exact transcript revision already exists with different immutable content."""


class SqliteSpeechTranscriptRepository(SpeechTranscriptRepository):
    def __init__(self, database: SqliteProjectDatabase) -> None:
        self._database = database

    def save(self, transcript: SpeechTranscript) -> None:
        payload = encode_speech_transcript(transcript)
        identity = (
            transcript.shot_ref.entity_id,
            transcript.shot_ref.revision,
            transcript.revision,
        )
        with self._database.write_connection() as connection:
            try:
                connection.execute(
                    """
                    INSERT INTO speech_transcripts (
                        shot_entity_id, shot_revision, transcript_revision, payload_json
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (*identity, payload),
                )
            except sqlite3.IntegrityError as exc:
                row = connection.execute(
                    """
                    SELECT payload_json FROM speech_transcripts
                    WHERE shot_entity_id = ?
                      AND shot_revision = ?
                      AND transcript_revision = ?
                    """,
                    identity,
                ).fetchone()
                if row is not None and str(row["payload_json"]) == payload:
                    return
                if row is not None:
                    raise SpeechTranscriptConflictError(
                        "speech transcript exact revision already exists with different content: "
                        f"{identity!r}"
                    ) from exc
                raise

    def load(self, shot_ref: EntityRevisionRef, revision: int) -> SpeechTranscript:
        with self._database.read_connection() as connection:
            row = connection.execute(
                """
                SELECT payload_json FROM speech_transcripts
                WHERE shot_entity_id = ?
                  AND shot_revision = ?
                  AND transcript_revision = ?
                """,
                (shot_ref.entity_id, shot_ref.revision, revision),
            ).fetchone()
        if row is None:
            raise KeyError((shot_ref, revision))
        transcript = decode_speech_transcript(str(row["payload_json"]))
        if transcript.shot_ref != shot_ref or transcript.revision != revision:
            raise PersistenceIntegrityError(
                "speech_transcript row identity disagrees with encoded transcript identity"
            )
        return transcript

    def latest(self, shot_ref: EntityRevisionRef) -> SpeechTranscript | None:
        with self._database.read_connection() as connection:
            row = connection.execute(
                """
                SELECT payload_json FROM speech_transcripts
                WHERE shot_entity_id = ? AND shot_revision = ?
                ORDER BY transcript_revision DESC
                LIMIT 1
                """,
                (shot_ref.entity_id, shot_ref.revision),
            ).fetchone()
        if row is None:
            return None
        transcript = decode_speech_transcript(str(row["payload_json"]))
        if transcript.shot_ref != shot_ref:
            raise PersistenceIntegrityError(
                "speech_transcript row Shot identity disagrees with encoded transcript"
            )
        return transcript

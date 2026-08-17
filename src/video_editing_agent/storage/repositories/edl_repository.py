from __future__ import annotations

from video_editing_agent.application.ports.edl_repository import EDLRepository
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.edl.codec import decode_edl, encode_edl
from video_editing_agent.domain.edl.model import EDL
from video_editing_agent.storage.repositories.record_codec import PersistenceIntegrityError
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase
from video_editing_agent.storage.repositories.sqlite_repositories import _save_immutable_record


class SqliteEDLRepository(EDLRepository):
    def __init__(self, database: SqliteProjectDatabase) -> None:
        self._database = database

    def save(self, edl: EDL) -> None:
        payload = encode_edl(edl).decode("utf-8")
        identity = (edl.envelope.id, edl.envelope.revision)
        with self._database.write_connection() as connection:
            _save_immutable_record(
                connection,
                table="edls",
                identity_columns=("entity_id", "revision"),
                identity_values=identity,
                insert_columns=(
                    "entity_id",
                    "revision",
                    "edit_plan_entity_id",
                    "edit_plan_revision",
                    "payload_json",
                ),
                insert_values=(
                    *identity,
                    edl.edit_plan_ref.entity_id,
                    edl.edit_plan_ref.revision,
                    payload,
                ),
                payload_json=payload,
            )

    def load(self, edl_ref: EntityRevisionRef) -> EDL:
        with self._database.read_connection() as connection:
            row = connection.execute(
                "SELECT payload_json FROM edls WHERE entity_id = ? AND revision = ?",
                (edl_ref.entity_id, edl_ref.revision),
            ).fetchone()
        if row is None:
            raise KeyError(edl_ref)
        edl = decode_edl(str(row["payload_json"]).encode("utf-8"))
        actual = EntityRevisionRef(edl.envelope.id, edl.envelope.revision)
        if actual != edl_ref:
            raise PersistenceIntegrityError(
                f"EDL row identity {edl_ref!r} disagrees with payload {actual!r}"
            )
        return edl

    def latest_revision(self, entity_id: str) -> int | None:
        with self._database.read_connection() as connection:
            row = connection.execute(
                "SELECT MAX(revision) AS revision FROM edls WHERE entity_id = ?",
                (entity_id,),
            ).fetchone()
        return None if row is None or row["revision"] is None else int(row["revision"])

    def count(self) -> int:
        with self._database.read_connection() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM edls").fetchone()[0])

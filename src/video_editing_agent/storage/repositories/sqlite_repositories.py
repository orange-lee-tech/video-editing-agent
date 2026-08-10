from __future__ import annotations

import sqlite3

from video_editing_agent.application.ports.asset_repository import AssetRepository
from video_editing_agent.application.ports.shot_analysis_repository import ShotAnalysisRepository
from video_editing_agent.application.ports.shot_repository import ShotPersistenceRepository
from video_editing_agent.domain.asset.model import Asset
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shot.analysis import ShotAnalysis
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.storage.repositories.record_codec import (
    PersistenceIntegrityError,
    decode_asset,
    decode_shot,
    decode_shot_analysis,
    encode_asset,
    encode_shot,
    encode_shot_analysis,
)
from video_editing_agent.storage.repositories.sqlite_database import (
    PersistenceError,
    SqliteProjectDatabase,
)


class RevisionConflictError(PersistenceError):
    """An exact revision already exists with different immutable content."""


def _save_immutable_record(
    connection: sqlite3.Connection,
    *,
    table: str,
    identity_columns: tuple[str, ...],
    identity_values: tuple[object, ...],
    insert_columns: tuple[str, ...],
    insert_values: tuple[object, ...],
    payload_json: str,
) -> None:
    placeholders = ", ".join("?" for _ in insert_columns)
    columns = ", ".join(insert_columns)
    try:
        connection.execute(
            f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
            insert_values,
        )
        return
    except sqlite3.IntegrityError as exc:
        where = " AND ".join(f"{column} = ?" for column in identity_columns)
        row = connection.execute(
            f"SELECT payload_json FROM {table} WHERE {where}", identity_values
        ).fetchone()
        if row is None:
            raise
        if str(row["payload_json"]) == payload_json:
            return
        raise RevisionConflictError(
            f"{table} exact revision already exists with different content: {identity_values!r}"
        ) from exc


class SqliteAssetRepository(AssetRepository):
    def __init__(self, database: SqliteProjectDatabase) -> None:
        self._database = database

    def save(self, asset: Asset) -> None:
        payload = encode_asset(asset)
        identity = (asset.envelope.id, asset.envelope.revision)
        with self._database.write_connection() as connection:
            _save_immutable_record(
                connection,
                table="assets",
                identity_columns=("entity_id", "revision"),
                identity_values=identity,
                insert_columns=("entity_id", "revision", "payload_json"),
                insert_values=(*identity, payload),
                payload_json=payload,
            )

    def load(self, asset_ref: EntityRevisionRef) -> Asset:
        with self._database.read_connection() as connection:
            row = connection.execute(
                "SELECT payload_json FROM assets WHERE entity_id = ? AND revision = ?",
                (asset_ref.entity_id, asset_ref.revision),
            ).fetchone()
        if row is None:
            raise KeyError(asset_ref)
        asset = decode_asset(str(row["payload_json"]))
        actual_ref = EntityRevisionRef(asset.envelope.id, asset.envelope.revision)
        if actual_ref != asset_ref:
            raise PersistenceIntegrityError(
                f"Asset row identity {asset_ref!r} disagrees with payload {actual_ref!r}"
            )
        return asset


class SqliteShotRepository(ShotPersistenceRepository):
    def __init__(self, database: SqliteProjectDatabase) -> None:
        self._database = database

    def save(self, shot: Shot) -> None:
        payload = encode_shot(shot)
        identity = (shot.envelope.id, shot.envelope.revision)
        with self._database.write_connection() as connection:
            _save_immutable_record(
                connection,
                table="shots",
                identity_columns=("entity_id", "revision"),
                identity_values=identity,
                insert_columns=(
                    "entity_id",
                    "revision",
                    "asset_entity_id",
                    "asset_revision",
                    "payload_json",
                ),
                insert_values=(
                    *identity,
                    shot.asset_ref.entity_id,
                    shot.asset_ref.revision,
                    payload,
                ),
                payload_json=payload,
            )

    def load(self, shot_ref: EntityRevisionRef) -> Shot:
        with self._database.read_connection() as connection:
            row = connection.execute(
                "SELECT payload_json FROM shots WHERE entity_id = ? AND revision = ?",
                (shot_ref.entity_id, shot_ref.revision),
            ).fetchone()
        if row is None:
            raise KeyError(shot_ref)
        shot = decode_shot(str(row["payload_json"]))
        actual_ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
        if actual_ref != shot_ref:
            raise PersistenceIntegrityError(
                f"Shot row identity {shot_ref!r} disagrees with payload {actual_ref!r}"
            )
        return shot


class SqliteShotAnalysisRepository(ShotAnalysisRepository):
    def __init__(self, database: SqliteProjectDatabase) -> None:
        self._database = database

    def save(self, analysis: ShotAnalysis) -> None:
        payload = encode_shot_analysis(analysis)
        identity = (
            analysis.shot_ref.entity_id,
            analysis.shot_ref.revision,
            analysis.revision,
        )
        with self._database.write_connection() as connection:
            _save_immutable_record(
                connection,
                table="shot_analyses",
                identity_columns=("shot_entity_id", "shot_revision", "analysis_revision"),
                identity_values=identity,
                insert_columns=(
                    "shot_entity_id",
                    "shot_revision",
                    "analysis_revision",
                    "payload_json",
                ),
                insert_values=(*identity, payload),
                payload_json=payload,
            )

    def latest(self, shot_ref: EntityRevisionRef) -> ShotAnalysis | None:
        with self._database.read_connection() as connection:
            row = connection.execute(
                """
                SELECT payload_json
                FROM shot_analyses
                WHERE shot_entity_id = ? AND shot_revision = ?
                ORDER BY analysis_revision DESC
                LIMIT 1
                """,
                (shot_ref.entity_id, shot_ref.revision),
            ).fetchone()
        if row is None:
            return None
        analysis = decode_shot_analysis(str(row["payload_json"]))
        if analysis.shot_ref != shot_ref:
            raise PersistenceIntegrityError(
                f"ShotAnalysis row identity {shot_ref!r} disagrees with payload "
                f"{analysis.shot_ref!r}"
            )
        return analysis

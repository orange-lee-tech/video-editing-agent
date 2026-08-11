from __future__ import annotations

import pathlib
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime

SCHEMA_VERSION = 2
_SUPPORTED_SCHEMA_VERSIONS = frozenset({0, 1, SCHEMA_VERSION})


class PersistenceError(RuntimeError):
    """Base error for local structured-record persistence."""


class UnsupportedSchemaVersionError(PersistenceError):
    """The database schema is newer or otherwise unsupported by this runtime."""


def _create_core_tables(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS assets (
            entity_id TEXT NOT NULL,
            revision INTEGER NOT NULL CHECK (revision >= 1),
            payload_json TEXT NOT NULL,
            PRIMARY KEY (entity_id, revision)
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS shots (
            entity_id TEXT NOT NULL,
            revision INTEGER NOT NULL CHECK (revision >= 1),
            asset_entity_id TEXT NOT NULL,
            asset_revision INTEGER NOT NULL CHECK (asset_revision >= 1),
            payload_json TEXT NOT NULL,
            PRIMARY KEY (entity_id, revision),
            FOREIGN KEY (asset_entity_id, asset_revision)
                REFERENCES assets (entity_id, revision)
                ON DELETE RESTRICT
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS shot_analyses (
            shot_entity_id TEXT NOT NULL,
            shot_revision INTEGER NOT NULL CHECK (shot_revision >= 1),
            analysis_revision INTEGER NOT NULL CHECK (analysis_revision >= 1),
            payload_json TEXT NOT NULL,
            PRIMARY KEY (shot_entity_id, shot_revision, analysis_revision),
            FOREIGN KEY (shot_entity_id, shot_revision)
                REFERENCES shots (entity_id, revision)
                ON DELETE RESTRICT
        )
        """
    )


def _create_v2_tables(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS project_migrations (
            migration_id TEXT NOT NULL PRIMARY KEY,
            from_version INTEGER NOT NULL CHECK (from_version >= 0),
            to_version INTEGER NOT NULL CHECK (to_version >= 1),
            applied_at TEXT NOT NULL
        )
        """
    )


def _record_migration(
    connection: sqlite3.Connection,
    *,
    from_version: int,
    to_version: int,
) -> None:
    migration_id = f"schema-{from_version}-to-{to_version}"
    connection.execute(
        """
        INSERT OR IGNORE INTO project_migrations (
            migration_id, from_version, to_version, applied_at
        ) VALUES (?, ?, ?, ?)
        """,
        (
            migration_id,
            from_version,
            to_version,
            datetime.now(UTC).isoformat(),
        ),
    )


class SqliteProjectDatabase:
    """Transactional schema/migration boundary for local revisioned structured records."""

    def __init__(self, path: pathlib.Path) -> None:
        self.path = path.expanduser().resolve()

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            current_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
            if current_version not in _SUPPORTED_SCHEMA_VERSIONS:
                raise UnsupportedSchemaVersionError(
                    f"unsupported SQLite schema version: {current_version}"
                )

            connection.execute("BEGIN IMMEDIATE")
            try:
                _create_core_tables(connection)
                _create_v2_tables(connection)
                if current_version < SCHEMA_VERSION:
                    _record_migration(
                        connection,
                        from_version=current_version,
                        to_version=SCHEMA_VERSION,
                    )
                    connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
                connection.execute("COMMIT")
            except BaseException:
                if connection.in_transaction:
                    connection.execute("ROLLBACK")
                raise

    def schema_version(self) -> int:
        with self._connect() as connection:
            return int(connection.execute("PRAGMA user_version").fetchone()[0])

    @contextmanager
    def read_connection(self) -> Iterator[sqlite3.Connection]:
        with self._connect() as connection:
            yield connection

    @contextmanager
    def write_connection(self) -> Iterator[sqlite3.Connection]:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                yield connection
                connection.execute("COMMIT")
            except BaseException:
                if connection.in_transaction:
                    connection.execute("ROLLBACK")
                raise

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, autocommit=True)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
        finally:
            connection.close()

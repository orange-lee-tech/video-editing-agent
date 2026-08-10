from __future__ import annotations

import pathlib
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

SCHEMA_VERSION = 1


class PersistenceError(RuntimeError):
    """Base error for local structured-record persistence."""


class UnsupportedSchemaVersionError(PersistenceError):
    """The database schema is newer or otherwise unsupported by this runtime."""


class SqliteProjectDatabase:
    """Schema/bootstrap boundary for local revisioned structured records."""

    def __init__(self, path: pathlib.Path) -> None:
        self.path = path.expanduser().resolve()

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            current_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
            if current_version not in (0, SCHEMA_VERSION):
                raise UnsupportedSchemaVersionError(
                    f"unsupported SQLite schema version: {current_version}"
                )

            connection.execute("BEGIN IMMEDIATE")
            try:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS assets (
                        entity_id TEXT NOT NULL,
                        revision INTEGER NOT NULL CHECK (revision >= 1),
                        payload_json TEXT NOT NULL,
                        PRIMARY KEY (entity_id, revision)
                    );

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
                    );

                    CREATE TABLE IF NOT EXISTS shot_analyses (
                        shot_entity_id TEXT NOT NULL,
                        shot_revision INTEGER NOT NULL CHECK (shot_revision >= 1),
                        analysis_revision INTEGER NOT NULL CHECK (analysis_revision >= 1),
                        payload_json TEXT NOT NULL,
                        PRIMARY KEY (shot_entity_id, shot_revision, analysis_revision),
                        FOREIGN KEY (shot_entity_id, shot_revision)
                            REFERENCES shots (entity_id, revision)
                            ON DELETE RESTRICT
                    );
                    """
                )
                if current_version == 0:
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

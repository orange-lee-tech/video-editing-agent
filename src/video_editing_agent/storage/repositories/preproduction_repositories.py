from __future__ import annotations

import sqlite3

from video_editing_agent.application.ports.brief_repository import BriefRepository
from video_editing_agent.application.ports.script_plan_repository import ScriptPlanRepository
from video_editing_agent.application.ports.shooting_plan_repository import ShootingPlanRepository
from video_editing_agent.domain.brief.model import Brief
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.script.model import ScriptPlan
from video_editing_agent.domain.shooting.model import ShootingPlan
from video_editing_agent.storage.repositories.preproduction_codec import (
    PreproductionPersistenceIntegrityError,
    decode_brief,
    decode_script_plan,
    decode_shooting_plan,
    encode_brief,
    encode_script_plan,
    encode_shooting_plan,
)
from video_editing_agent.storage.repositories.sqlite_database import (
    PersistenceError,
    SqliteProjectDatabase,
)


class PreproductionRevisionConflictError(PersistenceError):
    """An exact pre-production revision already exists with different immutable content."""


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
        raise PreproductionRevisionConflictError(
            f"{table} exact revision already exists with different content: {identity_values!r}"
        ) from exc


def _entity_ref(entity_id: str, revision: int) -> EntityRevisionRef:
    return EntityRevisionRef(entity_id=entity_id, revision=revision)


class SqliteBriefRepository(BriefRepository):
    def __init__(self, database: SqliteProjectDatabase) -> None:
        self._database = database

    def save(self, brief: Brief) -> None:
        payload = encode_brief(brief)
        identity = (brief.envelope.id, brief.envelope.revision)
        with self._database.write_connection() as connection:
            _save_immutable_record(
                connection,
                table="briefs",
                identity_columns=("entity_id", "revision"),
                identity_values=identity,
                insert_columns=("entity_id", "revision", "payload_json"),
                insert_values=(*identity, payload),
                payload_json=payload,
            )

    def load(self, brief_ref: EntityRevisionRef) -> Brief:
        with self._database.read_connection() as connection:
            row = connection.execute(
                "SELECT payload_json FROM briefs WHERE entity_id = ? AND revision = ?",
                (brief_ref.entity_id, brief_ref.revision),
            ).fetchone()
        if row is None:
            raise KeyError(brief_ref)
        brief = decode_brief(str(row["payload_json"]))
        actual_ref = _entity_ref(brief.envelope.id, brief.envelope.revision)
        if actual_ref != brief_ref:
            raise PreproductionPersistenceIntegrityError(
                f"Brief row identity {brief_ref!r} disagrees with payload {actual_ref!r}"
            )
        return brief


class SqliteScriptPlanRepository(ScriptPlanRepository):
    def __init__(self, database: SqliteProjectDatabase) -> None:
        self._database = database

    def save(self, script_plan: ScriptPlan) -> None:
        payload = encode_script_plan(script_plan)
        identity = (script_plan.envelope.id, script_plan.envelope.revision)
        with self._database.write_connection() as connection:
            _save_immutable_record(
                connection,
                table="script_plans",
                identity_columns=("entity_id", "revision"),
                identity_values=identity,
                insert_columns=(
                    "entity_id",
                    "revision",
                    "brief_entity_id",
                    "brief_revision",
                    "payload_json",
                ),
                insert_values=(
                    *identity,
                    script_plan.brief_ref.entity_id,
                    script_plan.brief_ref.revision,
                    payload,
                ),
                payload_json=payload,
            )

    def load(self, script_plan_ref: EntityRevisionRef) -> ScriptPlan:
        with self._database.read_connection() as connection:
            row = connection.execute(
                "SELECT payload_json FROM script_plans WHERE entity_id = ? AND revision = ?",
                (script_plan_ref.entity_id, script_plan_ref.revision),
            ).fetchone()
        if row is None:
            raise KeyError(script_plan_ref)
        script_plan = decode_script_plan(str(row["payload_json"]))
        actual_ref = _entity_ref(script_plan.envelope.id, script_plan.envelope.revision)
        if actual_ref != script_plan_ref:
            raise PreproductionPersistenceIntegrityError(
                f"ScriptPlan row identity {script_plan_ref!r} disagrees with payload {actual_ref!r}"
            )
        return script_plan


class SqliteShootingPlanRepository(ShootingPlanRepository):
    def __init__(self, database: SqliteProjectDatabase) -> None:
        self._database = database

    def save(self, shooting_plan: ShootingPlan) -> None:
        payload = encode_shooting_plan(shooting_plan)
        identity = (shooting_plan.envelope.id, shooting_plan.envelope.revision)
        with self._database.write_connection() as connection:
            _save_immutable_record(
                connection,
                table="shooting_plans",
                identity_columns=("entity_id", "revision"),
                identity_values=identity,
                insert_columns=(
                    "entity_id",
                    "revision",
                    "script_plan_entity_id",
                    "script_plan_revision",
                    "payload_json",
                ),
                insert_values=(
                    *identity,
                    shooting_plan.script_plan_ref.entity_id,
                    shooting_plan.script_plan_ref.revision,
                    payload,
                ),
                payload_json=payload,
            )

    def load(self, shooting_plan_ref: EntityRevisionRef) -> ShootingPlan:
        with self._database.read_connection() as connection:
            row = connection.execute(
                "SELECT payload_json FROM shooting_plans WHERE entity_id = ? AND revision = ?",
                (shooting_plan_ref.entity_id, shooting_plan_ref.revision),
            ).fetchone()
        if row is None:
            raise KeyError(shooting_plan_ref)
        shooting_plan = decode_shooting_plan(str(row["payload_json"]))
        actual_ref = _entity_ref(shooting_plan.envelope.id, shooting_plan.envelope.revision)
        if actual_ref != shooting_plan_ref:
            raise PreproductionPersistenceIntegrityError(
                f"ShootingPlan row identity {shooting_plan_ref!r} disagrees with "
                f"payload {actual_ref!r}"
            )
        return shooting_plan

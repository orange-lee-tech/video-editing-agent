from __future__ import annotations

import json
import sqlite3
from typing import Any

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.evidence.temporal import TemporalAnchor, TemporalEvidence
from video_editing_agent.storage.repositories.sqlite_database import (
    PersistenceError,
    SqliteProjectDatabase,
)


class TemporalEvidenceConflictError(PersistenceError):
    """An immutable temporal identity already exists with different content."""


def _insert_immutable(
    connection: sqlite3.Connection,
    *,
    table: str,
    identity: str,
    values: tuple[object, ...],
    payload: str,
) -> None:
    try:
        connection.execute(f"INSERT INTO {table} VALUES (?, ?, ?, ?)", values)
    except sqlite3.IntegrityError as exc:
        key = "evidence_id" if table == "temporal_evidence" else "anchor_id"
        row = connection.execute(
            f"SELECT payload_json FROM {table} WHERE {key} = ?", (identity,)
        ).fetchone()
        if row is not None and str(row["payload_json"]) == payload:
            return
        raise TemporalEvidenceConflictError(
            f"{table} identity already exists with different immutable content: {identity}"
        ) from exc


def _time(value: MediaTime) -> dict[str, int]:
    return {"value": value.value, "scale": value.scale}


def _decode_time(value: dict[str, Any]) -> MediaTime:
    return MediaTime(value["value"], value["scale"])


def _encode_evidence(evidence: TemporalEvidence) -> str:
    payload = {
        "evidence_id": evidence.evidence_id,
        "shot_ref": {
            "entity_id": evidence.shot_ref.entity_id,
            "revision": evidence.shot_ref.revision,
        },
        "kind": evidence.kind,
        "method": evidence.method,
        "producer_version": evidence.producer_version,
        "confidence": evidence.confidence,
        "source_range": None
        if evidence.source_range is None
        else {
            "start": _time(evidence.source_range.start),
            "duration": _time(evidence.source_range.duration),
        },
        "artifact_refs": list(evidence.artifact_refs),
        "source_refs": list(evidence.source_refs),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _encode_anchor(anchor: TemporalAnchor) -> str:
    return json.dumps(
        {
            "anchor_id": anchor.anchor_id,
            "shot_ref": {
                "entity_id": anchor.shot_ref.entity_id,
                "revision": anchor.shot_ref.revision,
            },
            "kind": anchor.kind,
            "source_time": _time(anchor.source_time),
            "confidence": anchor.confidence,
            "evidence_refs": list(anchor.evidence_refs),
            "method": anchor.method,
            "semantic_label": anchor.semantic_label,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


class SqliteTemporalEvidenceRepository:
    def __init__(self, database: SqliteProjectDatabase) -> None:
        self._database = database

    def save_evidence(self, evidence: TemporalEvidence) -> None:
        self.save_evidence_batch((evidence,))

    def save_evidence_batch(self, evidence: tuple[TemporalEvidence, ...]) -> None:
        if not evidence:
            return
        with self._database.write_connection() as connection:
            for item in evidence:
                encoded = _encode_evidence(item)
                _insert_immutable(
                    connection,
                    table="temporal_evidence",
                    identity=item.evidence_id,
                    values=(
                        item.evidence_id,
                        item.shot_ref.entity_id,
                        item.shot_ref.revision,
                        encoded,
                    ),
                    payload=encoded,
                )

    def save_anchor(self, anchor: TemporalAnchor) -> None:
        self.save_evidence_and_anchors((), (anchor,))

    def save_evidence_and_anchors(
        self, evidence: tuple[TemporalEvidence, ...], anchors: tuple[TemporalAnchor, ...]
    ) -> None:
        with self._database.write_connection() as connection:
            for item in evidence:
                encoded = _encode_evidence(item)
                _insert_immutable(
                    connection,
                    table="temporal_evidence",
                    identity=item.evidence_id,
                    values=(
                        item.evidence_id,
                        item.shot_ref.entity_id,
                        item.shot_ref.revision,
                        encoded,
                    ),
                    payload=encoded,
                )
            for anchor in anchors:
                for evidence_ref in anchor.evidence_refs:
                    row = connection.execute(
                        "SELECT 1 FROM temporal_evidence WHERE evidence_id = ? "
                        "AND shot_entity_id = ? AND shot_revision = ?",
                        (evidence_ref, anchor.shot_ref.entity_id, anchor.shot_ref.revision),
                    ).fetchone()
                    if row is None:
                        raise ValueError(
                            f"unknown evidence reference for exact Shot: {evidence_ref}"
                        )
                encoded = _encode_anchor(anchor)
                _insert_immutable(
                    connection,
                    table="temporal_anchors",
                    identity=anchor.anchor_id,
                    values=(
                        anchor.anchor_id,
                        anchor.shot_ref.entity_id,
                        anchor.shot_ref.revision,
                        encoded,
                    ),
                    payload=encoded,
                )

    def list_evidence(self, shot_ref: EntityRevisionRef) -> tuple[TemporalEvidence, ...]:
        with self._database.read_connection() as connection:
            rows = connection.execute(
                "SELECT payload_json FROM temporal_evidence "
                "WHERE shot_entity_id = ? AND shot_revision = ? ORDER BY evidence_id",
                (shot_ref.entity_id, shot_ref.revision),
            ).fetchall()
        return tuple(self._decode_evidence(json.loads(row["payload_json"])) for row in rows)

    def list_anchors(self, shot_ref: EntityRevisionRef) -> tuple[TemporalAnchor, ...]:
        with self._database.read_connection() as connection:
            rows = connection.execute(
                "SELECT payload_json FROM temporal_anchors "
                "WHERE shot_entity_id = ? AND shot_revision = ? ORDER BY anchor_id",
                (shot_ref.entity_id, shot_ref.revision),
            ).fetchall()
        return tuple(self._decode_anchor(json.loads(row["payload_json"])) for row in rows)

    @staticmethod
    def _decode_evidence(value: dict[str, Any]) -> TemporalEvidence:
        shot = value["shot_ref"]
        source = value["source_range"]
        return TemporalEvidence(
            value["evidence_id"],
            EntityRevisionRef(shot["entity_id"], shot["revision"]),
            value["kind"],
            value["method"],
            value["producer_version"],
            value["confidence"],
            None
            if source is None
            else MediaTimeRange(_decode_time(source["start"]), _decode_time(source["duration"])),
            tuple(value["artifact_refs"]),
            tuple(value["source_refs"]),
        )

    @staticmethod
    def _decode_anchor(value: dict[str, Any]) -> TemporalAnchor:
        shot = value["shot_ref"]
        return TemporalAnchor(
            value["anchor_id"],
            EntityRevisionRef(shot["entity_id"], shot["revision"]),
            value["kind"],
            _decode_time(value["source_time"]),
            value["confidence"],
            tuple(value["evidence_refs"]),
            value["method"],
            value["semantic_label"],
        )

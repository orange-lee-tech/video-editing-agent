from __future__ import annotations

import json
from typing import Any

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.evidence.temporal import TemporalAnchor, TemporalEvidence
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase


def _time(value: MediaTime) -> dict[str, int]:
    return {"value": value.value, "scale": value.scale}


def _decode_time(value: dict[str, Any]) -> MediaTime:
    return MediaTime(value["value"], value["scale"])


class SqliteTemporalEvidenceRepository:
    def __init__(self, database: SqliteProjectDatabase) -> None:
        self._database = database

    def save_evidence(self, evidence: TemporalEvidence) -> None:
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
        with self._database.write_connection() as connection:
            connection.execute(
                "INSERT INTO temporal_evidence VALUES (?, ?, ?, ?)",
                (
                    evidence.evidence_id,
                    evidence.shot_ref.entity_id,
                    evidence.shot_ref.revision,
                    json.dumps(payload, sort_keys=True, separators=(",", ":")),
                ),
            )

    def save_anchor(self, anchor: TemporalAnchor) -> None:
        payload = {
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
        }
        with self._database.write_connection() as connection:
            for evidence_ref in anchor.evidence_refs:
                row = connection.execute(
                    "SELECT 1 FROM temporal_evidence WHERE evidence_id = ? "
                    "AND shot_entity_id = ? AND shot_revision = ?",
                    (evidence_ref, anchor.shot_ref.entity_id, anchor.shot_ref.revision),
                ).fetchone()
                if row is None:
                    raise ValueError(f"unknown evidence reference for exact Shot: {evidence_ref}")
            connection.execute(
                "INSERT INTO temporal_anchors VALUES (?, ?, ?, ?)",
                (
                    anchor.anchor_id,
                    anchor.shot_ref.entity_id,
                    anchor.shot_ref.revision,
                    json.dumps(payload, sort_keys=True, separators=(",", ":")),
                ),
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

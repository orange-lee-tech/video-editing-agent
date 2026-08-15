from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.edit.model import DurationConstraint, EditPlan, EditSlot
from video_editing_agent.storage.repositories.record_codec import PersistenceIntegrityError

EDIT_PLAN_CODEC_VERSION = 1


def _ref(value: EntityRevisionRef | None) -> dict[str, object] | None:
    return None if value is None else {"entity_id": value.entity_id, "revision": value.revision}


def _time(value: MediaTime) -> dict[str, int]:
    return {"value": value.value, "scale": value.scale}


def encode_edit_plan(plan: EditPlan) -> str:
    payload = {
        "codec_version": EDIT_PLAN_CODEC_VERSION,
        "record_type": "edit_plan",
        "envelope": {
            "id": plan.envelope.id,
            "revision": plan.envelope.revision,
            "schema_version": plan.envelope.schema_version,
            "status": plan.envelope.status.value,
            "created_at": plan.envelope.created_at.isoformat(),
            "created_by": plan.envelope.created_by,
            "derived_from": [_ref(value) for value in plan.envelope.derived_from],
        },
        "brief_ref": _ref(plan.brief_ref),
        "script_plan_ref": _ref(plan.script_plan_ref),
        "shooting_plan_ref": _ref(plan.shooting_plan_ref),
        "slots": [
            {
                "slot_id": slot.slot_id,
                "purpose": slot.purpose,
                "order": slot.order,
                "narrative_role": slot.narrative_role,
                "semantic_query": slot.semantic_query,
                "target_duration": None
                if slot.target_duration is None
                else {
                    "minimum": _time(slot.target_duration.minimum),
                    "maximum": _time(slot.target_duration.maximum),
                },
                "pacing": slot.pacing,
                "continuity_hint": slot.continuity_hint,
                "allow_reuse": slot.allow_reuse,
                "importance": slot.importance,
            }
            for slot in plan.slots
        ],
    }
    return json.dumps(
        payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    )


def _object(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PersistenceIntegrityError(f"{name} must be an object")
    return value


def _decode_ref(value: object, name: str) -> EntityRevisionRef | None:
    if value is None:
        return None
    raw = _object(value, name)
    return EntityRevisionRef(str(raw["entity_id"]), int(raw["revision"]))


def _decode_time(value: object, name: str) -> MediaTime:
    raw = _object(value, name)
    return MediaTime(int(raw["value"]), int(raw["scale"]))


def decode_edit_plan(payload: str) -> EditPlan:
    try:
        value = _object(json.loads(payload), "EditPlan")
        if (
            value.get("codec_version") != EDIT_PLAN_CODEC_VERSION
            or value.get("record_type") != "edit_plan"
        ):
            raise PersistenceIntegrityError("unsupported EditPlan codec payload")
        envelope = _object(value.get("envelope"), "EditPlan envelope")
        derived_raw = envelope.get("derived_from")
        slots_raw = value.get("slots")
        if not isinstance(derived_raw, list) or not isinstance(slots_raw, list):
            raise PersistenceIntegrityError("EditPlan derived_from/slots must be arrays")
        slots = []
        for raw_slot in slots_raw:
            slot = _object(raw_slot, "EditSlot")
            duration_raw = slot.get("target_duration")
            duration = None
            if duration_raw is not None:
                duration_value = _object(duration_raw, "EditSlot target_duration")
                duration = DurationConstraint(
                    _decode_time(duration_value.get("minimum"), "minimum duration"),
                    _decode_time(duration_value.get("maximum"), "maximum duration"),
                )
            slots.append(
                EditSlot(
                    str(slot["slot_id"]),
                    str(slot["purpose"]),
                    int(slot["order"]),
                    str(slot["narrative_role"]),
                    str(slot["semantic_query"]),
                    duration,
                    str(slot["pacing"]),
                    None if slot.get("continuity_hint") is None else str(slot["continuity_hint"]),
                    bool(slot["allow_reuse"]),
                    int(slot["importance"]),
                )
            )
        return EditPlan(
            EntityEnvelope(
                str(envelope["id"]),
                int(envelope["revision"]),
                str(envelope["schema_version"]),
                EntityStatus(str(envelope["status"])),
                datetime.fromisoformat(str(envelope["created_at"])),
                str(envelope["created_by"]),
                tuple(ref for item in derived_raw if (ref := _decode_ref(item, "derived ref"))),
            ),
            _decode_ref(value.get("script_plan_ref"), "script_plan_ref"),
            _decode_ref(value.get("shooting_plan_ref"), "shooting_plan_ref"),
            tuple(slots),
            brief_ref=_decode_ref(value.get("brief_ref"), "brief_ref"),
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        if isinstance(exc, PersistenceIntegrityError):
            raise
        raise PersistenceIntegrityError("invalid EditPlan persistence payload") from exc

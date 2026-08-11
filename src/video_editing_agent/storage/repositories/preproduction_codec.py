from __future__ import annotations

import json
from datetime import datetime
from typing import Any, cast

from video_editing_agent.domain.brief.model import AuthoritativeFact, Brief, BriefReference
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.script.model import NarrativeSection, ScriptPlan
from video_editing_agent.domain.shooting.model import (
    CoveragePriority,
    ProductionConstraints,
    ProductionLocation,
    ShootingPlan,
    ShotRequirement,
)
from video_editing_agent.storage.repositories.sqlite_database import PersistenceError

PREPRODUCTION_CODEC_VERSION = 1
SHOOTING_PLAN_CODEC_VERSION = 2


class PreproductionPersistenceIntegrityError(PersistenceError):
    """Persisted pre-production payload is malformed or internally inconsistent."""


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _ref_payload(value: EntityRevisionRef) -> dict[str, object]:
    return {"entity_id": value.entity_id, "revision": value.revision}


def _optional_ref_payload(value: EntityRevisionRef | None) -> dict[str, object] | None:
    return None if value is None else _ref_payload(value)


def _ref_from_payload(value: object) -> EntityRevisionRef:
    if not isinstance(value, dict):
        raise PreproductionPersistenceIntegrityError("EntityRevisionRef payload must be an object")
    typed = cast(dict[str, Any], value)
    return EntityRevisionRef(entity_id=str(typed["entity_id"]), revision=int(typed["revision"]))


def _optional_ref_from_payload(value: object) -> EntityRevisionRef | None:
    return None if value is None else _ref_from_payload(value)


def _time_payload(value: MediaTime) -> dict[str, int]:
    return {"value": value.value, "scale": value.scale}


def _optional_time_payload(value: MediaTime | None) -> dict[str, int] | None:
    return None if value is None else _time_payload(value)


def _optional_time_from_payload(value: object) -> MediaTime | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise PreproductionPersistenceIntegrityError("MediaTime payload must be an object or null")
    typed = cast(dict[str, Any], value)
    return MediaTime(value=int(typed["value"]), scale=int(typed["scale"]))


def _envelope_payload(value: EntityEnvelope) -> dict[str, object]:
    return {
        "id": value.id,
        "revision": value.revision,
        "schema_version": value.schema_version,
        "status": value.status.value,
        "created_at": value.created_at.isoformat(),
        "created_by": value.created_by,
        "derived_from": [_ref_payload(item) for item in value.derived_from],
    }


def _envelope_from_payload(value: object) -> EntityEnvelope:
    if not isinstance(value, dict):
        raise PreproductionPersistenceIntegrityError("EntityEnvelope payload must be an object")
    typed = cast(dict[str, Any], value)
    derived_from = typed.get("derived_from", [])
    if not isinstance(derived_from, list):
        raise PreproductionPersistenceIntegrityError("EntityEnvelope derived_from must be a list")
    return EntityEnvelope(
        id=str(typed["id"]),
        revision=int(typed["revision"]),
        schema_version=str(typed["schema_version"]),
        status=EntityStatus(str(typed["status"])),
        created_at=datetime.fromisoformat(str(typed["created_at"])),
        created_by=str(typed["created_by"]),
        derived_from=tuple(_ref_from_payload(item) for item in derived_from),
    )


def _require_record(
    value: dict[str, Any],
    record_type: str,
    *,
    supported_versions: tuple[int, ...] = (PREPRODUCTION_CODEC_VERSION,),
) -> int:
    codec_version = value.get("codec_version")
    if isinstance(codec_version, bool) or not isinstance(codec_version, int):
        raise PreproductionPersistenceIntegrityError(
            f"unsupported {record_type} codec version: {codec_version!r}"
        )
    if codec_version not in supported_versions:
        raise PreproductionPersistenceIntegrityError(
            f"unsupported {record_type} codec version: {codec_version!r}"
        )
    if value.get("record_type") != record_type:
        raise PreproductionPersistenceIntegrityError(
            f"expected {record_type} payload, found {value.get('record_type')!r}"
        )
    return codec_version


def _string_tuple(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise PreproductionPersistenceIntegrityError(f"{field_name} must be an array of strings")
    return tuple(value)


def encode_brief(brief: Brief) -> str:
    return _canonical_json(
        {
            "codec_version": PREPRODUCTION_CODEC_VERSION,
            "record_type": "brief",
            "envelope": _envelope_payload(brief.envelope),
            "title": brief.title,
            "objective": brief.objective,
            "audience": brief.audience,
            "platform": brief.platform,
            "core_message": brief.core_message,
            "product_topic": brief.product_topic,
            "target_duration": _optional_time_payload(brief.target_duration),
            "authoritative_facts": [
                {
                    "fact_id": fact.fact_id,
                    "statement": fact.statement,
                    "source_note": fact.source_note,
                }
                for fact in brief.authoritative_facts
            ],
            "style_emotion": list(brief.style_emotion),
            "success_criteria": list(brief.success_criteria),
            "prohibited_content": list(brief.prohibited_content),
            "brand_constraints": list(brief.brand_constraints),
            "user_notes": brief.user_notes,
            "references": [
                {
                    "reference_id": reference.reference_id,
                    "kind": reference.kind,
                    "description": reference.description,
                    "asset_ref": _optional_ref_payload(reference.asset_ref),
                }
                for reference in brief.references
            ],
        }
    )


def decode_brief(payload: str) -> Brief:
    raw: Any = json.loads(payload)
    if not isinstance(raw, dict):
        raise PreproductionPersistenceIntegrityError("Brief payload must be an object")
    value = cast(dict[str, Any], raw)
    _require_record(value, "brief")

    fact_values = value.get("authoritative_facts", [])
    reference_values = value.get("references", [])
    if not isinstance(fact_values, list) or not all(isinstance(item, dict) for item in fact_values):
        raise PreproductionPersistenceIntegrityError(
            "authoritative_facts must be an array of objects"
        )
    if not isinstance(reference_values, list) or not all(
        isinstance(item, dict) for item in reference_values
    ):
        raise PreproductionPersistenceIntegrityError("references must be an array of objects")

    return Brief(
        envelope=_envelope_from_payload(value["envelope"]),
        title=str(value["title"]),
        objective=str(value["objective"]),
        audience=str(value["audience"]),
        platform=str(value["platform"]),
        core_message=str(value["core_message"]),
        product_topic=cast(str | None, value.get("product_topic")),
        target_duration=_optional_time_from_payload(value.get("target_duration")),
        authoritative_facts=tuple(
            AuthoritativeFact(
                fact_id=str(item["fact_id"]),
                statement=str(item["statement"]),
                source_note=cast(str | None, item.get("source_note")),
            )
            for item in cast(list[dict[str, Any]], fact_values)
        ),
        style_emotion=_string_tuple(value.get("style_emotion", []), "style_emotion"),
        success_criteria=_string_tuple(value.get("success_criteria", []), "success_criteria"),
        prohibited_content=_string_tuple(value.get("prohibited_content", []), "prohibited_content"),
        brand_constraints=_string_tuple(value.get("brand_constraints", []), "brand_constraints"),
        user_notes=cast(str | None, value.get("user_notes")),
        references=tuple(
            BriefReference(
                reference_id=str(item["reference_id"]),
                kind=str(item["kind"]),
                description=str(item["description"]),
                asset_ref=_optional_ref_from_payload(item.get("asset_ref")),
            )
            for item in cast(list[dict[str, Any]], reference_values)
        ),
    )


def _section_payload(section: NarrativeSection) -> dict[str, object]:
    return {
        "section_id": section.section_id,
        "narrative_role": section.narrative_role,
        "information_goal": section.information_goal,
        "spoken_content": section.spoken_content,
        "visual_requirement": section.visual_requirement,
        "target_duration": _optional_time_payload(section.target_duration),
        "on_screen_text_intent": section.on_screen_text_intent,
        "emotion": section.emotion,
        "pacing": section.pacing,
        "music_intent": section.music_intent,
        "editing_intent": section.editing_intent,
        "importance": section.importance,
        "protected_fact_ids": list(section.protected_fact_ids),
        "locked": section.locked,
    }


def _section_from_payload(value: object) -> NarrativeSection:
    if not isinstance(value, dict):
        raise PreproductionPersistenceIntegrityError("NarrativeSection payload must be an object")
    typed = cast(dict[str, Any], value)
    locked = typed.get("locked", False)
    if not isinstance(locked, bool):
        raise PreproductionPersistenceIntegrityError("NarrativeSection locked must be a bool")
    return NarrativeSection(
        section_id=str(typed["section_id"]),
        narrative_role=str(typed["narrative_role"]),
        information_goal=str(typed["information_goal"]),
        spoken_content=cast(str | None, typed.get("spoken_content")),
        visual_requirement=cast(str | None, typed.get("visual_requirement")),
        target_duration=_optional_time_from_payload(typed.get("target_duration")),
        on_screen_text_intent=cast(str | None, typed.get("on_screen_text_intent")),
        emotion=cast(str | None, typed.get("emotion")),
        pacing=cast(str | None, typed.get("pacing")),
        music_intent=cast(str | None, typed.get("music_intent")),
        editing_intent=cast(str | None, typed.get("editing_intent")),
        importance=cast(str | None, typed.get("importance")),
        protected_fact_ids=_string_tuple(typed.get("protected_fact_ids", []), "protected_fact_ids"),
        locked=locked,
    )


def encode_script_plan(script_plan: ScriptPlan) -> str:
    return _canonical_json(
        {
            "codec_version": PREPRODUCTION_CODEC_VERSION,
            "record_type": "script_plan",
            "envelope": _envelope_payload(script_plan.envelope),
            "brief_ref": _ref_payload(script_plan.brief_ref),
            "sections": [_section_payload(section) for section in script_plan.sections],
        }
    )


def decode_script_plan(payload: str) -> ScriptPlan:
    raw: Any = json.loads(payload)
    if not isinstance(raw, dict):
        raise PreproductionPersistenceIntegrityError("ScriptPlan payload must be an object")
    value = cast(dict[str, Any], raw)
    _require_record(value, "script_plan")
    sections = value.get("sections", [])
    if not isinstance(sections, list):
        raise PreproductionPersistenceIntegrityError("ScriptPlan sections must be an array")
    return ScriptPlan(
        envelope=_envelope_from_payload(value["envelope"]),
        brief_ref=_ref_from_payload(value["brief_ref"]),
        sections=tuple(_section_from_payload(item) for item in sections),
    )


def _location_payload(value: ProductionLocation) -> dict[str, object]:
    return {
        "location_id": value.location_id,
        "label": value.label,
        "notes": value.notes,
    }


def _locations_from_payload(value: object, *, codec_version: int) -> tuple[ProductionLocation, ...]:
    if not isinstance(value, list):
        raise PreproductionPersistenceIntegrityError("locations must be an array")
    if codec_version == 1:
        if any(not isinstance(item, str) for item in value):
            raise PreproductionPersistenceIntegrityError(
                "legacy shooting locations must be an array of strings"
            )
        return tuple(
            ProductionLocation(location_id=f"loc_legacy_{index + 1:03d}", label=item)
            for index, item in enumerate(cast(list[str], value))
        )
    locations: list[ProductionLocation] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise PreproductionPersistenceIntegrityError(
                f"locations[{index}] must be a ProductionLocation object"
            )
        typed = cast(dict[str, Any], item)
        if set(typed) != {"location_id", "label", "notes"}:
            raise PreproductionPersistenceIntegrityError(
                f"locations[{index}] must contain exactly location_id, label, and notes"
            )
        notes = typed["notes"]
        if notes is not None and not isinstance(notes, str):
            raise PreproductionPersistenceIntegrityError(
                f"locations[{index}].notes must be a string or null"
            )
        locations.append(
            ProductionLocation(
                location_id=str(typed["location_id"]),
                label=str(typed["label"]),
                notes=notes,
            )
        )
    return tuple(locations)


def _constraints_payload(value: ProductionConstraints) -> dict[str, object]:
    return {
        "camera_or_phone": value.camera_or_phone,
        "stabilizer": value.stabilizer,
        "lighting": value.lighting,
        "microphones": list(value.microphones),
        "people_count": value.people_count,
        "locations": [_location_payload(location) for location in value.locations],
        "available_time_notes": value.available_time_notes,
        "user_skill_level": value.user_skill_level,
        "notes": list(value.notes),
    }


def _constraints_from_payload(value: object, *, codec_version: int) -> ProductionConstraints:
    if not isinstance(value, dict):
        raise PreproductionPersistenceIntegrityError(
            "ProductionConstraints payload must be an object"
        )
    typed = cast(dict[str, Any], value)
    people_count = typed.get("people_count")
    if people_count is not None and (
        isinstance(people_count, bool) or not isinstance(people_count, int)
    ):
        raise PreproductionPersistenceIntegrityError("people_count must be an int or null")
    return ProductionConstraints(
        camera_or_phone=cast(str | None, typed.get("camera_or_phone")),
        stabilizer=cast(str | None, typed.get("stabilizer")),
        lighting=cast(str | None, typed.get("lighting")),
        microphones=_string_tuple(typed.get("microphones", []), "microphones"),
        people_count=people_count,
        locations=_locations_from_payload(typed.get("locations", []), codec_version=codec_version),
        available_time_notes=cast(str | None, typed.get("available_time_notes")),
        user_skill_level=cast(str | None, typed.get("user_skill_level")),
        notes=_string_tuple(typed.get("notes", []), "notes"),
    )


def _requirement_payload(value: ShotRequirement) -> dict[str, object]:
    return {
        "requirement_id": value.requirement_id,
        "script_section_ref": value.script_section_ref,
        "purpose": value.purpose,
        "subject": value.subject,
        "action": value.action,
        "location_ref": value.location_ref,
        "environment_description": value.environment_description,
        "framing": value.framing,
        "camera_motion": value.camera_motion,
        "target_duration": _optional_time_payload(value.target_duration),
        "minimum_duration": _optional_time_payload(value.minimum_duration),
        "audio_dialogue_requirement": value.audio_dialogue_requirement,
        "continuity_hint": value.continuity_hint,
        "visual_constraints": list(value.visual_constraints),
        "priority": value.priority.value,
        "backup_intent": value.backup_intent,
        "capture_instruction": value.capture_instruction,
        "alternate_coverage": list(value.alternate_coverage),
        "handle_before": _optional_time_payload(value.handle_before),
        "handle_after": _optional_time_payload(value.handle_after),
    }


def _requirement_from_payload(value: object, *, codec_version: int) -> ShotRequirement:
    if not isinstance(value, dict):
        raise PreproductionPersistenceIntegrityError("ShotRequirement payload must be an object")
    typed = cast(dict[str, Any], value)
    try:
        priority = CoveragePriority(str(typed["priority"]))
    except (KeyError, ValueError) as exc:
        raise PreproductionPersistenceIntegrityError("invalid ShotRequirement priority") from exc
    if codec_version == 1:
        location_ref = None
        environment_description = cast(str | None, typed.get("environment"))
    else:
        location_ref = cast(str | None, typed.get("location_ref"))
        environment_description = cast(str | None, typed.get("environment_description"))
    return ShotRequirement(
        requirement_id=str(typed["requirement_id"]),
        script_section_ref=str(typed["script_section_ref"]),
        purpose=str(typed["purpose"]),
        subject=str(typed["subject"]),
        action=cast(str | None, typed.get("action")),
        location_ref=location_ref,
        environment_description=environment_description,
        framing=cast(str | None, typed.get("framing")),
        camera_motion=cast(str | None, typed.get("camera_motion")),
        target_duration=_optional_time_from_payload(typed.get("target_duration")),
        minimum_duration=_optional_time_from_payload(typed.get("minimum_duration")),
        audio_dialogue_requirement=cast(str | None, typed.get("audio_dialogue_requirement")),
        continuity_hint=cast(str | None, typed.get("continuity_hint")),
        visual_constraints=_string_tuple(typed.get("visual_constraints", []), "visual_constraints"),
        priority=priority,
        backup_intent=cast(str | None, typed.get("backup_intent")),
        capture_instruction=cast(str | None, typed.get("capture_instruction")),
        alternate_coverage=_string_tuple(typed.get("alternate_coverage", []), "alternate_coverage"),
        handle_before=_optional_time_from_payload(typed.get("handle_before")),
        handle_after=_optional_time_from_payload(typed.get("handle_after")),
    )


def encode_shooting_plan(shooting_plan: ShootingPlan) -> str:
    return _canonical_json(
        {
            "codec_version": SHOOTING_PLAN_CODEC_VERSION,
            "record_type": "shooting_plan",
            "envelope": _envelope_payload(shooting_plan.envelope),
            "script_plan_ref": _ref_payload(shooting_plan.script_plan_ref),
            "requirements": [
                _requirement_payload(requirement) for requirement in shooting_plan.requirements
            ],
            "constraints": _constraints_payload(shooting_plan.constraints),
            "notes": list(shooting_plan.notes),
        }
    )


def decode_shooting_plan(payload: str) -> ShootingPlan:
    raw: Any = json.loads(payload)
    if not isinstance(raw, dict):
        raise PreproductionPersistenceIntegrityError("ShootingPlan payload must be an object")
    value = cast(dict[str, Any], raw)
    codec_version = _require_record(
        value,
        "shooting_plan",
        supported_versions=(PREPRODUCTION_CODEC_VERSION, SHOOTING_PLAN_CODEC_VERSION),
    )
    requirements = value.get("requirements", [])
    if not isinstance(requirements, list):
        raise PreproductionPersistenceIntegrityError("ShootingPlan requirements must be an array")
    constraints = _constraints_from_payload(
        value.get("constraints", {}),
        codec_version=codec_version,
    )
    return ShootingPlan(
        envelope=_envelope_from_payload(value["envelope"]),
        script_plan_ref=_ref_from_payload(value["script_plan_ref"]),
        requirements=tuple(
            _requirement_from_payload(item, codec_version=codec_version) for item in requirements
        ),
        constraints=constraints,
        notes=_string_tuple(value.get("notes", []), "notes"),
    )

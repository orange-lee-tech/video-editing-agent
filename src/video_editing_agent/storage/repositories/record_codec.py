from __future__ import annotations

import json
from datetime import datetime
from typing import Any, cast

from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.asset.policy import AssetUsageRole, default_asset_usage_role
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.shot.analysis import (
    AnalysisProfile,
    NamedQualityScore,
    ShotAnalysis,
    SpeechContent,
    VisualSemantics,
)
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.storage.repositories.sqlite_database import PersistenceError

CODEC_VERSION = 2
_SUPPORTED_CODEC_VERSIONS = frozenset({1, CODEC_VERSION})


class PersistenceIntegrityError(PersistenceError):
    """Persisted identity columns and encoded record content disagree."""


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _datetime_text(value: datetime) -> str:
    return value.isoformat()


def _optional_datetime_text(value: datetime | None) -> str | None:
    return None if value is None else _datetime_text(value)


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _optional_parse_datetime(value: str | None) -> datetime | None:
    return None if value is None else _parse_datetime(value)


def _ref_payload(value: EntityRevisionRef) -> dict[str, object]:
    return {"entity_id": value.entity_id, "revision": value.revision}


def _optional_ref_payload(value: EntityRevisionRef | None) -> dict[str, object] | None:
    return None if value is None else _ref_payload(value)


def _ref_from_payload(value: dict[str, Any]) -> EntityRevisionRef:
    return EntityRevisionRef(entity_id=str(value["entity_id"]), revision=int(value["revision"]))


def _optional_ref_from_payload(value: dict[str, Any] | None) -> EntityRevisionRef | None:
    return None if value is None else _ref_from_payload(value)


def _media_time_payload(value: MediaTime) -> dict[str, int]:
    return {"value": value.value, "scale": value.scale}


def _optional_media_time_payload(value: MediaTime | None) -> dict[str, int] | None:
    return None if value is None else _media_time_payload(value)


def _media_time_from_payload(value: dict[str, Any]) -> MediaTime:
    return MediaTime(value=int(value["value"]), scale=int(value["scale"]))


def _optional_media_time_from_payload(value: object) -> MediaTime | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise PersistenceIntegrityError("MediaTime payload must be an object or null")
    return _media_time_from_payload(cast(dict[str, Any], value))


def _media_time_range_payload(value: MediaTimeRange) -> dict[str, object]:
    return {
        "start": _media_time_payload(value.start),
        "duration": _media_time_payload(value.duration),
    }


def _media_time_range_from_payload(value: dict[str, Any]) -> MediaTimeRange:
    start = value.get("start")
    duration = value.get("duration")
    if not isinstance(start, dict) or not isinstance(duration, dict):
        raise PersistenceIntegrityError("MediaTimeRange start/duration must be objects")
    return MediaTimeRange(
        start=_media_time_from_payload(cast(dict[str, Any], start)),
        duration=_media_time_from_payload(cast(dict[str, Any], duration)),
    )


def _envelope_payload(value: EntityEnvelope) -> dict[str, object]:
    return {
        "id": value.id,
        "revision": value.revision,
        "schema_version": value.schema_version,
        "status": value.status.value,
        "created_at": _datetime_text(value.created_at),
        "created_by": value.created_by,
        "derived_from": [_ref_payload(item) for item in value.derived_from],
    }


def _envelope_from_payload(value: dict[str, Any]) -> EntityEnvelope:
    derived_from_payload = value.get("derived_from", [])
    if not isinstance(derived_from_payload, list):
        raise PersistenceIntegrityError("EntityEnvelope derived_from must be a list")
    return EntityEnvelope(
        id=str(value["id"]),
        revision=int(value["revision"]),
        schema_version=str(value["schema_version"]),
        status=EntityStatus(str(value["status"])),
        created_at=_parse_datetime(str(value["created_at"])),
        created_by=str(value["created_by"]),
        derived_from=tuple(_ref_from_payload(item) for item in derived_from_payload),
    )


def _codec_version(value: dict[str, Any], record_type: str) -> int:
    raw_version = value.get("codec_version")
    if isinstance(raw_version, bool) or not isinstance(raw_version, int):
        raise PersistenceIntegrityError(f"invalid {record_type} codec version: {raw_version!r}")
    if raw_version not in _SUPPORTED_CODEC_VERSIONS:
        raise PersistenceIntegrityError(f"unsupported {record_type} codec version: {raw_version!r}")
    if value.get("record_type") != record_type:
        raise PersistenceIntegrityError(
            f"expected {record_type} payload, found {value.get('record_type')!r}"
        )
    return raw_version


def _provenance_payload(value: AssetProvenance) -> dict[str, object]:
    return {
        "origin_type": value.origin_type,
        "provider": value.provider,
        "provider_asset_id": value.provider_asset_id,
        "source_page": value.source_page,
        "creator": value.creator,
        "retrieved_at": _optional_datetime_text(value.retrieved_at),
        "license_information": value.license_information,
        "attribution": value.attribution,
    }


def _provenance_from_payload(value: dict[str, Any]) -> AssetProvenance:
    return AssetProvenance(
        origin_type=str(value["origin_type"]),
        provider=value.get("provider"),
        provider_asset_id=value.get("provider_asset_id"),
        source_page=value.get("source_page"),
        creator=value.get("creator"),
        retrieved_at=_optional_parse_datetime(cast(str | None, value.get("retrieved_at"))),
        license_information=value.get("license_information"),
        attribution=value.get("attribution"),
    )


def encode_asset(asset: Asset) -> str:
    return _canonical_json(
        {
            "codec_version": CODEC_VERSION,
            "record_type": "asset",
            "envelope": _envelope_payload(asset.envelope),
            "media_kind": asset.media_kind,
            "origin": asset.origin,
            "usage_role": asset.usage_role.value,
            "storage_ref": asset.storage_ref,
            "content_hash": asset.content_hash,
            "byte_size": asset.byte_size,
            "provenance": _provenance_payload(asset.provenance),
            "imported_at": _datetime_text(asset.imported_at),
            "duration": _optional_media_time_payload(asset.duration),
            "width": asset.width,
            "height": asset.height,
            "fps": asset.fps,
            "codec": asset.codec,
            "audio_channels": asset.audio_channels,
            "sample_rate_hz": asset.sample_rate_hz,
            "user_labels": list(asset.user_labels),
            "collection_refs": list(asset.collection_refs),
        }
    )


def decode_asset(payload: str) -> Asset:
    value: dict[str, Any] = json.loads(payload)
    version = _codec_version(value, "asset")
    provenance_payload = value.get("provenance")
    if not isinstance(provenance_payload, dict):
        raise PersistenceIntegrityError("Asset provenance payload must be an object")

    media_kind = str(value["media_kind"])
    origin = str(value["origin"])
    if version == 1:
        duration_ms = value.get("duration_ms")
        duration = None if duration_ms is None else MediaTime.from_milliseconds(int(duration_ms))
        usage_role = default_asset_usage_role(media_kind=media_kind, origin=origin)
    else:
        duration = _optional_media_time_from_payload(value.get("duration"))
        try:
            usage_role = AssetUsageRole(str(value["usage_role"]))
        except (KeyError, ValueError) as exc:
            raise PersistenceIntegrityError("invalid Asset usage_role in codec v2 payload") from exc

    return Asset(
        envelope=_envelope_from_payload(value["envelope"]),
        media_kind=media_kind,
        origin=origin,
        usage_role=usage_role,
        storage_ref=str(value["storage_ref"]),
        content_hash=str(value["content_hash"]),
        byte_size=int(value["byte_size"]),
        provenance=_provenance_from_payload(cast(dict[str, Any], provenance_payload)),
        imported_at=_parse_datetime(str(value["imported_at"])),
        duration=duration,
        width=value.get("width"),
        height=value.get("height"),
        fps=value.get("fps"),
        codec=value.get("codec"),
        audio_channels=value.get("audio_channels"),
        sample_rate_hz=value.get("sample_rate_hz"),
        user_labels=tuple(str(item) for item in value.get("user_labels", [])),
        collection_refs=tuple(str(item) for item in value.get("collection_refs", [])),
    )


def encode_shot(shot: Shot) -> str:
    return _canonical_json(
        {
            "codec_version": CODEC_VERSION,
            "record_type": "shot",
            "envelope": _envelope_payload(shot.envelope),
            "asset_ref": _ref_payload(shot.asset_ref),
            "source_range": _media_time_range_payload(shot.source_range),
            "boundary_method": shot.boundary_method,
            "previous_shot_ref": _optional_ref_payload(shot.previous_shot_ref),
            "next_shot_ref": _optional_ref_payload(shot.next_shot_ref),
            "scene_ref": _optional_ref_payload(shot.scene_ref),
        }
    )


def decode_shot(payload: str) -> Shot:
    value: dict[str, Any] = json.loads(payload)
    version = _codec_version(value, "shot")
    envelope = _envelope_from_payload(value["envelope"])
    asset_ref = _ref_from_payload(value["asset_ref"])
    boundary_method = str(value["boundary_method"])
    previous_shot_ref = _optional_ref_from_payload(value.get("previous_shot_ref"))
    next_shot_ref = _optional_ref_from_payload(value.get("next_shot_ref"))
    scene_ref = _optional_ref_from_payload(value.get("scene_ref"))

    if version == 1:
        return Shot(
            envelope=envelope,
            asset_ref=asset_ref,
            source_start_ms=int(value["source_start_ms"]),
            source_end_ms=int(value["source_end_ms"]),
            boundary_method=boundary_method,
            previous_shot_ref=previous_shot_ref,
            next_shot_ref=next_shot_ref,
            scene_ref=scene_ref,
        )

    source_range_payload = value.get("source_range")
    if not isinstance(source_range_payload, dict):
        raise PersistenceIntegrityError("Shot source_range payload must be an object")
    return Shot(
        envelope=envelope,
        asset_ref=asset_ref,
        source_range=_media_time_range_from_payload(cast(dict[str, Any], source_range_payload)),
        boundary_method=boundary_method,
        previous_shot_ref=previous_shot_ref,
        next_shot_ref=next_shot_ref,
        scene_ref=scene_ref,
    )


def encode_shot_analysis(analysis: ShotAnalysis) -> str:
    visual = analysis.visual
    speech = analysis.speech
    return _canonical_json(
        {
            "codec_version": CODEC_VERSION,
            "record_type": "shot_analysis",
            "shot_ref": _ref_payload(analysis.shot_ref),
            "revision": analysis.revision,
            "profile": analysis.profile.value,
            "analyzed_at": _datetime_text(analysis.analyzed_at),
            "technical_quality": [
                {"name": item.name, "value": float(item.value)}
                for item in analysis.technical_quality
            ],
            "visual": None
            if visual is None
            else {
                "summary": visual.summary,
                "tags": list(visual.tags),
                "subjects": list(visual.subjects),
                "actions": list(visual.actions),
                "environment": visual.environment,
                "framing": visual.framing,
                "camera_motion": visual.camera_motion,
            },
            "speech": None
            if speech is None
            else {"transcript": speech.transcript, "language": speech.language},
            "embedding_ref": analysis.embedding_ref,
            "artifact_refs": list(analysis.artifact_refs),
        }
    )


def decode_shot_analysis(payload: str) -> ShotAnalysis:
    value: dict[str, Any] = json.loads(payload)
    _codec_version(value, "shot_analysis")
    visual = value.get("visual")
    speech = value.get("speech")
    if visual is not None and not isinstance(visual, dict):
        raise PersistenceIntegrityError("ShotAnalysis visual payload must be an object or null")
    if speech is not None and not isinstance(speech, dict):
        raise PersistenceIntegrityError("ShotAnalysis speech payload must be an object or null")

    visual_payload = cast(dict[str, Any] | None, visual)
    speech_payload = cast(dict[str, Any] | None, speech)
    return ShotAnalysis(
        shot_ref=_ref_from_payload(value["shot_ref"]),
        revision=int(value["revision"]),
        profile=AnalysisProfile(str(value["profile"])),
        analyzed_at=_parse_datetime(str(value["analyzed_at"])),
        technical_quality=tuple(
            NamedQualityScore(name=str(item["name"]), value=float(item["value"]))
            for item in value.get("technical_quality", [])
        ),
        visual=None
        if visual_payload is None
        else VisualSemantics(
            summary=visual_payload.get("summary"),
            tags=tuple(str(item) for item in visual_payload.get("tags", [])),
            subjects=tuple(str(item) for item in visual_payload.get("subjects", [])),
            actions=tuple(str(item) for item in visual_payload.get("actions", [])),
            environment=visual_payload.get("environment"),
            framing=visual_payload.get("framing"),
            camera_motion=visual_payload.get("camera_motion"),
        ),
        speech=None
        if speech_payload is None
        else SpeechContent(
            transcript=speech_payload.get("transcript"),
            language=speech_payload.get("language"),
        ),
        embedding_ref=value.get("embedding_ref"),
        artifact_refs=tuple(str(item) for item in value.get("artifact_refs", [])),
    )

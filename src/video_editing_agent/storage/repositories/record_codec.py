from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.shot.analysis import (
    AnalysisProfile,
    NamedQualityScore,
    ShotAnalysis,
    SpeechContent,
    VisualSemantics,
)
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.storage.repositories.sqlite_database import PersistenceError

CODEC_VERSION = 1


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


def _envelope_payload(value: EntityEnvelope) -> dict[str, object]:
    return {
        "id": value.id,
        "revision": value.revision,
        "schema_version": value.schema_version,
        "status": value.status.value,
        "created_at": _datetime_text(value.created_at),
        "created_by": value.created_by,
    }


def _envelope_from_payload(value: dict[str, Any]) -> EntityEnvelope:
    return EntityEnvelope(
        id=str(value["id"]),
        revision=int(value["revision"]),
        schema_version=str(value["schema_version"]),
        status=EntityStatus(str(value["status"])),
        created_at=_parse_datetime(str(value["created_at"])),
        created_by=str(value["created_by"]),
    )


def _require_codec(value: dict[str, Any], record_type: str) -> None:
    if value.get("codec_version") != CODEC_VERSION:
        raise PersistenceIntegrityError(
            f"unsupported {record_type} codec version: {value.get('codec_version')!r}"
        )
    if value.get("record_type") != record_type:
        raise PersistenceIntegrityError(
            f"expected {record_type} payload, found {value.get('record_type')!r}"
        )


def encode_asset(asset: Asset) -> str:
    provenance = asset.provenance
    return _canonical_json(
        {
            "codec_version": CODEC_VERSION,
            "record_type": "asset",
            "envelope": _envelope_payload(asset.envelope),
            "media_kind": asset.media_kind,
            "origin": asset.origin,
            "storage_ref": asset.storage_ref,
            "content_hash": asset.content_hash,
            "byte_size": asset.byte_size,
            "provenance": {
                "origin_type": provenance.origin_type,
                "provider": provenance.provider,
                "provider_asset_id": provenance.provider_asset_id,
                "source_page": provenance.source_page,
                "creator": provenance.creator,
                "retrieved_at": _optional_datetime_text(provenance.retrieved_at),
                "license_information": provenance.license_information,
                "attribution": provenance.attribution,
            },
            "imported_at": _datetime_text(asset.imported_at),
            "duration_ms": asset.duration_ms,
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
    _require_codec(value, "asset")
    provenance: dict[str, Any] = value["provenance"]
    return Asset(
        envelope=_envelope_from_payload(value["envelope"]),
        media_kind=str(value["media_kind"]),
        origin=str(value["origin"]),
        storage_ref=str(value["storage_ref"]),
        content_hash=str(value["content_hash"]),
        byte_size=int(value["byte_size"]),
        provenance=AssetProvenance(
            origin_type=str(provenance["origin_type"]),
            provider=provenance["provider"],
            provider_asset_id=provenance["provider_asset_id"],
            source_page=provenance["source_page"],
            creator=provenance["creator"],
            retrieved_at=_optional_parse_datetime(provenance["retrieved_at"]),
            license_information=provenance["license_information"],
            attribution=provenance["attribution"],
        ),
        imported_at=_parse_datetime(str(value["imported_at"])),
        duration_ms=value["duration_ms"],
        width=value["width"],
        height=value["height"],
        fps=value["fps"],
        codec=value["codec"],
        audio_channels=value["audio_channels"],
        sample_rate_hz=value["sample_rate_hz"],
        user_labels=tuple(str(item) for item in value["user_labels"]),
        collection_refs=tuple(str(item) for item in value["collection_refs"]),
    )


def encode_shot(shot: Shot) -> str:
    return _canonical_json(
        {
            "codec_version": CODEC_VERSION,
            "record_type": "shot",
            "envelope": _envelope_payload(shot.envelope),
            "asset_ref": _ref_payload(shot.asset_ref),
            "source_start_ms": shot.source_start_ms,
            "source_end_ms": shot.source_end_ms,
            "boundary_method": shot.boundary_method,
            "previous_shot_ref": _optional_ref_payload(shot.previous_shot_ref),
            "next_shot_ref": _optional_ref_payload(shot.next_shot_ref),
            "scene_ref": _optional_ref_payload(shot.scene_ref),
        }
    )


def decode_shot(payload: str) -> Shot:
    value: dict[str, Any] = json.loads(payload)
    _require_codec(value, "shot")
    return Shot(
        envelope=_envelope_from_payload(value["envelope"]),
        asset_ref=_ref_from_payload(value["asset_ref"]),
        source_start_ms=int(value["source_start_ms"]),
        source_end_ms=int(value["source_end_ms"]),
        boundary_method=str(value["boundary_method"]),
        previous_shot_ref=_optional_ref_from_payload(value["previous_shot_ref"]),
        next_shot_ref=_optional_ref_from_payload(value["next_shot_ref"]),
        scene_ref=_optional_ref_from_payload(value["scene_ref"]),
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
    _require_codec(value, "shot_analysis")
    visual: dict[str, Any] | None = value["visual"]
    speech: dict[str, Any] | None = value["speech"]
    return ShotAnalysis(
        shot_ref=_ref_from_payload(value["shot_ref"]),
        revision=int(value["revision"]),
        profile=AnalysisProfile(str(value["profile"])),
        analyzed_at=_parse_datetime(str(value["analyzed_at"])),
        technical_quality=tuple(
            NamedQualityScore(name=str(item["name"]), value=float(item["value"]))
            for item in value["technical_quality"]
        ),
        visual=None
        if visual is None
        else VisualSemantics(
            summary=visual["summary"],
            tags=tuple(str(item) for item in visual["tags"]),
            subjects=tuple(str(item) for item in visual["subjects"]),
            actions=tuple(str(item) for item in visual["actions"]),
            environment=visual["environment"],
            framing=visual["framing"],
            camera_motion=visual["camera_motion"],
        ),
        speech=None
        if speech is None
        else SpeechContent(transcript=speech["transcript"], language=speech["language"]),
        embedding_ref=value["embedding_ref"],
        artifact_refs=tuple(str(item) for item in value["artifact_refs"]),
    )

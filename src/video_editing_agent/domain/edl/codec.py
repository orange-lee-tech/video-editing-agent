from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from video_editing_agent.domain.common.entity import (
    EntityEnvelope,
    EntityRevisionRef,
    EntityStatus,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edl.automation import (
    EDLAudioAutomation,
    EDLAudioAutomationKind,
    EDLAudioKeyframe,
    EDLInterpolation,
    EDLSpatialAutomation,
    EDLSpatialKeyframe,
    ExactRational,
)
from video_editing_agent.domain.edl.model import EDL, EDLSegment, EDLTrack, EDLTrackFamily
from video_editing_agent.domain.edl.validation import validate_edl

EDL_SCHEMA_VERSION = "r0.12-edl-v2"


def _time(value: MediaTime) -> dict[str, int]:
    return {"value": value.value, "scale": value.scale}


def _range(value: MediaTimeRange) -> dict[str, dict[str, int]]:
    return {"start": _time(value.start), "duration": _time(value.duration)}


def _ref(value: EntityRevisionRef) -> dict[str, int | str]:
    return {"entity_id": value.entity_id, "revision": value.revision}


def _rational(value: ExactRational) -> dict[str, int]:
    return {"value": value.value, "scale": value.scale}


def _spatial(value: EDLSpatialAutomation | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return {
        "interpolation": value.interpolation.value,
        "keyframes": [
            {
                "timeline_time": _time(item.timeline_time),
                "source_time": _time(item.source_time),
                "crop": {
                    "left": item.crop_left,
                    "top": item.crop_top,
                    "width": item.crop_width,
                    "height": item.crop_height,
                },
                "scale": _rational(item.scale),
                "position_x": _rational(item.position_x),
                "position_y": _rational(item.position_y),
            }
            for item in value.keyframes
        ],
    }


def _audio(value: EDLAudioAutomation) -> dict[str, Any]:
    return {
        "kind": value.kind.value,
        "interpolation": value.interpolation.value,
        "keyframes": [
            {
                "timeline_time": _time(item.timeline_time),
                "gain_millibels": item.gain_millibels,
                "muted": item.muted,
            }
            for item in value.keyframes
        ],
        "loop_source_range": (
            None if value.loop_source_range is None else _range(value.loop_source_range)
        ),
    }


def encode_edl(edl: EDL) -> bytes:
    validation = validate_edl(edl)
    if not validation.is_valid:
        codes = ",".join(item.code.value for item in validation.diagnostics)
        raise ValueError(f"cannot serialize invalid EDL: {codes}")
    root = {
        "schema_version": EDL_SCHEMA_VERSION,
        "edl": {
            "envelope": {
                "id": edl.envelope.id,
                "revision": edl.envelope.revision,
                "schema_version": edl.envelope.schema_version,
                "status": edl.envelope.status.value,
                "created_at": edl.envelope.created_at.isoformat(),
                "created_by": edl.envelope.created_by,
                "derived_from": [_ref(item) for item in edl.envelope.derived_from],
            },
            "edit_plan_ref": _ref(edl.edit_plan_ref),
            "tracks": [
                {"track_id": item.track_id, "family": item.family.value, "layer": item.layer}
                for item in edl.effective_tracks
            ],
            "segments": [
                {
                    "segment_id": item.segment_id,
                    "asset_ref": _ref(item.asset_ref),
                    "shot_ref": None if item.shot_ref is None else _ref(item.shot_ref),
                    "source_range": _range(item.source_range),
                    "timeline_range": _range(item.timeline_range),
                    "track_id": item.track_id,
                    "spatial_decision_ref": item.spatial_decision_ref,
                    "audio_mix_decision_ref": item.audio_mix_decision_ref,
                    "spatial_automation": _spatial(item.spatial_automation),
                    "audio_automations": [_audio(value) for value in item.audio_automations],
                }
                for item in edl.ordered_segments
            ],
        },
    }
    return json.dumps(root, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be an array")
    return value


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string")
    return value


def _integer(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    return value


def _bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be a boolean")
    return value


def _decode_time(value: Any, name: str) -> MediaTime:
    raw = _object(value, name)
    return MediaTime(
        _integer(raw.get("value"), f"{name}.value"), _integer(raw.get("scale"), f"{name}.scale")
    )


def _decode_range(value: Any, name: str) -> MediaTimeRange:
    raw = _object(value, name)
    return MediaTimeRange(
        _decode_time(raw.get("start"), f"{name}.start"),
        _decode_time(raw.get("duration"), f"{name}.duration"),
    )


def _decode_ref(value: Any, name: str) -> EntityRevisionRef:
    raw = _object(value, name)
    return EntityRevisionRef(
        _string(raw.get("entity_id"), f"{name}.entity_id"),
        _integer(raw.get("revision"), f"{name}.revision"),
    )


def _decode_rational(value: Any, name: str) -> ExactRational:
    raw = _object(value, name)
    return ExactRational(
        _integer(raw.get("value"), f"{name}.value"),
        _integer(raw.get("scale"), f"{name}.scale"),
    )


def _decode_spatial(value: Any, name: str) -> EDLSpatialAutomation | None:
    if value is None:
        return None
    raw = _object(value, name)
    keyframes = []
    for index, value_item in enumerate(_list(raw.get("keyframes"), f"{name}.keyframes")):
        item = _object(value_item, f"{name}.keyframes[{index}]")
        crop = _object(item.get("crop"), f"{name}.keyframes[{index}].crop")
        keyframes.append(
            EDLSpatialKeyframe(
                _decode_time(item.get("timeline_time"), f"{name}.timeline_time"),
                _decode_time(item.get("source_time"), f"{name}.source_time"),
                _integer(crop.get("left"), f"{name}.crop.left"),
                _integer(crop.get("top"), f"{name}.crop.top"),
                _integer(crop.get("width"), f"{name}.crop.width"),
                _integer(crop.get("height"), f"{name}.crop.height"),
                _decode_rational(item.get("scale"), f"{name}.scale"),
                _decode_rational(item.get("position_x"), f"{name}.position_x"),
                _decode_rational(item.get("position_y"), f"{name}.position_y"),
            )
        )
    return EDLSpatialAutomation(
        EDLInterpolation(_string(raw.get("interpolation"), f"{name}.interpolation")),
        tuple(keyframes),
    )


def _decode_audio(value: Any, name: str) -> EDLAudioAutomation:
    raw = _object(value, name)
    keyframes = []
    for index, value_item in enumerate(_list(raw.get("keyframes"), f"{name}.keyframes")):
        item = _object(value_item, f"{name}.keyframes[{index}]")
        keyframes.append(
            EDLAudioKeyframe(
                _decode_time(item.get("timeline_time"), f"{name}.timeline_time"),
                _integer(item.get("gain_millibels"), f"{name}.gain_millibels"),
                _bool(item.get("muted"), f"{name}.muted"),
            )
        )
    loop_value = raw.get("loop_source_range")
    return EDLAudioAutomation(
        EDLAudioAutomationKind(_string(raw.get("kind"), f"{name}.kind")),
        EDLInterpolation(_string(raw.get("interpolation"), f"{name}.interpolation")),
        tuple(keyframes),
        None if loop_value is None else _decode_range(loop_value, f"{name}.loop_source_range"),
    )


def decode_edl(content: bytes) -> EDL:
    root = _object(json.loads(content), "root")
    if root.get("schema_version") != EDL_SCHEMA_VERSION:
        raise ValueError("unsupported EDL artifact schema")
    raw = _object(root.get("edl"), "edl")
    envelope_raw = _object(raw.get("envelope"), "edl.envelope")
    derived = tuple(
        _decode_ref(item, "edl.envelope.derived_from")
        for item in _list(envelope_raw.get("derived_from"), "edl.envelope.derived_from")
    )
    envelope = EntityEnvelope(
        _string(envelope_raw.get("id"), "edl.envelope.id"),
        _integer(envelope_raw.get("revision"), "edl.envelope.revision"),
        _string(envelope_raw.get("schema_version"), "edl.envelope.schema_version"),
        EntityStatus(_string(envelope_raw.get("status"), "edl.envelope.status")),
        datetime.fromisoformat(_string(envelope_raw.get("created_at"), "edl.envelope.created_at")),
        _string(envelope_raw.get("created_by"), "edl.envelope.created_by"),
        derived,
    )
    tracks = tuple(
        EDLTrack(
            _string(item.get("track_id"), "track.track_id"),
            EDLTrackFamily(_string(item.get("family"), "track.family")),
            _integer(item.get("layer"), "track.layer"),
        )
        for value in _list(raw.get("tracks"), "edl.tracks")
        for item in (_object(value, "track"),)
    )
    segments = []
    for index, value in enumerate(_list(raw.get("segments"), "edl.segments")):
        item = _object(value, f"segment[{index}]")
        shot_value = item.get("shot_ref")
        audio_values = _list(item.get("audio_automations"), "segment.audio_automations")
        segments.append(
            EDLSegment(
                _string(item.get("segment_id"), "segment.segment_id"),
                _decode_ref(item.get("asset_ref"), "segment.asset_ref"),
                source_range=_decode_range(item.get("source_range"), "segment.source_range"),
                timeline_range=_decode_range(item.get("timeline_range"), "segment.timeline_range"),
                track_id=_string(item.get("track_id"), "segment.track_id"),
                shot_ref=(
                    None if shot_value is None else _decode_ref(shot_value, "segment.shot_ref")
                ),
                spatial_decision_ref=(
                    None
                    if item.get("spatial_decision_ref") is None
                    else _string(item.get("spatial_decision_ref"), "segment.spatial_decision_ref")
                ),
                audio_mix_decision_ref=(
                    None
                    if item.get("audio_mix_decision_ref") is None
                    else _string(
                        item.get("audio_mix_decision_ref"), "segment.audio_mix_decision_ref"
                    )
                ),
                spatial_automation=_decode_spatial(
                    item.get("spatial_automation"), "segment.spatial_automation"
                ),
                audio_automations=tuple(
                    _decode_audio(audio, "segment.audio_automation") for audio in audio_values
                ),
            )
        )
    edl = EDL(
        envelope,
        _decode_ref(raw.get("edit_plan_ref"), "edl.edit_plan_ref"),
        tuple(segments),
        tracks,
    )
    validation = validate_edl(edl)
    if not validation.is_valid:
        codes = ",".join(item.code.value for item in validation.diagnostics)
        raise ValueError(f"decoded EDL is invalid: {codes}")
    return edl

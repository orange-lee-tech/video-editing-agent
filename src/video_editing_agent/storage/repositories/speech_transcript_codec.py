from __future__ import annotations

import json
from datetime import datetime
from typing import Any, cast

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.evidence.speech import (
    SpeechSegment,
    SpeechTranscript,
    SpeechWord,
)
from video_editing_agent.storage.repositories.record_codec import PersistenceIntegrityError

CODEC_VERSION = 1


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _time(value: MediaTime) -> dict[str, int]:
    return {"value": value.value, "scale": value.scale}


def _range(value: MediaTimeRange) -> dict[str, object]:
    return {"start": _time(value.start), "duration": _time(value.duration)}


def _decode_time(value: object) -> MediaTime:
    if not isinstance(value, dict):
        raise PersistenceIntegrityError("speech MediaTime payload must be an object")
    payload = cast(dict[str, Any], value)
    return MediaTime(value=int(payload["value"]), scale=int(payload["scale"]))


def _decode_range(value: object) -> MediaTimeRange:
    if not isinstance(value, dict):
        raise PersistenceIntegrityError("speech MediaTimeRange payload must be an object")
    payload = cast(dict[str, Any], value)
    return MediaTimeRange(
        start=_decode_time(payload.get("start")),
        duration=_decode_time(payload.get("duration")),
    )


def _word_payload(word: SpeechWord) -> dict[str, object]:
    return {
        "text": word.text,
        "source_range": _range(word.source_range),
        "confidence": word.confidence,
    }


def _segment_payload(segment: SpeechSegment) -> dict[str, object]:
    return {
        "text": segment.text,
        "source_range": _range(segment.source_range),
        "confidence": segment.confidence,
        "words": [_word_payload(word) for word in segment.words],
    }


def encode_speech_transcript(transcript: SpeechTranscript) -> str:
    return _canonical_json(
        {
            "codec_version": CODEC_VERSION,
            "record_type": "speech_transcript",
            "shot_ref": {
                "entity_id": transcript.shot_ref.entity_id,
                "revision": transcript.shot_ref.revision,
            },
            "revision": transcript.revision,
            "recognized_at": transcript.recognized_at.isoformat(),
            "provider_id": transcript.provider_id,
            "provider_revision": transcript.provider_revision,
            "text": transcript.text,
            "language": transcript.language,
            "segments": [_segment_payload(segment) for segment in transcript.segments],
            "artifact_refs": list(transcript.artifact_refs),
        }
    )


def _decode_word(value: object) -> SpeechWord:
    if not isinstance(value, dict):
        raise PersistenceIntegrityError("SpeechWord payload must be an object")
    payload = cast(dict[str, Any], value)
    confidence = payload.get("confidence")
    return SpeechWord(
        text=str(payload["text"]),
        source_range=_decode_range(payload.get("source_range")),
        confidence=None if confidence is None else float(confidence),
    )


def _decode_segment(value: object) -> SpeechSegment:
    if not isinstance(value, dict):
        raise PersistenceIntegrityError("SpeechSegment payload must be an object")
    payload = cast(dict[str, Any], value)
    raw_words = payload.get("words", [])
    if not isinstance(raw_words, list):
        raise PersistenceIntegrityError("SpeechSegment words must be a list")
    confidence = payload.get("confidence")
    return SpeechSegment(
        text=str(payload["text"]),
        source_range=_decode_range(payload.get("source_range")),
        words=tuple(_decode_word(word) for word in raw_words),
        confidence=None if confidence is None else float(confidence),
    )


def decode_speech_transcript(payload: str) -> SpeechTranscript:
    value: dict[str, Any] = json.loads(payload)
    if value.get("codec_version") != CODEC_VERSION:
        raise PersistenceIntegrityError(
            f"unsupported speech_transcript codec version: {value.get('codec_version')!r}"
        )
    if value.get("record_type") != "speech_transcript":
        raise PersistenceIntegrityError("expected speech_transcript payload")

    shot_ref = value.get("shot_ref")
    if not isinstance(shot_ref, dict):
        raise PersistenceIntegrityError("speech_transcript shot_ref must be an object")
    raw_segments = value.get("segments", [])
    if not isinstance(raw_segments, list):
        raise PersistenceIntegrityError("speech_transcript segments must be a list")
    raw_artifact_refs = value.get("artifact_refs", [])
    if not isinstance(raw_artifact_refs, list):
        raise PersistenceIntegrityError("speech_transcript artifact_refs must be a list")

    return SpeechTranscript(
        shot_ref=EntityRevisionRef(
            entity_id=str(shot_ref["entity_id"]),
            revision=int(shot_ref["revision"]),
        ),
        revision=int(value["revision"]),
        recognized_at=datetime.fromisoformat(str(value["recognized_at"])),
        provider_id=str(value["provider_id"]),
        provider_revision=str(value["provider_revision"]),
        text=str(value["text"]),
        language=None if value.get("language") is None else str(value["language"]),
        segments=tuple(_decode_segment(segment) for segment in raw_segments),
        artifact_refs=tuple(str(ref) for ref in raw_artifact_refs),
    )

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from datetime import UTC, datetime
from fractions import Fraction

from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.speech.service import ProviderNeutralSpeechRecognitionService
from video_editing_agent.media.speech.voice_activity import (
    SILENCE_KIND,
    SPEECH_ACTIVITY_KIND,
    ProviderNeutralVoiceActivityService,
)
from video_editing_agent.providers.speech.faster_whisper import (
    DEFAULT_MODEL_REVISION,
    FasterWhisperConfig,
    FasterWhisperSpeechRecognitionPort,
)
from video_editing_agent.providers.speech.silero_vad import (
    SileroVadConfig,
    SileroVadVoiceActivityPort,
)
from video_editing_agent.storage.asset.repository_media import RepositoryLocalAssetMediaResolver
from video_editing_agent.storage.repositories.speech_transcript_repository import (
    SqliteSpeechTranscriptRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase
from video_editing_agent.storage.repositories.sqlite_repositories import (
    SqliteAssetRepository,
    SqliteShotRepository,
)
from video_editing_agent.storage.repositories.temporal_evidence_repository import (
    SqliteTemporalEvidenceRepository,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the R0.8B live Speech/VAD owner probe")
    parser.add_argument("--media", required=True, type=pathlib.Path)
    parser.add_argument("--asr-model", required=True, type=pathlib.Path)
    parser.add_argument("--vad-model", required=True, type=pathlib.Path)
    parser.add_argument("--database", required=True, type=pathlib.Path)
    parser.add_argument("--ffmpeg", required=True)
    parser.add_argument("--shot-start", default="1")
    parser.add_argument("--shot-end", required=True)
    return parser


def _time(value: str) -> MediaTime:
    fraction = Fraction(value)
    return MediaTime(fraction.numerator, fraction.denominator)


def _envelope(entity_id: str) -> EntityEnvelope:
    return EntityEnvelope(
        entity_id,
        1,
        "0.2",
        EntityStatus.VALID,
        datetime(2026, 8, 13, tzinfo=UTC),
        "r0.8b-live-probe",
    )


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _require_fresh_database_path(database_path: pathlib.Path) -> None:
    if database_path.exists():
        raise FileExistsError(
            "probe database already exists; choose a fresh path instead of overwriting: "
            f"{database_path}"
        )


def run(args: argparse.Namespace) -> dict[str, object]:
    media = args.media.expanduser().resolve(strict=True)
    asr_model = args.asr_model.expanduser().resolve(strict=True)
    vad_model = args.vad_model.expanduser().resolve(strict=True)
    database_path = args.database.expanduser().resolve()
    start = _time(args.shot_start)
    end = _time(args.shot_end)
    source_range = MediaTimeRange(start, end - start)
    _check(start.as_fraction() > 0, "probe Shot start must be non-zero")
    _check(asr_model.is_dir(), "ASR model path must be a local directory")
    _require_fresh_database_path(database_path)

    database = SqliteProjectDatabase(database_path)
    database.initialize()
    assets = SqliteAssetRepository(database)
    shots = SqliteShotRepository(database)
    asset_ref = EntityRevisionRef("ast_r08b_live", 1)
    shot_ref = EntityRevisionRef("sht_r08b_live", 1)
    assets.save(
        Asset(
            _envelope(asset_ref.entity_id),
            "audio",
            "local",
            media.as_uri(),
            "sha256:" + hashlib.sha256(media.read_bytes()).hexdigest(),
            media.stat().st_size,
            AssetProvenance("local"),
            datetime(2026, 8, 13, tzinfo=UTC),
            duration=end,
        )
    )
    shot = Shot(
        _envelope(shot_ref.entity_id),
        asset_ref,
        source_range=source_range,
        boundary_method="r0.8b-live-probe",
    )
    shots.save(shot)
    resolver = RepositoryLocalAssetMediaResolver(assets)

    asr_port = FasterWhisperSpeechRecognitionPort(
        FasterWhisperConfig(
            model_id=str(asr_model),
            model_revision=DEFAULT_MODEL_REVISION,
            local_files_only=True,
        )
    )
    transcript = ProviderNeutralSpeechRecognitionService(
        shot_repository=shots,
        asset_media_resolver=resolver,
        transcript_repository=SqliteSpeechTranscriptRepository(database),
        speech_port=asr_port,
    ).recognize(shot_ref)
    _check(asr_port.config.local_files_only, "ASR local_files_only must remain true")
    _check(bool(transcript.segments), "ASR must return timed segments")
    words = tuple(word for segment in transcript.segments for word in segment.words)
    _check(bool(words), "ASR must return timed words")
    for segment in transcript.segments:
        _check(
            source_range.start.as_fraction() <= segment.source_range.start.as_fraction()
            and segment.source_range.end.as_fraction() <= source_range.end.as_fraction(),
            "ASR owner segment range escaped the exact Shot",
        )
    for word in words:
        _check(
            source_range.start.as_fraction() <= word.source_range.start.as_fraction()
            and word.source_range.end.as_fraction() <= source_range.end.as_fraction(),
            "ASR owner word range escaped the exact Shot",
        )

    vad_port = SileroVadVoiceActivityPort(
        SileroVadConfig(model_path=vad_model, ffmpeg_executable=args.ffmpeg)
    )
    evidence = ProviderNeutralVoiceActivityService(
        shot_repository=shots,
        asset_media_resolver=resolver,
        temporal_evidence_repository=SqliteTemporalEvidenceRepository(database),
        voice_activity_port=vad_port,
    ).analyze(shot_ref)
    first_range = evidence[0].source_range
    last_range = evidence[-1].source_range
    assert first_range is not None
    assert last_range is not None
    _check(first_range.start == source_range.start, "VAD must restore Asset offset")
    _check(last_range.end == source_range.end, "VAD must end at Shot end")
    _check(
        {item.kind for item in evidence} == {SPEECH_ACTIVITY_KIND, SILENCE_KIND},
        "VAD fixture must exercise speech and silence",
    )
    for left, right in zip(evidence, evidence[1:], strict=False):
        left_range = left.source_range
        right_range = right.source_range
        assert left_range is not None
        assert right_range is not None
        _check(left_range.end == right_range.start, "VAD partition gap/overlap")

    del database, assets, shots, resolver
    reopened = SqliteProjectDatabase(database_path)
    reopened.initialize()
    loaded_transcript = SqliteSpeechTranscriptRepository(reopened).load(shot_ref, 1)
    loaded_evidence = SqliteTemporalEvidenceRepository(reopened).list_evidence(shot_ref)
    _check(loaded_transcript == transcript, "reopened transcript differs from owner output")
    _check(
        loaded_evidence == tuple(sorted(evidence, key=lambda item: item.evidence_id)),
        "reopened VAD evidence differs from owner output",
    )

    return {
        "status": "PASS",
        "media": str(media),
        "database": str(database_path),
        "shot_range": {
            "start": [source_range.start.value, source_range.start.scale],
            "duration": [source_range.duration.value, source_range.duration.scale],
        },
        "asr": {
            "provider": transcript.provider_id,
            "provider_revision": transcript.provider_revision,
            "language": transcript.language,
            "text": transcript.text,
            "segments": len(transcript.segments),
            "words": len(words),
            "sqlite_reopen": True,
        },
        "vad": {
            "provider": evidence[0].method,
            "provider_revision": evidence[0].producer_version,
            "spans": len(evidence),
            "kinds": sorted({item.kind for item in evidence}),
            "evidence_ids": sorted(item.evidence_id for item in evidence),
            "sqlite_reopen": True,
        },
    }


def main() -> int:
    try:
        result = run(_parser().parse_args())
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

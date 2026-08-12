from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from math import isfinite

from video_editing_agent.application.ports.asset_media import AssetMediaResolver
from video_editing_agent.application.ports.shot_repository import ShotRepository
from video_editing_agent.application.ports.temporal_evidence_repository import (
    TemporalEvidenceRepository,
)
from video_editing_agent.application.ports.voice_activity import (
    VoiceActivityPort,
    VoiceActivityProposal,
    VoiceActivityRequest,
    VoiceActivityState,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTimeRange
from video_editing_agent.domain.evidence.temporal import TemporalEvidence
from video_editing_agent.domain.shot.model import Shot

SPEECH_ACTIVITY_KIND = "speech_activity"
SILENCE_KIND = "silence"
_VOICE_ACTIVITY_KINDS = frozenset({SPEECH_ACTIVITY_KIND, SILENCE_KIND})


def _validate_confidence(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("voice-activity confidence must be a number")
    normalized = float(value)
    if not isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise ValueError("voice-activity confidence must be finite and between 0 and 1")
    return normalized


def _kind_for_state(state: VoiceActivityState) -> str:
    if state is VoiceActivityState.SPEECH:
        return SPEECH_ACTIVITY_KIND
    if state is VoiceActivityState.SILENCE:
        return SILENCE_KIND
    raise TypeError("voice-activity state must be a VoiceActivityState")


def _absolute_range(relative_range: MediaTimeRange, shot: Shot) -> MediaTimeRange:
    return MediaTimeRange(
        start=shot.source_range.start + relative_range.start,
        duration=relative_range.duration,
    )


def _evidence_id(
    *,
    shot_ref: EntityRevisionRef,
    kind: str,
    source_range: MediaTimeRange,
    method: str,
    producer_version: str,
) -> str:
    payload = json.dumps(
        {
            "shot_ref": [shot_ref.entity_id, shot_ref.revision],
            "kind": kind,
            "source_range": {
                "start": [source_range.start.value, source_range.start.scale],
                "duration": [source_range.duration.value, source_range.duration.scale],
            },
            "method": method,
            "producer_version": producer_version,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"tev_vad_{digest}"


def _normalize_proposal(proposal: VoiceActivityProposal, shot: Shot) -> tuple[TemporalEvidence, ...]:
    provider_id = proposal.provider_id.strip()
    provider_revision = proposal.provider_revision.strip()
    if not provider_id:
        raise ValueError("voice-activity provider_id must not be empty")
    if not provider_revision:
        raise ValueError("voice-activity provider_revision must not be empty")
    if not proposal.spans:
        raise ValueError("voice-activity proposal must cover the complete Shot")

    shot_ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
    shot_duration = shot.source_range.duration.as_fraction()
    cursor = Fraction(0)
    previous_state: VoiceActivityState | None = None
    evidence: list[TemporalEvidence] = []

    for span in proposal.spans:
        if not isinstance(span.state, VoiceActivityState):
            raise TypeError("voice-activity state must be a VoiceActivityState")
        start = span.relative_range.start.as_fraction()
        end = span.relative_range.end.as_fraction()
        if start < 0:
            raise ValueError("voice-activity span must not start before the Shot")
        if end > shot_duration:
            raise ValueError("voice-activity span must stay inside the exact Shot duration")
        if start > cursor:
            raise ValueError("voice-activity partition must not contain gaps")
        if start < cursor:
            raise ValueError("voice-activity partition must not contain overlaps")
        if previous_state is span.state:
            raise ValueError("adjacent voice-activity spans with the same state must be merged")

        confidence = _validate_confidence(span.confidence)
        source_range = _absolute_range(span.relative_range, shot)
        kind = _kind_for_state(span.state)
        evidence.append(
            TemporalEvidence(
                evidence_id=_evidence_id(
                    shot_ref=shot_ref,
                    kind=kind,
                    source_range=source_range,
                    method=provider_id,
                    producer_version=provider_revision,
                ),
                shot_ref=shot_ref,
                kind=kind,
                method=provider_id,
                producer_version=provider_revision,
                confidence=confidence,
                source_range=source_range,
            )
        )
        cursor = end
        previous_state = span.state

    if cursor != shot_duration:
        raise ValueError("voice-activity partition must cover the complete Shot without gaps")
    return tuple(evidence)


class ProviderNeutralVoiceActivityService:
    """Own a complete validated VAD partition while providers propose relative spans only."""

    def __init__(
        self,
        *,
        shot_repository: ShotRepository,
        asset_media_resolver: AssetMediaResolver,
        temporal_evidence_repository: TemporalEvidenceRepository,
        voice_activity_port: VoiceActivityPort,
    ) -> None:
        self._shot_repository = shot_repository
        self._asset_media_resolver = asset_media_resolver
        self._temporal_evidence_repository = temporal_evidence_repository
        self._voice_activity_port = voice_activity_port

    def _load_exact_shot(self, shot_ref: EntityRevisionRef) -> Shot:
        shot = self._shot_repository.load(shot_ref)
        loaded_ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
        if loaded_ref != shot_ref:
            raise RuntimeError(
                f"ShotRepository returned {loaded_ref.entity_id}@{loaded_ref.revision} "
                f"for requested {shot_ref.entity_id}@{shot_ref.revision}"
            )
        return shot

    def analyze(self, shot_ref: EntityRevisionRef) -> tuple[TemporalEvidence, ...]:
        shot = self._load_exact_shot(shot_ref)
        resolved_media = self._asset_media_resolver.resolve_local(shot.asset_ref)
        if resolved_media.asset_ref != shot.asset_ref:
            raise RuntimeError("AssetMediaResolver returned a different Asset revision")

        proposal = self._voice_activity_port.analyze(
            VoiceActivityRequest(
                shot_ref=shot_ref,
                local_media_path=resolved_media.path,
                source_range=shot.source_range,
            )
        )
        evidence = _normalize_proposal(proposal, shot)

        existing = tuple(
            item
            for item in self._temporal_evidence_repository.list_evidence(shot_ref)
            if item.kind in _VOICE_ACTIVITY_KINDS
            and item.method == proposal.provider_id.strip()
            and item.producer_version == proposal.provider_revision.strip()
        )
        if existing and {item.evidence_id for item in existing} != {
            item.evidence_id for item in evidence
        }:
            raise ValueError(
                "same voice-activity provider revision produced a different partition; "
                "change provider_revision before persisting changed evidence"
            )

        self._temporal_evidence_repository.save_evidence_batch(evidence)
        return evidence

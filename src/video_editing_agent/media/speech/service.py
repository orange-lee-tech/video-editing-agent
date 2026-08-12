from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from fractions import Fraction
from math import isfinite

from video_editing_agent.application.ports.asset_media import AssetMediaResolver
from video_editing_agent.application.ports.shot_repository import ShotRepository
from video_editing_agent.application.ports.speech_recognition import (
    SpeechRecognitionPort,
    SpeechRecognitionProposal,
    SpeechRecognitionRequest,
    SpeechSegmentProposal,
    SpeechWordProposal,
)
from video_editing_agent.application.ports.speech_transcript_repository import (
    SpeechTranscriptRepository,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTimeRange
from video_editing_agent.domain.evidence.speech import (
    SpeechSegment,
    SpeechTranscript,
    SpeechWord,
)
from video_editing_agent.domain.shot.model import Shot


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _validate_confidence(value: float | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("provider confidence must be a float or None")
    normalized = float(value)
    if not isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise ValueError("provider confidence must be finite and between 0 and 1")
    return normalized


def _validate_relative_range(relative_range: MediaTimeRange, shot: Shot) -> None:
    if relative_range.start.as_fraction() < 0:
        raise ValueError("provider speech range must not start before the Shot")
    if relative_range.end.as_fraction() > shot.source_range.duration.as_fraction():
        raise ValueError("provider speech range must stay inside the exact Shot duration")


def _absolute_range(relative_range: MediaTimeRange, shot: Shot) -> MediaTimeRange:
    _validate_relative_range(relative_range, shot)
    return MediaTimeRange(
        start=shot.source_range.start + relative_range.start,
        duration=relative_range.duration,
    )


def _normalize_word(proposal: SpeechWordProposal, shot: Shot) -> SpeechWord:
    if not proposal.text.strip():
        raise ValueError("provider SpeechWord text must not be empty")
    return SpeechWord(
        text=proposal.text,
        source_range=_absolute_range(proposal.relative_range, shot),
        confidence=_validate_confidence(proposal.confidence),
    )


def _normalize_segment(proposal: SpeechSegmentProposal, shot: Shot) -> SpeechSegment:
    if not proposal.text.strip():
        raise ValueError("provider SpeechSegment text must not be empty")
    _validate_relative_range(proposal.relative_range, shot)

    previous_word_end = proposal.relative_range.start.as_fraction()
    normalized_words: list[SpeechWord] = []
    for word in proposal.words:
        if word.relative_range.start.as_fraction() < proposal.relative_range.start.as_fraction():
            raise ValueError("provider SpeechWord must stay inside its SpeechSegment")
        if word.relative_range.end.as_fraction() > proposal.relative_range.end.as_fraction():
            raise ValueError("provider SpeechWord must stay inside its SpeechSegment")
        if word.relative_range.start.as_fraction() < previous_word_end:
            raise ValueError("provider SpeechWord ranges must be ordered and non-overlapping")
        previous_word_end = word.relative_range.end.as_fraction()
        normalized_words.append(_normalize_word(word, shot))

    return SpeechSegment(
        text=proposal.text,
        source_range=_absolute_range(proposal.relative_range, shot),
        words=tuple(normalized_words),
        confidence=_validate_confidence(proposal.confidence),
    )


def _normalize_proposal(
    proposal: SpeechRecognitionProposal,
    shot: Shot,
    *,
    revision: int,
    recognized_at: datetime,
) -> SpeechTranscript:
    provider_id = proposal.provider_id.strip()
    provider_revision = proposal.provider_revision.strip()
    if not provider_id:
        raise ValueError("speech provider_id must not be empty")
    if not provider_revision:
        raise ValueError("speech provider_revision must not be empty")
    language = None if proposal.language is None else proposal.language.strip()
    if language == "":
        raise ValueError("speech language must be non-empty or None")
    if proposal.segments and not proposal.text.strip():
        raise ValueError("provider transcript text must not be empty when segments exist")
    if proposal.text.strip() and not proposal.segments:
        raise ValueError("provider must return timed segments for non-empty transcript text")

    previous_segment_end: Fraction | None = None
    segments: list[SpeechSegment] = []
    for segment in proposal.segments:
        _validate_relative_range(segment.relative_range, shot)
        start = segment.relative_range.start.as_fraction()
        if previous_segment_end is not None and start < previous_segment_end:
            raise ValueError("provider SpeechSegment ranges must be ordered and non-overlapping")
        previous_segment_end = segment.relative_range.end.as_fraction()
        segments.append(_normalize_segment(segment, shot))

    return SpeechTranscript(
        shot_ref=EntityRevisionRef(shot.envelope.id, shot.envelope.revision),
        revision=revision,
        recognized_at=recognized_at,
        provider_id=provider_id,
        provider_revision=provider_revision,
        text=proposal.text,
        language=language,
        segments=tuple(segments),
    )


class ProviderNeutralSpeechRecognitionService:
    """Own validated speech evidence while providers propose Shot-relative timing only."""

    def __init__(
        self,
        *,
        shot_repository: ShotRepository,
        asset_media_resolver: AssetMediaResolver,
        transcript_repository: SpeechTranscriptRepository,
        speech_port: SpeechRecognitionPort,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._shot_repository = shot_repository
        self._asset_media_resolver = asset_media_resolver
        self._transcript_repository = transcript_repository
        self._speech_port = speech_port
        self._clock = clock

    def _load_exact_shot(self, shot_ref: EntityRevisionRef) -> Shot:
        shot = self._shot_repository.load(shot_ref)
        loaded_ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
        if loaded_ref != shot_ref:
            raise RuntimeError(
                f"ShotRepository returned {loaded_ref.entity_id}@{loaded_ref.revision} "
                f"for requested {shot_ref.entity_id}@{shot_ref.revision}"
            )
        return shot

    def _recognize(self, shot_ref: EntityRevisionRef, *, revision: int) -> SpeechTranscript:
        shot = self._load_exact_shot(shot_ref)
        resolved_media = self._asset_media_resolver.resolve_local(shot.asset_ref)
        if resolved_media.asset_ref != shot.asset_ref:
            raise RuntimeError("AssetMediaResolver returned a different Asset revision")

        proposal = self._speech_port.recognize(
            SpeechRecognitionRequest(
                shot_ref=shot_ref,
                local_media_path=resolved_media.path,
                source_range=shot.source_range,
            )
        )
        transcript = _normalize_proposal(
            proposal,
            shot,
            revision=revision,
            recognized_at=self._clock(),
        )
        self._transcript_repository.save(transcript)
        return transcript

    def recognize(self, shot_ref: EntityRevisionRef) -> SpeechTranscript:
        if self._transcript_repository.latest(shot_ref) is not None:
            raise ValueError(
                "Shot already has speech evidence; use rerecognize() for a new revision"
            )
        return self._recognize(shot_ref, revision=1)

    def rerecognize(self, shot_ref: EntityRevisionRef) -> SpeechTranscript:
        latest = self._transcript_repository.latest(shot_ref)
        if latest is None:
            raise ValueError("Shot has no speech evidence; use recognize() for the first revision")
        if latest.shot_ref != shot_ref:
            raise RuntimeError("SpeechTranscriptRepository returned a different Shot revision")
        return self._recognize(shot_ref, revision=latest.revision + 1)

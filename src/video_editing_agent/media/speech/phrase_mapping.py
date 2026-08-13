from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTimeRange
from video_editing_agent.domain.evidence.speech import SpeechTranscript, SpeechWord
from video_editing_agent.domain.evidence.temporal import TemporalEvidence
from video_editing_agent.media.speech.voice_activity import (
    SILENCE_KIND,
    SPEECH_ACTIVITY_KIND,
)


@dataclass(frozen=True, slots=True)
class PhraseMatchCandidate:
    """A deterministic phrase location; it is evidence, not a selection or edit decision."""

    shot_ref: EntityRevisionRef
    transcript_revision: int
    transcript_provider_id: str
    transcript_provider_revision: str
    requested_phrase: str
    matched_text: str
    source_range: MediaTimeRange
    first_word_index: int
    last_word_index: int
    relevant_vad_evidence_ids: tuple[str, ...] = ()
    enclosing_speech_evidence_id: str | None = None
    preceding_silence_evidence_id: str | None = None
    following_silence_evidence_id: str | None = None


def _normalized_units(text: str) -> tuple[str, ...]:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return tuple(character for character in normalized if character.isalnum())


def _timed_words(transcript: SpeechTranscript) -> tuple[SpeechWord, ...]:
    return tuple(word for segment in transcript.segments for word in segment.words)


def _overlaps(left: MediaTimeRange, right: MediaTimeRange) -> bool:
    return (
        left.start.as_fraction() < right.end.as_fraction()
        and right.start.as_fraction() < left.end.as_fraction()
    )


def _vad_context(
    phrase_range: MediaTimeRange,
    evidence: tuple[TemporalEvidence, ...],
) -> tuple[tuple[str, ...], str | None, str | None, str | None]:
    ranged = tuple(item for item in evidence if item.source_range is not None)
    relevant = tuple(
        item.evidence_id
        for item in ranged
        if item.source_range is not None and _overlaps(item.source_range, phrase_range)
    )
    enclosing = next(
        (
            item.evidence_id
            for item in ranged
            if item.kind == SPEECH_ACTIVITY_KIND
            and item.source_range is not None
            and item.source_range.start.as_fraction() <= phrase_range.start.as_fraction()
            and phrase_range.end.as_fraction() <= item.source_range.end.as_fraction()
        ),
        None,
    )
    preceding = next(
        (
            item.evidence_id
            for item in reversed(ranged)
            if item.kind == SILENCE_KIND
            and item.source_range is not None
            and item.source_range.end == phrase_range.start
        ),
        None,
    )
    following = next(
        (
            item.evidence_id
            for item in ranged
            if item.kind == SILENCE_KIND
            and item.source_range is not None
            and item.source_range.start == phrase_range.end
        ),
        None,
    )
    return relevant, enclosing, preceding, following


def map_phrase_to_time(
    transcript: SpeechTranscript,
    desired_phrase: str,
    *,
    vad_evidence: tuple[TemporalEvidence, ...] = (),
) -> tuple[PhraseMatchCandidate, ...]:
    """Find every contiguous normalized phrase occurrence backed by timed words."""

    requested = _normalized_units(desired_phrase)
    if not requested:
        raise ValueError("desired phrase must contain a letter or number after normalization")
    if any(item.shot_ref != transcript.shot_ref for item in vad_evidence):
        raise ValueError("VAD evidence must belong to the transcript's exact Shot revision")

    words = _timed_words(transcript)
    stream: list[str] = []
    word_by_unit: list[int] = []
    for word_index, word in enumerate(words):
        units = _normalized_units(word.text)
        stream.extend(units)
        word_by_unit.extend((word_index,) * len(units))

    if not stream:
        return ()

    candidates: list[PhraseMatchCandidate] = []
    width = len(requested)
    for start in range(len(stream) - width + 1):
        if tuple(stream[start : start + width]) != requested:
            continue
        first_index = word_by_unit[start]
        last_index = word_by_unit[start + width - 1]
        first_word = words[first_index]
        last_word = words[last_index]
        source_range = MediaTimeRange(
            start=first_word.source_range.start,
            duration=last_word.source_range.end - first_word.source_range.start,
        )
        relevant, enclosing, preceding, following = _vad_context(source_range, vad_evidence)
        candidates.append(
            PhraseMatchCandidate(
                shot_ref=transcript.shot_ref,
                transcript_revision=transcript.revision,
                transcript_provider_id=transcript.provider_id,
                transcript_provider_revision=transcript.provider_revision,
                requested_phrase=desired_phrase,
                matched_text="".join(word.text for word in words[first_index : last_index + 1]),
                source_range=source_range,
                first_word_index=first_index,
                last_word_index=last_index,
                relevant_vad_evidence_ids=relevant,
                enclosing_speech_evidence_id=enclosing,
                preceding_silence_evidence_id=preceding,
                following_silence_evidence_id=following,
            )
        )
    return tuple(candidates)

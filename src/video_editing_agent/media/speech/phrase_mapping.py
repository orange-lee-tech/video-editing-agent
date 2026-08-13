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

_VAD_KINDS = frozenset({SPEECH_ACTIVITY_KIND, SILENCE_KIND})


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


def _timed_words(transcript: SpeechTranscript) -> tuple[tuple[SpeechWord, int], ...]:
    return tuple(
        (word, segment_index)
        for segment_index, segment in enumerate(transcript.segments)
        for word in segment.words
    )


def _overlaps(left: MediaTimeRange, right: MediaTimeRange) -> bool:
    return (
        left.start.as_fraction() < right.end.as_fraction()
        and right.start.as_fraction() < left.end.as_fraction()
    )


def _validate_vad_evidence(
    transcript: SpeechTranscript,
    evidence: tuple[TemporalEvidence, ...],
) -> None:
    if any(item.shot_ref != transcript.shot_ref for item in evidence):
        raise ValueError("VAD evidence must belong to the transcript's exact Shot revision")
    if any(item.kind not in _VAD_KINDS or item.source_range is None for item in evidence):
        raise ValueError("VAD evidence must contain only timed speech_activity/silence evidence")
    producer_revisions = {(item.method, item.producer_version) for item in evidence}
    if len(producer_revisions) > 1:
        raise ValueError("VAD evidence must come from one producer revision")


def _vad_context(
    phrase_range: MediaTimeRange,
    evidence: tuple[TemporalEvidence, ...],
) -> tuple[tuple[str, ...], str | None, str | None, str | None]:
    ranged = tuple(
        sorted(
            evidence,
            key=lambda item: (
                item.source_range.start.as_fraction() if item.source_range is not None else 0,
                item.source_range.end.as_fraction() if item.source_range is not None else 0,
                item.evidence_id,
            ),
        )
    )
    relevant = tuple(
        item.evidence_id
        for item in ranged
        if item.source_range is not None and _overlaps(item.source_range, phrase_range)
    )
    enclosing_item = next(
        (
            item
            for item in ranged
            if item.kind == SPEECH_ACTIVITY_KIND
            and item.source_range is not None
            and item.source_range.start.as_fraction() <= phrase_range.start.as_fraction()
            and phrase_range.end.as_fraction() <= item.source_range.end.as_fraction()
        ),
        None,
    )
    context_start = (
        enclosing_item.source_range.start
        if enclosing_item is not None and enclosing_item.source_range is not None
        else phrase_range.start
    )
    context_end = (
        enclosing_item.source_range.end
        if enclosing_item is not None and enclosing_item.source_range is not None
        else phrase_range.end
    )
    preceding = next(
        (
            item.evidence_id
            for item in reversed(ranged)
            if item.kind == SILENCE_KIND
            and item.source_range is not None
            and item.source_range.end == context_start
        ),
        None,
    )
    following = next(
        (
            item.evidence_id
            for item in ranged
            if item.kind == SILENCE_KIND
            and item.source_range is not None
            and item.source_range.start == context_end
        ),
        None,
    )
    return (
        relevant,
        None if enclosing_item is None else enclosing_item.evidence_id,
        preceding,
        following,
    )


def _crosses_discontinuous_segment_boundary(
    words: tuple[SpeechWord, ...],
    segment_by_word: tuple[int, ...],
    first_index: int,
    last_index: int,
) -> bool:
    for index in range(first_index, last_index):
        if segment_by_word[index] == segment_by_word[index + 1]:
            continue
        if words[index].source_range.end != words[index + 1].source_range.start:
            return True
    return False


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
    _validate_vad_evidence(transcript, vad_evidence)

    timed_words = _timed_words(transcript)
    words = tuple(word for word, _ in timed_words)
    segment_by_word = tuple(segment_index for _, segment_index in timed_words)
    stream: list[str] = []
    word_by_unit: list[int] = []
    for word_index, word in enumerate(words):
        units = _normalized_units(word.text)
        stream.extend(units)
        word_by_unit.extend((word_index,) * len(units))

    if not stream:
        return ()

    candidates: list[PhraseMatchCandidate] = []
    seen_word_ranges: set[tuple[int, int]] = set()
    width = len(requested)
    for start in range(len(stream) - width + 1):
        if tuple(stream[start : start + width]) != requested:
            continue
        first_index = word_by_unit[start]
        last_index = word_by_unit[start + width - 1]
        word_range = (first_index, last_index)
        if word_range in seen_word_ranges:
            continue
        if _crosses_discontinuous_segment_boundary(
            words,
            segment_by_word,
            first_index,
            last_index,
        ):
            continue
        seen_word_ranges.add(word_range)
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

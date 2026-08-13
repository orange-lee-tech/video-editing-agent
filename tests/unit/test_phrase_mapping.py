from datetime import UTC, datetime

import pytest

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.evidence.speech import SpeechSegment, SpeechTranscript, SpeechWord
from video_editing_agent.domain.evidence.temporal import TemporalEvidence
from video_editing_agent.media.speech.phrase_mapping import map_phrase_to_time

SHOT_REF = EntityRevisionRef("sht_phrase", 2)
NOW = datetime(2026, 8, 13, tzinfo=UTC)


def _range(start: int, end: int) -> MediaTimeRange:
    return MediaTimeRange(MediaTime(start, 1), MediaTime(end - start, 1))


def _transcript(*segments: tuple[str, tuple[tuple[str, int, int], ...]]) -> SpeechTranscript:
    built = tuple(
        SpeechSegment(
            text,
            _range(words[0][1], words[-1][2]),
            tuple(SpeechWord(word, _range(start, end)) for word, start, end in words),
        )
        for text, words in segments
    )
    return SpeechTranscript(
        SHOT_REF,
        3,
        NOW,
        "local:asr",
        "pinned-r1",
        "".join(text for text, _ in segments),
        "en",
        built,
    )


def _vad(evidence_id: str, kind: str, start: int, end: int, *, shot_ref=SHOT_REF):
    return TemporalEvidence(evidence_id, shot_ref, kind, "vad", "r1", 0.9, _range(start, end))


def test_english_normalization_and_multiple_words_preserve_asset_time() -> None:
    transcript = _transcript(("Hello,   WORLD!", ((" Hello,", 11, 12), (" WORLD!", 12, 14))))
    match = map_phrase_to_time(transcript, "  hELLo world ")[0]
    assert match.source_range == _range(11, 14)
    assert (match.first_word_index, match.last_word_index) == (0, 1)
    assert match.transcript_revision == 3


def test_chinese_without_spaces_crosses_whisper_word_boundaries() -> None:
    transcript = _transcript(("今天 天气很好", (("今天", 5, 6), (" 天气", 6, 7), ("很好。", 7, 8))))
    match = map_phrase_to_time(transcript, "今天天气很好")[0]
    assert match.source_range == _range(5, 8)


def test_repeated_english_and_chinese_return_all_ordered_candidates() -> None:
    english = _transcript(
        ("go now, go now", (("go", 1, 2), ("now", 2, 3), ("go", 6, 7), ("now", 7, 8)))
    )
    chinese = _transcript(("你好你好", (("你好", 2, 3), ("你好", 4, 5))))
    assert [item.source_range for item in map_phrase_to_time(english, "GO NOW")] == [
        _range(1, 3),
        _range(6, 8),
    ]
    assert [item.source_range for item in map_phrase_to_time(chinese, "你好")] == [
        _range(2, 3),
        _range(4, 5),
    ]


def test_no_match_and_no_timed_words_do_not_guess_time() -> None:
    transcript = _transcript(("hello", (("hello", 3, 4),)))
    no_words = SpeechTranscript(
        SHOT_REF,
        1,
        NOW,
        "asr",
        "r1",
        "segment prose",
        "en",
        (SpeechSegment("segment prose", _range(3, 5)),),
    )
    assert map_phrase_to_time(transcript, "missing") == ()
    assert map_phrase_to_time(no_words, "segment") == ()


def test_match_can_span_segment_boundary_when_timed_words_are_contiguous() -> None:
    transcript = _transcript(("one", (("one", 3, 4),)), ("two", (("two", 4, 5),)))
    assert map_phrase_to_time(transcript, "one two")[0].source_range == _range(3, 5)


def test_vad_context_is_distinct_from_phrase_range() -> None:
    transcript = _transcript(("hello world", (("hello", 3, 4), ("world", 4, 5))))
    evidence = (
        _vad("silence-before", "silence", 2, 3),
        _vad("speech", "speech_activity", 3, 5),
        _vad("silence-after", "silence", 5, 6),
    )
    match = map_phrase_to_time(transcript, "hello world", vad_evidence=evidence)[0]
    assert match.relevant_vad_evidence_ids == ("speech",)
    assert match.enclosing_speech_evidence_id == "speech"
    assert match.preceding_silence_evidence_id == "silence-before"
    assert match.following_silence_evidence_id == "silence-after"
    assert match.source_range == _range(3, 5)


def test_wrong_shot_vad_and_empty_normalized_phrase_are_rejected() -> None:
    transcript = _transcript(("hello", (("hello", 3, 4),)))
    with pytest.raises(ValueError, match="exact Shot revision"):
        map_phrase_to_time(
            transcript,
            "hello",
            vad_evidence=(
                _vad("wrong", "speech_activity", 3, 4, shot_ref=EntityRevisionRef("sht_phrase", 1)),
            ),
        )
    with pytest.raises(ValueError, match="letter or number"):
        map_phrase_to_time(transcript, " ... !!! ")

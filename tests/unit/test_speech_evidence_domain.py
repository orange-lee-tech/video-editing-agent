from datetime import UTC, datetime

import pytest

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.evidence.speech import SpeechSegment, SpeechTranscript, SpeechWord

NOW = datetime(2026, 8, 12, 16, 30, tzinfo=UTC)


def _range(start: int, duration: int) -> MediaTimeRange:
    return MediaTimeRange(MediaTime(start, 10), MediaTime(duration, 10))


def test_speech_transcript_preserves_exact_rational_source_time() -> None:
    word = SpeechWord("hello", _range(101, 2), confidence=0.9)
    segment = SpeechSegment("hello", _range(100, 5), (word,), confidence=0.8)
    transcript = SpeechTranscript(
        shot_ref=EntityRevisionRef("sht_1", 2),
        revision=1,
        recognized_at=NOW,
        provider_id="example-asr",
        provider_revision="v1",
        text="hello",
        language="en",
        segments=(segment,),
    )

    assert transcript.segments[0].source_range.start == MediaTime(10, 1)
    assert transcript.segments[0].words[0].source_range.start == MediaTime(101, 10)


def test_word_must_stay_inside_segment() -> None:
    word = SpeechWord("outside", _range(90, 2))

    with pytest.raises(ValueError, match="inside"):
        SpeechSegment("segment", _range(100, 5), (word,))


def test_nonempty_transcript_requires_timed_segments() -> None:
    with pytest.raises(ValueError, match="timed"):
        SpeechTranscript(
            shot_ref=EntityRevisionRef("sht_1", 1),
            revision=1,
            recognized_at=NOW,
            provider_id="example-asr",
            provider_revision="v1",
            text="speech without timing",
        )


def test_empty_transcript_can_represent_no_detected_speech() -> None:
    transcript = SpeechTranscript(
        shot_ref=EntityRevisionRef("sht_1", 1),
        revision=1,
        recognized_at=NOW,
        provider_id="example-asr",
        provider_revision="v1",
        text="",
        language=None,
        segments=(),
    )

    assert transcript.text == ""
    assert transcript.segments == ()

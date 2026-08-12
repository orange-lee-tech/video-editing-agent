from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from fractions import Fraction
from math import isfinite

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTimeRange


def _validate_confidence(value: float | None) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("confidence must be a float or None")
    if not isfinite(float(value)) or not 0.0 <= float(value) <= 1.0:
        raise ValueError("confidence must be finite and between 0 and 1")


def _range_contains(outer: MediaTimeRange, inner: MediaTimeRange) -> bool:
    return (
        outer.start.as_fraction() <= inner.start.as_fraction()
        and inner.end.as_fraction() <= outer.end.as_fraction()
    )


@dataclass(frozen=True, slots=True)
class SpeechWord:
    """Validated word evidence in original Asset source time."""

    text: str
    source_range: MediaTimeRange
    confidence: float | None = None

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("SpeechWord text must not be empty")
        if self.source_range.start.as_fraction() < 0:
            raise ValueError("SpeechWord source_range must start at or after zero")
        _validate_confidence(self.confidence)


@dataclass(frozen=True, slots=True)
class SpeechSegment:
    """Validated segment evidence in original Asset source time."""

    text: str
    source_range: MediaTimeRange
    words: tuple[SpeechWord, ...] = ()
    confidence: float | None = None

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("SpeechSegment text must not be empty")
        if self.source_range.start.as_fraction() < 0:
            raise ValueError("SpeechSegment source_range must start at or after zero")
        _validate_confidence(self.confidence)

        previous_end = self.source_range.start.as_fraction()
        for word in self.words:
            if not _range_contains(self.source_range, word.source_range):
                raise ValueError("SpeechWord source_range must stay inside its SpeechSegment")
            if word.source_range.start.as_fraction() < previous_end:
                raise ValueError("SpeechWord ranges must be ordered and non-overlapping")
            previous_end = word.source_range.end.as_fraction()


@dataclass(frozen=True, slots=True)
class SpeechTranscript:
    """Revisioned, provider-derived speech evidence bound to one exact Shot revision."""

    shot_ref: EntityRevisionRef
    revision: int
    recognized_at: datetime
    provider_id: str
    provider_revision: str
    text: str
    language: str | None = None
    segments: tuple[SpeechSegment, ...] = ()
    artifact_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if isinstance(self.revision, bool) or not isinstance(self.revision, int):
            raise TypeError("SpeechTranscript revision must be an int")
        if self.revision < 1:
            raise ValueError("SpeechTranscript revision must be >= 1")
        if not self.provider_id.strip():
            raise ValueError("SpeechTranscript provider_id must not be empty")
        if not self.provider_revision.strip():
            raise ValueError("SpeechTranscript provider_revision must not be empty")
        if self.language is not None and not self.language.strip():
            raise ValueError("SpeechTranscript language must be non-empty or None")
        if self.segments and not self.text.strip():
            raise ValueError("SpeechTranscript text must not be empty when segments exist")
        if self.text.strip() and not self.segments:
            raise ValueError(
                "timed SpeechTranscript segments are required when transcript text exists"
            )
        if any(not ref.strip() for ref in self.artifact_refs):
            raise ValueError("SpeechTranscript artifact_refs must not contain empty values")

        previous_end: Fraction | None = None
        for segment in self.segments:
            start = segment.source_range.start.as_fraction()
            if previous_end is not None and start < previous_end:
                raise ValueError("SpeechSegment ranges must be ordered and non-overlapping")
            previous_end = segment.source_range.end.as_fraction()

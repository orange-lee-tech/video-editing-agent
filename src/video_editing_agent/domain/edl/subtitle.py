from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from video_editing_agent.domain.common.media_time import MediaTimeRange


class SubtitleEmphasisStyle(StrEnum):
    BOLD = "bold"
    HIGHLIGHT = "highlight"


class SubtitleLayoutRegion(StrEnum):
    LOWER_SAFE = "lower_safe"
    UPPER_SAFE = "upper_safe"


@dataclass(frozen=True, slots=True)
class SubtitleEmphasisSpan:
    start: int
    end: int
    style: SubtitleEmphasisStyle


@dataclass(frozen=True, slots=True)
class StructuredSubtitleCue:
    """Approved subtitle wording and intent; it is not raw ASR evidence."""

    cue_id: str
    timeline_range: MediaTimeRange
    text: str
    language: str
    speaker_ref: str | None = None
    emphasis: tuple[SubtitleEmphasisSpan, ...] = ()
    layout: SubtitleLayoutRegion = SubtitleLayoutRegion.LOWER_SAFE


@dataclass(frozen=True, slots=True)
class EDLSubtitleCue:
    """Self-contained canonical subtitle execution truth."""

    cue_id: str
    track_id: str
    timeline_range: MediaTimeRange
    text: str
    language: str
    speaker_ref: str | None = None
    emphasis: tuple[SubtitleEmphasisSpan, ...] = ()
    layout: SubtitleLayoutRegion = SubtitleLayoutRegion.LOWER_SAFE

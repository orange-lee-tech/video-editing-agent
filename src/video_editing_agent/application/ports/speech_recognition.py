from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTimeRange


class SpeechRecognitionCapabilityUnavailable(RuntimeError):
    """The approved ASR runtime/model is unavailable for a grounded speech request."""


@dataclass(frozen=True, slots=True)
class SpeechWordProposal:
    """Provider proposal whose range is relative to the requested Shot start."""

    text: str
    relative_range: MediaTimeRange
    confidence: float | None = None


@dataclass(frozen=True, slots=True)
class SpeechSegmentProposal:
    """Provider segment proposal in Shot-relative time, never authoritative source time."""

    text: str
    relative_range: MediaTimeRange
    words: tuple[SpeechWordProposal, ...] = ()
    confidence: float | None = None


@dataclass(frozen=True, slots=True)
class SpeechRecognitionRequest:
    """Exact local media and authoritative Shot range supplied to a speech provider."""

    shot_ref: EntityRevisionRef
    local_media_path: pathlib.Path
    source_range: MediaTimeRange


@dataclass(frozen=True, slots=True)
class SpeechRecognitionProposal:
    """Non-authoritative provider result; all proposed timing is Shot-relative."""

    provider_id: str
    provider_revision: str
    text: str
    language: str | None = None
    segments: tuple[SpeechSegmentProposal, ...] = ()


class SpeechRecognitionPort(Protocol):
    """Propose transcript/timing evidence without owning source-time truth or persistence."""

    def recognize(self, request: SpeechRecognitionRequest) -> SpeechRecognitionProposal: ...

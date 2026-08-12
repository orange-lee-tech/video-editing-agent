from __future__ import annotations

import pathlib
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTimeRange


class VoiceActivityState(StrEnum):
    SPEECH = "speech"
    SILENCE = "silence"


@dataclass(frozen=True, slots=True)
class VoiceActivitySpanProposal:
    """One provider-proposed class span in time relative to the requested Shot start."""

    state: VoiceActivityState
    relative_range: MediaTimeRange
    confidence: float


@dataclass(frozen=True, slots=True)
class VoiceActivityRequest:
    """Exact local media plus authoritative Shot range supplied to a VAD provider."""

    shot_ref: EntityRevisionRef
    local_media_path: pathlib.Path
    source_range: MediaTimeRange


@dataclass(frozen=True, slots=True)
class VoiceActivityProposal:
    """Non-authoritative complete speech/silence partition proposed for one Shot."""

    provider_id: str
    provider_revision: str
    spans: tuple[VoiceActivitySpanProposal, ...]


class VoiceActivityPort(Protocol):
    """Propose a full Shot-relative speech/silence partition without persistence authority."""

    def analyze(self, request: VoiceActivityRequest) -> VoiceActivityProposal: ...

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime


@dataclass(frozen=True, slots=True)
class SpeechSynthesisRequest:
    text: str
    language: str
    target_duration: MediaTime
    source_evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.text.strip() or not self.language.strip():
            raise ValueError("speech synthesis text and language must not be empty")
        if not self.source_evidence_refs:
            raise ValueError("speech synthesis requires grounded source evidence")


@dataclass(frozen=True, slots=True)
class SynthesizedSpeechAsset:
    """Approved derived speech Asset; provider output never replaces source authority."""

    asset_ref: EntityRevisionRef
    derived_from_asset_refs: tuple[EntityRevisionRef, ...]
    provider_id: str
    provider_revision: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.asset_ref in self.derived_from_asset_refs:
            raise ValueError("synthesized speech must be a distinct derived Asset revision")
        if not self.derived_from_asset_refs:
            raise ValueError("synthesized speech requires source provenance")


class SpeechSynthesisPort(Protocol):
    def synthesize(self, request: SpeechSynthesisRequest) -> SynthesizedSpeechAsset: ...

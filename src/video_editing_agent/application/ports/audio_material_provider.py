from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.domain.asset.rights import RightsEligibility


@dataclass(frozen=True, slots=True)
class MusicDiscoveryQuery:
    """Audio-only discovery request. Visual material discovery is intentionally absent."""

    query: str
    commercial_use_required: bool = True
    generated_audio_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise ValueError("query must not be empty")
        if not isinstance(self.commercial_use_required, bool):
            raise TypeError("commercial_use_required must be a bool")
        if not isinstance(self.generated_audio_allowed, bool):
            raise TypeError("generated_audio_allowed must be a bool")


@dataclass(frozen=True, slots=True)
class AudioMaterialCandidate:
    """Provider proposal only; it is not an Asset and carries no timeline authority."""

    provider: str
    provider_item_id: str
    rights_eligibility: RightsEligibility
    title: str | None = None
    source_page: str | None = None
    license_snapshot_id: str | None = None
    is_generated_audio: bool = False

    def __post_init__(self) -> None:
        if not self.provider.strip():
            raise ValueError("provider must not be empty")
        if not self.provider_item_id.strip():
            raise ValueError("provider_item_id must not be empty")
        if not isinstance(self.is_generated_audio, bool):
            raise TypeError("is_generated_audio must be a bool")


class AudioMaterialProvider(Protocol):
    """Future rights-aware audio discovery seam. It cannot create Assets or visual candidates."""

    def search_music(self, query: MusicDiscoveryQuery) -> tuple[AudioMaterialCandidate, ...]: ...

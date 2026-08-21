from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTimeRange


class AudioStemRole(StrEnum):
    ORIGINAL_AUDIO = "original_audio"
    SPEECH = "speech"
    AMBIENCE = "ambience"
    MUSIC = "music"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class AudioSeparationRequest:
    source_asset_ref: EntityRevisionRef
    source_range: MediaTimeRange
    requested_roles: tuple[AudioStemRole, ...]

    def __post_init__(self) -> None:
        if not self.requested_roles:
            raise ValueError("audio separation requires at least one requested stem role")
        if len(set(self.requested_roles)) != len(self.requested_roles):
            raise ValueError("requested stem roles must be unique")


@dataclass(frozen=True, slots=True)
class DerivedAudioStem:
    asset_ref: EntityRevisionRef
    role: AudioStemRole
    derived_from_asset_ref: EntityRevisionRef
    source_range: MediaTimeRange
    provider_id: str
    provider_revision: str
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.asset_ref == self.derived_from_asset_ref:
            raise ValueError("audio stem must be a distinct derived Asset revision")
        if not self.provider_id.strip() or not self.provider_revision.strip():
            raise ValueError("derived audio stem requires provider provenance")


class AudioSeparationPort(Protocol):
    def separate(self, request: AudioSeparationRequest) -> tuple[DerivedAudioStem, ...]: ...

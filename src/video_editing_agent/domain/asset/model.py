from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityEnvelope


@dataclass(frozen=True, slots=True)
class Asset:
    envelope: EntityEnvelope
    media_kind: str
    origin: str
    storage_ref: str
    content_hash: str

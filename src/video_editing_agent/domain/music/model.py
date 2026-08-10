from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef


@dataclass(frozen=True, slots=True)
class BeatMap:
    envelope: EntityEnvelope
    audio_asset_ref: EntityRevisionRef

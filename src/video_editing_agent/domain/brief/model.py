from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityEnvelope


@dataclass(frozen=True, slots=True)
class Brief:
    envelope: EntityEnvelope
    title: str
    objective: str
    audience: str
    platform: str
    core_message: str

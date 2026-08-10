from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef


@dataclass(frozen=True, slots=True)
class ReviewReport:
    envelope: EntityEnvelope
    stage: str
    target_ref: EntityRevisionRef
    passed: bool

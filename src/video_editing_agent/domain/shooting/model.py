from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef


@dataclass(frozen=True, slots=True)
class ShotRequirement:
    requirement_id: str
    script_section_ref: str
    purpose: str
    subject: str


@dataclass(frozen=True, slots=True)
class ShootingPlan:
    envelope: EntityEnvelope
    script_plan_ref: EntityRevisionRef
    requirements: tuple[ShotRequirement, ...]

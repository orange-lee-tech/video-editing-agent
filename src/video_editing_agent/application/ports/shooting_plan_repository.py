from __future__ import annotations

from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shooting.model import ShootingPlan


class ShootingPlanRepository(Protocol):
    """Persist already-created ShootingPlan revisions without planning authority."""

    def load(self, shooting_plan_ref: EntityRevisionRef) -> ShootingPlan: ...

    def save(self, shooting_plan: ShootingPlan) -> None: ...

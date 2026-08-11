from __future__ import annotations

from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.script.model import ScriptPlan


class ScriptPlanRepository(Protocol):
    """Persist already-created ScriptPlan revisions without planning authority."""

    def load(self, script_plan_ref: EntityRevisionRef) -> ScriptPlan: ...

    def save(self, script_plan: ScriptPlan) -> None: ...

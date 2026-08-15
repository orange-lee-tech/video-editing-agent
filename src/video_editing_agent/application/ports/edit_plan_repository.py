from __future__ import annotations

from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.edit.model import EditPlan


class EditPlanRepository(Protocol):
    def save(self, edit_plan: EditPlan) -> None: ...

    def load(self, edit_plan_ref: EntityRevisionRef) -> EditPlan: ...

    def latest_revision(self, entity_id: str) -> int | None: ...

    def count(self) -> int: ...

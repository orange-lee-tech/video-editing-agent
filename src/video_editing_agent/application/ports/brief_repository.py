from __future__ import annotations

from typing import Protocol

from video_editing_agent.domain.brief.model import Brief
from video_editing_agent.domain.common.entity import EntityRevisionRef


class BriefRepository(Protocol):
    """Persist already-created Brief revisions without gaining semantic ownership."""

    def load(self, brief_ref: EntityRevisionRef) -> Brief: ...

    def save(self, brief: Brief) -> None: ...

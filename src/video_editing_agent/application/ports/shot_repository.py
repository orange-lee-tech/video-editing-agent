from __future__ import annotations

from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shot.model import Shot


class ShotRepository(Protocol):
    """Load authoritative Shot identity by exact revision."""

    def load(self, shot_ref: EntityRevisionRef) -> Shot: ...

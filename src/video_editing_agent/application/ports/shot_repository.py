from __future__ import annotations

from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shot.model import Shot


class ShotRepository(Protocol):
    """Load authoritative Shot identity by exact revision."""

    def load(self, shot_ref: EntityRevisionRef) -> Shot: ...


class ShotPersistenceRepository(ShotRepository, Protocol):
    """Persist already-created Shot revisions without acquiring identity ownership."""

    def save(self, shot: Shot) -> None: ...

    def save_many(self, shots: tuple[Shot, ...]) -> None: ...

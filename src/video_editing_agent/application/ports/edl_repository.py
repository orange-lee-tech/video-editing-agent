from __future__ import annotations

from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.edl.model import EDL


class EDLRepository(Protocol):
    def save(self, edl: EDL) -> None: ...

    def load(self, edl_ref: EntityRevisionRef) -> EDL: ...

    def latest_revision(self, entity_id: str) -> int | None: ...

    def count(self) -> int: ...

from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef


@dataclass(frozen=True, slots=True)
class Shot:
    envelope: EntityEnvelope
    asset_ref: EntityRevisionRef
    source_start_ms: int
    source_end_ms: int

    @property
    def duration_ms(self) -> int:
        return self.source_end_ms - self.source_start_ms

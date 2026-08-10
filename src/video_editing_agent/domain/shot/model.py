from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef


@dataclass(frozen=True, slots=True)
class Shot:
    envelope: EntityEnvelope
    asset_ref: EntityRevisionRef
    source_start_ms: int
    source_end_ms: int
    boundary_method: str
    previous_shot_ref: EntityRevisionRef | None = None
    next_shot_ref: EntityRevisionRef | None = None
    scene_ref: EntityRevisionRef | None = None

    def __post_init__(self) -> None:
        if isinstance(self.source_start_ms, bool) or not isinstance(self.source_start_ms, int):
            raise TypeError("source_start_ms must be an int")
        if isinstance(self.source_end_ms, bool) or not isinstance(self.source_end_ms, int):
            raise TypeError("source_end_ms must be an int")
        if self.source_start_ms < 0:
            raise ValueError("source_start_ms must be >= 0")
        if self.source_end_ms <= self.source_start_ms:
            raise ValueError("source_end_ms must be greater than source_start_ms")
        if not self.boundary_method.strip():
            raise ValueError("boundary_method must not be empty")

    @property
    def duration_ms(self) -> int:
        return self.source_end_ms - self.source_start_ms

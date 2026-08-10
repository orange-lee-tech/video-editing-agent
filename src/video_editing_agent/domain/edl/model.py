from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef


@dataclass(frozen=True, slots=True)
class EDLSegment:
    segment_id: str
    asset_ref: EntityRevisionRef
    source_in_ms: int
    source_out_ms: int
    timeline_in_ms: int
    timeline_out_ms: int


@dataclass(frozen=True, slots=True)
class EDL:
    envelope: EntityEnvelope
    edit_plan_ref: EntityRevisionRef
    segments: tuple[EDLSegment, ...]

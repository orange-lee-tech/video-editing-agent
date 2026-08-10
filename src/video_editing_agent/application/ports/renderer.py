from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef


@dataclass(frozen=True, slots=True)
class RenderArtifact:
    path: str


class Renderer(Protocol):
    def render(self, edl_ref: EntityRevisionRef) -> RenderArtifact: ...

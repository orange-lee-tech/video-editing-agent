from __future__ import annotations

from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shot.analysis import ShotAnalysis


class ShotAnalysisRepository(Protocol):
    """Persistence seam for derived ShotAnalysis revisions; no semantic authority."""

    def latest(self, shot_ref: EntityRevisionRef) -> ShotAnalysis | None: ...

    def save(self, analysis: ShotAnalysis) -> None: ...

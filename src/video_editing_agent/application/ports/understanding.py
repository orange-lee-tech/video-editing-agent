from __future__ import annotations

from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shot.analysis import AnalysisProfile, ShotAnalysis


class UnderstandingService(Protocol):
    """Application-facing owner of derived ShotAnalysis revisions."""

    def analyze(self, shot_ref: EntityRevisionRef, profile: AnalysisProfile) -> ShotAnalysis: ...

    def reanalyze(self, shot_ref: EntityRevisionRef, profile: AnalysisProfile) -> ShotAnalysis: ...

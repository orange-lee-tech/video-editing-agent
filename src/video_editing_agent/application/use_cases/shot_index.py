from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from video_editing_agent.application.ports.shot_analysis_repository import ShotAnalysisRepository
from video_editing_agent.application.ports.shot_index import ShotIndex, ShotIndexSource
from video_editing_agent.application.ports.shot_repository import ShotRepository
from video_editing_agent.domain.common.entity import EntityRevisionRef


@dataclass(frozen=True, slots=True)
class ShotIndexRebuildResult:
    requested_count: int
    indexed_count: int
    skipped_without_analysis: tuple[EntityRevisionRef, ...]


class MaintainShotIndex:
    """Application orchestration for a rebuildable, non-authoritative ShotIndex."""

    def __init__(
        self,
        *,
        shot_repository: ShotRepository,
        analysis_repository: ShotAnalysisRepository,
        shot_index: ShotIndex,
    ) -> None:
        self._shot_repository = shot_repository
        self._analysis_repository = analysis_repository
        self._shot_index = shot_index

    def refresh(self, shot_ref: EntityRevisionRef) -> bool:
        shot = self._shot_repository.load(shot_ref)
        analysis = self._analysis_repository.latest(shot_ref)
        if analysis is None:
            self._shot_index.remove(shot_ref)
            return False

        self._shot_index.upsert(ShotIndexSource(shot=shot, analysis=analysis))
        return True

    def rebuild(self, shot_refs: Iterable[EntityRevisionRef]) -> ShotIndexRebuildResult:
        ordered_refs = tuple(shot_refs)
        if len(set(ordered_refs)) != len(ordered_refs):
            raise ValueError("shot_refs must not contain duplicate exact revisions")

        sources: list[ShotIndexSource] = []
        skipped: list[EntityRevisionRef] = []
        for shot_ref in ordered_refs:
            shot = self._shot_repository.load(shot_ref)
            analysis = self._analysis_repository.latest(shot_ref)
            if analysis is None:
                skipped.append(shot_ref)
                continue
            sources.append(ShotIndexSource(shot=shot, analysis=analysis))

        self._shot_index.rebuild(sources)
        return ShotIndexRebuildResult(
            requested_count=len(ordered_refs),
            indexed_count=len(sources),
            skipped_without_analysis=tuple(skipped),
        )

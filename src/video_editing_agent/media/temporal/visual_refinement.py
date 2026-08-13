from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.application.ports.shot_repository import ShotRepository
from video_editing_agent.application.ports.temporal_evidence_repository import (
    TemporalEvidenceRepository,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.evidence.temporal import TemporalAnchor, TemporalEvidence
from video_editing_agent.media.temporal.visual_events import (
    CAMERA_REGION_KIND,
    RESIDUAL_REGION_KIND,
    MotionEventPolicy,
    VisualMotionEventService,
)
from video_editing_agent.media.temporal.visual_motion import VisualMotionEvidenceService


@dataclass(frozen=True, slots=True)
class VisualRefinementPolicy:
    policy_id: str
    neighborhood_padding: MediaTime
    event_policy: MotionEventPolicy

    def __post_init__(self) -> None:
        if not self.policy_id.strip():
            raise ValueError("refinement policy_id must not be empty")
        if self.neighborhood_padding.as_fraction() < 0:
            raise ValueError("refinement padding must not be negative")


class VisualMotionRefinementService:
    """Refine an explicitly selected coarse region without acquiring edit authority."""

    def __init__(
        self,
        *,
        shot_repository: ShotRepository,
        temporal_evidence_repository: TemporalEvidenceRepository,
        motion_evidence_service: VisualMotionEvidenceService,
        event_service: VisualMotionEventService,
    ) -> None:
        self._shots = shot_repository
        self._repository = temporal_evidence_repository
        self._motion = motion_evidence_service
        self._events = event_service

    def refine(
        self,
        shot_ref: EntityRevisionRef,
        coarse_region_evidence_id: str,
        policy: VisualRefinementPolicy,
    ) -> tuple[tuple[TemporalEvidence, ...], tuple[TemporalAnchor, ...]]:
        shot = self._shots.load(shot_ref)
        region = next(
            (
                item
                for item in self._repository.list_evidence(shot_ref)
                if item.evidence_id == coarse_region_evidence_id
            ),
            None,
        )
        if region is None:
            raise KeyError(coarse_region_evidence_id)
        if region.kind not in (CAMERA_REGION_KIND, RESIDUAL_REGION_KIND):
            raise ValueError("refinement input must be a coarse motion region")
        if region.source_range is None:
            raise ValueError("coarse motion region must have an exact source range")
        shot_start = shot.source_range.start.as_fraction()
        shot_end = shot.source_range.end.as_fraction()
        start = max(
            shot_start,
            region.source_range.start.as_fraction() - policy.neighborhood_padding.as_fraction(),
        )
        end = min(
            shot_end,
            region.source_range.end.as_fraction() + policy.neighborhood_padding.as_fraction(),
        )
        analysis_range = MediaTimeRange(
            MediaTime(start.numerator, start.denominator),
            MediaTime((end - start).numerator, (end - start).denominator),
        )
        measurement = self._motion.measure(shot_ref, analysis_range)[0]
        return self._events.reduce(shot_ref, measurement.evidence_id, policy.event_policy)

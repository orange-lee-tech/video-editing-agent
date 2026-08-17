from __future__ import annotations

import hashlib

from video_editing_agent.application.ports.shot_index import ShotIndex, ShotSearchConstraints
from video_editing_agent.application.ports.shot_repository import ShotRepository
from video_editing_agent.application.ports.temporal_evidence_repository import (
    TemporalEvidenceRepository,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.model import EditPlan, EditSlot
from video_editing_agent.domain.edit.resolution import CandidateWindow, ResolutionDecision
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.editing.director.candidate_windows import generate_candidate_windows
from video_editing_agent.editing.resolver.optimizer import ResolverCandidate, optimize_sequence


class GroundedEditPlanResolver:
    """Promote indexed Shot evidence into grounded Resolver decisions without timeline authority."""

    def __init__(
        self,
        *,
        shot_index: ShotIndex,
        shot_repository: ShotRepository,
        temporal_evidence_repository: TemporalEvidenceRepository,
        search_limit: int = 20,
    ) -> None:
        if isinstance(search_limit, bool) or not isinstance(search_limit, int):
            raise TypeError("search_limit must be an int")
        if search_limit < 1:
            raise ValueError("search_limit must be >= 1")
        self._shot_index = shot_index
        self._shots = shot_repository
        self._temporal = temporal_evidence_repository
        self._search_limit = search_limit

    def resolve(self, edit_plan: EditPlan) -> tuple[ResolutionDecision, ...]:
        plan_ref = EntityRevisionRef(edit_plan.envelope.id, edit_plan.envelope.revision)
        candidates_by_slot = {slot.slot_id: self._slot_candidates(slot) for slot in edit_plan.slots}
        return optimize_sequence(edit_plan, candidates_by_slot, plan_ref=plan_ref)

    def _slot_candidates(self, slot: EditSlot) -> tuple[ResolverCandidate, ...]:
        minimum = None if slot.target_duration is None else slot.target_duration.minimum
        retrieved = self._shot_index.search(
            slot.semantic_query,
            constraints=ShotSearchConstraints(min_duration=minimum),
            limit=self._search_limit,
        )
        candidates: list[ResolverCandidate] = []
        for item in retrieved:
            shot = self._shots.load(item.shot_ref)
            shot_ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
            if shot_ref != item.shot_ref:
                raise RuntimeError("ShotRepository returned a different exact Shot revision")
            windows = generate_candidate_windows(
                slot,
                shot,
                self._temporal.list_anchors(shot_ref),
                self._temporal.list_evidence(shot_ref),
            )
            grounded = tuple(value.window for value in windows)
            if not grounded:
                fallback = _shot_boundary_window(slot, shot)
                grounded = () if fallback is None else (fallback,)
            for window in grounded:
                confidence = 0.5 if window.confidence is None else window.confidence
                candidates.append(
                    ResolverCandidate(
                        window,
                        item.retrieval_score,
                        confidence,
                        confidence,
                    )
                )
        return tuple(candidates)


def _shot_boundary_window(slot: EditSlot, shot: Shot) -> CandidateWindow | None:
    shot_ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
    if slot.target_duration is None:
        source_range = shot.source_range
    else:
        shot_duration = shot.source_range.duration
        minimum = slot.target_duration.minimum
        if shot_duration.as_fraction() < minimum.as_fraction():
            return None
        maximum = slot.target_duration.maximum
        duration = _min_time(shot_duration, maximum)
        source_range = MediaTimeRange(shot.source_range.start, duration)
    evidence_ref = f"shot-boundary:{shot_ref.entity_id}@{shot_ref.revision}"
    digest = hashlib.sha256(
        f"{slot.slot_id}:{shot_ref}:{source_range}:{evidence_ref}:product-flow-v1".encode()
    ).hexdigest()
    return CandidateWindow(
        f"cwin_{digest}",
        shot_ref,
        source_range,
        0.5,
        evidence_refs=(evidence_ref,),
    )


def _min_time(left: MediaTime, right: MediaTime) -> MediaTime:
    return left if left.as_fraction() <= right.as_fraction() else right

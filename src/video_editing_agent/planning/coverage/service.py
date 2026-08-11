from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from video_editing_agent.application.ports.asset_repository import AssetRepository
from video_editing_agent.application.ports.shot_index import ShotCandidate, ShotIndex
from video_editing_agent.application.ports.shot_repository import ShotRepository
from video_editing_agent.domain.asset.policy import is_visual_resolver_eligible
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.shooting.model import CoveragePriority, ShootingPlan, ShotRequirement


class CoverageState(StrEnum):
    UNMATCHED = "unmatched"
    WEAK = "weak"
    SATISFIED = "satisfied"
    OVERCOVERED = "overcovered"


class CoverageAction(StrEnum):
    NONE = "none"
    RESHOOT_RECOMMENDED = "reshoot_recommended"
    RESHOOT_REQUIRED = "reshoot_required"


@dataclass(frozen=True, slots=True)
class CoverageEvaluationPolicy:
    """Calibratable coverage policy; no implicit overcoverage threshold is assumed."""

    overcovered_candidate_count: int | None = None
    search_limit: int = 20

    def __post_init__(self) -> None:
        if self.overcovered_candidate_count is not None:
            if (
                isinstance(self.overcovered_candidate_count, bool)
                or not isinstance(self.overcovered_candidate_count, int)
            ):
                raise TypeError("overcovered_candidate_count must be an int or None")
            if self.overcovered_candidate_count < 2:
                raise ValueError("overcovered_candidate_count must be >= 2")
        if isinstance(self.search_limit, bool) or not isinstance(self.search_limit, int):
            raise TypeError("search_limit must be an int")
        if self.search_limit < 1:
            raise ValueError("search_limit must be >= 1")


@dataclass(frozen=True, slots=True)
class CoverageCandidate:
    shot_ref: EntityRevisionRef
    analysis_revision: int
    retrieval_score: float
    matched_terms: tuple[str, ...]
    duration: MediaTime


@dataclass(frozen=True, slots=True)
class CoverageAssessment:
    requirement_id: str
    state: CoverageState
    action: CoverageAction
    candidates: tuple[CoverageCandidate, ...]
    reason: str
    reshoot_instruction: str | None = None


@dataclass(frozen=True, slots=True)
class CoverageReport:
    shooting_plan_ref: EntityRevisionRef
    assessments: tuple[CoverageAssessment, ...]

    @property
    def unresolved_required_ids(self) -> tuple[str, ...]:
        return tuple(
            assessment.requirement_id
            for assessment in self.assessments
            if assessment.action is CoverageAction.RESHOOT_REQUIRED
        )


def _requirement_query(requirement: ShotRequirement) -> str:
    parts = (
        requirement.subject,
        requirement.action,
        requirement.purpose,
        requirement.environment,
        requirement.framing,
        *requirement.visual_constraints,
    )
    query = " ".join(part.strip() for part in parts if part is not None and part.strip())
    if not query:
        raise ValueError(f"ShotRequirement {requirement.requirement_id!r} has no searchable content")
    return query


def _meets_duration(candidate: CoverageCandidate, required: MediaTime | None) -> bool:
    if required is None:
        return True
    return candidate.duration.as_fraction() >= required.as_fraction()


def _action_for(requirement: ShotRequirement, state: CoverageState) -> CoverageAction:
    if state in {CoverageState.SATISFIED, CoverageState.OVERCOVERED}:
        return CoverageAction.NONE
    if requirement.priority is CoveragePriority.REQUIRED:
        return CoverageAction.RESHOOT_REQUIRED
    if requirement.priority is CoveragePriority.RECOMMENDED:
        return CoverageAction.RESHOOT_RECOMMENDED
    return CoverageAction.NONE


def _reshoot_instruction(requirement: ShotRequirement, action: CoverageAction) -> str | None:
    if action is CoverageAction.NONE:
        return None
    if requirement.capture_instruction is not None:
        return requirement.capture_instruction
    pieces = [
        f"Capture additional footage for: {requirement.purpose}.",
        f"Show {requirement.subject}.",
    ]
    if requirement.action is not None:
        pieces.append(f"Action: {requirement.action}.")
    if requirement.framing is not None:
        pieces.append(f"Framing: {requirement.framing}.")
    return " ".join(pieces)


class CoverageService:
    """Evaluate ShootingPlan coverage from eligible user footage without source selection."""

    def __init__(
        self,
        *,
        shot_index: ShotIndex,
        shot_repository: ShotRepository,
        asset_repository: AssetRepository,
        policy: CoverageEvaluationPolicy | None = None,
    ) -> None:
        self._shot_index = shot_index
        self._shot_repository = shot_repository
        self._asset_repository = asset_repository
        self._policy = CoverageEvaluationPolicy() if policy is None else policy

    def evaluate(self, shooting_plan: ShootingPlan) -> CoverageReport:
        shooting_plan_ref = EntityRevisionRef(
            shooting_plan.envelope.id,
            shooting_plan.envelope.revision,
        )
        assessments = tuple(self._evaluate_requirement(item) for item in shooting_plan.requirements)
        return CoverageReport(shooting_plan_ref=shooting_plan_ref, assessments=assessments)

    def _evaluate_requirement(self, requirement: ShotRequirement) -> CoverageAssessment:
        raw_candidates = self._shot_index.search(
            _requirement_query(requirement),
            limit=self._policy.search_limit,
        )
        candidates = tuple(
            candidate
            for raw in raw_candidates
            if (candidate := self._eligible_candidate(raw)) is not None
        )

        if not candidates:
            state = CoverageState.UNMATCHED
            reason = "No constitutionally eligible local visual Shot matched this requirement."
        else:
            minimum_candidates = tuple(
                candidate
                for candidate in candidates
                if _meets_duration(candidate, requirement.minimum_duration)
            )
            if not minimum_candidates:
                state = CoverageState.WEAK
                reason = "Matched local footage is shorter than the declared minimum duration."
            else:
                target_candidates = tuple(
                    candidate
                    for candidate in minimum_candidates
                    if _meets_duration(candidate, requirement.target_duration)
                )
                if requirement.target_duration is not None and not target_candidates:
                    state = CoverageState.WEAK
                    reason = "Eligible footage meets the minimum but not the target duration."
                else:
                    effective = target_candidates or minimum_candidates
                    threshold = self._policy.overcovered_candidate_count
                    if threshold is not None and len(effective) >= threshold:
                        state = CoverageState.OVERCOVERED
                        reason = (
                            "Multiple eligible alternatives meet the configured coverage policy."
                        )
                    else:
                        state = CoverageState.SATISFIED
                        reason = (
                            "At least one eligible local Shot meets the declared duration need."
                        )

        action = _action_for(requirement, state)
        return CoverageAssessment(
            requirement_id=requirement.requirement_id,
            state=state,
            action=action,
            candidates=candidates,
            reason=reason,
            reshoot_instruction=_reshoot_instruction(requirement, action),
        )

    def _eligible_candidate(self, candidate: ShotCandidate) -> CoverageCandidate | None:
        shot = self._shot_repository.load(candidate.shot_ref)
        asset = self._asset_repository.load(shot.asset_ref)
        if not is_visual_resolver_eligible(
            media_kind=asset.media_kind,
            origin=asset.origin,
            usage_role=asset.usage_role,
        ):
            return None
        return CoverageCandidate(
            shot_ref=candidate.shot_ref,
            analysis_revision=candidate.analysis_revision,
            retrieval_score=candidate.retrieval_score,
            matched_terms=candidate.matched_terms,
            duration=shot.source_range.duration,
        )

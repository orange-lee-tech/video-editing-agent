from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import UTC, datetime

from video_editing_agent.application.ports.artifact_store import ArtifactStore
from video_editing_agent.application.ports.asset_media import AssetMediaResolver
from video_editing_agent.application.ports.shot_analysis_repository import ShotAnalysisRepository
from video_editing_agent.application.ports.shot_repository import ShotRepository
from video_editing_agent.application.ports.understanding import UnderstandingService
from video_editing_agent.application.ports.visual_understanding import (
    VisualUnderstandingPort,
    VisualUnderstandingRequest,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shot.analysis import AnalysisProfile, ShotAnalysis
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.understanding.artifacts import persist_extracted_frame_samples
from video_editing_agent.media.understanding.frame_extraction import FramePlanExtractor
from video_editing_agent.media.understanding.sampling import (
    FrameSamplingOptions,
    plan_uniform_frame_samples,
)
from video_editing_agent.media.understanding.visual_validation import (
    normalize_visual_understanding_proposal,
)

VISUAL_FRAME_BUDGETS: Mapping[AnalysisProfile, int] = {
    AnalysisProfile.SEMANTIC: 3,
    AnalysisProfile.DEEP_VISUAL: 7,
    AnalysisProfile.EDITORIAL: 5,
}


class UnsupportedAnalysisProfile(ValueError):
    """Raised when this visual owner cannot truthfully satisfy an AnalysisProfile yet."""


def _utc_now() -> datetime:
    return datetime.now(UTC)


class ProviderNeutralVisualUnderstandingService(UnderstandingService):
    """Own visual ShotAnalysis revisions while keeping providers and storage non-authoritative."""

    def __init__(
        self,
        *,
        shot_repository: ShotRepository,
        asset_media_resolver: AssetMediaResolver,
        analysis_repository: ShotAnalysisRepository,
        frame_extractor: FramePlanExtractor,
        artifact_store: ArtifactStore,
        visual_port: VisualUnderstandingPort,
        clock: Callable[[], datetime] = _utc_now,
        frame_budgets: Mapping[AnalysisProfile, int] = VISUAL_FRAME_BUDGETS,
    ) -> None:
        self._shot_repository = shot_repository
        self._asset_media_resolver = asset_media_resolver
        self._analysis_repository = analysis_repository
        self._frame_extractor = frame_extractor
        self._artifact_store = artifact_store
        self._visual_port = visual_port
        self._clock = clock
        self._frame_budgets = dict(frame_budgets)

    def _frame_budget(self, profile: AnalysisProfile) -> int:
        try:
            budget = self._frame_budgets[profile]
        except KeyError as exc:
            raise UnsupportedAnalysisProfile(
                f"visual understanding does not support profile: {profile.value}"
            ) from exc
        if isinstance(budget, bool) or not isinstance(budget, int) or budget < 1:
            raise ValueError(f"frame budget for {profile.value} must be a positive int")
        return budget

    def _load_exact_shot(self, shot_ref: EntityRevisionRef) -> Shot:
        shot = self._shot_repository.load(shot_ref)
        loaded_ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
        if loaded_ref != shot_ref:
            raise RuntimeError(
                f"ShotRepository returned {loaded_ref.entity_id}@{loaded_ref.revision} "
                f"for requested {shot_ref.entity_id}@{shot_ref.revision}"
            )
        return shot

    def _create_analysis(
        self,
        shot_ref: EntityRevisionRef,
        profile: AnalysisProfile,
        *,
        revision: int,
    ) -> ShotAnalysis:
        frame_budget = self._frame_budget(profile)
        shot = self._load_exact_shot(shot_ref)
        resolved_media = self._asset_media_resolver.resolve_local(shot.asset_ref)
        if resolved_media.asset_ref != shot.asset_ref:
            raise RuntimeError("AssetMediaResolver returned a different Asset revision")

        plan = plan_uniform_frame_samples(
            shot,
            FrameSamplingOptions(max_frames=frame_budget),
        )
        extracted_frames = self._frame_extractor.extract(resolved_media.path, plan)
        if len(extracted_frames) != len(plan.samples):
            raise RuntimeError("FramePlanExtractor changed sampling-plan cardinality")
        stored_frames = persist_extracted_frame_samples(extracted_frames, self._artifact_store)
        if any(stored.sample.shot_ref != shot_ref for stored in stored_frames):
            raise RuntimeError("persisted frame sample changed Shot identity")

        proposal = self._visual_port.analyze(
            VisualUnderstandingRequest(
                shot_ref=shot_ref,
                profile=profile,
                frames=tuple(stored.visual_ref for stored in stored_frames),
            )
        )
        validated = normalize_visual_understanding_proposal(proposal)
        analysis = ShotAnalysis(
            shot_ref=shot_ref,
            revision=revision,
            profile=profile,
            analyzed_at=self._clock(),
            technical_quality=validated.quality_scores,
            visual=validated.visual,
            artifact_refs=tuple(
                stored.visual_ref.artifact_ref.artifact_id for stored in stored_frames
            ),
        )
        self._analysis_repository.save(analysis)
        return analysis

    def analyze(self, shot_ref: EntityRevisionRef, profile: AnalysisProfile) -> ShotAnalysis:
        if self._analysis_repository.latest(shot_ref) is not None:
            raise ValueError("Shot already has analysis; use reanalyze() to create a new revision")
        return self._create_analysis(shot_ref, profile, revision=1)

    def reanalyze(self, shot_ref: EntityRevisionRef, profile: AnalysisProfile) -> ShotAnalysis:
        latest = self._analysis_repository.latest(shot_ref)
        if latest is None:
            raise ValueError("Shot has no prior analysis; use analyze() for the first revision")
        if latest.shot_ref != shot_ref:
            raise RuntimeError(
                "ShotAnalysisRepository returned analysis for a different Shot revision"
            )
        return self._create_analysis(shot_ref, profile, revision=latest.revision + 1)

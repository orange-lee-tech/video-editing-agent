from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from video_editing_agent.application.edl_builder import DeterministicEDLBuilder, EDLBuildRequest
from video_editing_agent.application.ports.director import DirectorPort
from video_editing_agent.application.ports.preproduction_planning import (
    ScriptPlanningPort,
    ShootingPlanningPort,
)
from video_editing_agent.application.ports.preproduction_review import (
    ScriptProposalReviewPort,
    ShootingProposalReviewPort,
)
from video_editing_agent.application.ports.rendered_media_qc import RenderedMediaQc
from video_editing_agent.application.ports.renderer import (
    OutputSpec,
    RenderRequest,
    Renderer,
    RenderResult,
)
from video_editing_agent.application.ports.shot_detector import ShotDetectionOptions, ShotDetector
from video_editing_agent.application.ports.understanding import UnderstandingService
from video_editing_agent.application.use_cases.editing_director import GenerateEditPlanRequest
from video_editing_agent.application.use_cases.product_audio import (
    build_conservative_source_audio_mix,
)
from video_editing_agent.application.use_cases.product_flow import (
    EditingProductFlow,
    EditingProductOperations,
    PlanningProductFlow,
    PlanningProductOperations,
    ProductBriefInput,
)
from video_editing_agent.application.use_cases.review_runtime import (
    ReviewApplicationRuntime,
    ReviewRequest,
)
from video_editing_agent.domain.asset.model import AssetProvenance
from video_editing_agent.domain.asset.policy import AssetUsageRole
from video_editing_agent.domain.brief.model import Brief
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.edit.model import EditPlan
from video_editing_agent.domain.edit.resolution import ResolutionDecision, ResolutionDecisionType
from video_editing_agent.domain.edl.model import EDL
from video_editing_agent.domain.review.model import ReviewVerdict
from video_editing_agent.domain.shot.analysis import AnalysisProfile
from video_editing_agent.editing.resolver.product_resolution import GroundedEditPlanResolver
from video_editing_agent.media.ingest.probe import MediaProbe
from video_editing_agent.media.ingest.service import AssetIngestService
from video_editing_agent.media.ingest.source import LocalMediaSource
from video_editing_agent.planning.brief.service import BriefContent
from video_editing_agent.storage.asset.repository_media import RepositoryLocalAssetMediaResolver
from video_editing_agent.storage.project.workspace import ProjectWorkspace


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _edit_plan_id() -> str:
    return f"epl_{uuid.uuid4().hex}"


def _edl_id() -> str:
    return f"edl_{uuid.uuid4().hex}"


@dataclass(frozen=True, slots=True)
class PlanningProductCapabilities:
    script_planning: ScriptPlanningPort
    script_review: ScriptProposalReviewPort
    shooting_planning: ShootingPlanningPort
    shooting_review: ShootingProposalReviewPort


@dataclass(frozen=True, slots=True)
class EditingProductCapabilities:
    media_probe: MediaProbe
    shot_detector: ShotDetector
    shot_detection_options: ShotDetectionOptions
    understanding: UnderstandingService
    director: DirectorPort
    renderer: Renderer
    rendered_media_qc: RenderedMediaQc
    analysis_profile: AnalysisProfile = AnalysisProfile.SEMANTIC
    output_width: int = 1920
    output_height: int = 1080
    output_fps: int = 30
    edit_plan_id_factory: Callable[[], str] = _edit_plan_id
    edl_id_factory: Callable[[], str] = _edl_id
    clock: Callable[[], datetime] = _utc_now

    def __post_init__(self) -> None:
        for name, value in (
            ("output_width", self.output_width),
            ("output_height", self.output_height),
            ("output_fps", self.output_fps),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive int")


def _brief_content(value: ProductBriefInput) -> BriefContent:
    return BriefContent(
        title=value.title,
        objective=value.objective,
        audience=value.audience,
        platform=value.platform,
        core_message=value.core_message,
        product_topic=value.product_topic,
        target_duration=value.target_duration,
        authoritative_facts=value.authoritative_facts,
        style_emotion=value.style_emotion,
        success_criteria=value.success_criteria,
        prohibited_content=value.prohibited_content,
        brand_constraints=value.brand_constraints,
        user_notes=value.user_notes,
        references=value.references,
    )


def _create_brief(
    workspace: ProjectWorkspace,
    value: ProductBriefInput,
    created_by: str,
) -> Brief:
    return workspace.brief_service.create(_brief_content(value), created_by=created_by)


def build_planning_product_flow(
    workspace: ProjectWorkspace,
    capabilities: PlanningProductCapabilities,
) -> PlanningProductFlow:
    runtime = workspace.runtime(
        script_planning=capabilities.script_planning,
        script_review=capabilities.script_review,
        shooting_planning=capabilities.shooting_planning,
        shooting_review=capabilities.shooting_review,
    )
    return PlanningProductFlow(
        PlanningProductOperations(
            lambda value, created_by: _create_brief(workspace, value, created_by),
            runtime.preproduction.generate_script,
            runtime.preproduction.generate_shooting,
        )
    )


def build_editing_product_flow(
    workspace: ProjectWorkspace,
    capabilities: EditingProductCapabilities,
) -> EditingProductFlow:
    editing_runtime = workspace.editing_runtime(director=capabilities.director)
    resolver = GroundedEditPlanResolver(
        shot_index=workspace.shot_index,
        shot_repository=workspace.shots,
        temporal_evidence_repository=workspace.temporal,
    )
    builder = DeterministicEDLBuilder()
    media_resolver = RepositoryLocalAssetMediaResolver(workspace.assets)
    review_runtime = ReviewApplicationRuntime(capabilities.rendered_media_qc)
    ingest = AssetIngestService(capabilities.media_probe, repository=workspace.assets)

    def create_brief(value: ProductBriefInput, created_by: str) -> Brief:
        return _create_brief(workspace, value, created_by)

    def prepare_media(paths: tuple[Path, ...]) -> tuple[EntityRevisionRef, ...]:
        asset_refs: list[EntityRevisionRef] = []
        for path in paths:
            asset = ingest.ingest(
                LocalMediaSource(
                    path,
                    "local",
                    AssetProvenance(origin_type="local"),
                    AssetUsageRole.EDITABLE_VISUAL_FOOTAGE,
                ),
                created_by="product-flow",
            )
            asset_ref = EntityRevisionRef(asset.envelope.id, asset.envelope.revision)
            asset_refs.append(asset_ref)
            shots = workspace.detect(
                asset_ref,
                capabilities.shot_detector,
                capabilities.shot_detection_options,
            )
            for shot in shots:
                shot_ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
                capabilities.understanding.analyze(shot_ref, capabilities.analysis_profile)
        workspace.rebuild_index()
        return tuple(asset_refs)

    def generate_edit_plan(
        brief_ref: EntityRevisionRef,
        script_ref: EntityRevisionRef | None,
        shooting_ref: EntityRevisionRef | None,
        created_by: str,
    ) -> EditPlan:
        return editing_runtime.editing.generate_edit_plan(
            GenerateEditPlanRequest(
                capabilities.edit_plan_id_factory(),
                brief_ref,
                script_ref,
                shooting_ref,
                created_by=created_by,
            )
        )

    def resolve_edit_plan(edit_plan: EditPlan) -> tuple[ResolutionDecision, ...]:
        return resolver.resolve(edit_plan)

    def build_edl(
        edit_plan: EditPlan,
        decisions: tuple[ResolutionDecision, ...],
        requires_audible_output: bool,
    ) -> EDL:
        shot_refs = {
            selection.shot_ref
            for decision in decisions
            if decision.decision_type is ResolutionDecisionType.RESOLVED
            for selection in decision.selections
        }
        shots = tuple(
            workspace.shots.load(ref)
            for ref in sorted(shot_refs, key=lambda item: (item.entity_id, item.revision))
        )
        plan_ref = EntityRevisionRef(edit_plan.envelope.id, edit_plan.envelope.revision)
        result = builder.build(
            EDLBuildRequest(
                EntityEnvelope(
                    capabilities.edl_id_factory(),
                    1,
                    "0.2",
                    EntityStatus.VALID,
                    capabilities.clock(),
                    "product-flow",
                    derived_from=(plan_ref,),
                ),
                edit_plan,
                decisions,
                shots,
                audio_mix=build_conservative_source_audio_mix(edit_plan, decisions),
                requires_audible_output=requires_audible_output,
            )
        )
        if result.edl is None or result.diagnostics:
            codes = ",".join(item.code.value for item in result.diagnostics)
            raise ValueError(f"canonical EDL assembly failed: {codes}")
        return result.edl

    def save_edl(edl: EDL) -> None:
        workspace.edls.save(edl)

    def render(edl: EDL, output_path: Path) -> RenderResult:
        asset_refs = sorted(
            {segment.asset_ref for segment in edl.segments},
            key=lambda item: (item.entity_id, item.revision),
        )
        media = tuple(media_resolver.resolve_local(ref) for ref in asset_refs)
        return capabilities.renderer.render(
            RenderRequest(
                edl,
                media,
                OutputSpec(
                    output_path,
                    capabilities.output_width,
                    capabilities.output_height,
                    capabilities.output_fps,
                ),
            )
        )

    def review(
        edl_ref: EntityRevisionRef,
        render_result: RenderResult,
        requires_audible_output: bool,
    ) -> ReviewVerdict:
        return review_runtime.review(
            ReviewRequest(edl_ref, render_result, requires_audible_output)
        )

    return EditingProductFlow(
        EditingProductOperations(
            create_brief,
            prepare_media,
            generate_edit_plan,
            resolve_edit_plan,
            build_edl,
            save_edl,
            render,
            review,
        )
    )

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from video_editing_agent.application.ports.director import (
    DirectorProposal,
    DirectorRequest,
    EditSlotProposal,
)
from video_editing_agent.application.ports.executor import DeterministicToolInvocation
from video_editing_agent.application.ports.preproduction_planning import (
    NarrativeSectionProposal,
    ScriptPlanningRequest,
    ScriptPlanProposal,
    ShootingPlanningRequest,
    ShootingPlanProposal,
    ShotRequirementProposal,
)
from video_editing_agent.application.ports.preproduction_review import (
    ScriptProposalReview,
    ScriptProposalReviewRequest,
    ShootingProposalReview,
    ShootingProposalReviewRequest,
)
from video_editing_agent.application.ports.rendered_media_qc import RenderedMediaQc
from video_editing_agent.application.ports.renderer import (
    RenderArtifact,
    RenderRequest,
    RenderResult,
)
from video_editing_agent.application.ports.shot_detector import (
    ShotBoundaryProposal,
    ShotDetectionOptions,
)
from video_editing_agent.application.use_cases.product_flow import (
    EditingProductRequest,
    PlanningProductRequest,
    ProductBriefInput,
    ProductFlowOutcome,
)
from video_editing_agent.application.use_cases.review_runtime import ReviewRequest
from video_editing_agent.domain.common.entity import (
    EntityEnvelope,
    EntityRevisionRef,
    EntityStatus,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.review.model import (
    ReviewCorrectionRoute,
    ReviewDisposition,
    ReviewReport,
    ReviewStage,
    ReviewVerdict,
)
from video_editing_agent.domain.shooting.model import ProductionConstraints
from video_editing_agent.domain.shot.analysis import (
    AnalysisProfile,
    ShotAnalysis,
    VisualSemantics,
)
from video_editing_agent.media.ingest.probe import MediaTechnicalMetadata
from video_editing_agent.storage.project import product_flow as composition_module
from video_editing_agent.storage.project.product_flow import (
    EditingProductCapabilities,
    PlanningProductCapabilities,
    build_editing_product_flow,
    build_planning_product_flow,
)
from video_editing_agent.storage.project.workspace import ProjectWorkspace

NOW = datetime(2026, 8, 17, 14, 0, tzinfo=UTC)


class FakeScriptPlanning:
    def propose(self, request: ScriptPlanningRequest) -> ScriptPlanProposal:
        assert request.brief.core_message == "value product"
        return ScriptPlanProposal(
            (
                NarrativeSectionProposal(
                    "sec_value",
                    "hook",
                    "show value",
                    spoken_content="Here is the value.",
                    visual_requirement="show the product",
                ),
            )
        )


class AcceptScriptReview:
    def review(self, request: ScriptProposalReviewRequest) -> ScriptProposalReview:
        assert request.proposal.sections
        return ScriptProposalReview(True)


class FakeShootingPlanning:
    def propose(self, request: ShootingPlanningRequest) -> ShootingPlanProposal:
        assert request.script_plan.sections[0].section_id == "sec_value"
        return ShootingPlanProposal(
            (
                ShotRequirementProposal(
                    "req_value",
                    "sec_value",
                    "show value",
                    "product",
                    action="show",
                    priority="required",
                ),
            )
        )


class AcceptShootingReview:
    def review(self, request: ShootingProposalReviewRequest) -> ShootingProposalReview:
        assert request.proposal.requirements
        return ShootingProposalReview(True)


class FakeMediaProbe:
    def probe(self, path: Path) -> MediaTechnicalMetadata:
        assert path.is_file()
        return MediaTechnicalMetadata(
            "video",
            duration=MediaTime(4, 1),
            width=320,
            height=180,
            fps=30.0,
            codec="h264",
            audio_channels=1,
            sample_rate_hz=48_000,
        )


class FakeShotDetector:
    def detect(
        self,
        asset_ref: EntityRevisionRef,
        options: ShotDetectionOptions,
    ) -> tuple[ShotBoundaryProposal, ...]:
        assert options == ShotDetectionOptions()
        return (
            ShotBoundaryProposal(
                asset_ref,
                detection_method="product-composition-test",
                confidence=1.0,
                source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(4, 1)),
            ),
        )


class FakeUnderstanding:
    def __init__(self, workspace: ProjectWorkspace) -> None:
        self._workspace = workspace

    def analyze(self, shot_ref: EntityRevisionRef, profile: AnalysisProfile) -> ShotAnalysis:
        analysis = ShotAnalysis(
            shot_ref,
            1,
            profile,
            NOW,
            visual=VisualSemantics(
                summary="show value product",
                tags=("value", "product"),
                subjects=("product",),
                actions=("show",),
            ),
        )
        self._workspace.analyses.save(analysis)
        return analysis

    def reanalyze(self, shot_ref: EntityRevisionRef, profile: AnalysisProfile) -> ShotAnalysis:
        return self.analyze(shot_ref, profile)


class FakeDirector:
    def propose(self, request: DirectorRequest) -> DirectorProposal:
        assert request.footage
        return DirectorProposal(
            (
                EditSlotProposal(
                    "slot_value",
                    0,
                    "proof",
                    "show value",
                    "value product",
                    minimum_duration=MediaTime(2, 1),
                    maximum_duration=MediaTime(3, 1),
                ),
            )
        )


class FakeRenderer:
    def __init__(self) -> None:
        self.requests: list[RenderRequest] = []

    def render(self, request: RenderRequest) -> RenderResult:
        self.requests.append(request)
        request.output_spec.path.parent.mkdir(parents=True, exist_ok=True)
        request.output_spec.path.write_bytes(b"rendered-product-flow")
        invocation = DeterministicToolInvocation("fixture", "fixture", ())
        return RenderResult(
            RenderArtifact(
                request.output_spec.path,
                EntityRevisionRef(request.edl.envelope.id, request.edl.envelope.revision),
                request.output_spec,
                invocation,
                invocation,
            ),
            (),
        )


class UnusedRenderedMediaQc:
    def inspect(self, path: Path):  # type: ignore[no-untyped-def]
        raise AssertionError(f"unit composition test must not execute PCM QC: {path}")


class FakeReviewRuntime:
    def __init__(self, rendered_media_qc: RenderedMediaQc) -> None:
        self._rendered_media_qc = rendered_media_qc

    def review(self, request: ReviewRequest) -> ReviewVerdict:
        report = ReviewReport(
            EntityEnvelope(
                f"review:{request.edl_ref.entity_id}",
                1,
                "review-report/v1",
                EntityStatus.VALID,
                NOW,
                "test-review",
                derived_from=(request.edl_ref,),
            ),
            ReviewStage.FINAL_TECHNICAL_QC,
            request.edl_ref,
            True,
        )
        return ReviewVerdict(
            ReviewDisposition.PASS,
            report,
            ReviewCorrectionRoute.NONE,
            request.repair_attempt,
        )


def _brief() -> ProductBriefInput:
    return ProductBriefInput(
        "Product value",
        "show the product value",
        "buyers",
        "short-video",
        "value product",
    )


def test_concrete_planning_composition_persists_script_and_shooting_plan(tmp_path: Path) -> None:
    workspace = ProjectWorkspace.open(tmp_path / "planning-project")
    flow = build_planning_product_flow(
        workspace,
        PlanningProductCapabilities(
            FakeScriptPlanning(),
            AcceptScriptReview(),
            FakeShootingPlanning(),
            AcceptShootingReview(),
        ),
    )

    result = flow.run(
        PlanningProductRequest(
            workspace.root,
            _brief(),
            ProductionConstraints(),
        )
    )

    assert result.outcome is ProductFlowOutcome.COMPLETED
    assert result.brief_ref is not None
    assert result.script_plan_ref is not None
    assert result.shooting_plan_ref is not None
    assert workspace.briefs.load(result.brief_ref).envelope.id == result.brief_ref.entity_id
    assert workspace.scripts.load(result.script_plan_ref).brief_ref == result.brief_ref
    assert (
        workspace.shooting_plans.load(result.shooting_plan_ref).script_plan_ref
        == result.script_plan_ref
    )


def test_concrete_editing_composition_reaches_durable_edl_render_and_review(
    tmp_path: Path,
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(composition_module, "ReviewApplicationRuntime", FakeReviewRuntime)
    workspace = ProjectWorkspace.open(tmp_path / "editing-project")
    source = tmp_path / "source.mp4"
    source.write_bytes(b"original-user-media")
    output = tmp_path / "output" / "final.mp4"
    renderer = FakeRenderer()
    flow = build_editing_product_flow(
        workspace,
        EditingProductCapabilities(
            FakeMediaProbe(),
            FakeShotDetector(),
            ShotDetectionOptions(),
            FakeUnderstanding(workspace),
            FakeDirector(),
            renderer,
            cast(RenderedMediaQc, UnusedRenderedMediaQc()),
            output_width=320,
            output_height=180,
            output_fps=30,
            edit_plan_id_factory=lambda: "epl_product_composition",
            edl_id_factory=lambda: "edl_product_composition",
            clock=lambda: NOW,
        ),
    )

    result = flow.run(
        EditingProductRequest(
            workspace.root,
            _brief(),
            (source,),
            output,
        )
    )

    assert result.outcome is ProductFlowOutcome.COMPLETED
    assert result.output_path == output
    assert result.edl_ref == EntityRevisionRef("edl_product_composition", 1)
    assert source.read_bytes() == b"original-user-media"
    assert output.read_bytes() == b"rendered-product-flow"
    assert workspace.edit_plans.count() == 1
    assert workspace.edls.count() == 1
    persisted_edl = workspace.edls.load(EntityRevisionRef("edl_product_composition", 1))
    assert persisted_edl == renderer.requests[0].edl
    assert renderer.requests[0].asset_media[0].path == source.resolve()
    assert renderer.requests[0].edl.segments[0].source_range == MediaTimeRange(
        MediaTime(0, 1),
        MediaTime(3, 1),
    )

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from video_editing_agent.application.ports.executor import DeterministicToolInvocation
from video_editing_agent.application.ports.renderer import OutputSpec, RenderArtifact, RenderResult
from video_editing_agent.application.use_cases.product_flow import (
    EditingProductFlow,
    EditingProductOperations,
    EditingProductRequest,
    PlanningProductFlow,
    PlanningProductOperations,
    PlanningProductRequest,
    ProductBriefInput,
    ProductFlowOutcome,
    ProductFlowStage,
)
from video_editing_agent.domain.brief.model import Brief
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.model import EditPlan, EditSlot
from video_editing_agent.domain.edit.resolution import (
    ResolutionDecision,
    ResolutionDecisionType,
    ResolvedSelection,
)
from video_editing_agent.domain.edl.model import EDL, EDLSegment, EDLTrack, EDLTrackFamily
from video_editing_agent.domain.review.model import (
    ReviewCorrectionRoute,
    ReviewDisposition,
    ReviewReport,
    ReviewStage,
    ReviewVerdict,
)
from video_editing_agent.domain.script.model import NarrativeSection, ScriptPlan
from video_editing_agent.domain.shooting.model import ProductionConstraints, ShootingPlan


def _envelope(identity: str) -> EntityEnvelope:
    return EntityEnvelope(identity, 1, "test", EntityStatus.VALID, datetime.now(UTC), "test")


def _brief(identity: str = "brf_flow") -> Brief:
    return Brief(_envelope(identity), "Title", "Objective", "Audience", "Platform", "Message")


def _script(brief_ref: EntityRevisionRef) -> ScriptPlan:
    return ScriptPlan(
        _envelope("scp_flow"),
        brief_ref,
        (NarrativeSection("sec_1", "hook", "show value", target_duration=MediaTime(3, 1)),),
    )


def _shooting(script_ref: EntityRevisionRef) -> ShootingPlan:
    return ShootingPlan(_envelope("shp_flow"), script_ref, (), ProductionConstraints())


def _edit_plan(brief_ref: EntityRevisionRef) -> EditPlan:
    return EditPlan(
        _envelope("epl_flow"),
        None,
        None,
        (EditSlot("slot_1", "show value", semantic_query="value"),),
        brief_ref,
    )


def _decision(plan_ref: EntityRevisionRef) -> ResolutionDecision:
    source = MediaTimeRange(MediaTime(0, 1), MediaTime(3, 1))
    return ResolutionDecision(
        "res_flow",
        plan_ref,
        ("slot_1",),
        ResolutionDecisionType.RESOLVED,
        (
            ResolvedSelection(
                "sel_flow",
                EntityRevisionRef("sht_flow", 1),
                source,
                0,
                evidence_refs=("shot-boundary:sht_flow@1",),
            ),
        ),
        0.8,
        0.8,
    )


def _unresolved(plan_ref: EntityRevisionRef) -> ResolutionDecision:
    return ResolutionDecision(
        "res_missing",
        plan_ref,
        ("slot_1",),
        ResolutionDecisionType.UNRESOLVED,
    )


def _edl(plan_ref: EntityRevisionRef) -> EDL:
    source = MediaTimeRange(MediaTime(0, 1), MediaTime(3, 1))
    return EDL(
        _envelope("edl_flow"),
        plan_ref,
        (
            EDLSegment(
                "seg_flow",
                EntityRevisionRef("ast_flow", 1),
                source_range=source,
                timeline_range=source,
                shot_ref=EntityRevisionRef("sht_flow", 1),
            ),
        ),
        (EDLTrack("video", EDLTrackFamily.VIDEO),),
    )


def _review(edl_ref: EntityRevisionRef, passed: bool) -> ReviewVerdict:
    report = ReviewReport(
        _envelope("review_flow"),
        ReviewStage.FINAL_TECHNICAL_QC,
        edl_ref,
        passed,
        (),
    )
    if passed:
        return ReviewVerdict(ReviewDisposition.PASS, report, ReviewCorrectionRoute.NONE, 0)
    return ReviewVerdict(
        ReviewDisposition.CORRECTION_REQUIRED,
        report,
        ReviewCorrectionRoute.RETURN_TO_AUDIO_EDITORIAL,
        0,
    )


def _render(edl: EDL, output: Path) -> RenderResult:
    invocation = DeterministicToolInvocation("render", "fixture", ())
    artifact = RenderArtifact(
        output,
        EntityRevisionRef(edl.envelope.id, edl.envelope.revision),
        OutputSpec(output, 1280, 720, 30),
        invocation,
        invocation,
    )
    return RenderResult(artifact, ())


def _brief_input() -> ProductBriefInput:
    return ProductBriefInput("Title", "Objective", "Audience", "Platform", "Message")


def test_planning_flow_calls_existing_owners_in_order_and_returns_exact_refs(tmp_path: Path) -> None:
    calls: list[str] = []

    def create_brief(value: ProductBriefInput, created_by: str) -> Brief:
        calls.append("brief")
        assert value == _brief_input()
        assert created_by == "product-flow"
        return _brief()

    def generate_script(ref: EntityRevisionRef, policy) -> ScriptPlan:
        calls.append("script")
        return _script(ref)

    def generate_shooting(ref: EntityRevisionRef, constraints, policy) -> ShootingPlan:
        calls.append("shooting")
        return _shooting(ref)

    result = PlanningProductFlow(
        PlanningProductOperations(create_brief, generate_script, generate_shooting)
    ).run(PlanningProductRequest(tmp_path, _brief_input(), ProductionConstraints()))

    assert calls == ["brief", "script", "shooting"]
    assert result.outcome is ProductFlowOutcome.COMPLETED
    assert result.brief_ref == EntityRevisionRef("brf_flow", 1)
    assert result.script_plan_ref == EntityRevisionRef("scp_flow", 1)
    assert result.shooting_plan_ref == EntityRevisionRef("shp_flow", 1)
    assert tuple(item.stage for item in result.events)[-1] is ProductFlowStage.COMPLETED


def test_planning_failure_stops_at_owner_boundary_with_failed_progress(tmp_path: Path) -> None:
    calls: list[str] = []

    def create_brief(value: ProductBriefInput, created_by: str) -> Brief:
        calls.append("brief")
        return _brief()

    def generate_script(ref: EntityRevisionRef, policy) -> ScriptPlan:
        calls.append("script")
        raise RuntimeError("proposal rejected")

    def generate_shooting(ref: EntityRevisionRef, constraints, policy) -> ShootingPlan:
        calls.append("shooting")
        return _shooting(ref)

    result = PlanningProductFlow(
        PlanningProductOperations(create_brief, generate_script, generate_shooting)
    ).run(PlanningProductRequest(tmp_path, _brief_input(), ProductionConstraints()))

    assert calls == ["brief", "script"]
    assert result.outcome is ProductFlowOutcome.FAILED
    assert result.events[-1].stage is ProductFlowStage.FAILED
    assert result.diagnostic == "RuntimeError: proposal rejected"


def test_editing_flow_starts_from_local_paths_and_reaches_reviewed_output(tmp_path: Path) -> None:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"original")
    output = tmp_path / "final.mp4"
    calls: list[str] = []
    saved: list[EDL] = []

    def create_brief(value: ProductBriefInput, created_by: str) -> Brief:
        calls.append("brief")
        return _brief()

    def prepare_media(paths: tuple[Path, ...]) -> tuple[EntityRevisionRef, ...]:
        calls.append("media")
        assert paths == (source,)
        return (EntityRevisionRef("ast_flow", 1),)

    def generate_edit_plan(brief_ref, script_ref, shooting_ref, created_by) -> EditPlan:
        calls.append("edit_plan")
        assert script_ref is None and shooting_ref is None
        return _edit_plan(brief_ref)

    def resolve_edit_plan(plan: EditPlan) -> tuple[ResolutionDecision, ...]:
        calls.append("resolve")
        return (_decision(EntityRevisionRef(plan.envelope.id, plan.envelope.revision)),)

    def build_edl(plan: EditPlan, decisions, audible: bool) -> EDL:
        calls.append("edl")
        assert audible is True
        assert decisions[0].selections[0].selected_source_range == MediaTimeRange(
            MediaTime(0, 1), MediaTime(3, 1)
        )
        return _edl(EntityRevisionRef(plan.envelope.id, plan.envelope.revision))

    def save_edl(edl: EDL) -> None:
        calls.append("save_edl")
        saved.append(edl)

    def render(edl: EDL, path: Path) -> RenderResult:
        calls.append("render")
        path.write_bytes(b"rendered")
        return _render(edl, path)

    def review(edl_ref: EntityRevisionRef, rendered: RenderResult, audible: bool) -> ReviewVerdict:
        calls.append("review")
        return _review(edl_ref, True)

    operations = EditingProductOperations(
        create_brief,
        prepare_media,
        generate_edit_plan,
        resolve_edit_plan,
        build_edl,
        save_edl,
        render,
        review,
    )
    result = EditingProductFlow(operations).run(
        EditingProductRequest(tmp_path, _brief_input(), (source,), output)
    )

    assert calls == ["brief", "media", "edit_plan", "resolve", "edl", "save_edl", "render", "review"]
    assert result.outcome is ProductFlowOutcome.COMPLETED
    assert result.output_path == output
    assert result.edl_ref == EntityRevisionRef("edl_flow", 1)
    assert saved and saved[0].edit_plan_ref == EntityRevisionRef("epl_flow", 1)
    assert source.read_bytes() == b"original"
    assert tuple(item.stage for item in result.events)[-1] is ProductFlowStage.COMPLETED


def test_unresolved_edit_slot_fails_closed_before_edl_or_render(tmp_path: Path) -> None:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"original")
    downstream: list[str] = []

    operations = EditingProductOperations(
        lambda value, created_by: _brief(),
        lambda paths: (EntityRevisionRef("ast_flow", 1),),
        lambda brief_ref, script_ref, shooting_ref, created_by: _edit_plan(brief_ref),
        lambda plan: (_unresolved(EntityRevisionRef(plan.envelope.id, plan.envelope.revision)),),
        lambda plan, decisions, audible: downstream.append("edl") or _edl(
            EntityRevisionRef(plan.envelope.id, plan.envelope.revision)
        ),
        lambda edl: downstream.append("save"),
        lambda edl, path: downstream.append("render") or _render(edl, path),
        lambda edl_ref, rendered, audible: _review(edl_ref, True),
    )

    result = EditingProductFlow(operations).run(
        EditingProductRequest(tmp_path, _brief_input(), (source,), tmp_path / "final.mp4")
    )

    assert result.outcome is ProductFlowOutcome.FAILED
    assert result.events[-1].stage is ProductFlowStage.FAILED
    assert "unresolved EditPlan slots: slot_1" in (result.diagnostic or "")
    assert downstream == []


def test_review_correction_route_is_surfaced_not_silently_repaired(tmp_path: Path) -> None:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"original")
    output = tmp_path / "final.mp4"

    def generate_edit_plan(brief_ref, script_ref, shooting_ref, created_by) -> EditPlan:
        assert script_ref == EntityRevisionRef("scp_context", 2)
        assert shooting_ref == EntityRevisionRef("shp_context", 3)
        return _edit_plan(brief_ref)

    operations = EditingProductOperations(
        lambda value, created_by: _brief(),
        lambda paths: (EntityRevisionRef("ast_flow", 1),),
        generate_edit_plan,
        lambda plan: (_decision(EntityRevisionRef(plan.envelope.id, plan.envelope.revision)),),
        lambda plan, decisions, audible: _edl(EntityRevisionRef(plan.envelope.id, plan.envelope.revision)),
        lambda edl: None,
        lambda edl, path: _render(edl, path),
        lambda edl_ref, rendered, audible: _review(edl_ref, False),
    )

    result = EditingProductFlow(operations).run(
        EditingProductRequest(
            tmp_path,
            _brief_input(),
            (source,),
            output,
            script_plan_ref=EntityRevisionRef("scp_context", 2),
            shooting_plan_ref=EntityRevisionRef("shp_context", 3),
        )
    )

    assert result.outcome is ProductFlowOutcome.CORRECTION_REQUIRED
    assert result.output_path is None
    assert result.review_verdict is not None
    assert result.review_verdict.correction_route is ReviewCorrectionRoute.RETURN_TO_AUDIO_EDITORIAL
    assert result.events[-1].stage is ProductFlowStage.CORRECTION_REQUIRED

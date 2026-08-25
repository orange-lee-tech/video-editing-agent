from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from video_editing_agent.application.ports.executor import DeterministicToolInvocation
from video_editing_agent.application.ports.preproduction_review import (
    ScriptProposalReview,
    ScriptProposalViolation,
)
from video_editing_agent.application.ports.renderer import OutputSpec, RenderArtifact, RenderResult
from video_editing_agent.application.use_cases.product_flow import (
    EditingOutputProfile,
    EditingProductFlow,
    EditingProductOperations,
    EditingProductRequest,
    ProductBriefInput,
    ProductFlowEventLevel,
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
from video_editing_agent.planning.script.workflow import _repair_instruction
from video_editing_agent.providers.llm.deepseek_director import _SYSTEM_PROMPT

NOW = datetime(2026, 8, 25, tzinfo=UTC)


def _envelope(identity: str, revision: int = 1) -> EntityEnvelope:
    return EntityEnvelope(identity, revision, "test", EntityStatus.VALID, NOW, "test")


def _brief() -> Brief:
    return Brief(_envelope("brf_gate"), "Bottle", "Show the product", "commuters", "short", "Daily use")


def _brief_input() -> ProductBriefInput:
    return ProductBriefInput("Bottle", "Show the product", "commuters", "short", "Daily use")


def _plan(revision: int, slot: EditSlot) -> EditPlan:
    return EditPlan(
        _envelope("epl_gate", revision),
        None,
        None,
        (slot,),
        EntityRevisionRef("brf_gate", 1),
    )


def _unresolved(plan: EditPlan) -> ResolutionDecision:
    return ResolutionDecision(
        f"res_missing_{plan.envelope.revision}",
        EntityRevisionRef(plan.envelope.id, plan.envelope.revision),
        (plan.slots[0].slot_id,),
        ResolutionDecisionType.UNRESOLVED,
        reasons=("no legal grounded candidate",),
    )


def _resolved(plan: EditPlan) -> ResolutionDecision:
    source = MediaTimeRange(MediaTime(0, 1), MediaTime(2, 1))
    return ResolutionDecision(
        f"res_ok_{plan.envelope.revision}",
        EntityRevisionRef(plan.envelope.id, plan.envelope.revision),
        (plan.slots[0].slot_id,),
        ResolutionDecisionType.RESOLVED,
        (
            ResolvedSelection(
                "sel_gate",
                EntityRevisionRef("sht_gate", 1),
                source,
                0,
                evidence_refs=("shot-boundary:sht_gate@1",),
            ),
        ),
        0.8,
        0.8,
    )


def _edl(plan: EditPlan) -> EDL:
    source = MediaTimeRange(MediaTime(0, 1), MediaTime(2, 1))
    return EDL(
        _envelope("edl_gate"),
        EntityRevisionRef(plan.envelope.id, plan.envelope.revision),
        (
            EDLSegment(
                "seg_gate",
                EntityRevisionRef("ast_gate", 1),
                source_range=source,
                timeline_range=source,
                shot_ref=EntityRevisionRef("sht_gate", 1),
            ),
        ),
        (EDLTrack("video", EDLTrackFamily.VIDEO),),
    )


def _render(edl: EDL, output: Path) -> RenderResult:
    invocation = DeterministicToolInvocation("render", "fixture", ())
    artifact = RenderArtifact(
        output,
        EntityRevisionRef(edl.envelope.id, edl.envelope.revision),
        OutputSpec(output, 640, 360, 24),
        invocation,
        invocation,
    )
    return RenderResult(artifact, ())


def _review(edl_ref: EntityRevisionRef) -> ReviewVerdict:
    report = ReviewReport(
        _envelope("review_gate"),
        ReviewStage.FINAL_TECHNICAL_QC,
        edl_ref,
        True,
        (),
    )
    return ReviewVerdict(ReviewDisposition.PASS, report, ReviewCorrectionRoute.NONE, 0)


def test_script_repair_reframes_unsupported_commute_convenience_as_neutral_observation() -> None:
    review = ScriptProposalReview(
        False,
        (
            ScriptProposalViolation(
                "unsupported_claim",
                "The demonstration implies convenient commute access without authoritative facts.",
                "demonstration",
                "easy to carry and access",
            ),
        ),
    )

    instruction = _repair_instruction(review, None)

    assert "remove the unsupported semantic property itself" in instruction
    assert "non-claim framing or a neutral observable action/state" in instruction
    assert "placing, carrying, or taking out the product" in instruction
    assert "must not say or imply that doing so is easy, convenient, adequate" in instruction
    assert "Do not turn a neutral action into a demonstration of the unsupported result" in instruction


def test_director_contract_requires_slots_to_be_grounded_and_declares_importance_semantics() -> None:
    assert "Every proposed slot must be grounded in at least one supplied footage_evidence item" in _SYSTEM_PROMPT
    assert "importance 1 or 2" in _SYSTEM_PROMPT
    assert "importance 3 intent" in _SYSTEM_PROMPT
    assert "Never invent missing coverage" in _SYSTEM_PROMPT
    assert "Resolver feedback is operational evidence about coverage failure" in _SYSTEM_PROMPT


def test_editing_flow_replans_once_and_continues_with_later_edit_plan_revision(tmp_path: Path) -> None:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"original")
    output = tmp_path / "final.mp4"
    first = _plan(
        1,
        EditSlot(
            "slot_6",
            "Show a commute-access beat",
            semantic_query="commuter takes bottle from backpack",
            importance=1,
        ),
    )
    recovered = _plan(
        2,
        EditSlot(
            "slot_1",
            "Show the bottle already visible in the supplied footage",
            semantic_query="bottle visible",
            importance=2,
        ),
    )
    resolve_calls: list[int] = []
    recovery_calls: list[tuple[int, tuple[str, ...]]] = []

    def resolve(plan: EditPlan) -> tuple[ResolutionDecision, ...]:
        resolve_calls.append(plan.envelope.revision)
        return (_unresolved(plan),) if plan.envelope.revision == 1 else (_resolved(plan),)

    def recover(
        plan: EditPlan, unresolved: tuple[ResolutionDecision, ...]
    ) -> EditPlan:
        recovery_calls.append(
            (
                plan.envelope.revision,
                tuple(slot_id for item in unresolved for slot_id in item.target_slot_ids),
            )
        )
        return recovered

    def build_edl(plan: EditPlan, decisions: tuple[ResolutionDecision, ...], audible: bool) -> EDL:
        assert plan == recovered
        assert decisions[0].decision_type is ResolutionDecisionType.RESOLVED
        return _edl(plan)

    operations = EditingProductOperations(
        lambda value, created_by: _brief(),
        lambda paths: (EntityRevisionRef("ast_gate", 1),),
        lambda brief_ref, script_ref, shooting_ref, created_by: first,
        resolve,
        build_edl,
        lambda edl: None,
        lambda edl, path, profile: _render(edl, path),
        lambda edl_ref, rendered, audible: _review(edl_ref),
        recover_edit_plan=recover,
    )

    result = EditingProductFlow(operations).run(
        EditingProductRequest(
            tmp_path,
            _brief_input(),
            (source,),
            output,
            requires_audible_output=False,
            output_profile=EditingOutputProfile("test", 640, 360, 24),
        )
    )

    assert result.outcome is ProductFlowOutcome.COMPLETED
    assert result.edit_plan_ref == EntityRevisionRef("epl_gate", 2)
    assert resolve_calls == [1, 2]
    assert recovery_calls == [(1, ("slot_6",))]
    recovery_events = tuple(
        event
        for event in result.events
        if event.stage is ProductFlowStage.RESOLVING
        and event.level is ProductFlowEventLevel.WARNING
    )
    assert len(recovery_events) == 1
    assert "adapting the EditPlan" in recovery_events[0].message
    assert source.read_bytes() == b"original"


def test_editing_flow_second_unresolved_failure_names_missing_coverage_not_slot_id(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"original")
    first = _plan(
        1,
        EditSlot(
            "slot_6",
            "Show the product being poured into a glass",
            semantic_query="product pouring into glass",
            importance=3,
        ),
    )
    recovered = _plan(
        2,
        EditSlot(
            "slot_6",
            "Show the product being poured into a glass",
            semantic_query="product pouring into glass",
            importance=3,
        ),
    )
    downstream: list[str] = []

    operations = EditingProductOperations(
        lambda value, created_by: _brief(),
        lambda paths: (EntityRevisionRef("ast_gate", 1),),
        lambda brief_ref, script_ref, shooting_ref, created_by: first,
        lambda plan: (_unresolved(plan),),
        lambda plan, decisions, audible: downstream.append("edl") or _edl(plan),
        lambda edl: downstream.append("save"),
        lambda edl, path, profile: downstream.append("render") or _render(edl, path),
        lambda edl_ref, rendered, audible: _review(edl_ref),
        recover_edit_plan=lambda plan, unresolved: recovered,
    )

    result = EditingProductFlow(operations).run(
        EditingProductRequest(
            tmp_path,
            _brief_input(),
            (source,),
            tmp_path / "final.mp4",
            requires_audible_output=False,
        )
    )

    assert result.outcome is ProductFlowOutcome.FAILED
    assert result.events[-1].stage is ProductFlowStage.FAILED
    assert result.diagnostic is not None
    assert "Show the product being poured into a glass" in result.diagnostic
    assert "Add footage that shows this content" in result.diagnostic
    assert "slot_6" not in result.diagnostic
    assert downstream == []

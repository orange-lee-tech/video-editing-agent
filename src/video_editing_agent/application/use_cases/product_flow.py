from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from video_editing_agent.application.ports.preproduction_planning import PlanningPolicyGuidance
from video_editing_agent.application.ports.renderer import RenderResult
from video_editing_agent.domain.brief.model import (
    AuthoritativeFact,
    Brief,
    BriefReference,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.edit.model import EditPlan
from video_editing_agent.domain.edit.resolution import ResolutionDecision, ResolutionDecisionType
from video_editing_agent.domain.edl.model import EDL
from video_editing_agent.domain.review.model import ReviewDisposition, ReviewVerdict
from video_editing_agent.domain.script.model import ScriptPlan
from video_editing_agent.domain.shooting.model import ProductionConstraints, ShootingPlan


class ProductFlowStage(StrEnum):
    PROJECT_READY = "project_ready"
    INPUT_VALIDATION = "input_validation"
    INGEST_UNDERSTANDING = "ingest_understanding"
    PLANNING_GENERATION = "planning_generation"
    EDITING_DECISION = "editing_decision"
    RESOLVING = "resolving"
    EDL_ASSEMBLY = "edl_assembly"
    RENDERING = "rendering"
    REVIEW_QC = "review_qc"
    COMPLETED = "completed"
    CORRECTION_REQUIRED = "correction_required"
    FAILED = "failed"


class ProductFlowOutcome(StrEnum):
    COMPLETED = "completed"
    CORRECTION_REQUIRED = "correction_required"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ProductFlowEvent:
    stage: ProductFlowStage
    message: str

    def __post_init__(self) -> None:
        if not self.message.strip():
            raise ValueError("product-flow event message must not be empty")


@dataclass(frozen=True, slots=True)
class ProductBriefInput:
    title: str
    objective: str
    audience: str
    platform: str
    core_message: str
    product_topic: str | None = None
    target_duration: MediaTime | None = None
    authoritative_facts: tuple[AuthoritativeFact, ...] = ()
    style_emotion: tuple[str, ...] = ()
    success_criteria: tuple[str, ...] = ()
    prohibited_content: tuple[str, ...] = ()
    brand_constraints: tuple[str, ...] = ()
    user_notes: str | None = None
    references: tuple[BriefReference, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("title", self.title),
            ("objective", self.objective),
            ("audience", self.audience),
            ("platform", self.platform),
            ("core_message", self.core_message),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")


@dataclass(frozen=True, slots=True)
class PlanningProductRequest:
    project_location: Path
    brief: ProductBriefInput
    production_constraints: ProductionConstraints
    policy_guidance: PlanningPolicyGuidance | None = None
    created_by: str = "product-flow"

    def __post_init__(self) -> None:
        if not self.created_by.strip():
            raise ValueError("created_by must not be empty")


@dataclass(frozen=True, slots=True)
class PlanningProductOperations:
    create_brief: Callable[[ProductBriefInput, str], Brief]
    generate_script: Callable[[EntityRevisionRef, PlanningPolicyGuidance | None], ScriptPlan]
    generate_shooting: Callable[
        [EntityRevisionRef, ProductionConstraints, PlanningPolicyGuidance | None], ShootingPlan
    ]


@dataclass(frozen=True, slots=True)
class PlanningProductResult:
    outcome: ProductFlowOutcome
    project_location: Path
    brief_ref: EntityRevisionRef | None
    script_plan_ref: EntityRevisionRef | None
    shooting_plan_ref: EntityRevisionRef | None
    events: tuple[ProductFlowEvent, ...]
    diagnostic: str | None = None


@dataclass(frozen=True, slots=True)
class EditingProductRequest:
    project_location: Path
    brief: ProductBriefInput
    local_media_paths: tuple[Path, ...]
    output_path: Path
    requires_audible_output: bool = True
    script_plan_ref: EntityRevisionRef | None = None
    shooting_plan_ref: EntityRevisionRef | None = None
    created_by: str = "product-flow"

    def __post_init__(self) -> None:
        if not self.local_media_paths:
            raise ValueError("Editing product request requires at least one local media path")
        if not self.created_by.strip():
            raise ValueError("created_by must not be empty")
        if not isinstance(self.requires_audible_output, bool):
            raise TypeError("requires_audible_output must be a bool")
        if self.shooting_plan_ref is not None and self.script_plan_ref is None:
            raise ValueError("shooting_plan_ref requires script_plan_ref")


@dataclass(frozen=True, slots=True)
class EditingProductOperations:
    create_brief: Callable[[ProductBriefInput, str], Brief]
    prepare_media: Callable[[tuple[Path, ...]], tuple[EntityRevisionRef, ...]]
    generate_edit_plan: Callable[
        [EntityRevisionRef, EntityRevisionRef | None, EntityRevisionRef | None, str], EditPlan
    ]
    resolve_edit_plan: Callable[[EditPlan], tuple[ResolutionDecision, ...]]
    build_edl: Callable[[EditPlan, tuple[ResolutionDecision, ...], bool], EDL]
    save_edl: Callable[[EDL], None]
    render: Callable[[EDL, Path], RenderResult]
    review: Callable[[EntityRevisionRef, RenderResult, bool], ReviewVerdict]


@dataclass(frozen=True, slots=True)
class EditingProductResult:
    outcome: ProductFlowOutcome
    project_location: Path
    brief_ref: EntityRevisionRef | None
    edit_plan_ref: EntityRevisionRef | None
    edl_ref: EntityRevisionRef | None
    output_path: Path | None
    review_verdict: ReviewVerdict | None
    events: tuple[ProductFlowEvent, ...]
    diagnostic: str | None = None


def _ref(entity: Brief | ScriptPlan | ShootingPlan | EditPlan | EDL) -> EntityRevisionRef:
    return EntityRevisionRef(entity.envelope.id, entity.envelope.revision)


def _diagnostic(exc: Exception) -> str:
    message = str(exc).strip()
    return type(exc).__name__ if not message else f"{type(exc).__name__}: {message}"


class PlanningProductFlow:
    def __init__(self, operations: PlanningProductOperations) -> None:
        self._operations = operations

    def run(self, request: PlanningProductRequest) -> PlanningProductResult:
        events: list[ProductFlowEvent] = [
            ProductFlowEvent(ProductFlowStage.PROJECT_READY, "Project is open and ready"),
            ProductFlowEvent(ProductFlowStage.INPUT_VALIDATION, "Planning input accepted"),
        ]
        brief_ref: EntityRevisionRef | None = None
        script_ref: EntityRevisionRef | None = None
        shooting_ref: EntityRevisionRef | None = None
        try:
            brief = self._operations.create_brief(request.brief, request.created_by)
            brief_ref = _ref(brief)
            events.append(
                ProductFlowEvent(
                    ProductFlowStage.PLANNING_GENERATION,
                    "Generating and validating ScriptPlan",
                )
            )
            script = self._operations.generate_script(brief_ref, request.policy_guidance)
            script_ref = _ref(script)
            events.append(
                ProductFlowEvent(
                    ProductFlowStage.PLANNING_GENERATION,
                    "Generating and validating ShootingPlan",
                )
            )
            shooting = self._operations.generate_shooting(
                script_ref,
                request.production_constraints,
                request.policy_guidance,
            )
            shooting_ref = _ref(shooting)
        except Exception as exc:
            events.append(ProductFlowEvent(ProductFlowStage.FAILED, "Planning flow failed"))
            return PlanningProductResult(
                ProductFlowOutcome.FAILED,
                request.project_location,
                brief_ref,
                script_ref,
                shooting_ref,
                tuple(events),
                _diagnostic(exc),
            )
        events.append(ProductFlowEvent(ProductFlowStage.COMPLETED, "Planning flow completed"))
        return PlanningProductResult(
            ProductFlowOutcome.COMPLETED,
            request.project_location,
            brief_ref,
            script_ref,
            shooting_ref,
            tuple(events),
        )


class EditingProductFlow:
    def __init__(self, operations: EditingProductOperations) -> None:
        self._operations = operations

    def run(self, request: EditingProductRequest) -> EditingProductResult:
        events: list[ProductFlowEvent] = [
            ProductFlowEvent(ProductFlowStage.PROJECT_READY, "Project is open and ready"),
            ProductFlowEvent(ProductFlowStage.INPUT_VALIDATION, "Editing input accepted"),
        ]
        brief_ref: EntityRevisionRef | None = None
        edit_plan_ref: EntityRevisionRef | None = None
        edl_ref: EntityRevisionRef | None = None
        try:
            brief = self._operations.create_brief(request.brief, request.created_by)
            brief_ref = _ref(brief)
            events.append(
                ProductFlowEvent(
                    ProductFlowStage.INGEST_UNDERSTANDING,
                    "Ingesting and understanding local media",
                )
            )
            self._operations.prepare_media(request.local_media_paths)
            events.append(
                ProductFlowEvent(
                    ProductFlowStage.EDITING_DECISION,
                    "Generating and persisting EditPlan",
                )
            )
            edit_plan = self._operations.generate_edit_plan(
                brief_ref,
                request.script_plan_ref,
                request.shooting_plan_ref,
                request.created_by,
            )
            edit_plan_ref = _ref(edit_plan)
            events.append(
                ProductFlowEvent(ProductFlowStage.RESOLVING, "Resolving grounded source selections")
            )
            decisions = self._operations.resolve_edit_plan(edit_plan)
            unresolved = tuple(
                decision
                for decision in decisions
                if decision.decision_type is ResolutionDecisionType.UNRESOLVED
            )
            if unresolved:
                slot_ids = ",".join(
                    slot_id for decision in unresolved for slot_id in decision.target_slot_ids
                )
                raise ValueError(f"unresolved EditPlan slots: {slot_ids}")
            events.append(
                ProductFlowEvent(ProductFlowStage.EDL_ASSEMBLY, "Building canonical EDL")
            )
            edl = self._operations.build_edl(
                edit_plan,
                decisions,
                request.requires_audible_output,
            )
            edl_ref = _ref(edl)
            self._operations.save_edl(edl)
            events.append(ProductFlowEvent(ProductFlowStage.RENDERING, "Rendering canonical EDL"))
            render_result = self._operations.render(edl, request.output_path)
            events.append(
                ProductFlowEvent(ProductFlowStage.REVIEW_QC, "Reviewing delivered output")
            )
            verdict = self._operations.review(
                edl_ref,
                render_result,
                request.requires_audible_output,
            )
        except Exception as exc:
            events.append(ProductFlowEvent(ProductFlowStage.FAILED, "Editing flow failed"))
            return EditingProductResult(
                ProductFlowOutcome.FAILED,
                request.project_location,
                brief_ref,
                edit_plan_ref,
                edl_ref,
                None,
                None,
                tuple(events),
                _diagnostic(exc),
            )

        if verdict.disposition is not ReviewDisposition.PASS:
            events.append(
                ProductFlowEvent(
                    ProductFlowStage.CORRECTION_REQUIRED,
                    f"Review requires correction via {verdict.correction_route.value}",
                )
            )
            return EditingProductResult(
                ProductFlowOutcome.CORRECTION_REQUIRED,
                request.project_location,
                brief_ref,
                edit_plan_ref,
                edl_ref,
                None,
                verdict,
                tuple(events),
                verdict.correction_route.value,
            )

        artifact = render_result.artifact
        if artifact is None:
            events.append(ProductFlowEvent(ProductFlowStage.FAILED, "Review passed without output"))
            return EditingProductResult(
                ProductFlowOutcome.FAILED,
                request.project_location,
                brief_ref,
                edit_plan_ref,
                edl_ref,
                None,
                verdict,
                tuple(events),
                "Review PASS requires a RenderArtifact",
            )
        events.append(ProductFlowEvent(ProductFlowStage.COMPLETED, "Editing flow completed"))
        return EditingProductResult(
            ProductFlowOutcome.COMPLETED,
            request.project_location,
            brief_ref,
            edit_plan_ref,
            edl_ref,
            artifact.path,
            verdict,
            tuple(events),
        )

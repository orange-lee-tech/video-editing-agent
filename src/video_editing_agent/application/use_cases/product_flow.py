from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, replace
from enum import StrEnum
from pathlib import Path

from video_editing_agent.application.ports.preproduction_planning import (
    PlanningPolicyGuidance,
    ReferenceStyleGuidance,
)
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
from video_editing_agent.domain.edl.subtitle import SubtitleStyleProfile
from video_editing_agent.domain.music.model import BeatMap
from video_editing_agent.domain.review.model import ReviewDisposition, ReviewVerdict
from video_editing_agent.domain.script.model import ScriptPlan
from video_editing_agent.domain.shooting.model import ProductionConstraints, ShootingPlan


class ProductFlowStage(StrEnum):
    PROJECT_READY = "project_ready"
    INPUT_VALIDATION = "input_validation"
    INGEST_UNDERSTANDING = "ingest_understanding"
    MUSIC_PREPARATION = "music_preparation"
    PLANNING_GENERATION = "planning_generation"
    EDITING_DECISION = "editing_decision"
    RESOLVING = "resolving"
    EDL_ASSEMBLY = "edl_assembly"
    AUDIO_ASSEMBLY = "audio_assembly"
    VOICE_PREPARATION = "voice_preparation"
    SUBTITLE_COMPILATION = "subtitle_compilation"
    RENDERING = "rendering"
    REVIEW_QC = "review_qc"
    COMPLETED = "completed"
    CORRECTION_REQUIRED = "correction_required"
    FAILED = "failed"


class ProductFlowEventLevel(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ProductFlowOutcome(StrEnum):
    COMPLETED = "completed"
    CORRECTION_REQUIRED = "correction_required"
    FAILED = "failed"


class VoiceMode(StrEnum):
    ORIGINAL = "original"
    SYNTHETIC = "synthetic"


class PlanningReferenceKind(StrEnum):
    DIRECT_HTTPS_VIDEO = "direct_https_video"
    LOCAL_VIDEO = "local_video"


@dataclass(frozen=True, slots=True)
class PlanningReferenceInput:
    reference_id: str
    kind: PlanningReferenceKind
    description: str
    url: str | None = None
    local_path: Path | None = None

    def __post_init__(self) -> None:
        if not self.reference_id.strip() or not self.description.strip():
            raise ValueError("reference_id and description must not be empty")
        if self.kind is PlanningReferenceKind.DIRECT_HTTPS_VIDEO:
            if self.url is None or not self.url.strip() or self.local_path is not None:
                raise ValueError("direct HTTPS reference requires only url")
        elif self.local_path is None or self.url is not None:
            raise ValueError("local reference requires only local_path")


@dataclass(frozen=True, slots=True)
class PreparedPlanningReferences:
    brief_references: tuple[BriefReference, ...]
    guidance: tuple[ReferenceStyleGuidance, ...]


@dataclass(frozen=True, slots=True)
class ProductFlowEvent:
    stage: ProductFlowStage
    message: str
    level: ProductFlowEventLevel = ProductFlowEventLevel.INFO

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
    reference_inputs: tuple[PlanningReferenceInput, ...] = ()

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
    prepare_references: (
        Callable[[tuple[PlanningReferenceInput, ...]], PreparedPlanningReferences] | None
    ) = None
    generate_script_with_references: (
        Callable[
            [EntityRevisionRef, PlanningPolicyGuidance | None, tuple[ReferenceStyleGuidance, ...]],
            ScriptPlan,
        ]
        | None
    ) = None
    generate_shooting_with_references: (
        Callable[
            [
                EntityRevisionRef,
                ProductionConstraints,
                PlanningPolicyGuidance | None,
                tuple[ReferenceStyleGuidance, ...],
            ],
            ShootingPlan,
        ]
        | None
    ) = None


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
class EditingOutputProfile:
    # User-visible target geometry for the ordinary Editing product route.
    profile_id: str
    width: int
    height: int
    frames_per_second: int

    def __post_init__(self) -> None:
        if not self.profile_id.strip():
            raise ValueError("output profile_id must not be empty")
        for name, value in (
            ("width", self.width),
            ("height", self.height),
            ("frames_per_second", self.frames_per_second),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"output profile {name} must be a positive int")


OUTPUT_PROFILE_VERTICAL_1080P = EditingOutputProfile("vertical_9_16_1080p30", 1080, 1920, 30)
OUTPUT_PROFILE_HORIZONTAL_1080P = EditingOutputProfile("horizontal_16_9_1080p30", 1920, 1080, 30)
OUTPUT_PROFILE_SQUARE_1080P = EditingOutputProfile("square_1_1_1080p30", 1080, 1080, 30)
OUTPUT_PROFILE_PRESETS = (
    OUTPUT_PROFILE_VERTICAL_1080P,
    OUTPUT_PROFILE_HORIZONTAL_1080P,
    OUTPUT_PROFILE_SQUARE_1080P,
)


@dataclass(frozen=True, slots=True)
class EditingMusicInput:
    """Explicit user-selected local BGM plus the ordinary-user rights gate."""

    local_path: Path
    rights_attested: bool

    def __post_init__(self) -> None:
        if not isinstance(self.rights_attested, bool):
            raise TypeError("music rights_attested must be a bool")
        if not self.rights_attested:
            raise ValueError("local music requires explicit user rights attestation")


@dataclass(frozen=True, slots=True)
class PreparedEditingMusic:
    """Rights-grounded music material prepared before timeline assembly."""

    asset_ref: EntityRevisionRef
    beat_map: BeatMap
    rights_evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.beat_map.audio_asset_ref != self.asset_ref:
            raise ValueError("prepared music BeatMap must reference the exact music Asset")
        if not self.rights_evidence_refs or any(
            not value.strip() for value in self.rights_evidence_refs
        ):
            raise ValueError("prepared music requires durable rights evidence")


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
    output_profile: EditingOutputProfile = OUTPUT_PROFILE_HORIZONTAL_1080P
    music: EditingMusicInput | None = None
    voice_mode: VoiceMode = VoiceMode.ORIGINAL
    subtitle_style: SubtitleStyleProfile = SubtitleStyleProfile.OUTLINED

    def __post_init__(self) -> None:
        if not self.local_media_paths:
            raise ValueError("Editing product request requires at least one local media path")
        if not self.created_by.strip():
            raise ValueError("created_by must not be empty")
        if not isinstance(self.requires_audible_output, bool):
            raise TypeError("requires_audible_output must be a bool")
        if self.shooting_plan_ref is not None and self.script_plan_ref is None:
            raise ValueError("shooting_plan_ref requires script_plan_ref")
        if not isinstance(self.voice_mode, VoiceMode):
            raise TypeError("voice_mode must be a VoiceMode")
        if not isinstance(self.subtitle_style, SubtitleStyleProfile):
            raise TypeError("subtitle_style must be a SubtitleStyleProfile")


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
    render: Callable[[EDL, Path, EditingOutputProfile], RenderResult]
    review: Callable[[EntityRevisionRef, RenderResult, bool], ReviewVerdict]
    prepare_music: (
        Callable[
            [
                EditingMusicInput | None,
                ProductBriefInput,
                Callable[[ProductFlowEventLevel, str], None],
            ],
            PreparedEditingMusic | None,
        ]
        | None
    ) = None
    build_edl_with_music: (
        Callable[[EditPlan, tuple[ResolutionDecision, ...], bool, PreparedEditingMusic], EDL] | None
    ) = None
    validate_audio: Callable[[EDL, tuple[ResolutionDecision, ...]], EDL] | None = None
    finalize_voice: (
        Callable[
            [EDL, tuple[ResolutionDecision, ...], VoiceMode],
            EDL,
        ]
        | None
    ) = None
    compile_subtitles: (
        Callable[
            [
                EDL,
                tuple[ResolutionDecision, ...],
                SubtitleStyleProfile,
                Callable[[ProductFlowEventLevel, str], None],
            ],
            EDL,
        ]
        | None
    ) = None
    recover_edit_plan: (
        Callable[[EditPlan, tuple[ResolutionDecision, ...]], EditPlan] | None
    ) = None


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
    safe = re.sub(
        r"(?i)(api[_ -]?key|secret|authorization)(\s*[:=]\s*)(\S+)",
        r"\1\2[REDACTED]",
        message,
    )
    return type(exc).__name__ if not safe else f"{type(exc).__name__}: {safe}"


class PlanningProductFlow:
    def __init__(self, operations: PlanningProductOperations) -> None:
        self._operations = operations

    def run(
        self,
        request: PlanningProductRequest,
        event_sink: Callable[[ProductFlowEvent], None] | None = None,
    ) -> PlanningProductResult:
        events: list[ProductFlowEvent] = []

        def emit(event: ProductFlowEvent) -> None:
            events.append(event)
            if event_sink is not None:
                event_sink(event)

        emit(ProductFlowEvent(ProductFlowStage.PROJECT_READY, "Project is open and ready"))
        emit(ProductFlowEvent(ProductFlowStage.INPUT_VALIDATION, "Planning input accepted"))
        brief_ref: EntityRevisionRef | None = None
        script_ref: EntityRevisionRef | None = None
        shooting_ref: EntityRevisionRef | None = None
        try:
            prepared = PreparedPlanningReferences((), ())
            if request.reference_inputs:
                if self._operations.prepare_references is None:
                    raise RuntimeError("reference analysis capability is unavailable")
                emit(
                    ProductFlowEvent(
                        ProductFlowStage.INGEST_UNDERSTANDING,
                        "Acquiring and analyzing reference-only media",
                    )
                )
                prepared = self._operations.prepare_references(request.reference_inputs)
            brief_input = replace(
                request.brief,
                references=(*request.brief.references, *prepared.brief_references),
            )
            brief = self._operations.create_brief(brief_input, request.created_by)
            brief_ref = _ref(brief)
            emit(
                ProductFlowEvent(
                    ProductFlowStage.PLANNING_GENERATION,
                    "Generating and validating ScriptPlan",
                )
            )
            script = (
                self._operations.generate_script(brief_ref, request.policy_guidance)
                if self._operations.generate_script_with_references is None
                else self._operations.generate_script_with_references(
                    brief_ref, request.policy_guidance, prepared.guidance
                )
            )
            script_ref = _ref(script)
            emit(
                ProductFlowEvent(
                    ProductFlowStage.PLANNING_GENERATION,
                    "Generating and validating ShootingPlan",
                )
            )
            shooting = (
                self._operations.generate_shooting(
                    script_ref, request.production_constraints, request.policy_guidance
                )
                if self._operations.generate_shooting_with_references is None
                else self._operations.generate_shooting_with_references(
                    script_ref,
                    request.production_constraints,
                    request.policy_guidance,
                    prepared.guidance,
                )
            )
            shooting_ref = _ref(shooting)
        except Exception as exc:
            diagnostic = _diagnostic(exc)
            emit(
                ProductFlowEvent(
                    ProductFlowStage.FAILED,
                    f"Planning flow failed during {events[-1].stage.value}: {diagnostic}",
                )
            )
            return PlanningProductResult(
                ProductFlowOutcome.FAILED,
                request.project_location,
                brief_ref,
                script_ref,
                shooting_ref,
                tuple(events),
                diagnostic,
            )
        emit(ProductFlowEvent(ProductFlowStage.COMPLETED, "Planning flow completed"))
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

    def run(
        self,
        request: EditingProductRequest,
        event_sink: Callable[[ProductFlowEvent], None] | None = None,
    ) -> EditingProductResult:
        events: list[ProductFlowEvent] = []

        def emit(event: ProductFlowEvent) -> None:
            events.append(event)
            if event_sink is not None:
                event_sink(event)

        emit(ProductFlowEvent(ProductFlowStage.PROJECT_READY, "Project is open and ready"))
        emit(ProductFlowEvent(ProductFlowStage.INPUT_VALIDATION, "Editing input accepted"))
        brief_ref: EntityRevisionRef | None = None
        edit_plan_ref: EntityRevisionRef | None = None
        edl_ref: EntityRevisionRef | None = None
        current_stage = ProductFlowStage.INPUT_VALIDATION
        try:
            brief = self._operations.create_brief(request.brief, request.created_by)
            brief_ref = _ref(brief)
            emit(
                ProductFlowEvent(
                    ProductFlowStage.INGEST_UNDERSTANDING,
                    "Ingesting and understanding local media",
                )
            )
            current_stage = ProductFlowStage.INGEST_UNDERSTANDING
            self._operations.prepare_media(request.local_media_paths)
            prepared_music: PreparedEditingMusic | None = None
            music_preparer = self._operations.prepare_music
            music_builder = self._operations.build_edl_with_music
            wants_music = request.music is not None or request.requires_audible_output
            if wants_music and music_preparer is not None and music_builder is not None:
                emit(
                    ProductFlowEvent(
                        ProductFlowStage.MUSIC_PREPARATION,
                        (
                            "Preparing rights-attested local music"
                            if request.music is not None
                            else "Selecting rights-verified public background music"
                        ),
                    )
                )
                current_stage = ProductFlowStage.MUSIC_PREPARATION
                prepared_music = music_preparer(
                    request.music,
                    request.brief,
                    lambda level, message: emit(
                        ProductFlowEvent(ProductFlowStage.MUSIC_PREPARATION, message, level)
                    ),
                )
                if request.music is not None and prepared_music is None:
                    raise RuntimeError("explicit local music could not be prepared")
            elif request.music is not None:
                raise RuntimeError("local music capability is unavailable")
            emit(
                ProductFlowEvent(
                    ProductFlowStage.EDITING_DECISION,
                    "Generating and persisting EditPlan",
                )
            )
            current_stage = ProductFlowStage.EDITING_DECISION
            edit_plan = self._operations.generate_edit_plan(
                brief_ref,
                request.script_plan_ref,
                request.shooting_plan_ref,
                request.created_by,
            )
            edit_plan_ref = _ref(edit_plan)
            emit(
                ProductFlowEvent(ProductFlowStage.RESOLVING, "Resolving grounded source selections")
            )
            current_stage = ProductFlowStage.RESOLVING
            decisions = self._operations.resolve_edit_plan(edit_plan)
            unresolved = tuple(
                decision
                for decision in decisions
                if decision.decision_type is ResolutionDecisionType.UNRESOLVED
            )
            if unresolved and self._operations.recover_edit_plan is not None:
                emit(
                    ProductFlowEvent(
                        ProductFlowStage.RESOLVING,
                        "Some planned edit beats were not grounded; adapting the EditPlan to "
                        "available local footage",
                        ProductFlowEventLevel.WARNING,
                    )
                )
                previous_plan = edit_plan
                edit_plan = self._operations.recover_edit_plan(previous_plan, unresolved)
                if (
                    edit_plan.envelope.id != previous_plan.envelope.id
                    or edit_plan.envelope.revision <= previous_plan.envelope.revision
                ):
                    raise RuntimeError(
                        "resolver recovery must persist a later revision of the same EditPlan"
                    )
                if (
                    edit_plan.brief_ref != previous_plan.brief_ref
                    or edit_plan.script_plan_ref != previous_plan.script_plan_ref
                    or edit_plan.shooting_plan_ref != previous_plan.shooting_plan_ref
                ):
                    raise RuntimeError("resolver recovery changed authoritative EditPlan lineage")
                edit_plan_ref = _ref(edit_plan)
                decisions = self._operations.resolve_edit_plan(edit_plan)
                unresolved = tuple(
                    decision
                    for decision in decisions
                    if decision.decision_type is ResolutionDecisionType.UNRESOLVED
                )
            if unresolved:
                slots = {slot.slot_id: slot for slot in edit_plan.slots}
                missing_purposes = tuple(
                    dict.fromkeys(
                        slots[slot_id].purpose
                        for decision in unresolved
                        for slot_id in decision.target_slot_ids
                        if slot_id in slots
                    )
                )
                detail = "; ".join(missing_purposes) or "one or more required visual beats"
                raise ValueError(
                    "available local footage still cannot cover the planned edit: "
                    f"{detail}. Add footage that shows this content or adjust the requested video "
                    "intent"
                )
            emit(ProductFlowEvent(ProductFlowStage.EDL_ASSEMBLY, "Building canonical EDL"))
            current_stage = ProductFlowStage.EDL_ASSEMBLY
            if prepared_music is None:
                edl = self._operations.build_edl(
                    edit_plan,
                    decisions,
                    request.requires_audible_output,
                )
            else:
                build_with_music = self._operations.build_edl_with_music
                if build_with_music is None:
                    raise RuntimeError("music EDL capability is unavailable")
                edl = build_with_music(
                    edit_plan,
                    decisions,
                    request.requires_audible_output,
                    prepared_music,
                )
            emit(
                ProductFlowEvent(
                    ProductFlowStage.AUDIO_ASSEMBLY,
                    "Validating canonical source-audio and background-music lanes",
                )
            )
            current_stage = ProductFlowStage.AUDIO_ASSEMBLY
            if self._operations.validate_audio is not None:
                edl = self._operations.validate_audio(edl, decisions)
            emit(
                ProductFlowEvent(
                    ProductFlowStage.VOICE_PREPARATION,
                    (
                        "Preserving grounded original source voice"
                        if request.voice_mode is VoiceMode.ORIGINAL
                        else "Preparing requested synthetic voice"
                    ),
                )
            )
            current_stage = ProductFlowStage.VOICE_PREPARATION
            if (
                request.voice_mode is VoiceMode.SYNTHETIC
                and self._operations.finalize_voice is None
            ):
                raise RuntimeError(
                    "Synthetic voice requested but no approved SpeechSynthesisPort capability "
                    "is configured"
                )
            if self._operations.finalize_voice is not None:
                edl = self._operations.finalize_voice(edl, decisions, request.voice_mode)
            emit(
                ProductFlowEvent(
                    ProductFlowStage.SUBTITLE_COMPILATION,
                    "Compiling trusted speech evidence into canonical subtitle timing",
                )
            )
            current_stage = ProductFlowStage.SUBTITLE_COMPILATION
            if self._operations.compile_subtitles is not None:
                edl = self._operations.compile_subtitles(
                    edl,
                    decisions,
                    request.subtitle_style,
                    lambda level, message: emit(
                        ProductFlowEvent(ProductFlowStage.SUBTITLE_COMPILATION, message, level)
                    ),
                )
            edl_ref = _ref(edl)
            self._operations.save_edl(edl)
            emit(ProductFlowEvent(ProductFlowStage.RENDERING, "Rendering canonical EDL"))
            current_stage = ProductFlowStage.RENDERING
            render_result = self._operations.render(
                edl, request.output_path, request.output_profile
            )
            emit(ProductFlowEvent(ProductFlowStage.REVIEW_QC, "Reviewing delivered output"))
            current_stage = ProductFlowStage.REVIEW_QC
            verdict = self._operations.review(
                edl_ref,
                render_result,
                request.requires_audible_output,
            )
        except Exception as exc:
            diagnostic = _diagnostic(exc)
            emit(
                ProductFlowEvent(
                    ProductFlowStage.FAILED,
                    f"Failed during {current_stage.value}: {diagnostic}",
                    ProductFlowEventLevel.ERROR,
                )
            )
            return EditingProductResult(
                ProductFlowOutcome.FAILED,
                request.project_location,
                brief_ref,
                edit_plan_ref,
                edl_ref,
                None,
                None,
                tuple(events),
                f"stage={current_stage.value}; {diagnostic}",
            )

        if verdict.disposition is not ReviewDisposition.PASS:
            emit(
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
            emit(ProductFlowEvent(ProductFlowStage.FAILED, "Review passed without output"))
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
        emit(ProductFlowEvent(ProductFlowStage.COMPLETED, "Editing flow completed"))
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

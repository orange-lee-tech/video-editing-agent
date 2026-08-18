from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from video_editing_agent.application.use_cases.product_flow import (
    EditingProductFlow,
    EditingProductRequest,
    EditingProductResult,
    PlanningProductFlow,
    PlanningProductRequest,
    PlanningProductResult,
    PlanningReferenceInput,
    PlanningReferenceKind,
    ProductBriefInput,
    ProductFlowEvent,
)
from video_editing_agent.domain.brief.model import AuthoritativeFact
from video_editing_agent.domain.shooting.model import ProductionConstraints

_MEDIA_EXTENSIONS = frozenset({".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"})


def expand_media_inputs(files: tuple[Path, ...], folder: Path | None = None) -> tuple[Path, ...]:
    candidates = [item.expanduser().resolve(strict=True) for item in files]
    if folder is not None:
        root = folder.expanduser().resolve(strict=True)
        if not root.is_dir():
            raise ValueError(f"media folder is not a directory: {root}")
        candidates.extend(
            item.resolve()
            for item in root.iterdir()
            if item.is_file() and item.suffix.casefold() in _MEDIA_EXTENSIONS
        )
    ordered = sorted(set(candidates), key=lambda item: str(item).casefold())
    if not ordered:
        raise ValueError("select at least one supported local media file")
    return tuple(ordered)


@dataclass(frozen=True, slots=True)
class BriefForm:
    title: str
    objective: str
    audience: str
    platform: str
    core_message: str
    authoritative_fact_statements: tuple[str, ...] = ()

    def to_product_input(self) -> ProductBriefInput:
        facts = tuple(
            AuthoritativeFact(f"fact_{index:03d}", statement.strip(), "user supplied")
            for index, statement in enumerate(self.authoritative_fact_statements, start=1)
            if statement.strip()
        )
        return ProductBriefInput(
            self.title,
            self.objective,
            self.audience,
            self.platform,
            self.core_message,
            authoritative_facts=facts,
        )


@dataclass(frozen=True, slots=True)
class PlanningForm:
    project: Path
    brief: BriefForm
    constraints: ProductionConstraints = ProductionConstraints()
    reference_url: str | None = None
    local_reference: Path | None = None

    def to_request(self) -> PlanningProductRequest:
        references: list[PlanningReferenceInput] = []
        if self.reference_url is not None and self.reference_url.strip():
            references.append(
                PlanningReferenceInput(
                    "reference_url_001",
                    PlanningReferenceKind.DIRECT_HTTPS_VIDEO,
                    "User supplied direct video reference",
                    url=self.reference_url.strip(),
                )
            )
        if self.local_reference is not None:
            references.append(
                PlanningReferenceInput(
                    "reference_local_001",
                    PlanningReferenceKind.LOCAL_VIDEO,
                    "User selected local video reference",
                    local_path=self.local_reference.expanduser().resolve(strict=True),
                )
            )
        return PlanningProductRequest(
            self.project.expanduser().resolve(strict=False),
            self.brief.to_product_input(),
            self.constraints,
            reference_inputs=tuple(references),
        )


@dataclass(frozen=True, slots=True)
class EditingForm:
    project: Path
    brief: BriefForm
    output_path: Path
    media_files: tuple[Path, ...] = ()
    media_folder: Path | None = None
    requires_audible_output: bool = True

    def to_request(self) -> EditingProductRequest:
        return EditingProductRequest(
            self.project.expanduser().resolve(strict=False),
            self.brief.to_product_input(),
            expand_media_inputs(self.media_files, self.media_folder),
            self.output_path.expanduser().resolve(strict=False),
            self.requires_audible_output,
        )


class ProductController:
    def __init__(
        self,
        planning_flow: PlanningProductFlow | None = None,
        editing_flow: EditingProductFlow | None = None,
    ) -> None:
        self._planning = planning_flow
        self._editing = editing_flow

    def run_planning(
        self, form: PlanningForm, sink: Callable[[ProductFlowEvent], None] | None = None
    ) -> PlanningProductResult:
        if self._planning is None:
            raise RuntimeError("Planning runtime is not configured")
        return self._planning.run(form.to_request(), sink)

    def run_editing(
        self, form: EditingForm, sink: Callable[[ProductFlowEvent], None] | None = None
    ) -> EditingProductResult:
        if self._editing is None:
            raise RuntimeError("Editing runtime is not configured")
        return self._editing.run(form.to_request(), sink)

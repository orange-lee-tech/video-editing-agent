from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from video_editing_agent.application.ports.preproduction_planning import PlanningPolicyGuidance
from video_editing_agent.application.ports.shot_detector import ShotDetectionOptions, ShotDetector
from video_editing_agent.application.ports.shot_index import ShotCandidate
from video_editing_agent.application.use_cases.editing_director import GenerateEditPlanRequest
from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.asset.policy import AssetUsageRole
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.edit.model import EditPlan
from video_editing_agent.domain.script.model import ScriptPlan
from video_editing_agent.domain.shooting.model import ProductionConstraints, ShootingPlan
from video_editing_agent.domain.shot.analysis import AnalysisProfile, ShotAnalysis
from video_editing_agent.domain.shot.model import Shot


@dataclass(frozen=True, slots=True)
class AssetIngestRequest:
    path: Path
    origin: str
    provenance: AssetProvenance
    usage_role: AssetUsageRole | None = None


@dataclass(frozen=True, slots=True)
class CoverageResult:
    shooting_plan_ref: EntityRevisionRef
    payload: dict[str, object]


@dataclass(frozen=True, slots=True)
class PreproductionOperations:
    generate_script: Callable[[EntityRevisionRef, PlanningPolicyGuidance | None], ScriptPlan]
    revise_script: Callable[[EntityRevisionRef, str, PlanningPolicyGuidance | None], ScriptPlan]
    generate_shooting: Callable[
        [EntityRevisionRef, ProductionConstraints, PlanningPolicyGuidance | None], ShootingPlan
    ]


@dataclass(frozen=True, slots=True)
class MediaOperations:
    ingest: Callable[[AssetIngestRequest], Asset]
    detect: Callable[[EntityRevisionRef, ShotDetector, ShotDetectionOptions], tuple[Shot, ...]]
    analyze: Callable[[EntityRevisionRef, AnalysisProfile], ShotAnalysis]
    rebuild_index: Callable[[], int]
    query_index: Callable[[str, int], tuple[ShotCandidate, ...]]
    coverage: Callable[[EntityRevisionRef], CoverageResult]


@dataclass(frozen=True, slots=True)
class ApplicationRuntime:
    """Stable application surface whose injected operations retain their existing owners."""

    preproduction: PreproductionOperations
    media: MediaOperations | None = None


@dataclass(frozen=True, slots=True)
class EditingOperations:
    generate_edit_plan: Callable[[GenerateEditPlanRequest], EditPlan]
    show_edit_plan: Callable[[EntityRevisionRef], EditPlan]


@dataclass(frozen=True, slots=True)
class EditingApplicationRuntime:
    """Independent Editing entry; Planning artifacts are optional context only."""

    editing: EditingOperations

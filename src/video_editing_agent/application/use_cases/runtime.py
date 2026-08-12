from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from video_editing_agent.application.ports.preproduction_planning import PlanningPolicyGuidance
from video_editing_agent.application.ports.shot_detector import ShotDetectionOptions, ShotDetector
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.script.model import ScriptPlan
from video_editing_agent.domain.shooting.model import ProductionConstraints, ShootingPlan
from video_editing_agent.domain.shot.analysis import AnalysisProfile, ShotAnalysis
from video_editing_agent.domain.shot.model import Shot


@dataclass(frozen=True, slots=True)
class PreproductionOperations:
    generate_script: Callable[[EntityRevisionRef, PlanningPolicyGuidance | None], ScriptPlan]
    revise_script: Callable[[EntityRevisionRef, str, PlanningPolicyGuidance | None], ScriptPlan]
    generate_shooting: Callable[
        [EntityRevisionRef, ProductionConstraints, PlanningPolicyGuidance | None], ShootingPlan
    ]


@dataclass(frozen=True, slots=True)
class MediaOperations:
    detect: Callable[[EntityRevisionRef, ShotDetector, ShotDetectionOptions], tuple[Shot, ...]]
    analyze: Callable[[EntityRevisionRef, AnalysisProfile], ShotAnalysis]
    rebuild_index: Callable[[], int]


@dataclass(frozen=True, slots=True)
class ApplicationRuntime:
    """Stable application surface whose injected operations retain their existing owners."""

    preproduction: PreproductionOperations
    media: MediaOperations | None = None

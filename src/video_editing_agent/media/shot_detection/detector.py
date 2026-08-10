from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.application.ports.shot_detector import (
    ShotBoundaryProposal,
    ShotDetectionOptions,
    ShotDetector,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.media.shot_detection.policy import (
    enforce_shot_duration_policy,
    scene_end_times_to_split_points_ms,
    split_points_to_ranges_ms,
)


@dataclass(frozen=True, slots=True)
class SceneDetectionResult:
    """Model/backend output normalized before local duration policy is applied."""

    total_duration_ms: int
    scene_end_times_ms: tuple[int, ...]
    detection_method: str

    def __post_init__(self) -> None:
        if isinstance(self.total_duration_ms, bool) or not isinstance(self.total_duration_ms, int):
            raise TypeError("total_duration_ms must be an int")
        if self.total_duration_ms < 0:
            raise ValueError("total_duration_ms must be >= 0")
        if not self.detection_method.strip():
            raise ValueError("detection_method must not be empty")


class SceneBoundaryBackend(Protocol):
    """Infrastructure-facing scene detector normalized to millisecond scene ends."""

    def detect_scenes(self, asset_ref: EntityRevisionRef) -> SceneDetectionResult: ...


class PolicyDrivenShotDetector(ShotDetector):
    """Translate backend scene observations into application boundary proposals.

    The backend owns model/media integration. This class owns only deterministic conversion
    and duration policy. It never creates Domain `Shot` identity.
    """

    def __init__(self, backend: SceneBoundaryBackend) -> None:
        self._backend = backend

    def detect(
        self,
        asset_ref: EntityRevisionRef,
        options: ShotDetectionOptions,
    ) -> tuple[ShotBoundaryProposal, ...]:
        result = self._backend.detect_scenes(asset_ref)
        if result.total_duration_ms == 0:
            return ()

        split_points_ms = scene_end_times_to_split_points_ms(result.scene_end_times_ms)
        constrained_split_points_ms = enforce_shot_duration_policy(
            split_points_ms,
            total_duration_ms=result.total_duration_ms,
            min_shot_duration_ms=options.min_shot_duration_ms,
            max_shot_duration_ms=options.max_shot_duration_ms,
        )
        ranges_ms = split_points_to_ranges_ms(
            constrained_split_points_ms,
            total_duration_ms=result.total_duration_ms,
        )

        return tuple(
            ShotBoundaryProposal(
                asset_ref=asset_ref,
                source_start_ms=start_ms,
                source_end_ms=end_ms,
                detection_method=result.detection_method,
            )
            for start_ms, end_ms in ranges_ms
            if end_ms > start_ms
        )

from dataclasses import dataclass

from video_editing_agent.application.ports.shot_detector import ShotDetectionOptions
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.media.shot_detection.detector import (
    PolicyDrivenShotDetector,
    SceneBoundaryResult,
)


@dataclass
class FakeSceneBoundaryBackend:
    result: SceneBoundaryResult
    received_asset_ref: EntityRevisionRef | None = None

    def detect_boundaries(self, asset_ref: EntityRevisionRef) -> SceneBoundaryResult:
        self.received_asset_ref = asset_ref
        return self.result


def test_detector_turns_internal_boundaries_into_asset_scoped_proposals() -> None:
    asset_ref = EntityRevisionRef("ast_test", 3)
    backend = FakeSceneBoundaryBackend(
        SceneBoundaryResult(
            total_duration_ms=4_000,
            boundary_times_ms=(1_000, 2_500),
            detection_method="fake-transnetv2",
        )
    )

    detector = PolicyDrivenShotDetector(backend)
    proposals = detector.detect(asset_ref, ShotDetectionOptions())

    assert backend.received_asset_ref == asset_ref
    assert [(p.source_start_ms, p.source_end_ms) for p in proposals] == [
        (0, 1_000),
        (1_000, 2_500),
        (2_500, 4_000),
    ]
    assert all(p.asset_ref == asset_ref for p in proposals)
    assert all(p.detection_method == "fake-transnetv2" for p in proposals)


def test_detector_retains_last_internal_boundary_regression() -> None:
    backend = FakeSceneBoundaryBackend(
        SceneBoundaryResult(
            total_duration_ms=4_000,
            boundary_times_ms=(960, 1_960, 2_960),
            detection_method="fake-transnetv2",
        )
    )

    proposals = PolicyDrivenShotDetector(backend).detect(
        EntityRevisionRef("ast_test", 1),
        ShotDetectionOptions(),
    )

    assert [(p.source_start_ms, p.source_end_ms) for p in proposals] == [
        (0, 960),
        (960, 1_960),
        (1_960, 2_960),
        (2_960, 4_000),
    ]


def test_detector_applies_duration_policy_after_backend_detection() -> None:
    backend = FakeSceneBoundaryBackend(
        SceneBoundaryResult(
            total_duration_ms=4_000,
            boundary_times_ms=(1_000, 2_500),
            detection_method="fake-transnetv2",
        )
    )

    detector = PolicyDrivenShotDetector(backend)
    proposals = detector.detect(
        EntityRevisionRef("ast_test", 1),
        ShotDetectionOptions(min_shot_duration_ms=2_000),
    )

    assert [(p.source_start_ms, p.source_end_ms) for p in proposals] == [(0, 4_000)]


def test_detector_can_force_maximum_duration_without_backend_cut_points() -> None:
    backend = FakeSceneBoundaryBackend(
        SceneBoundaryResult(
            total_duration_ms=3_000,
            boundary_times_ms=(),
            detection_method="fake-transnetv2",
        )
    )

    detector = PolicyDrivenShotDetector(backend)
    proposals = detector.detect(
        EntityRevisionRef("ast_test", 1),
        ShotDetectionOptions(max_shot_duration_ms=1_000),
    )

    assert [(p.source_start_ms, p.source_end_ms) for p in proposals] == [
        (0, 1_000),
        (1_000, 2_000),
        (2_000, 3_000),
    ]


def test_zero_duration_asset_produces_no_boundary_proposals() -> None:
    backend = FakeSceneBoundaryBackend(
        SceneBoundaryResult(
            total_duration_ms=0,
            boundary_times_ms=(),
            detection_method="fake-transnetv2",
        )
    )

    detector = PolicyDrivenShotDetector(backend)

    assert detector.detect(EntityRevisionRef("ast_empty", 1), ShotDetectionOptions()) == ()

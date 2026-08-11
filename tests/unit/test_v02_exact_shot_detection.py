from __future__ import annotations

import pathlib

import pytest

from video_editing_agent.application.ports.shot_detector import ShotDetectionOptions
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.media.shot_detection.catalog import ShotCatalog
from video_editing_agent.media.shot_detection.v02_exact import (
    ExactPolicyDrivenShotDetector,
    ExactSceneBoundaryResult,
)


class StaticExactBackend:
    def __init__(self, result: ExactSceneBoundaryResult) -> None:
        self._result = result

    def detect_boundaries(self, asset_ref: EntityRevisionRef) -> ExactSceneBoundaryResult:
        del asset_ref
        return self._result


def _shot_ids():
    counter = 0

    def next_id() -> str:
        nonlocal counter
        counter += 1
        return f"sht_exact_{counter}"

    return next_id


def test_exact_detector_preserves_non_millisecond_duration_through_shot_identity() -> None:
    asset_ref = EntityRevisionRef("ast_exact", 1)
    total_duration = MediaTime(1001, 400)  # 2.5025 seconds
    first_cut = MediaTime(1, 24)
    backend = StaticExactBackend(
        ExactSceneBoundaryResult(
            total_duration=total_duration,
            boundary_times=(first_cut,),
            detection_method="exact-test",
        )
    )

    proposals = ExactPolicyDrivenShotDetector(backend).detect(asset_ref, ShotDetectionOptions())
    shots = ShotCatalog(shot_id_factory=_shot_ids()).commit_boundaries(proposals)

    assert len(shots) == 2
    assert shots[0].source_range.start == MediaTime(0, 1)
    assert shots[0].source_range.end == first_cut
    assert shots[1].source_range.start == first_cut
    assert shots[-1].source_range.end == total_duration
    assert all(shot.asset_ref == asset_ref for shot in shots)


def test_non_millisecond_cut_never_silently_rounds_through_legacy_adapter() -> None:
    asset_ref = EntityRevisionRef("ast_exact", 1)
    backend = StaticExactBackend(
        ExactSceneBoundaryResult(
            total_duration=MediaTime(2, 1),
            boundary_times=(MediaTime(1, 24),),
            detection_method="exact-test",
        )
    )

    proposals = ExactPolicyDrivenShotDetector(backend).detect(asset_ref, ShotDetectionOptions())

    assert proposals[0].source_range.end == MediaTime(1, 24)
    with pytest.raises(ValueError, match="exact integer millisecond"):
        _ = proposals[0].source_end_ms


def test_exact_max_duration_policy_partitions_without_millisecond_rounding() -> None:
    asset_ref = EntityRevisionRef("ast_exact", 1)
    total_duration = MediaTime(1001, 400)  # 2.5025 seconds
    backend = StaticExactBackend(
        ExactSceneBoundaryResult(
            total_duration=total_duration,
            boundary_times=(),
            detection_method="exact-test",
        )
    )

    proposals = ExactPolicyDrivenShotDetector(backend).detect(
        asset_ref,
        ShotDetectionOptions(max_shot_duration_ms=1_000),
    )

    assert len(proposals) == 3
    assert proposals[0].source_range.start == MediaTime(0, 1)
    assert proposals[-1].source_range.end == total_duration
    assert all(proposal.source_range.duration == MediaTime(1001, 1200) for proposal in proposals)
    assert all(
        previous.source_range.end == current.source_range.start
        for previous, current in zip(proposals, proposals[1:], strict=False)
    )


def test_exact_scene_boundary_result_rejects_unsorted_or_duplicate_cuts() -> None:
    with pytest.raises(ValueError, match="unique, increasing"):
        ExactSceneBoundaryResult(
            total_duration=MediaTime(2, 1),
            boundary_times=(MediaTime(1, 2), MediaTime(1, 4)),
            detection_method="exact-test",
        )


def test_exact_scene_boundary_result_has_no_filesystem_authority() -> None:
    result = ExactSceneBoundaryResult(
        total_duration=MediaTime(1, 1),
        boundary_times=(),
        detection_method="exact-test",
    )

    assert result.total_duration == MediaTime(1, 1)
    assert not hasattr(result, "path")
    assert not isinstance(result.total_duration, pathlib.Path)

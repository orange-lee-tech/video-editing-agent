from dataclasses import replace

import pytest

from video_editing_agent.application.ports.spatial_composer import (
    OutputCanvas,
    PixelCrop,
    SourceFrameGeometry,
    SpatialCropKeyframe,
    SpatialInterpolationMode,
    SpatialTransformPlan,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.render.spatial_plan_ffmpeg import (
    compile_spatial_plan,
)


def _plan(mode=SpatialInterpolationMode.HOLD) -> SpatialTransformPlan:
    return SpatialTransformPlan(
        "selection",
        EntityRevisionRef("shot", 1),
        MediaTimeRange(MediaTime(7, 10), MediaTime(19, 10)),
        SourceFrameGeometry(320, 200),
        OutputCanvas(540, 960),
        (
            SpatialCropKeyframe(MediaTime(7, 10), PixelCrop(10, 0, 99, 176)),
            SpatialCropKeyframe(MediaTime(6, 5), PixelCrop(40, 10, 99, 176)),
            SpatialCropKeyframe(MediaTime(17, 10), PixelCrop(20, 20, 99, 176)),
        ),
        mode,
    )


def test_hold_execution_remains_canonical_and_held() -> None:
    plan = _plan()
    execution = compile_spatial_plan(plan)

    assert execution.adapter_id == "ffmpeg-spatial-transform-plan-v2"
    assert execution.source_start_seconds == "0.7"
    assert execution.source_duration_seconds == "1.9"
    assert "if(gte(t\\,1/2)\\,40\\,10)" in execution.video_filter
    assert plan.evaluate_crop(MediaTime(19, 20)).left == 10
    assert plan.evaluate_crop(MediaTime(6, 5)).left == 40


def test_linear_execution_midpoint_segments_boundaries_and_clamping() -> None:
    plan = _plan(SpatialInterpolationMode.LINEAR)
    execution = compile_spatial_plan(plan)

    assert (
        "floor(10+(60)*max(t-0\\,0)+(-100)*max(t-1/2\\,0)"
        "+(40)*max(t-1\\,0)+0.5)" in execution.video_filter
    )
    assert plan.evaluate_crop(MediaTime(0, 1)).left == 10
    assert plan.evaluate_crop(MediaTime(19, 20)) == PixelCrop(25, 5, 99, 176)
    assert plan.evaluate_crop(MediaTime(6, 5)) == PixelCrop(40, 10, 99, 176)
    assert plan.evaluate_crop(MediaTime(29, 20)) == PixelCrop(30, 15, 99, 176)
    assert plan.evaluate_crop(MediaTime(3, 1)).left == 20


def test_linear_rounding_is_exact_rational_half_up() -> None:
    plan = replace(
        _plan(SpatialInterpolationMode.LINEAR),
        keyframes=(
            SpatialCropKeyframe(MediaTime(7, 10), PixelCrop(10, 0, 99, 176)),
            SpatialCropKeyframe(MediaTime(17, 10), PixelCrop(11, 1, 99, 176)),
        ),
    )
    assert plan.evaluate_crop(MediaTime(6, 5)) == PixelCrop(11, 1, 99, 176)


def test_interpolation_participates_in_plan_identity_and_unsupported_fails_closed() -> None:
    assert _plan() != _plan(SpatialInterpolationMode.LINEAR)
    with pytest.raises(ValueError, match="unsupported spatial interpolation"):
        replace(_plan(), interpolation="spline")


def test_compile_spatial_plan_rejects_unexecutable_crop_size_changes() -> None:
    plan = _plan()
    changed = replace(
        plan,
        keyframes=(
            plan.keyframes[0],
            SpatialCropKeyframe(MediaTime(6, 5), PixelCrop(40, 0, 81, 144)),
        ),
    )
    with pytest.raises(ValueError, match="constant crop dimensions"):
        compile_spatial_plan(changed)


def test_linear_compiler_scales_without_nested_per_keyframe_conditionals() -> None:
    plan = replace(
        _plan(SpatialInterpolationMode.LINEAR),
        source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(4, 1)),
        keyframes=tuple(
            SpatialCropKeyframe(MediaTime(index, 30), PixelCrop(index % 100, 0, 99, 176))
            for index in range(100)
        ),
    )
    execution = compile_spatial_plan(plan)
    assert "if(lt" not in execution.video_filter
    assert "max(t-" in execution.video_filter

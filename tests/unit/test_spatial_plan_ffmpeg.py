from video_editing_agent.application.ports.spatial_composer import (
    OutputCanvas,
    PixelCrop,
    SourceFrameGeometry,
    SpatialCropKeyframe,
    SpatialTransformPlan,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.render.spatial_plan_ffmpeg import compile_spatial_plan


def _plan() -> SpatialTransformPlan:
    return SpatialTransformPlan(
        "selection",
        EntityRevisionRef("shot", 1),
        MediaTimeRange(MediaTime(7, 10), MediaTime(19, 10)),
        SourceFrameGeometry(320, 180),
        OutputCanvas(540, 960),
        (
            SpatialCropKeyframe(MediaTime(7, 10), PixelCrop(10, 0, 99, 176)),
            SpatialCropKeyframe(MediaTime(6, 5), PixelCrop(40, 0, 99, 176)),
        ),
    )


def test_compile_spatial_plan_consumes_exact_canonical_keyframes() -> None:
    execution = compile_spatial_plan(_plan())

    assert execution.adapter_id == "ffmpeg-spatial-transform-plan-step-v1"
    assert execution.source_start_seconds == "0.7"
    assert execution.source_duration_seconds == "1.9"
    assert execution.video_filter == (
        "setpts=PTS-STARTPTS,scale=320:180,"
        "crop=99:176:if(gte(t\\,1/2)\\,40\\,10):0,scale=540:960:flags=lanczos"
    )


def test_compile_spatial_plan_rejects_unexecutable_crop_size_changes() -> None:
    plan = _plan()
    changed = SpatialTransformPlan(
        plan.selection_id,
        plan.shot_ref,
        plan.source_range,
        plan.source_geometry,
        plan.output_canvas,
        (
            plan.keyframes[0],
            SpatialCropKeyframe(MediaTime(6, 5), PixelCrop(40, 0, 81, 144)),
        ),
    )

    try:
        compile_spatial_plan(changed)
    except ValueError as exc:
        assert "constant crop dimensions" in str(exc)
    else:
        raise AssertionError("variable crop dimensions must fail closed")

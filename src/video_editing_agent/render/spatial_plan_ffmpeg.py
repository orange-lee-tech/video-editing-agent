from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from video_editing_agent.application.ports.spatial_composer import SpatialTransformPlan


def _ffmpeg_fraction(value: Fraction) -> str:
    return (
        str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    )


def _ffmpeg_seconds(value: Fraction) -> str:
    return f"{float(value):.9f}".rstrip("0").rstrip(".")


def _step_expression(plan: SpatialTransformPlan, attribute: str) -> str:
    first, *remaining = plan.keyframes
    current = getattr(first.crop, attribute)
    expression = str(current)
    start = plan.source_range.start
    for keyframe in remaining:
        value = getattr(keyframe.crop, attribute)
        if value == current:
            continue
        relative = (keyframe.source_time - start).as_fraction()
        expression = f"if(gte(t\\,{_ffmpeg_fraction(relative)})\\,{value}\\,{expression})"
        current = value
    return expression


@dataclass(frozen=True, slots=True)
class SpatialFfmpegExecution:
    adapter_id: str
    source_start_seconds: str
    source_duration_seconds: str
    video_filter: str
    output_width: int
    output_height: int


def compile_spatial_plan(plan: SpatialTransformPlan) -> SpatialFfmpegExecution:
    """Translate canonical crop decisions into a step-held FFmpeg filter graph."""

    crop = plan.keyframes[0].crop
    if any(
        keyframe.crop.width != crop.width or keyframe.crop.height != crop.height
        for keyframe in plan.keyframes
    ):
        raise ValueError("FFmpeg spatial execution requires constant crop dimensions")
    start = plan.source_range.start.as_fraction()
    duration = plan.source_range.duration.as_fraction()
    left = _step_expression(plan, "left")
    top = _step_expression(plan, "top")
    video_filter = (
        "setpts=PTS-STARTPTS,"
        f"scale={plan.source_geometry.width}:{plan.source_geometry.height},"
        f"crop={crop.width}:{crop.height}:{left}:{top},"
        f"scale={plan.output_canvas.width}:{plan.output_canvas.height}:flags=lanczos"
    )
    return SpatialFfmpegExecution(
        "ffmpeg-spatial-transform-plan-step-v1",
        _ffmpeg_seconds(start),
        _ffmpeg_seconds(duration),
        video_filter,
        plan.output_canvas.width,
        plan.output_canvas.height,
    )

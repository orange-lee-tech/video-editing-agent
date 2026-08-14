from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from video_editing_agent.application.ports.spatial_composer import (
    PixelCrop,
    SpatialInterpolationMode,
    SpatialTransformPlan,
)
from video_editing_agent.domain.common.media_time import MediaTime


def _ffmpeg_fraction(value: Fraction) -> str:
    return (
        str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    )


def _ffmpeg_seconds(value: Fraction) -> str:
    return f"{float(value):.9f}".rstrip("0").rstrip(".")


def _round_half_up(value: Fraction) -> int:
    return (
        value.numerator // value.denominator
        if value.denominator == 1
        else (2 * value.numerator + value.denominator) // (2 * value.denominator)
    )


def evaluate_spatial_crop(plan: SpatialTransformPlan, source_time: MediaTime) -> PixelCrop:
    """Evaluate canonical interpolation using exact rational time and round-half-up pixels."""

    time = source_time.as_fraction()
    frames = plan.keyframes
    if time <= frames[0].source_time.as_fraction():
        return frames[0].crop
    if time >= frames[-1].source_time.as_fraction():
        return frames[-1].crop
    for left, right in zip(frames, frames[1:], strict=False):
        start = left.source_time.as_fraction()
        end = right.source_time.as_fraction()
        if time == end:
            return right.crop
        if start <= time < end:
            if plan.interpolation is SpatialInterpolationMode.HOLD:
                return left.crop
            if plan.interpolation is not SpatialInterpolationMode.LINEAR:
                raise ValueError("unsupported spatial interpolation mode")
            ratio = (time - start) / (end - start)
            return PixelCrop(
                _round_half_up(
                    Fraction(left.crop.left) + ratio * (right.crop.left - left.crop.left)
                ),
                _round_half_up(Fraction(left.crop.top) + ratio * (right.crop.top - left.crop.top)),
                left.crop.width,
                left.crop.height,
            )
    raise AssertionError("canonical spatial interval lookup failed")


def _hold_expression(plan: SpatialTransformPlan, attribute: str) -> str:
    first, *remaining = plan.keyframes
    expression = str(getattr(first.crop, attribute))
    current = getattr(first.crop, attribute)
    start = plan.source_range.start
    for keyframe in remaining:
        value = getattr(keyframe.crop, attribute)
        if value != current:
            relative = (keyframe.source_time - start).as_fraction()
            expression = f"if(gte(t\\,{_ffmpeg_fraction(relative)})\\,{value}\\,{expression})"
            current = value
    return expression


def _linear_expression(plan: SpatialTransformPlan, attribute: str) -> str:
    """Compile a piecewise-linear curve as non-nested slope changes."""

    start = plan.source_range.start
    frames = plan.keyframes
    if len(frames) == 1:
        return str(getattr(frames[0].crop, attribute))
    times = tuple((item.source_time - start).as_fraction() for item in frames)
    values = tuple(getattr(item.crop, attribute) for item in frames)
    slopes = tuple(
        Fraction(right_value - left_value, 1) / (right_time - left_time)
        for left_value, right_value, left_time, right_time in zip(
            values[:-1], values[1:], times[:-1], times[1:], strict=True
        )
    )
    if not any(slopes):
        return str(values[0])
    terms = [str(values[0])]
    previous = Fraction(0)
    for time, slope in zip(times[:-1], slopes, strict=True):
        change = slope - previous
        if change:
            terms.append(f"+({_ffmpeg_fraction(change)})*max(t-{_ffmpeg_fraction(time)}\\,0)")
        previous = slope
    if previous:
        terms.append(f"+({_ffmpeg_fraction(-previous)})*max(t-{_ffmpeg_fraction(times[-1])}\\,0)")
    return f"floor({''.join(terms)}+0.5)"


@dataclass(frozen=True, slots=True)
class SpatialFfmpegExecution:
    adapter_id: str
    source_start_seconds: str
    source_duration_seconds: str
    video_filter: str
    output_width: int
    output_height: int


def compile_spatial_plan(plan: SpatialTransformPlan) -> SpatialFfmpegExecution:
    """Compile only interpolation and crops already owned by the canonical spatial plan."""

    crop = plan.keyframes[0].crop
    if any(
        keyframe.crop.width != crop.width or keyframe.crop.height != crop.height
        for keyframe in plan.keyframes
    ):
        raise ValueError("FFmpeg spatial execution requires constant crop dimensions")
    if plan.interpolation is SpatialInterpolationMode.HOLD:
        expression = _hold_expression
    elif plan.interpolation is SpatialInterpolationMode.LINEAR:
        expression = _linear_expression
    else:
        raise ValueError("unsupported spatial interpolation mode")
    left = expression(plan, "left")
    top = expression(plan, "top")
    video_filter = (
        "setpts=PTS-STARTPTS,"
        f"scale={plan.source_geometry.width}:{plan.source_geometry.height},"
        f"crop={crop.width}:{crop.height}:{left}:{top},"
        f"scale={plan.output_canvas.width}:{plan.output_canvas.height}:flags=lanczos"
    )
    return SpatialFfmpegExecution(
        "ffmpeg-spatial-transform-plan-v2",
        _ffmpeg_seconds(plan.source_range.start.as_fraction()),
        _ffmpeg_seconds(plan.source_range.duration.as_fraction()),
        video_filter,
        plan.output_canvas.width,
        plan.output_canvas.height,
    )

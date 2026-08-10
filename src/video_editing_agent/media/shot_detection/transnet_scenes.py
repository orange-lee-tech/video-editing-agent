from __future__ import annotations

import math
from collections.abc import Iterable


def _normalize_threshold(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("threshold must be a number")
    threshold = float(value)
    if not math.isfinite(threshold):
        raise ValueError("threshold must be finite")
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1")
    return threshold


def _normalize_frames_per_second(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("frames_per_second must be an int")
    if value <= 0:
        raise ValueError("frames_per_second must be > 0")
    return value


def _normalize_probability(value: float, *, index: int) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"prediction[{index}] must be a number")
    probability = float(value)
    if not math.isfinite(probability):
        raise ValueError(f"prediction[{index}] must be finite")
    if not 0.0 <= probability <= 1.0:
        raise ValueError(f"prediction[{index}] must be between 0 and 1")
    return probability


def _frame_index_to_ms(frame_index: int, *, frames_per_second: int) -> int:
    return (frame_index * 1000 + frames_per_second // 2) // frames_per_second


def single_frame_predictions_to_boundary_times_ms(
    predictions: Iterable[float],
    *,
    threshold: float = 0.5,
    frames_per_second: int = 25,
) -> tuple[int, ...]:
    """Convert TransNetV2 transition probabilities into gap-free internal cut timestamps.

    A contiguous above-threshold transition run contributes one cut at the midpoint of that
    run. Only internal source boundaries are returned; media end is carried separately by the
    authoritative source duration.
    """
    normalized_threshold = _normalize_threshold(threshold)
    normalized_fps = _normalize_frames_per_second(frames_per_second)
    normalized_predictions = tuple(
        _normalize_probability(value, index=index) for index, value in enumerate(predictions)
    )
    if len(normalized_predictions) < 2:
        return ()

    transition_start: int | None = None
    boundary_times_ms: list[int] = []

    for index, probability in enumerate(normalized_predictions):
        is_transition = probability > normalized_threshold
        if is_transition and transition_start is None:
            transition_start = index
            continue
        if is_transition or transition_start is None:
            continue

        transition_end = index - 1
        midpoint_frame = (transition_start + transition_end + 1) // 2
        if transition_start > 0 and transition_end < len(normalized_predictions) - 1:
            boundary_times_ms.append(
                _frame_index_to_ms(midpoint_frame, frames_per_second=normalized_fps)
            )
        transition_start = None

    if transition_start is not None:
        transition_end = len(normalized_predictions) - 1
        midpoint_frame = (transition_start + transition_end + 1) // 2
        if transition_start > 0 and transition_end < len(normalized_predictions) - 1:
            boundary_times_ms.append(
                _frame_index_to_ms(midpoint_frame, frames_per_second=normalized_fps)
            )

    return tuple(dict.fromkeys(boundary_times_ms))

from __future__ import annotations

import math
from collections.abc import Iterable
from typing import Protocol

from video_editing_agent.media.shot_detection.transnet_window import (
    TRANSNETV2_CONTEXT_FRAMES,
    TRANSNETV2_WINDOW_FRAMES,
    iter_transnetv2_windows,
)


class TransNetV2WindowPredictor(Protocol):
    """Heavy model adapters implement only one 100-frame inference operation."""

    def predict_single_frame_probabilities(
        self,
        frames: tuple[bytes, ...],
    ) -> tuple[float, ...]:
        ...


def _validate_probability(value: float, *, index: int) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"prediction[{index}] must be a number")
    normalized = float(value)
    if not math.isfinite(normalized):
        raise ValueError(f"prediction[{index}] must be finite")
    if not 0.0 <= normalized <= 1.0:
        raise ValueError(f"prediction[{index}] must be between 0 and 1")
    return normalized


def collect_transnetv2_single_frame_predictions(
    frames: Iterable[bytes],
    predictor: TransNetV2WindowPredictor,
) -> tuple[float, ...]:
    """Run streaming TransNetV2 windows and stitch only valid center predictions.

    Raw video frames remain streaming/bounded-memory. Keeping one probability per source frame
    is intentionally cheap enough for later scene conversion and review diagnostics.
    """
    predictions: list[float] = []

    for window in iter_transnetv2_windows(frames):
        raw_predictions = predictor.predict_single_frame_probabilities(window.frames)
        if len(raw_predictions) != TRANSNETV2_WINDOW_FRAMES:
            raise ValueError(
                "TransNetV2 predictor must return one probability per model-window frame: "
                f"expected {TRANSNETV2_WINDOW_FRAMES}, got {len(raw_predictions)}"
            )

        output_start = TRANSNETV2_CONTEXT_FRAMES
        output_end = output_start + window.valid_output_frames
        for local_index, probability in enumerate(
            raw_predictions[output_start:output_end],
            start=output_start,
        ):
            predictions.append(_validate_probability(probability, index=local_index))

    return tuple(predictions)

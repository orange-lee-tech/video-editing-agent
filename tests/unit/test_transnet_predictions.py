import math

import pytest

from video_editing_agent.media.shot_detection.transnet_predictions import (
    collect_transnetv2_single_frame_predictions,
)


class EchoFramePredictor:
    def predict_single_frame_probabilities(self, frames: tuple[bytes, ...]) -> tuple[float, ...]:
        return tuple(frame[0] / 255.0 for frame in frames)


class ConstantPredictor:
    def __init__(self, predictions: tuple[float, ...]) -> None:
        self._predictions = predictions

    def predict_single_frame_probabilities(self, frames: tuple[bytes, ...]) -> tuple[float, ...]:
        del frames
        return self._predictions


def test_prediction_stitcher_returns_one_center_prediction_per_real_frame() -> None:
    frames = [bytes([index]) for index in range(125)]

    predictions = collect_transnetv2_single_frame_predictions(frames, EchoFramePredictor())

    assert predictions == tuple(index / 255.0 for index in range(125))


def test_prediction_stitcher_handles_empty_source() -> None:
    assert collect_transnetv2_single_frame_predictions([], EchoFramePredictor()) == ()


def test_prediction_stitcher_requires_one_prediction_per_window_frame() -> None:
    with pytest.raises(ValueError, match="expected 100, got 99"):
        collect_transnetv2_single_frame_predictions(
            [b"a"],
            ConstantPredictor((0.5,) * 99),
        )


@pytest.mark.parametrize("bad_value", [-0.1, 1.1, math.inf, math.nan])
def test_prediction_stitcher_rejects_invalid_probabilities(bad_value: float) -> None:
    predictions = [0.5] * 100
    predictions[25] = bad_value

    with pytest.raises(ValueError):
        collect_transnetv2_single_frame_predictions(
            [b"a"],
            ConstantPredictor(tuple(predictions)),
        )


def test_prediction_stitcher_rejects_non_numeric_probability() -> None:
    predictions: list[object] = [0.5] * 100
    predictions[25] = "bad"

    with pytest.raises(TypeError, match="must be a number"):
        collect_transnetv2_single_frame_predictions(
            [b"a"],
            ConstantPredictor(tuple(predictions)),  # type: ignore[arg-type]
        )

import math

import pytest

from video_editing_agent.media.shot_detection.transnet_scenes import (
    single_frame_predictions_to_scene_end_times_ms,
)


def test_transition_run_contributes_one_midpoint_cut() -> None:
    predictions = [0.0] * 75
    predictions[24] = 0.9
    predictions[25] = 0.8

    assert single_frame_predictions_to_scene_end_times_ms(predictions) == (1000,)


def test_multiple_transition_runs_preserve_order() -> None:
    predictions = [0.0] * 100
    predictions[10:13] = [0.9, 0.9, 0.9]
    predictions[50:52] = [0.8, 0.8]

    assert single_frame_predictions_to_scene_end_times_ms(predictions) == (440, 2040)


def test_starting_transition_does_not_emit_zero_cut() -> None:
    predictions = [0.9, 0.9, 0.0, 0.0]

    assert single_frame_predictions_to_scene_end_times_ms(predictions) == ()


@pytest.mark.parametrize("threshold", [-0.1, 1.1, math.inf, math.nan])
def test_invalid_threshold_is_rejected(threshold: float) -> None:
    with pytest.raises(ValueError):
        single_frame_predictions_to_scene_end_times_ms([0.0, 0.0], threshold=threshold)


def test_non_numeric_prediction_is_rejected() -> None:
    with pytest.raises(TypeError, match=r"prediction\[1\]"):
        single_frame_predictions_to_scene_end_times_ms([0.0, "bad"])  # type: ignore[list-item]

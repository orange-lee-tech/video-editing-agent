import importlib.metadata

import pytest

from video_editing_agent.application.ports.seeded_tracking import NormalizedRectangle
from video_editing_agent.providers.vision.mediapipe_recovery_tracking import (
    MediaPipeRecoveryTrackingConfig,
    MediaPipeRecoveryTrackingPort,
    MediaPipeRecoveryTrackingUnavailableError,
)


def _provider() -> MediaPipeRecoveryTrackingPort:
    return MediaPipeRecoveryTrackingPort(MediaPipeRecoveryTrackingConfig("external-model.tflite"))


def test_optional_runtime_absent_fails_clearly(monkeypatch) -> None:
    def missing(package):
        raise importlib.metadata.PackageNotFoundError(package)

    monkeypatch.setattr(importlib.metadata, "version", missing)
    with pytest.raises(MediaPipeRecoveryTrackingUnavailableError, match="optional MediaPipe"):
        _provider()._runtime()


def test_same_target_reseed_is_deterministic_and_wrong_or_ambiguous_target_is_rejected() -> None:
    provider = _provider()
    last = (240.0, 68.0, 285.0, 148.0)
    same_target = (((238.0, 67.0, 284.0, 149.0), 0.8),)
    wrong_target = (((0.0, 0.0, 20.0, 20.0), 0.99),)
    ambiguous = (
        ((238.0, 67.0, 284.0, 149.0), 0.8),
        ((242.0, 69.0, 286.0, 147.0), 0.7),
    )

    assert provider._select_reseed_index(same_target, last) == 0
    assert provider._select_reseed_index(tuple(reversed(same_target)), last) == 0
    assert provider._select_reseed_index(wrong_target, last) is None
    assert provider._select_reseed_index(ambiguous, last) is None


def test_grounded_detection_maps_to_identity_anchored_seed_roi_inside_source() -> None:
    rectangle = _provider()._focus_rectangle(
        (300.0, 160.0, 330.0, 190.0), NormalizedRectangle(0.0, 0.0, 0.13, 0.44)
    )
    assert rectangle.width == 0.13 and rectangle.height == 0.44
    assert rectangle.x + rectangle.width == pytest.approx(1.0)
    assert rectangle.y + rectangle.height == pytest.approx(1.0)

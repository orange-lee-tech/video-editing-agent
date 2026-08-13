import importlib
import importlib.metadata

import pytest

from video_editing_agent.providers.vision.opencv_seeded_tracking import (
    OpenCvSeededTrackingPort,
    OpenCvSeededTrackingUnavailableError,
)


def test_optional_tracking_runtime_absent_is_clean(monkeypatch) -> None:
    def missing(package):
        raise importlib.metadata.PackageNotFoundError(package)

    monkeypatch.setattr(importlib.metadata, "version", missing)
    with pytest.raises(OpenCvSeededTrackingUnavailableError, match="unavailable"):
        OpenCvSeededTrackingPort()._runtime()


def test_wrong_opencv_version_is_rejected(monkeypatch) -> None:
    monkeypatch.setattr(importlib.metadata, "version", lambda package: "4.12.0.0")
    monkeypatch.setattr(importlib, "import_module", lambda package: object())
    with pytest.raises(OpenCvSeededTrackingUnavailableError, match="version mismatch"):
        OpenCvSeededTrackingPort()._runtime()

from __future__ import annotations

import importlib
import importlib.metadata

import pytest

from video_editing_agent.providers.vision.opencv_motion import (
    OpenCvMotionUnavailableError,
    OpenCvVisualMotionPort,
)


def test_provider_is_cleanly_unavailable_without_optional_runtime(monkeypatch) -> None:
    def missing(package: str) -> str:
        raise importlib.metadata.PackageNotFoundError(package)

    monkeypatch.setattr(importlib.metadata, "version", missing)
    with pytest.raises(OpenCvMotionUnavailableError, match="unavailable"):
        OpenCvVisualMotionPort()._runtime()


def test_provider_rejects_wrong_candidate_version(monkeypatch) -> None:
    monkeypatch.setattr(importlib.metadata, "version", lambda package: "4.12.0.0")
    monkeypatch.setattr(importlib, "import_module", lambda package: object())
    with pytest.raises(OpenCvMotionUnavailableError, match="version mismatch"):
        OpenCvVisualMotionPort()._runtime()

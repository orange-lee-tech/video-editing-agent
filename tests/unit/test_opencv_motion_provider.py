from __future__ import annotations

import importlib
import importlib.metadata
from pathlib import Path

import pytest

from video_editing_agent.application.ports.visual_motion import (
    VisualMotionMeasurement,
    VisualMotionRequest,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.providers.vision import opencv_motion
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


def test_provider_processes_frame_pairs_without_materializing_the_shot(monkeypatch) -> None:
    yielded = 0
    observed: list[tuple[int, int, int, int]] = []

    def frames(*args, **kwargs):
        nonlocal yielded
        for index in range(5):
            yielded += 1
            yield bytes([index])

    class FakeArray:
        def __init__(self, value: int) -> None:
            self.value = value

        def reshape(self, *shape):
            return self

    class FakeNumpy:
        uint8 = object()

        @staticmethod
        def frombuffer(frame: bytes, dtype):
            return FakeArray(frame[0])

    class FakeCv2:
        COLOR_RGB2GRAY = 1

        @staticmethod
        def cvtColor(array: FakeArray, code: int) -> int:
            return array.value

    class StreamingProbePort(OpenCvVisualMotionPort):
        def _runtime(self):
            return FakeCv2(), FakeNumpy()

        def _pair(self, cv2, np, left, right, index):
            observed.append((index, yielded, left, right))
            return VisualMotionMeasurement(
                MediaTimeRange(MediaTime(index, 10), MediaTime(1, 10)),
                "unavailable",
                "insufficient_features",
                0,
                0,
                0.0,
                0,
                0.0,
                None,
                None,
                None,
                None,
                None,
                None,
                0.0,
                None,
                None,
                None,
            )

    monkeypatch.setattr(opencv_motion, "iter_video_rgb24_frames", frames)
    proposal = StreamingProbePort().measure(
        VisualMotionRequest(
            EntityRevisionRef("sht_streaming", 1),
            Path("unused.mp4"),
            MediaTimeRange(MediaTime(1, 1), MediaTime(1, 1)),
        )
    )

    assert len(proposal.measurements) == 4
    assert observed == [
        (0, 2, 0, 1),
        (1, 3, 1, 2),
        (2, 4, 2, 3),
        (3, 5, 3, 4),
    ]

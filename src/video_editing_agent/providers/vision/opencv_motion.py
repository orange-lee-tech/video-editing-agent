from __future__ import annotations

import importlib
import importlib.metadata
import math
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from video_editing_agent.application.ports.visual_motion import (
    VisualMotionMeasurement,
    VisualMotionPort,
    VisualMotionProposal,
    VisualMotionRequest,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.media.shot_detection.ffmpeg_frames import iter_video_rgb24_frames

OPENCV_PACKAGE_VERSION = "4.13.0.92"


class OpenCvMotionUnavailableError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class OpenCvMotionConfig:
    ffmpeg_executable: str = "ffmpeg"
    frames_per_second: int = 10
    width: int = 320
    height: int = 180


class OpenCvVisualMotionPort(VisualMotionPort):
    def __init__(self, config: OpenCvMotionConfig | None = None) -> None:
        self._config = config or OpenCvMotionConfig()

    def _runtime(self) -> tuple[Any, Any]:
        try:
            version = importlib.metadata.version("opencv-python-headless")
            cv2 = importlib.import_module("cv2")
            np = importlib.import_module("numpy")
        except (importlib.metadata.PackageNotFoundError, ModuleNotFoundError) as exc:
            raise OpenCvMotionUnavailableError(
                "optional OpenCV motion runtime is unavailable"
            ) from exc
        if version != OPENCV_PACKAGE_VERSION:
            raise OpenCvMotionUnavailableError(
                "opencv-python-headless version mismatch: "
                f"expected {OPENCV_PACKAGE_VERSION}, found {version}"
            )
        return cv2, np

    def measure(self, request: VisualMotionRequest) -> VisualMotionProposal:
        cv2, np = self._runtime()
        config = self._config
        frames: Iterable[bytes] = iter_video_rgb24_frames(
            request.local_media_path,
            ffmpeg_executable=config.ffmpeg_executable,
            frames_per_second=config.frames_per_second,
            target_width=config.width,
            target_height=config.height,
            source_range=request.source_range,
        )
        grays = [
            cv2.cvtColor(
                np.frombuffer(frame, dtype=np.uint8).reshape(config.height, config.width, 3),
                cv2.COLOR_RGB2GRAY,
            )
            for frame in frames
        ]
        measurements = tuple(
            self._pair(cv2, np, left, right, index)
            for index, (left, right) in enumerate(zip(grays, grays[1:], strict=False))
        )
        return VisualMotionProposal(
            request.shot_ref,
            "local:opencv-sparse-lk-motion",
            f"opencv-python-headless@{OPENCV_PACKAGE_VERSION};adapter=r0.8c-v1",
            config.frames_per_second,
            config.width,
            config.height,
            measurements,
        )

    def _pair(
        self, cv2: Any, np: Any, left: Any, right: Any, index: int
    ) -> VisualMotionMeasurement:
        points = cv2.goodFeaturesToTrack(left, 300, 0.01, 7, blockSize=7)
        interval = MediaTimeRange(
            MediaTime(index, self._config.frames_per_second),
            MediaTime(1, self._config.frames_per_second),
        )
        if points is None or len(points) < 6:
            return VisualMotionMeasurement(
                interval,
                "unavailable",
                "insufficient_features",
                0 if points is None else len(points),
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
        tracked, status, _ = cv2.calcOpticalFlowPyrLK(left, right, points, None)
        if tracked is None or status is None:
            return VisualMotionMeasurement(
                interval,
                "unavailable",
                "tracking_failure",
                len(points),
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
        valid = status.reshape(-1) == 1
        source = points.reshape(-1, 2)[valid]
        target = tracked.reshape(-1, 2)[valid]
        tracked_count = len(source)
        if tracked_count < 6:
            return VisualMotionMeasurement(
                interval,
                "unavailable",
                "tracking_failure",
                len(points),
                tracked_count,
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
        transform, mask = cv2.estimateAffinePartial2D(
            source,
            target,
            method=cv2.RANSAC,
            ransacReprojThreshold=2.0,
            maxIters=2000,
            confidence=0.99,
        )
        raw = np.linalg.norm(target - source, axis=1)
        xs = source[:, 0]
        ys = source[:, 1]
        coverage = float(
            (xs.max() - xs.min())
            * (ys.max() - ys.min())
            / (self._config.width * self._config.height)
        )
        if transform is None or mask is None:
            return VisualMotionMeasurement(
                interval,
                "unavailable",
                "weak_global_fit",
                len(points),
                tracked_count,
                coverage,
                0,
                0.0,
                None,
                None,
                None,
                None,
                None,
                None,
                float(np.median(raw)),
                None,
                None,
                None,
            )
        inliers = mask.reshape(-1).astype(bool)
        inlier_count = int(inliers.sum())
        ratio = inlier_count / tracked_count
        predicted = source @ transform[:, :2].T + transform[:, 2]
        residual = np.linalg.norm(target - predicted, axis=1)
        fit = float(np.median(residual[inliers])) if inlier_count else None
        a, b = float(transform[0, 0]), float(transform[0, 1])
        scale = math.hypot(a, b)
        return VisualMotionMeasurement(
            interval,
            "available",
            None,
            len(points),
            tracked_count,
            coverage,
            inlier_count,
            ratio,
            float(transform[0, 2]),
            float(transform[1, 2]),
            math.atan2(b, a),
            scale,
            fit,
            float(np.median(np.linalg.norm(predicted - source, axis=1))),
            float(np.median(raw)),
            float(np.median(residual)),
            float(np.percentile(residual, 95)),
            float(np.max(residual)),
        )

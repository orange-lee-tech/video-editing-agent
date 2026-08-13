from __future__ import annotations

import importlib
import importlib.metadata
from dataclasses import dataclass
from typing import Any

from video_editing_agent.application.ports.seeded_tracking import (
    NormalizedRectangle,
    SeededTrackingPort,
    SeededTrackingProposal,
    SeededTrackingRequest,
    TrackingSample,
)
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.media.shot_detection.ffmpeg_frames import iter_video_rgb24_frames
from video_editing_agent.providers.vision.opencv_motion import OPENCV_PACKAGE_VERSION


class OpenCvSeededTrackingUnavailableError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class OpenCvSeededTrackingConfig:
    ffmpeg_executable: str = "ffmpeg"
    frames_per_second: int = 30
    width: int = 320
    height: int = 180
    minimum_support: int = 4
    maximum_lk_error: float = 20.0
    maximum_round_trip_error: float = 1.0


class OpenCvSeededTrackingPort(SeededTrackingPort):
    def __init__(self, config: OpenCvSeededTrackingConfig | None = None) -> None:
        self._config = config or OpenCvSeededTrackingConfig()

    def _runtime(self) -> tuple[Any, Any]:
        try:
            version = importlib.metadata.version("opencv-python-headless")
            cv2 = importlib.import_module("cv2")
            np = importlib.import_module("numpy")
        except (importlib.metadata.PackageNotFoundError, ModuleNotFoundError) as exc:
            raise OpenCvSeededTrackingUnavailableError(
                "optional OpenCV tracking runtime is unavailable"
            ) from exc
        if version != OPENCV_PACKAGE_VERSION:
            raise OpenCvSeededTrackingUnavailableError(
                "opencv-python-headless version mismatch: "
                f"expected {OPENCV_PACKAGE_VERSION}, found {version}"
            )
        return cv2, np

    def track(self, request: SeededTrackingRequest) -> SeededTrackingProposal:
        cv2, np = self._runtime()
        config = self._config
        frames = iter_video_rgb24_frames(
            request.local_media_path,
            ffmpeg_executable=config.ffmpeg_executable,
            frames_per_second=config.frames_per_second,
            target_width=config.width,
            target_height=config.height,
            source_range=request.source_range,
        )
        grays = (
            cv2.cvtColor(
                np.frombuffer(frame, dtype=np.uint8).reshape(config.height, config.width, 3),
                cv2.COLOR_RGB2GRAY,
            )
            for frame in frames
        )
        first = next(grays, None)
        if first is None:
            raise RuntimeError("tracking decode produced no frames")
        rect = request.seed_rectangle
        x = rect.x * config.width
        y = rect.y * config.height
        w = rect.width * config.width
        h = rect.height * config.height
        mask = np.zeros(first.shape, dtype=np.uint8)
        mask[int(y) : int(y + h), int(x) : int(x + w)] = 255
        points = cv2.goodFeaturesToTrack(first, 100, 0.01, 3, mask=mask, blockSize=5)
        samples = [
            TrackingSample(
                MediaTime(0, config.frames_per_second),
                "available",
                None,
                rect,
                0 if points is None else len(points),
                1.0,
            )
        ]
        previous = first
        initial = 0 if points is None else len(points)
        if points is None or initial < config.minimum_support:
            samples[0] = TrackingSample(
                samples[0].relative_time, "lost", "insufficient_features", None, initial, 0.0
            )
        else:
            for index, current in enumerate(grays, start=1):
                tracked, status, error = cv2.calcOpticalFlowPyrLK(previous, current, points, None)
                if tracked is None or status is None or error is None:
                    samples.append(
                        TrackingSample(
                            MediaTime(index, config.frames_per_second),
                            "lost",
                            "tracking_failure",
                            None,
                            0,
                            0.0,
                        )
                    )
                    break
                returned, reverse_status, _ = cv2.calcOpticalFlowPyrLK(
                    current, previous, tracked, None
                )
                if returned is None or reverse_status is None:
                    samples.append(
                        TrackingSample(
                            MediaTime(index, config.frames_per_second),
                            "lost",
                            "round_trip_failure",
                            None,
                            0,
                            0.0,
                        )
                    )
                    break
                round_trip = np.linalg.norm(returned.reshape(-1, 2) - points.reshape(-1, 2), axis=1)
                valid = (
                    (status.reshape(-1) == 1)
                    & (reverse_status.reshape(-1) == 1)
                    & (error.reshape(-1) <= config.maximum_lk_error)
                    & (round_trip <= config.maximum_round_trip_error)
                )
                source = points.reshape(-1, 2)[valid]
                target = tracked.reshape(-1, 2)[valid]
                if len(target) < config.minimum_support:
                    reason = (
                        "target_exit"
                        if x < 0 or y < 0 or x + w > config.width or y + h > config.height
                        else "insufficient_support"
                    )
                    samples.append(
                        TrackingSample(
                            MediaTime(index, config.frames_per_second),
                            "lost",
                            reason,
                            None,
                            len(target),
                            len(target) / initial,
                        )
                    )
                    break
                delta = np.median(target - source, axis=0)
                predicted_x = x + float(delta[0])
                predicted_y = y + float(delta[1])
                margin = 3.0
                inside = (
                    (target[:, 0] >= predicted_x - margin)
                    & (target[:, 0] <= predicted_x + w + margin)
                    & (target[:, 1] >= predicted_y - margin)
                    & (target[:, 1] <= predicted_y + h + margin)
                )
                target = target[inside]
                source = source[inside]
                if len(target) < config.minimum_support:
                    samples.append(
                        TrackingSample(
                            MediaTime(index, config.frames_per_second),
                            "lost",
                            "insufficient_target_support",
                            None,
                            len(target),
                            len(target) / initial,
                        )
                    )
                    break
                delta = np.median(target - source, axis=0)
                x += float(delta[0])
                y += float(delta[1])
                if x + w <= 0 or y + h <= 0 or x >= config.width or y >= config.height:
                    samples.append(
                        TrackingSample(
                            MediaTime(index, config.frames_per_second),
                            "lost",
                            "target_exit",
                            None,
                            len(target),
                            len(target) / initial,
                        )
                    )
                    break
                rect = NormalizedRectangle(
                    x / config.width, y / config.height, w / config.width, h / config.height
                )
                samples.append(
                    TrackingSample(
                        MediaTime(index, config.frames_per_second),
                        "available",
                        None,
                        rect,
                        len(target),
                        len(target) / initial,
                    )
                )
                points = target.reshape(-1, 1, 2)
                previous = current
        return SeededTrackingProposal(
            request.shot_ref,
            request.source_range,
            request.seed_id,
            request.seed_rectangle,
            "local:opencv-seeded-sparse-lk",
            f"opencv-python-headless@{OPENCV_PACKAGE_VERSION};adapter=r0.8f-v1",
            config.frames_per_second,
            config.width,
            config.height,
            tuple(samples),
        )

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import math
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

MEDIAPIPE_PACKAGE_VERSION = "0.10.31"
EFFICIENTDET_LITE0_SHA256 = "0720bf247bd76e6594ea28fa9c6f7c5242be774818997dbbeffc4da460c723bb"


class MediaPipeRecoveryTrackingUnavailableError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class MediaPipeRecoveryTrackingConfig:
    model_path: str
    ffmpeg_executable: str = "ffmpeg"
    frames_per_second: int = 30
    width: int = 320
    height: int = 180
    detector_score_threshold: float = 0.25
    initial_seed_iou: float = 0.1
    tracking_association_iou: float = 0.05
    reseed_maximum_normalized_distance: float = 0.55
    reseed_minimum_area_ratio: float = 0.35
    reseed_maximum_area_ratio: float = 2.85
    minimum_lk_support: int = 4
    maximum_lk_error: float = 20.0
    maximum_round_trip_error: float = 1.0


class MediaPipeRecoveryTrackingPort(SeededTrackingPort):
    """Ground observations with MediaPipe and use Sparse-LK only for association/reseed."""

    def __init__(self, config: MediaPipeRecoveryTrackingConfig) -> None:
        self._config = config

    def _runtime(self) -> tuple[Any, Any, Any, Any, str]:
        try:
            mediapipe_version = importlib.metadata.version("mediapipe")
            opencv_version = importlib.metadata.version("opencv-python-headless")
            mp = importlib.import_module("mediapipe")
            cv2 = importlib.import_module("cv2")
            np = importlib.import_module("numpy")
            vision = importlib.import_module("mediapipe.tasks.python.vision")
            tasks_python = importlib.import_module("mediapipe.tasks.python")
        except (importlib.metadata.PackageNotFoundError, ModuleNotFoundError) as exc:
            raise MediaPipeRecoveryTrackingUnavailableError(
                "optional MediaPipe recovery tracking runtime is unavailable; "
                "install the mediapipe-recovery extra"
            ) from exc
        if mediapipe_version != MEDIAPIPE_PACKAGE_VERSION:
            raise MediaPipeRecoveryTrackingUnavailableError(
                "mediapipe version mismatch: "
                f"expected {MEDIAPIPE_PACKAGE_VERSION}, found {mediapipe_version}"
            )
        if opencv_version != OPENCV_PACKAGE_VERSION:
            raise MediaPipeRecoveryTrackingUnavailableError(
                "opencv-python-headless version mismatch: "
                f"expected {OPENCV_PACKAGE_VERSION}, found {opencv_version}"
            )
        model_path = self._config.model_path
        try:
            with open(model_path, "rb") as model_file:
                model_sha = hashlib.sha256(model_file.read()).hexdigest()
        except OSError as exc:
            raise MediaPipeRecoveryTrackingUnavailableError(
                f"MediaPipe detector model is unavailable: {model_path}"
            ) from exc
        if model_sha != EFFICIENTDET_LITE0_SHA256:
            raise MediaPipeRecoveryTrackingUnavailableError(
                "MediaPipe detector model SHA-256 mismatch"
            )
        return mp, cv2, np, (tasks_python, vision), model_sha

    @staticmethod
    def _iou(np: Any, first: Any, second: Any) -> float:
        left, top = max(first[0], second[0]), max(first[1], second[1])
        right, bottom = min(first[2], second[2]), min(first[3], second[3])
        intersection = max(0.0, right - left) * max(0.0, bottom - top)
        union = (
            (first[2] - first[0]) * (first[3] - first[1])
            + (second[2] - second[0]) * (second[3] - second[1])
            - intersection
        )
        return 0.0 if union <= 0 else float(intersection / union)

    def _deterministic_reseed(
        self, detections: list[tuple[Any, float]], last: Any
    ) -> tuple[Any, float] | None:
        boxes = tuple(
            (
                (
                    float(box[0]),
                    float(box[1]),
                    float(box[2]),
                    float(box[3]),
                ),
                score,
            )
            for box, score in detections
        )
        last_box = (float(last[0]), float(last[1]), float(last[2]), float(last[3]))
        selected_index = self._select_reseed_index(boxes, last_box)
        return None if selected_index is None else detections[selected_index]

    def _select_reseed_index(
        self,
        detections: tuple[tuple[tuple[float, float, float, float], float], ...],
        last: tuple[float, float, float, float],
    ) -> int | None:
        config = self._config
        diagonal = (config.width**2 + config.height**2) ** 0.5
        last_center = ((last[0] + last[2]) / 2, (last[1] + last[3]) / 2)
        last_area = (last[2] - last[0]) * (last[3] - last[1])
        eligible: list[tuple[float, float, tuple[float, ...], int]] = []
        for index, (box, score) in enumerate(detections):
            center = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)
            distance = math.hypot(center[0] - last_center[0], center[1] - last_center[1]) / diagonal
            area_ratio = ((box[2] - box[0]) * (box[3] - box[1])) / last_area
            if (
                distance <= config.reseed_maximum_normalized_distance
                and config.reseed_minimum_area_ratio
                <= area_ratio
                <= config.reseed_maximum_area_ratio
            ):
                eligible.append((distance, -score, box, index))
        if len(eligible) != 1:
            return None
        return eligible[0][-1]

    def _focus_rectangle(
        self, box: tuple[float, float, float, float], seed: NormalizedRectangle
    ) -> NormalizedRectangle:
        config = self._config
        width = seed.width * config.width
        height = seed.height * config.height
        center_x = (box[0] + box[2]) / 2
        center_y = (box[1] + box[3]) / 2
        left = min(max(center_x - width / 2, 0.0), config.width - width)
        top = min(max(center_y - height / 2, 0.0), config.height - height)
        return NormalizedRectangle(
            left / config.width,
            top / config.height,
            seed.width,
            seed.height,
        )

    def track(self, request: SeededTrackingRequest) -> SeededTrackingProposal:
        mp, cv2, np, task_modules, model_sha = self._runtime()
        tasks_python, vision = task_modules
        config = self._config
        options = vision.ObjectDetectorOptions(
            base_options=tasks_python.BaseOptions(model_asset_path=config.model_path),
            score_threshold=config.detector_score_threshold,
            category_allowlist=["person"],
            running_mode=vision.RunningMode.IMAGE,
        )
        detector = vision.ObjectDetector.create_from_options(options)
        frames = iter_video_rgb24_frames(
            request.local_media_path,
            ffmpeg_executable=config.ffmpeg_executable,
            frames_per_second=config.frames_per_second,
            target_width=config.width,
            target_height=config.height,
            source_range=request.source_range,
        )
        seed = request.seed_rectangle
        seed_box = np.asarray(
            [
                seed.x * config.width,
                seed.y * config.height,
                (seed.x + seed.width) * config.width,
                (seed.y + seed.height) * config.height,
            ],
            dtype=float,
        )
        samples: list[TrackingSample] = []
        previous = None
        points = None
        box = None
        lost = False

        def features(gray: Any, active_box: Any) -> Any:
            mask = np.zeros(gray.shape, dtype=np.uint8)
            x1, y1, x2, y2 = active_box.astype(int)
            mask[max(0, y1) : min(config.height, y2), max(0, x1) : min(config.width, x2)] = 255
            return cv2.goodFeaturesToTrack(gray, 100, 0.01, 3, mask=mask, blockSize=5)

        try:
            for index, frame in enumerate(frames):
                relative_time = MediaTime(index, config.frames_per_second)
                if relative_time.as_fraction() >= request.source_range.duration.as_fraction():
                    break
                rgb = np.frombuffer(frame, dtype=np.uint8).reshape(config.height, config.width, 3)
                gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
                result = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
                detections = []
                for detection in result.detections:
                    category = detection.categories[0]
                    if category.category_name != "person":
                        continue
                    bounds = detection.bounding_box
                    detected = np.asarray(
                        [
                            bounds.origin_x,
                            bounds.origin_y,
                            bounds.origin_x + bounds.width,
                            bounds.origin_y + bounds.height,
                        ],
                        dtype=float,
                    )
                    detections.append((detected, float(category.score)))
                detections.sort(key=lambda item: (-item[1], *item[0].tolist()))
                selected = None
                predicted = None
                if previous is None:
                    ranked = sorted(
                        detections,
                        key=lambda item: (
                            -self._iou(np, seed_box, item[0]),
                            -item[1],
                            *item[0].tolist(),
                        ),
                    )
                    if ranked and self._iou(np, seed_box, ranked[0][0]) >= config.initial_seed_iou:
                        selected = ranked[0]
                elif points is not None and box is not None:
                    tracked, status, error = cv2.calcOpticalFlowPyrLK(previous, gray, points, None)
                    returned, reverse_status, _ = (
                        (None, None, None)
                        if tracked is None
                        else cv2.calcOpticalFlowPyrLK(gray, previous, tracked, None)
                    )
                    if (
                        tracked is not None
                        and status is not None
                        and error is not None
                        and returned is not None
                        and reverse_status is not None
                    ):
                        round_trip = np.linalg.norm(
                            returned.reshape(-1, 2) - points.reshape(-1, 2), axis=1
                        )
                        valid = (
                            (status.reshape(-1) == 1)
                            & (reverse_status.reshape(-1) == 1)
                            & (error.reshape(-1) <= config.maximum_lk_error)
                            & (round_trip <= config.maximum_round_trip_error)
                        )
                        source_points = points.reshape(-1, 2)[valid]
                        target_points = tracked.reshape(-1, 2)[valid]
                        if len(target_points) >= config.minimum_lk_support:
                            delta = np.median(target_points - source_points, axis=0)
                            predicted = box + np.asarray([delta[0], delta[1], delta[0], delta[1]])
                if previous is not None and box is not None:
                    if not lost and predicted is not None and detections:
                        ranked = sorted(
                            detections,
                            key=lambda item: (
                                -self._iou(np, predicted, item[0]),
                                -item[1],
                                *item[0].tolist(),
                            ),
                        )
                        if (
                            self._iou(np, predicted, ranked[0][0])
                            >= config.tracking_association_iou
                        ):
                            selected = ranked[0]
                    else:
                        selected = self._deterministic_reseed(detections, box)
                if selected is None:
                    points = None
                    lost = True
                    samples.append(
                        TrackingSample(
                            relative_time,
                            "lost",
                            "no_grounded_same_target_detection",
                            None,
                            0,
                            0.0,
                        )
                    )
                else:
                    box, score = selected
                    box = np.asarray(
                        [
                            min(max(float(box[0]), 0.0), float(config.width)),
                            min(max(float(box[1]), 0.0), float(config.height)),
                            min(max(float(box[2]), 0.0), float(config.width)),
                            min(max(float(box[3]), 0.0), float(config.height)),
                        ],
                        dtype=float,
                    )
                    if box[2] <= box[0] or box[3] <= box[1]:
                        points = None
                        lost = True
                        samples.append(
                            TrackingSample(
                                relative_time,
                                "lost",
                                "detector_box_outside_source_geometry",
                                None,
                                0,
                                0.0,
                            )
                        )
                        previous = gray
                        continue
                    points = features(gray, box)
                    support = 0 if points is None else len(points)
                    if support < config.minimum_lk_support:
                        points = None
                        lost = True
                        samples.append(
                            TrackingSample(
                                relative_time,
                                "lost",
                                "insufficient_reseed_features",
                                None,
                                support,
                                float(score),
                            )
                        )
                    else:
                        rectangle = self._focus_rectangle(
                            (
                                float(box[0]),
                                float(box[1]),
                                float(box[2]),
                                float(box[3]),
                            ),
                            request.seed_rectangle,
                        )
                        samples.append(
                            TrackingSample(
                                relative_time,
                                "available",
                                None,
                                rectangle,
                                support,
                                float(score),
                            )
                        )
                        lost = False
                previous = gray
        finally:
            detector.close()
        if not samples:
            raise RuntimeError("recovery tracking decode produced no frames")
        revision = (
            f"mediapipe@{MEDIAPIPE_PACKAGE_VERSION};opencv-python-headless@"
            f"{OPENCV_PACKAGE_VERSION};model=efficientdet_lite0.tflite;sha256={model_sha};"
            "observation=identity-anchored-seed-roi;adapter=detector-sparse-lk-reseed-v2"
        )
        return SeededTrackingProposal(
            request.shot_ref,
            request.source_range,
            request.seed_id,
            request.seed_rectangle,
            "local:mediapipe-object-detector-sparse-lk-reseed",
            revision,
            config.frames_per_second,
            config.width,
            config.height,
            tuple(samples),
        )

from __future__ import annotations

import argparse
import pathlib

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.media.shot_detection.transnet_backend import (
    ResolvedVideoAsset,
    TransNetV2BackendConfig,
    TransNetV2SceneBoundaryBackend,
)
from video_editing_agent.media.shot_detection.transnet_runtime import (
    TorchTransNetV2Config,
    TorchTransNetV2WindowPredictor,
)


class StaticVideoAssetResolver:
    def __init__(self, path: pathlib.Path, duration_ms: int) -> None:
        self._resolved = ResolvedVideoAsset(path=path, duration_ms=duration_ms)

    def resolve_video(self, asset_ref: EntityRevisionRef) -> ResolvedVideoAsset:
        del asset_ref
        return self._resolved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe the complete FFmpeg -> TransNetV2 scene-boundary path on one video."
    )
    parser.add_argument("video", type=pathlib.Path)
    parser.add_argument("--duration-ms", type=int, required=True)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument(
        "--device",
        default="cpu",
        choices=("auto", "cpu", "cuda", "mps"),
    )
    parser.add_argument("--require-boundary", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    video_path = args.video.expanduser().resolve()
    if not video_path.is_file():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if args.duration_ms <= 0:
        raise ValueError("duration-ms must be > 0")

    predictor = TorchTransNetV2WindowPredictor(TorchTransNetV2Config(device=args.device))
    backend = TransNetV2SceneBoundaryBackend(
        StaticVideoAssetResolver(video_path, args.duration_ms),
        predictor,
        config=TransNetV2BackendConfig(
            threshold=args.threshold,
            ffmpeg_executable=args.ffmpeg,
        ),
    )
    result = backend.detect_scenes(EntityRevisionRef("ast_transnet_video_probe", 1))

    if result.total_duration_ms != args.duration_ms:
        raise RuntimeError("Probe backend changed authoritative source duration")
    if tuple(sorted(set(result.scene_end_times_ms))) != result.scene_end_times_ms:
        raise RuntimeError("Scene boundaries must be unique and ordered")
    if any(not 0 < boundary_ms < args.duration_ms for boundary_ms in result.scene_end_times_ms):
        raise RuntimeError("Scene boundaries must stay inside the source duration")
    if args.require_boundary and not result.scene_end_times_ms:
        raise RuntimeError("TransNetV2 produced no internal boundary for the probe video")

    print("TransNetV2 video probe: PASS")
    print(f"video={video_path}")
    print(f"duration_ms={result.total_duration_ms}")
    print(f"boundary_count={len(result.scene_end_times_ms)}")
    print(f"scene_end_times_ms={result.scene_end_times_ms}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

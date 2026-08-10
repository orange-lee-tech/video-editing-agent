from __future__ import annotations

import argparse
import pathlib

from video_editing_agent.media.shot_detection.transnet_runtime import (
    TRANSNETV2_BYTES_PER_FRAME,
    TorchTransNetV2Config,
    TorchTransNetV2WindowPredictor,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe the optional transnetv2-pytorch runtime with one synthetic model window."
    )
    parser.add_argument(
        "--device",
        default="cpu",
        choices=("auto", "cpu", "cuda", "mps"),
        help="TransNetV2 device selection. CPU is the reproducible default.",
    )
    parser.add_argument(
        "--weights",
        type=pathlib.Path,
        default=None,
        help="Explicit path to transnetv2-pytorch-weights.pth if package-local discovery fails.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    predictor = TorchTransNetV2WindowPredictor(
        TorchTransNetV2Config(
            device=args.device,
            weights_path=args.weights,
        )
    )
    black_frame = b"\x00" * TRANSNETV2_BYTES_PER_FRAME
    predictions = predictor.predict_single_frame_probabilities((black_frame,) * 100)

    print("TransNetV2 runtime probe: PASS")
    print(f"prediction_count={len(predictions)}")
    print(f"prediction_min={min(predictions):.6f}")
    print(f"prediction_max={max(predictions):.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

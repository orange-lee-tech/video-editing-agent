from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any

from video_editing_agent.adapters.bootstrap.runtime import PackagedRuntimeLocator


def run_probe(
    locator: PackagedRuntimeLocator,
    *,
    speech_wav: Path | None = None,
) -> dict[str, Any]:
    ffmpeg = locator.existing_component_path("ffmpeg")
    ffprobe = locator.existing_component_path("ffprobe")
    if ffmpeg is None or ffprobe is None:
        raise RuntimeError("owned ffmpeg runtime is unavailable")

    locator.activate_managed_python_runtime("transnet-runtime")
    torch = importlib.import_module("torch")
    transnetv2_pytorch = importlib.import_module("transnetv2_pytorch")

    model = transnetv2_pytorch.TransNetV2(device="cpu")
    predictions = model.predict_raw(torch.zeros((1, 100, 27, 48, 3), dtype=torch.uint8))
    transnet = {
        "torch": torch.__version__,
        "outputs": [list(item.shape) for item in predictions],
        "finite": all(bool(torch.isfinite(item).all()) for item in predictions),
    }

    speech: dict[str, Any]
    if speech_wav is None:
        speech = {
            "status": "deferred_not_shipped_1_0",
            "reason": (
                "advanced speech continuity / multilingual voice production "
                "is deferred to 2.0"
            ),
        }
    else:
        locator.activate_managed_python_runtime("speech-runtime")
        av = importlib.import_module("av")
        ctranslate2 = importlib.import_module("ctranslate2")
        WhisperModel = importlib.import_module("faster_whisper").WhisperModel

        model_path = locator.existing_component_path("speech-model")
        if model_path is None:
            raise RuntimeError("owned pinned speech model is unavailable")
        whisper = WhisperModel(
            str(model_path), device="cpu", compute_type="int8", local_files_only=True
        )
        segments, info = whisper.transcribe(str(speech_wav), beam_size=1, language="en")
        text = " ".join(segment.text.strip() for segment in segments)
        speech = {
            "status": "probed_optional_component",
            "ctranslate2": ctranslate2.__version__,
            "av": av.__version__,
            "language": info.language,
            "language_probability": info.language_probability,
            "text": text,
        }

    return {
        "ffmpeg": str(ffmpeg),
        "ffprobe": str(ffprobe),
        "transnet": transnet,
        "speech": speech,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Probe packaged heavyweight runtime components")
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--speech-wav", type=Path)
    args = parser.parse_args(argv)

    locator = PackagedRuntimeLocator(args.runtime_root, args.manifest)
    payload = run_probe(locator, speech_wav=args.speech_wav)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

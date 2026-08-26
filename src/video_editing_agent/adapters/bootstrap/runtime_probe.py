from __future__ import annotations

import argparse
import importlib
import json
import subprocess
from pathlib import Path
from typing import Any

from video_editing_agent.adapters.bootstrap.resource_locator import default_runtime_locator


def run_runtime_probe(speech_wav: Path | None = None) -> dict[str, Any]:
    locator = default_runtime_locator()
    ffmpeg = locator.executable("ffmpeg", development_name="ffmpeg")
    ffprobe = locator.executable("ffprobe", development_name="ffprobe")
    if ffmpeg is None or ffprobe is None:
        raise RuntimeError("owned FFmpeg payload is unavailable")
    versions = {}
    for name, executable in (("ffmpeg", ffmpeg), ("ffprobe", ffprobe)):
        completed = subprocess.run(
            (executable, "-version"), check=True, capture_output=True, text=True, timeout=20
        )
        output = completed.stdout
        configuration = next(
            (line for line in output.splitlines() if line.startswith("configuration:")), ""
        )
        if "--enable-gpl" in configuration or "--enable-nonfree" in configuration:
            raise RuntimeError("FFmpeg payload violates LGPL-only configuration policy")
        versions[name] = {
            "version": output.splitlines()[0],
            "configuration": configuration,
        }

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
            "reason": " ".join(
                (
                    "advanced speech continuity / multilingual voice production",
                    "is deferred to 2.0",
                )
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
            "text": text,
            "local_files_only": True,
            "device": "cpu",
            "compute_type": "int8",
        }

    return {
        "schema": "video-editing-agent-runtime-probe/v1",
        "ffmpeg": versions,
        "transnet": transnet,
        "speech": speech,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--speech-wav", type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(run_runtime_probe(args.speech_wav), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

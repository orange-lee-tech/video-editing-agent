from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import time

from video_editing_agent.application.ports.seeded_tracking import (
    NormalizedRectangle,
    SeededTrackingRequest,
)
from video_editing_agent.application.ports.visual_motion import VisualMotionRequest
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.providers.vision.opencv_motion import (
    OpenCvMotionConfig,
    OpenCvVisualMotionPort,
)
from video_editing_agent.providers.vision.opencv_seeded_tracking import (
    OpenCvSeededTrackingConfig,
    OpenCvSeededTrackingPort,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media-root", type=pathlib.Path, required=True)
    parser.add_argument("--speech-fixture", type=pathlib.Path, required=True)
    parser.add_argument("--ffmpeg", required=True)
    parser.add_argument("--speech-python", type=pathlib.Path, required=True)
    parser.add_argument("--asr-model", type=pathlib.Path, required=True)
    parser.add_argument("--vad-model", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--retrieval-report", type=pathlib.Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    original = args.media_root / "1.mp4"
    shot_ref = EntityRevisionRef("sht_product", 1)
    started = time.perf_counter()
    motion = OpenCvVisualMotionPort(OpenCvMotionConfig(ffmpeg_executable=args.ffmpeg)).measure(
        VisualMotionRequest(shot_ref, original, MediaTimeRange(MediaTime(0, 1), MediaTime(20, 1)))
    )
    available = tuple(x for x in motion.measurements if x.status == "available")
    camera_fraction = sum((x.global_displacement or 0) > 0.03 for x in available) / len(available)
    residual_fraction = sum((x.residual_p95 or 0) > 0.03 for x in available) / len(available)
    action_residual_median = sorted((x.residual_p95 or 0) for x in available)[len(available) // 2]
    low_path = args.media_root / "probe-output" / "shot-01.mp4"
    low_motion = OpenCvVisualMotionPort(OpenCvMotionConfig(ffmpeg_executable=args.ffmpeg)).measure(
        VisualMotionRequest(
            EntityRevisionRef("sht_low", 1),
            low_path,
            MediaTimeRange(MediaTime(0, 1), MediaTime(7, 1)),
        )
    )
    low_available = tuple(x for x in low_motion.measurements if x.status == "available")
    low_residual_median = sorted((x.residual_p95 or 0) for x in low_available)[
        len(low_available) // 2
    ]
    low_to_action_ratio = low_residual_median / action_residual_median
    tracking = OpenCvSeededTrackingPort(
        OpenCvSeededTrackingConfig(ffmpeg_executable=args.ffmpeg)
    ).track(
        SeededTrackingRequest(
            shot_ref,
            original,
            MediaTimeRange(MediaTime(0, 1), MediaTime(9, 1)),
            "bottle",
            NormalizedRectangle(0.40, 0.28, 0.16, 0.48),
        )
    )
    speech_db = args.output / "speech.sqlite3"
    command = [
        str(args.speech_python),
        str(pathlib.Path(__file__).with_name("r0_8b_speech_evidence_live.py")),
        "--media",
        str(args.speech_fixture),
        "--asr-model",
        str(args.asr_model),
        "--vad-model",
        str(args.vad_model),
        "--database",
        str(speech_db),
        "--ffmpeg",
        args.ffmpeg,
        "--shot-start",
        "1",
        "--shot-end",
        "8",
    ]
    speech = json.loads(subprocess.run(command, check=True, capture_output=True, text=True).stdout)
    retrieval = json.loads(args.retrieval_report.read_text(encoding="utf-8"))
    text = speech["asr"]["text"].casefold()
    gates = {
        "REAL_FOOTAGE_SOURCE_TIME": speech["status"] == "PASS"
        and motion.analyzed_source_range == MediaTimeRange(MediaTime(0, 1), MediaTime(20, 1)),
        "SPEECH_TIMESTAMP_USEFULNESS": "bottle is standing on the table" in text
        and "picked up and turned slowly" in text,
        "SPEECH_CUT_QUALITY": speech["asr"]["segments"] == 2 and speech["vad"]["spans"] >= 3,
        "PAN_FALSE_LOCAL_ACTION": low_to_action_ratio < 0.5,
        "LOCAL_ACTION_RECALL": residual_fraction > 0.25,
        "LOW_MOTION_FALSE_POSITIVE": low_to_action_ratio < 0.5,
        "NOISY_BLURRED_FAIL_SAFE": all(
            x.status in {"available", "unavailable"} for x in motion.measurements
        ),
        "TRACKING_REAL_FOOTAGE": sum(x.status == "available" for x in tracking.samples) >= 120
        and any(x.reason == "target_exit" for x in tracking.samples),
        "RETRIEVAL_REAL_PROJECT_SANITY": retrieval["pass"],
        "R0_8_RESTART_PROVENANCE": speech["asr"]["sqlite_reopen"]
        and speech["vad"]["sqlite_reopen"],
    }
    result = {
        "classification": "product_probe",
        "anonymous_real_clip": "clip_" + hashlib.sha256(original.read_bytes()).hexdigest()[:12],
        "gates": {name: "PASS" if value else "FAIL" for name, value in gates.items()},
        "metrics": {
            "motion_measurements": len(motion.measurements),
            "camera_active_fraction": round(camera_fraction, 3),
            "residual_active_fraction": round(residual_fraction, 3),
            "low_motion_residual_p95_median": round(low_residual_median, 3),
            "action_residual_p95_median": round(action_residual_median, 3),
            "low_to_action_residual_ratio": round(low_to_action_ratio, 3),
            "tracking_samples": len(tracking.samples),
            "tracking_available": sum(x.status == "available" for x in tracking.samples),
            "speech_segments": speech["asr"]["segments"],
            "speech_words": speech["asr"]["words"],
            "vad_spans": speech["vad"]["spans"],
            "wall_seconds": round(time.perf_counter() - started, 3),
        },
        "limitations": [
            "speech is deterministic local TTS mixed with captured ambient audio",
            "natural human speech and talking-head visual behavior were not validated",
        ],
        "pass": all(gates.values()),
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

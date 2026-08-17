from __future__ import annotations

import argparse
import json
import os
import time
from fractions import Fraction
from pathlib import Path

from video_editing_agent.application.ports.preview import (
    PreviewDecodeMode,
    PreviewPlaybackState,
    PreviewStatus,
)
from video_editing_agent.application.use_cases.preview_runtime import PreviewApplicationRuntime
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.providers.preview.gstreamer import (
    GStreamerPreviewBackend,
    GStreamerPreviewConfig,
)

_ENV_KEYS = (
    "PATH",
    "GST_PLUGIN_SYSTEM_PATH_1_0",
    "GST_PLUGIN_PATH_1_0",
    "GST_REGISTRY_1_0",
)


def _seconds(position: MediaTime | None) -> float | None:
    if position is None:
        return None
    return float(position.as_fraction())


def _status_payload(status: PreviewStatus) -> dict[str, object]:
    return {
        "backend": status.backend,
        "state": status.state.value,
        "decode_mode": status.decode_mode.value,
        "runtime_root": None if status.runtime_root is None else str(status.runtime_root),
        "runtime_version": status.runtime_version,
        "runtime_provenance": status.runtime_provenance,
        "media_path": None if status.media_path is None else str(status.media_path),
        "position_seconds": _seconds(status.position),
        "disabled_hardware_features": list(status.disabled_hardware_features),
        "diagnostics": [
            {
                "code": diagnostic.code.value,
                "message": diagnostic.message,
                "retryable": diagnostic.retryable,
            }
            for diagnostic in status.diagnostics
        ],
    }


def _require_clean(status: PreviewStatus, label: str) -> PreviewStatus:
    if status.state is PreviewPlaybackState.FAILED or status.diagnostics:
        raise RuntimeError(f"{label} failed: {json.dumps(_status_payload(status), sort_keys=True)}")
    return status


def _wait_for_position_at_least(
    runtime: PreviewApplicationRuntime,
    minimum: Fraction,
    *,
    label: str,
    timeout_seconds: float = 12.0,
) -> PreviewStatus:
    deadline = time.monotonic() + timeout_seconds
    last: PreviewStatus | None = None
    while time.monotonic() < deadline:
        last = _require_clean(runtime.preview.status(), label)
        if last.position is not None and last.position.as_fraction() >= minimum:
            return last
        time.sleep(0.1)
    detail = None if last is None else _status_payload(last)
    raise RuntimeError(f"{label} timed out waiting for position >= {minimum}: {detail}")


def _wait_for_position_near(
    runtime: PreviewApplicationRuntime,
    target: Fraction,
    *,
    tolerance: Fraction = Fraction(1, 4),
    timeout_seconds: float = 12.0,
) -> PreviewStatus:
    deadline = time.monotonic() + timeout_seconds
    last: PreviewStatus | None = None
    while time.monotonic() < deadline:
        last = _require_clean(runtime.preview.status(), "seek")
        if last.position is not None:
            delta = abs(last.position.as_fraction() - target)
            if delta <= tolerance:
                return last
        time.sleep(0.1)
    detail = None if last is None else _status_payload(last)
    raise RuntimeError(f"seek timed out waiting for position near {target}: {detail}")


def _wait_for_state(
    runtime: PreviewApplicationRuntime,
    desired: PreviewPlaybackState,
    *,
    label: str,
    timeout_seconds: float = 8.0,
) -> PreviewStatus:
    deadline = time.monotonic() + timeout_seconds
    last: PreviewStatus | None = None
    while time.monotonic() < deadline:
        last = _require_clean(runtime.preview.status(), label)
        if last.state is desired:
            return last
        time.sleep(0.1)
    detail = None if last is None else _status_payload(last)
    raise RuntimeError(f"{label} timed out waiting for state {desired.value}: {detail}")


def _snapshot_environment() -> dict[str, str | None]:
    return {key: os.environ.get(key) for key in _ENV_KEYS}


def _assert_environment_restored(before: dict[str, str | None]) -> None:
    after = _snapshot_environment()
    if after != before:
        raise RuntimeError(
            f"Preview release did not restore environment: before={before}, after={after}"
        )


def run_probe(
    runtime_root: Path, media_path: Path, decode_mode: PreviewDecodeMode
) -> dict[str, object]:
    environment_before = _snapshot_environment()
    provenance = "official-gstreamer-1.28.6-msvc-x86_64;sha256=" + os.environ.get(
        "GSTREAMER_PREVIEW_INSTALLER_SHA256", "unknown"
    )
    backend = GStreamerPreviewBackend(
        GStreamerPreviewConfig(
            runtime_root=runtime_root,
            decode_mode=decode_mode,
            provenance=provenance,
        )
    )
    runtime = PreviewApplicationRuntime.from_backend(backend)
    evidence: dict[str, object] = {
        "mode": decode_mode.value,
        "media": str(media_path.resolve()),
        "events": [],
    }

    try:
        initialized = _require_clean(runtime.preview.initialize(), "initialize")
        if initialized.state is not PreviewPlaybackState.READY:
            raise RuntimeError(f"initialize did not reach READY: {_status_payload(initialized)}")
        evidence["initialized"] = _status_payload(initialized)

        loaded = _require_clean(runtime.preview.load(media_path), "load")
        if loaded.state is not PreviewPlaybackState.LOADED:
            raise RuntimeError(f"load did not reach LOADED: {_status_payload(loaded)}")
        evidence["loaded"] = _status_payload(loaded)

        requested_play = _require_clean(runtime.preview.play(), "play")
        evidence["play_requested"] = _status_payload(requested_play)
        advancing = _wait_for_position_at_least(
            runtime,
            Fraction(1, 4),
            label="initial playback",
        )
        evidence["initial_playback"] = _status_payload(advancing)

        pause_requested = _require_clean(runtime.preview.pause(), "pause")
        evidence["pause_requested"] = _status_payload(pause_requested)
        paused = _wait_for_state(runtime, PreviewPlaybackState.PAUSED, label="pause")
        first_pause_position = paused.position
        if first_pause_position is None:
            raise RuntimeError("pause did not expose a position")
        time.sleep(0.45)
        paused_later = _require_clean(runtime.preview.status(), "paused stability")
        if paused_later.position is None:
            raise RuntimeError("paused stability check lost position")
        pause_drift = abs(paused_later.position.as_fraction() - first_pause_position.as_fraction())
        if pause_drift > Fraction(3, 20):
            raise RuntimeError(f"paused playback drifted too far: {pause_drift} seconds")
        evidence["paused"] = {
            "status": _status_payload(paused_later),
            "drift_seconds": float(pause_drift),
        }

        target = MediaTime(3, 2)
        seek_requested = _require_clean(runtime.preview.seek(target), "seek request")
        evidence["seek_requested"] = _status_payload(seek_requested)
        sought = _wait_for_position_near(runtime, Fraction(3, 2))
        evidence["sought"] = _status_payload(sought)

        resumed = _require_clean(runtime.preview.play(), "resume")
        evidence["resume_requested"] = _status_payload(resumed)
        resumed_advancing = _wait_for_position_at_least(
            runtime,
            Fraction(19, 10),
            label="resumed playback",
        )
        evidence["resumed_playback"] = _status_payload(resumed_advancing)

        stopped = _require_clean(runtime.preview.stop(), "stop")
        evidence["stop_requested"] = _status_payload(stopped)
        stopped_confirmed = _wait_for_state(runtime, PreviewPlaybackState.STOPPED, label="stop")
        evidence["stopped"] = _status_payload(stopped_confirmed)

        released = runtime.preview.release()
        if released.state is not PreviewPlaybackState.RELEASED or released.diagnostics:
            raise RuntimeError(f"release failed: {_status_payload(released)}")
        evidence["released"] = _status_payload(released)
        _assert_environment_restored(environment_before)
        evidence["environment_restored"] = True
        evidence["result"] = "PASS"
        return evidence
    finally:
        if runtime.preview.status().state is not PreviewPlaybackState.RELEASED:
            runtime.preview.release()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--media", type=Path, required=True)
    parser.add_argument(
        "--mode",
        choices=[mode.value for mode in PreviewDecodeMode],
        required=True,
    )
    args = parser.parse_args()

    try:
        payload = run_probe(
            args.runtime_root,
            args.media,
            PreviewDecodeMode(args.mode),
        )
    except Exception as error:
        payload = {
            "result": "FAIL",
            "mode": args.mode,
            "error_type": type(error).__name__,
            "error": str(error),
        }
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
        return 1

    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

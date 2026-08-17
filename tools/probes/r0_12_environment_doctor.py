from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, cast


def _load(path: Path) -> tuple[str, dict[str, Any]]:
    raw = path.read_text(encoding="utf-8-sig")
    value = cast(dict[str, Any], json.loads(raw))
    return raw, value


def _check_map(value: dict[str, Any]) -> dict[str, dict[str, Any]]:
    checks = value.get("checks")
    if not isinstance(checks, list):
        raise ValueError("Doctor report checks must be a list")
    mapped: dict[str, dict[str, Any]] = {}
    for item in checks:
        if not isinstance(item, dict):
            raise ValueError("Doctor check must be an object")
        capability = item.get("capability")
        if not isinstance(capability, str):
            raise ValueError("Doctor capability must be a string")
        mapped[capability] = cast(dict[str, Any], item)
    return mapped


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    sentinel = os.environ.get("DOCTOR_SENTINEL", "")
    if not sentinel:
        raise RuntimeError("DOCTOR_SENTINEL must be configured for redaction validation")

    raw, report = _load(args.report)
    checks = _check_map(report)
    required = {
        "host_runtime",
        "media_probe_render",
        "preview_playback",
        "planning_cloud",
        "editing_cloud_director",
        "visual_understanding",
    }
    missing = required - checks.keys()
    if missing:
        raise AssertionError(f"Doctor report is missing capabilities: {sorted(missing)}")

    gates = {
        "SCHEMA_V1": report.get("schema_version") == 1,
        "WINDOWS_HOST_READY": checks["host_runtime"].get("status") == "ready",
        "FFMPEG_TOOLCHAIN_READY": checks["media_probe_render"].get("status") == "ready",
        "PREVIEW_UNCONFIGURED_TYPED": (
            checks["preview_playback"].get("status") == "available_after_install"
        ),
        "DEEPSEEK_PLANNING_CONFIGURED": checks["planning_cloud"].get("status") == "ready",
        "DEEPSEEK_DIRECTOR_CONFIGURED": (
            checks["editing_cloud_director"].get("status") == "ready"
        ),
        "VISUAL_PROVIDER_CONFIGURED": checks["visual_understanding"].get("status") == "ready",
        "SENTINEL_REDACTED": sentinel not in raw,
        "NO_GLOBAL_ENVIRONMENT_OK": "environment_ok" not in report,
        "REPAIR_REPORT_PRESENT": isinstance(report.get("repair_report"), str)
        and "rerun video-editing-agent doctor" in report["repair_report"],
    }
    output = {
        "classification": "WINDOWS_ENVIRONMENT_DOCTOR_ENGINEERING_PROBE",
        "gates": {name: "PASS" if passed else "FAIL" for name, passed in gates.items()},
        "host_evidence": checks["host_runtime"].get("evidence"),
        "media_evidence": checks["media_probe_render"].get("evidence"),
        "preview_status": checks["preview_playback"].get("status"),
        "provider_evidence": {
            "planning": checks["planning_cloud"].get("evidence"),
            "director": checks["editing_cloud_director"].get("evidence"),
            "visual": checks["visual_understanding"].get("evidence"),
        },
        "pass": all(gates.values()),
    }
    print(json.dumps(output, sort_keys=True))
    return 0 if output["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

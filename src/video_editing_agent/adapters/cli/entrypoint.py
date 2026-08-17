from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from video_editing_agent.adapters.cli.main import main as project_main
from video_editing_agent.application.ports.environment_doctor import ProductCapability
from video_editing_agent.application.use_cases.environment_doctor import (
    EnvironmentDoctor,
    EnvironmentDoctorResult,
)
from video_editing_agent.providers.environment import (
    ConfiguredSecretProbe,
    FFmpegToolchainProbe,
    PreviewRuntimeProbe,
    SystemHostProbe,
    VisualProviderConfigurationProbe,
)
from video_editing_agent.providers.preview.gstreamer import (
    GStreamerPreviewBackend,
    GStreamerPreviewConfig,
)


def _doctor_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="video-editing-agent doctor")
    parser.add_argument("--preview-runtime", type=Path)
    return parser


def _build_environment_doctor(preview_runtime: Path | None) -> EnvironmentDoctor:
    preview_backend = None
    if preview_runtime is not None:
        preview_backend = GStreamerPreviewBackend(
            GStreamerPreviewConfig(
                preview_runtime,
                provenance="environment-doctor-user-configured-private-runtime",
            )
        )
    return EnvironmentDoctor(
        (
            SystemHostProbe(),
            FFmpegToolchainProbe(),
            PreviewRuntimeProbe(preview_backend),
            ConfiguredSecretProbe(
                component="deepseek",
                environment_key="DEEPSEEK_API_KEY",
                capabilities=(
                    ProductCapability.PLANNING_CLOUD,
                    ProductCapability.EDITING_CLOUD_DIRECTOR,
                ),
            ),
            VisualProviderConfigurationProbe(),
        )
    )


def _doctor_json(result: EnvironmentDoctorResult) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "checks": [
            {
                "capability": item.capability.value,
                "component": item.component,
                "status": item.status.value,
                "summary": item.summary,
                "evidence": list(item.evidence),
                "repair_guidance": item.repair_guidance,
            }
            for item in result.report.checks
        ],
        "repair_report": result.repair_report,
    }


def _doctor_main(argv: list[str]) -> int:
    try:
        args = _doctor_parser().parse_args(argv)
        result = _build_environment_doctor(args.preview_runtime).inspect()
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(_doctor_json(result), ensure_ascii=False, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] == "doctor":
        return _doctor_main(arguments[1:])
    return project_main(arguments)

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from collections.abc import Callable, Mapping
from pathlib import Path

from video_editing_agent.application.ports.environment_doctor import (
    CapabilityStatus,
    EnvironmentCapabilityCheck,
    ProductCapability,
)
from video_editing_agent.application.ports.preview import (
    PreviewBackend,
    PreviewDiagnosticCode,
    PreviewPlaybackState,
)

ExecutableLocator = Callable[[str], str | None]
ToolRunner = Callable[[tuple[str, ...]], subprocess.CompletedProcess[str]]


def _system_name() -> str:
    return platform.system()


def _architecture() -> str:
    return platform.machine()


def _python_version() -> tuple[int, int, int]:
    return (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)


def _free_disk_bytes() -> int | None:
    try:
        return shutil.disk_usage(Path.cwd()).free
    except OSError:
        return None


def _run_tool(arguments: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        check=False,
        capture_output=True,
        text=True,
        shell=False,
        timeout=10,
    )


def _first_line(value: str) -> str:
    return value.splitlines()[0].strip() if value.splitlines() else ""


class SystemHostProbe:
    def __init__(
        self,
        *,
        system_name: Callable[[], str] = _system_name,
        architecture: Callable[[], str] = _architecture,
        python_version: Callable[[], tuple[int, int, int]] = _python_version,
        free_disk_bytes: Callable[[], int | None] = _free_disk_bytes,
    ) -> None:
        self._system_name = system_name
        self._architecture = architecture
        self._python_version = python_version
        self._free_disk_bytes = free_disk_bytes

    def probe(self) -> tuple[EnvironmentCapabilityCheck, ...]:
        system_name = self._system_name().strip() or "unknown"
        architecture = self._architecture().strip() or "unknown"
        python_version = self._python_version()
        python_text = ".".join(str(value) for value in python_version)
        free_disk = self._free_disk_bytes()
        evidence = [
            f"os={system_name}",
            f"python={python_text}",
            f"architecture={architecture}",
        ]
        if free_disk is not None:
            evidence.append(f"free_disk_gib={free_disk / (1024**3):.1f}")

        if system_name.casefold() != "windows":
            status = CapabilityStatus.UNAVAILABLE
            summary = "Stage-A ordinary-user runtime currently targets Windows"
            repair = "Run the Stage-A product on a supported Windows host, then rerun Doctor."
        elif python_version < (3, 12, 0):
            status = CapabilityStatus.AVAILABLE_AFTER_INSTALL
            summary = "Windows is supported but the running Python is older than 3.12"
            repair = (
                "Install a product-supported Python 3.12+ runtime from an approved source, "
                "then rerun Doctor."
            )
        else:
            status = CapabilityStatus.READY
            summary = "Windows host and Python runtime satisfy the current Stage-A baseline"
            repair = None

        return (
            EnvironmentCapabilityCheck(
                ProductCapability.HOST_RUNTIME,
                "windows_python",
                status,
                summary,
                tuple(evidence),
                repair,
            ),
        )


class FFmpegToolchainProbe:
    def __init__(
        self,
        *,
        locator: ExecutableLocator = shutil.which,
        runner: ToolRunner = _run_tool,
    ) -> None:
        self._locator = locator
        self._runner = runner

    def probe(self) -> tuple[EnvironmentCapabilityCheck, ...]:
        resolved = {name: self._locator(name) for name in ("ffmpeg", "ffprobe")}
        missing = tuple(name for name, path in resolved.items() if path is None)
        if missing:
            return (
                EnvironmentCapabilityCheck(
                    ProductCapability.MEDIA_PROBE_RENDER,
                    "ffmpeg_toolchain",
                    CapabilityStatus.AVAILABLE_AFTER_INSTALL,
                    "Required FFmpeg toolchain executables are not both resolvable",
                    tuple(f"missing={name}" for name in missing),
                    (
                        "Install the product-approved FFmpeg/ffprobe runtime from an official or "
                        "product-approved source, then rerun Doctor."
                    ),
                ),
            )

        evidence: list[str] = []
        for name in ("ffmpeg", "ffprobe"):
            executable = resolved[name]
            assert executable is not None
            try:
                completed = self._runner((executable, "-version"))
            except (OSError, subprocess.TimeoutExpired):
                return (
                    EnvironmentCapabilityCheck(
                        ProductCapability.MEDIA_PROBE_RENDER,
                        "ffmpeg_toolchain",
                        CapabilityStatus.UNAVAILABLE,
                        f"{name} resolved but its bounded runtime probe could not execute",
                        (f"{name}_probe=execution_error",),
                        (
                            "Repair the product-approved FFmpeg toolchain and rerun Doctor; "
                            "executable presence alone is not sufficient."
                        ),
                    ),
                )
            if completed.returncode != 0:
                return (
                    EnvironmentCapabilityCheck(
                        ProductCapability.MEDIA_PROBE_RENDER,
                        "ffmpeg_toolchain",
                        CapabilityStatus.UNAVAILABLE,
                        f"{name} resolved but its bounded runtime probe failed",
                        (f"{name}_exit={completed.returncode}",),
                        "Repair the FFmpeg toolchain and rerun Doctor.",
                    ),
                )
            version_line = _first_line(completed.stdout or completed.stderr)
            evidence.append(f"{name}_probe=ready")
            if version_line:
                evidence.append(f"{name}_version={version_line}")

        return (
            EnvironmentCapabilityCheck(
                ProductCapability.MEDIA_PROBE_RENDER,
                "ffmpeg_toolchain",
                CapabilityStatus.READY,
                "FFmpeg and ffprobe both passed bounded execution probes",
                tuple(evidence),
            ),
        )


class ConfiguredSecretProbe:
    def __init__(
        self,
        *,
        component: str,
        environment_key: str,
        capabilities: tuple[ProductCapability, ...],
        environment: Mapping[str, str] | None = None,
    ) -> None:
        self._component = component
        self._environment_key = environment_key
        self._capabilities = capabilities
        self._environment = os.environ if environment is None else environment

    def probe(self) -> tuple[EnvironmentCapabilityCheck, ...]:
        configured = bool(self._environment.get(self._environment_key, "").strip())
        status = CapabilityStatus.READY if configured else CapabilityStatus.UNAVAILABLE
        summary = (
            f"{self._component} credential is configured"
            if configured
            else f"{self._component} credential is not configured"
        )
        repair = None
        if not configured:
            repair = (
                f"Configure {self._environment_key} in the product secret/configuration store; "
                "do not include the credential value in repair logs."
            )
        evidence = ("credential=configured" if configured else "credential=missing",)
        return tuple(
            EnvironmentCapabilityCheck(
                capability,
                self._component,
                status,
                summary,
                evidence,
                repair,
            )
            for capability in self._capabilities
        )


class VisualProviderConfigurationProbe:
    def __init__(self, environment: Mapping[str, str] | None = None) -> None:
        self._environment = os.environ if environment is None else environment

    def probe(self) -> tuple[EnvironmentCapabilityCheck, ...]:
        configured = tuple(
            name
            for name, key in (
                ("gemini", "GEMINI_API_KEY"),
                ("openai", "OPENAI_API_KEY"),
            )
            if self._environment.get(key, "").strip()
        )
        if configured:
            return (
                EnvironmentCapabilityCheck(
                    ProductCapability.VISUAL_UNDERSTANDING,
                    "cloud_visual_provider",
                    CapabilityStatus.READY,
                    "At least one supported visual-understanding provider is configured",
                    tuple(f"configured_provider={name}" for name in configured),
                ),
            )
        return (
            EnvironmentCapabilityCheck(
                ProductCapability.VISUAL_UNDERSTANDING,
                "cloud_visual_provider",
                CapabilityStatus.UNAVAILABLE,
                "No supported cloud visual-understanding provider is configured",
                ("configured_provider=none",),
                (
                    "Configure either GEMINI_API_KEY or OPENAI_API_KEY in the product secret/"
                    "configuration store, then rerun Doctor."
                ),
            ),
        )


class PreviewRuntimeProbe:
    def __init__(self, backend: PreviewBackend | None) -> None:
        self._backend = backend

    def probe(self) -> tuple[EnvironmentCapabilityCheck, ...]:
        if self._backend is None:
            return (
                EnvironmentCapabilityCheck(
                    ProductCapability.PREVIEW_PLAYBACK,
                    "gstreamer_private_runtime",
                    CapabilityStatus.AVAILABLE_AFTER_INSTALL,
                    "Approved GStreamer private Preview runtime is not configured for this run",
                    ("preview_runtime=config_missing",),
                    (
                        "Install/configure the approved private GStreamer 1.28.x runtime and "
                        "rerun Doctor with --preview-runtime."
                    ),
                ),
            )

        try:
            status = self._backend.initialize()
        except (OSError, RuntimeError, ValueError) as exc:
            return (
                EnvironmentCapabilityCheck(
                    ProductCapability.PREVIEW_PLAYBACK,
                    "gstreamer_private_runtime",
                    CapabilityStatus.UNAVAILABLE,
                    "Production Preview runtime probe raised a bounded initialization failure",
                    (f"preview_probe_error={type(exc).__name__}",),
                    "Repair the approved private Preview runtime and rerun Doctor.",
                ),
            )

        evidence = [f"backend={status.backend}", f"state={status.state.value}"]
        if status.runtime_version is not None:
            evidence.append(f"runtime_version={status.runtime_version}")
        evidence.extend(f"diagnostic={item.code.value}" for item in status.diagnostics)

        try:
            if status.state is PreviewPlaybackState.READY and status.is_usable:
                return (
                    EnvironmentCapabilityCheck(
                        ProductCapability.PREVIEW_PLAYBACK,
                        "gstreamer_private_runtime",
                        CapabilityStatus.READY,
                        "Production Preview runtime initialized successfully",
                        tuple(evidence),
                    ),
                )
            install_codes = {
                PreviewDiagnosticCode.RUNTIME_NOT_FOUND,
                PreviewDiagnosticCode.RUNTIME_INVALID,
                PreviewDiagnosticCode.LIBRARY_LOAD_FAILED,
            }
            install_required = any(item.code in install_codes for item in status.diagnostics)
            return (
                EnvironmentCapabilityCheck(
                    ProductCapability.PREVIEW_PLAYBACK,
                    "gstreamer_private_runtime",
                    (
                        CapabilityStatus.AVAILABLE_AFTER_INSTALL
                        if install_required
                        else CapabilityStatus.UNAVAILABLE
                    ),
                    "Production Preview runtime did not initialize as ready",
                    tuple(evidence),
                    "Repair the approved private GStreamer runtime and rerun Doctor.",
                ),
            )
        finally:
            if status.state is PreviewPlaybackState.READY:
                self._backend.release()

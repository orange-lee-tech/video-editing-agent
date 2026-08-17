from __future__ import annotations

import subprocess
from pathlib import Path

from video_editing_agent.application.ports.environment_doctor import (
    CapabilityStatus,
    EnvironmentCapabilityCheck,
    ProductCapability,
)
from video_editing_agent.application.ports.preview import (
    PreviewDecodeMode,
    PreviewPlaybackState,
    PreviewStatus,
)
from video_editing_agent.application.use_cases.environment_doctor import EnvironmentDoctor
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.providers.environment.probes import (
    ConfiguredSecretProbe,
    FFmpegToolchainProbe,
    PreviewRuntimeProbe,
    SystemHostProbe,
    VisualProviderConfigurationProbe,
)


class FakeProbe:
    def __init__(self, *checks: EnvironmentCapabilityCheck) -> None:
        self._checks = checks

    def probe(self) -> tuple[EnvironmentCapabilityCheck, ...]:
        return self._checks


class FakePreviewBackend:
    def __init__(self, status: PreviewStatus) -> None:
        self._status = status
        self.release_calls = 0

    def initialize(self) -> PreviewStatus:
        return self._status

    def load(self, path: Path) -> PreviewStatus:
        raise AssertionError("Doctor must not load media")

    def play(self) -> PreviewStatus:
        raise AssertionError("Doctor must not play media")

    def pause(self) -> PreviewStatus:
        raise AssertionError("Doctor must not pause media")

    def seek(self, position: MediaTime) -> PreviewStatus:
        raise AssertionError("Doctor must not seek media")

    def status(self) -> PreviewStatus:
        return self._status

    def stop(self) -> PreviewStatus:
        raise AssertionError("Doctor must not stop media")

    def release(self) -> PreviewStatus:
        self.release_calls += 1
        return PreviewStatus(
            self._status.backend,
            PreviewPlaybackState.RELEASED,
            self._status.decode_mode,
        )


def _completed(
    arguments: tuple[str, ...], return_code: int = 0, stdout: str = ""
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(arguments, return_code, stdout=stdout, stderr="")


def test_windows_python_312_host_is_ready() -> None:
    probe = SystemHostProbe(
        system_name=lambda: "Windows",
        architecture=lambda: "AMD64",
        python_version=lambda: (3, 12, 10),
        free_disk_bytes=lambda: 128 * 1024**3,
    )

    check = probe.probe()[0]

    assert check.capability is ProductCapability.HOST_RUNTIME
    assert check.status is CapabilityStatus.READY
    assert "python=3.12.10" in check.evidence
    assert "free_disk_gib=128.0" in check.evidence


def test_non_windows_host_is_reported_without_crashing() -> None:
    check = SystemHostProbe(
        system_name=lambda: "Linux",
        python_version=lambda: (3, 12, 10),
    ).probe()[0]

    assert check.status is CapabilityStatus.UNAVAILABLE
    assert "Windows" in check.summary


def test_old_python_on_windows_is_install_required() -> None:
    check = SystemHostProbe(
        system_name=lambda: "Windows",
        python_version=lambda: (3, 11, 9),
    ).probe()[0]

    assert check.status is CapabilityStatus.AVAILABLE_AFTER_INSTALL
    assert "3.12" in check.summary


def test_ffmpeg_missing_is_install_required() -> None:
    probe = FFmpegToolchainProbe(locator=lambda name: None)

    check = probe.probe()[0]

    assert check.status is CapabilityStatus.AVAILABLE_AFTER_INSTALL
    assert set(check.evidence) == {"missing=ffmpeg", "missing=ffprobe"}


def test_ffmpeg_presence_without_execution_is_not_ready() -> None:
    def runner(arguments: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
        return _completed(arguments, return_code=1)

    probe = FFmpegToolchainProbe(locator=lambda name: f"C:/{name}.exe", runner=runner)

    check = probe.probe()[0]

    assert check.status is CapabilityStatus.UNAVAILABLE
    assert check.evidence == ("ffmpeg_exit=1",)


def test_ffmpeg_and_ffprobe_execution_success_is_ready() -> None:
    def runner(arguments: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
        tool = Path(arguments[0]).stem
        return _completed(arguments, stdout=f"{tool} version 8.1\n")

    probe = FFmpegToolchainProbe(locator=lambda name: f"C:/{name}.exe", runner=runner)

    check = probe.probe()[0]

    assert check.status is CapabilityStatus.READY
    assert "ffmpeg_probe=ready" in check.evidence
    assert "ffprobe_probe=ready" in check.evidence


def test_preview_unconfigured_is_typed_without_backend_switch() -> None:
    check = PreviewRuntimeProbe(None).probe()[0]

    assert check.capability is ProductCapability.PREVIEW_PLAYBACK
    assert check.status is CapabilityStatus.AVAILABLE_AFTER_INSTALL
    assert check.component == "gstreamer_private_runtime"


def test_preview_ready_uses_production_backend_contract_and_releases() -> None:
    backend = FakePreviewBackend(
        PreviewStatus(
            "gstreamer",
            PreviewPlaybackState.READY,
            PreviewDecodeMode.AUTO,
            runtime_version="1.28.6.0",
        )
    )

    check = PreviewRuntimeProbe(backend).probe()[0]

    assert check.status is CapabilityStatus.READY
    assert "runtime_version=1.28.6.0" in check.evidence
    assert backend.release_calls == 1


def test_provider_secret_presence_never_echoes_value() -> None:
    sentinel = "SENTINEL-SECRET-DO-NOT-LEAK"
    doctor = EnvironmentDoctor(
        (
            ConfiguredSecretProbe(
                component="deepseek",
                environment_key="DEEPSEEK_API_KEY",
                capabilities=(
                    ProductCapability.PLANNING_CLOUD,
                    ProductCapability.EDITING_CLOUD_DIRECTOR,
                ),
                environment={"DEEPSEEK_API_KEY": sentinel},
            ),
        )
    )

    result = doctor.inspect()

    assert all(item.status is CapabilityStatus.READY for item in result.report.checks)
    assert sentinel not in result.repair_report
    assert sentinel not in repr(result.report.checks)
    assert all(item.evidence == ("credential=configured",) for item in result.report.checks)


def test_missing_deepseek_key_blocks_only_named_cloud_capabilities() -> None:
    checks = ConfiguredSecretProbe(
        component="deepseek",
        environment_key="DEEPSEEK_API_KEY",
        capabilities=(
            ProductCapability.PLANNING_CLOUD,
            ProductCapability.EDITING_CLOUD_DIRECTOR,
        ),
        environment={},
    ).probe()

    assert {item.capability for item in checks} == {
        ProductCapability.PLANNING_CLOUD,
        ProductCapability.EDITING_CLOUD_DIRECTOR,
    }
    assert all(item.status is CapabilityStatus.UNAVAILABLE for item in checks)


def test_visual_provider_alternatives_do_not_require_both_keys() -> None:
    gemini = VisualProviderConfigurationProbe({"GEMINI_API_KEY": "configured"}).probe()[0]
    openai = VisualProviderConfigurationProbe({"OPENAI_API_KEY": "configured"}).probe()[0]
    missing = VisualProviderConfigurationProbe({}).probe()[0]

    assert gemini.status is CapabilityStatus.READY
    assert gemini.evidence == ("configured_provider=gemini",)
    assert openai.status is CapabilityStatus.READY
    assert openai.evidence == ("configured_provider=openai",)
    assert missing.status is CapabilityStatus.UNAVAILABLE


def test_report_preserves_optional_hardware_block_without_global_environment_bool() -> None:
    ready = EnvironmentCapabilityCheck(
        ProductCapability.MEDIA_PROBE_RENDER,
        "ffmpeg_toolchain",
        CapabilityStatus.READY,
        "ready",
    )
    blocked = EnvironmentCapabilityCheck(
        ProductCapability.OPTIONAL_LOCAL_ACCELERATION,
        "gpu_acceleration",
        CapabilityStatus.HARDWARE_BLOCKED,
        "optional hardware acceleration unavailable",
    )

    result = EnvironmentDoctor((FakeProbe(ready, blocked),)).inspect()

    assert result.report.checks == (ready, blocked)
    assert result.report.for_capability(ProductCapability.MEDIA_PROBE_RENDER) == (ready,)
    assert not hasattr(result.report, "environment_ok")
    assert "hardware_blocked" in result.repair_report

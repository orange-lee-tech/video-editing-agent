from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

from video_editing_agent.adapters.bootstrap.capability_doctor import RuntimeManifestProbe
from video_editing_agent.adapters.bootstrap.package_validation import inspect_staged_package
from video_editing_agent.adapters.bootstrap.resource_locator import (
    ResourceRuntimeLocator,
    RuntimeLayout,
    default_runtime_locator,
)
from video_editing_agent.adapters.bootstrap.runtime_manifest import (
    load_runtime_manifest,
    parse_runtime_manifest,
)
from video_editing_agent.application.ports.environment_doctor import CapabilityStatus


def _component(**updates: object) -> dict[str, object]:
    value: dict[str, object] = {
        "id": "ffmpeg",
        "kind": "executable",
        "classification": "bundled-required",
        "capability": "media-probe-render",
        "version": "8.1",
        "location_policy": "install-relative",
        "provenance": "approved release source",
        "license_state": "reviewed",
        "inclusion": "include",
        "hash_policy": "build-generated",
        "path": "tools/ffmpeg.exe",
        "platform": "windows",
        "architecture": "x86_64",
        "absence_fatal": True,
    }
    value.update(updates)
    return value


def _payload(*components: dict[str, object]) -> dict[str, object]:
    return {
        "schema": "video-editing-agent/runtime-manifest/v1",
        "application_version": "0.1.0",
        "components": list(components or (_component(),)),
    }


def test_checked_in_runtime_bom_loads_and_covers_frozen_runtime_terrain() -> None:
    manifest = load_runtime_manifest(Path("resources/packaging/runtime-manifest.json"))
    assert manifest.component("application") is not None
    assert manifest.component("python-runtime") is not None
    assert manifest.component("tk-runtime-data") is not None
    assert manifest.component("ffmpeg") is not None
    assert manifest.component("transnet-weights") is not None
    speech = manifest.component("speech-model")
    assert speech is not None and "ebe41f70" in speech.version
    assert manifest.component("cloud-providers") is not None
    assert manifest.component("development-tooling") is not None
    for component_id in (
        "ffmpeg",
        "ffprobe",
        "transnet-runtime",
        "transnet-weights",
    ):
        component = manifest.component(component_id)
        assert component is not None
        assert component.inclusion.value == "include"
        assert component.license_state.value == "reviewed"
    for component_id in ("speech-runtime", "speech-model"):
        component = manifest.component(component_id)
        assert component is not None
        assert component.inclusion.value == "exclude"
        assert component.license_state.value == "reviewed"


@pytest.mark.parametrize("path", ("../escape.exe", "/absolute/tool", "C:/tool.exe", "a\\b"))
def test_manifest_rejects_unbounded_release_paths(path: str) -> None:
    with pytest.raises(ValueError, match="component path"):
        parse_runtime_manifest(_payload(_component(path=path)))


def test_manifest_rejects_unknown_schema_keys_duplicates_and_developer_release_path() -> None:
    unknown = _payload()
    unknown["secret"] = "never accepted"
    with pytest.raises(ValueError, match="keys must be exactly"):
        parse_runtime_manifest(unknown)
    with pytest.raises(ValueError, match="unique"):
        parse_runtime_manifest(_payload(_component(), _component()))
    with pytest.raises(ValueError, match="developer-only"):
        parse_runtime_manifest(_payload(_component(path=".tools/ffmpeg.exe")))


def test_distributable_validation_requires_reviewed_license_and_hash_when_exact() -> None:
    with pytest.raises(ValueError, match="license"):
        parse_runtime_manifest(_payload(_component(license_state="external-review-required")))
    with pytest.raises(ValueError, match="sha256"):
        parse_runtime_manifest(_payload(_component(hash_policy="exact")))


def test_frozen_locator_never_uses_path_or_repository_fallback(tmp_path: Path) -> None:
    manifest = parse_runtime_manifest(_payload())
    locator = ResourceRuntimeLocator(
        RuntimeLayout.FROZEN,
        tmp_path / "install",
        manifest,
        repository_root=tmp_path / "repo",
        path_locator=lambda _name: "C:/ambient/ffmpeg.exe",
    )
    assert locator.executable("ffmpeg", development_name="ffmpeg") is None


def test_development_locator_prefers_manifest_then_allows_path(tmp_path: Path) -> None:
    manifest = parse_runtime_manifest(_payload())
    tool = tmp_path / "install/tools/ffmpeg.exe"
    tool.parent.mkdir(parents=True)
    tool.write_bytes(b"packaged")
    locator = ResourceRuntimeLocator(
        RuntimeLayout.DEVELOPMENT,
        tmp_path / "install",
        manifest,
        path_locator=lambda _name: "C:/ambient/ffmpeg.exe",
    )
    assert locator.executable("ffmpeg", development_name="ffmpeg") == str(tool.resolve())
    tool.unlink()
    assert locator.executable("ffmpeg", development_name="ffmpeg") == "C:/ambient/ffmpeg.exe"


def test_default_locator_reads_repository_manifest_without_cwd_authority(tmp_path: Path) -> None:
    locator = default_runtime_locator(repository_root=Path.cwd(), managed_root=tmp_path)
    assert locator.layout is RuntimeLayout.DEVELOPMENT
    assert locator.manifest.component("speech-model") is not None


def test_managed_python_runtime_activation_is_explicit_and_bounded(tmp_path: Path) -> None:
    manifest = parse_runtime_manifest(
        _payload(
            _component(
                id="runtime",
                kind="runtime",
                classification="managed-optional",
                inclusion="external",
                path="runtimes/component",
                license_state="external-review-required",
                hash_policy="not-applicable",
                absence_fatal=False,
            )
        )
    )
    runtime = tmp_path / "managed/runtimes/component"
    runtime.mkdir(parents=True)
    locator = ResourceRuntimeLocator(
        RuntimeLayout.FROZEN, tmp_path / "install", manifest, managed_root=tmp_path / "managed"
    )
    try:
        assert locator.activate_managed_python_runtime("runtime")
        assert sys.path[0] == str(runtime.resolve())
        assert not locator.activate_managed_python_runtime("unknown")
    finally:
        if str(runtime.resolve()) in sys.path:
            sys.path.remove(str(runtime.resolve()))


def test_manifest_probe_reports_required_optional_and_integrity(tmp_path: Path) -> None:
    present = tmp_path / "resources/present.bin"
    present.parent.mkdir(parents=True)
    present.write_bytes(b"known")
    exact = hashlib.sha256(b"known").hexdigest()
    manifest = parse_runtime_manifest(
        _payload(
            _component(
                id="present",
                kind="resource",
                path="resources/present.bin",
                hash_policy="exact",
                sha256=exact,
            ),
            _component(id="required", path="missing.exe"),
            _component(
                id="optional",
                classification="managed-optional",
                inclusion="external",
                path="optional/tool.exe",
                license_state="external-review-required",
                hash_policy="not-applicable",
                absence_fatal=False,
            ),
        )
    )
    checks = RuntimeManifestProbe(
        ResourceRuntimeLocator(RuntimeLayout.FROZEN, tmp_path, manifest, managed_root=tmp_path)
    ).probe()
    assert tuple(item.status for item in checks) == (
        CapabilityStatus.READY,
        CapabilityStatus.UNAVAILABLE,
        CapabilityStatus.AVAILABLE_AFTER_INSTALL,
    )


def test_manifest_probe_fails_closed_on_hash_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "runtime/component.bin"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"tampered")
    manifest = parse_runtime_manifest(
        _payload(
            _component(
                id="component",
                kind="runtime",
                path="runtime/component.bin",
                hash_policy="exact",
                sha256="0" * 64,
            )
        )
    )
    check = RuntimeManifestProbe(
        ResourceRuntimeLocator(RuntimeLayout.FROZEN, tmp_path, manifest)
    ).probe()[0]
    assert check.status is CapabilityStatus.UNAVAILABLE
    assert "sha256_match=false" in check.evidence


def test_static_package_inspection_rejects_forbidden_content_and_missing_required(
    tmp_path: Path,
) -> None:
    manifest = parse_runtime_manifest(_payload(_component(path="VideoEditingAgent.exe")))
    stage = tmp_path / "stage"
    stage.mkdir()
    with pytest.raises(ValueError, match="missing"):
        inspect_staged_package(stage, manifest)
    (stage / "VideoEditingAgent.exe").write_bytes(b"exe")
    forbidden = stage / ".private"
    forbidden.mkdir()
    (forbidden / "secret.txt").write_text("not a real secret", encoding="utf-8")
    with pytest.raises(ValueError, match="forbidden"):
        inspect_staged_package(stage, manifest)


def test_static_package_inspection_rejects_plaintext_provider_secret(tmp_path: Path) -> None:
    manifest = parse_runtime_manifest(_payload(_component(path="VideoEditingAgent.exe")))
    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / "VideoEditingAgent.exe").write_bytes(b"exe")
    (stage / "config.txt").write_text("OPENAI_API_KEY=abcdefghijklmnop", encoding="utf-8")
    with pytest.raises(ValueError, match="plaintext"):
        inspect_staged_package(stage, manifest)


def test_static_package_inspection_hashes_owned_runtime_tree_deterministically(
    tmp_path: Path,
) -> None:
    manifest = parse_runtime_manifest(
        _payload(_component(id="runtime", kind="runtime", path="runtimes/component"))
    )
    stage = tmp_path / "stage"
    runtime = stage / "runtimes/component"
    runtime.mkdir(parents=True)
    (runtime / "b.bin").write_bytes(b"second")
    (runtime / "a.bin").write_bytes(b"first")
    first = inspect_staged_package(stage, manifest).component_hashes["runtime"]
    second = inspect_staged_package(stage, manifest).component_hashes["runtime"]
    assert first == second
    (runtime / "a.bin").write_bytes(b"changed")
    assert inspect_staged_package(stage, manifest).component_hashes["runtime"] != first


def test_guided_installer_avoids_preinit_app_constant_and_excluded_directory_skeletons() -> None:
    installer = Path("packaging/windows/VideoEditingAgent.iss").read_text(encoding="utf-8")

    assert "DisableWelcomePage=no" in installer
    assert "ExpandConstant('{app}" not in installer
    assert "CurInstallProgressChanged" in installer
    assert "InstallEtaRemaining" in installer

    core_source = next(
        line
        for line in installer.splitlines()
        if line.startswith('Source: "{#StageRoot}\\*";') and "Components: core;" in line
    )
    assert "recursesubdirs" in core_source
    assert "createallsubdirs" not in core_source


def test_packaging_separates_windowed_gui_from_console_diagnostics_cli() -> None:
    spec = Path("packaging/video_editing_agent.spec").read_text(encoding="utf-8")
    package_script = Path("scripts/package_windows.ps1").read_text(encoding="utf-8")

    assert 'name="VideoEditingAgent"' in spec
    assert 'name="VideoEditingAgent-cli"' in spec
    assert "console=False" in spec
    assert "console=True" in spec
    assert "VideoEditingAgent-cli.exe" in package_script
    assert "$CliExecutable doctor" in package_script
    assert "$CliExecutable runtime-probe" in package_script


def test_packaged_gui_smoke_waits_for_windowed_process_completion() -> None:
    package_script = Path("scripts/package_windows.ps1").read_text(encoding="utf-8")

    assert "Start-Process -FilePath $GuiExecutable -Wait -PassThru" in package_script
    assert "Remove-Item -LiteralPath $Workspace -Recurse -Force" in package_script

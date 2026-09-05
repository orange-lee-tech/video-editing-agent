from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath

import pytest

from video_editing_agent.adapters.product import component_update
from video_editing_agent.adapters.product.component_update import (
    PATCH_SCHEMA,
    apply_component_archives,
    plan_component_update,
)
from video_editing_agent.adapters.product.update_check import (
    UpdateComponent,
    UpdateManifest,
)
from video_editing_agent.adapters.product.update_state import (
    InstalledComponentState,
    InstalledUpdateState,
    UpdateFileRecord,
    save_update_state,
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _record(path: str, data: bytes) -> UpdateFileRecord:
    return UpdateFileRecord(PurePosixPath(path), _sha(data), len(data))


def _state() -> InstalledUpdateState:
    return InstalledUpdateState(
        application_version="1.0.0",
        components=(
            InstalledComponentState(
                "app-core",
                "1.0.0",
                (
                    _record("VideoEditingAgent.exe", b"old-exe"),
                    _record("_internal/app.txt", b"old-app"),
                ),
            ),
            InstalledComponentState(
                "media-runtime",
                "ffmpeg-1",
                (_record("_internal/tools/ffmpeg.exe", b"ffmpeg"),),
            ),
            InstalledComponentState(
                "transnet-runtime",
                "transnet-1",
                (_record("_internal/runtimes/transnet/model.bin", b"model"),),
            ),
        ),
    )


def _manifest(component: UpdateComponent) -> UpdateManifest:
    return UpdateManifest(
        version="1.0.1",
        published_at="2026-08-31T00:00:00Z",
        release_notes_url="https://example.invalid/notes",
        download_url="https://example.invalid/setup.exe",
        installer_sha256="a" * 64,
        mandatory=False,
        components=(
            component,
            UpdateComponent(
                "media-runtime",
                "ffmpeg-1",
                "https://example.invalid/media.zip",
                "b" * 64,
                100,
            ),
            UpdateComponent(
                "transnet-runtime",
                "transnet-1",
                "https://example.invalid/transnet.zip",
                "c" * 64,
                100,
            ),
        ),
    )


def _write_patch(
    path: Path,
    *,
    component_id: str,
    version: str,
    files: dict[str, bytes],
) -> str:
    records = [
        {
            "path": relative,
            "sha256": _sha(data),
            "size_bytes": len(data),
        }
        for relative, data in files.items()
    ]
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as package:
        package.writestr(
            "patch.json",
            json.dumps(
                {
                    "schema": PATCH_SCHEMA,
                    "component_id": component_id,
                    "version": version,
                    "layout_version": 1,
                    "files": records,
                }
            ),
        )
        for relative, data in files.items():
            package.writestr(f"payload/{relative}", data)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_patch_plan_downloads_only_changed_component() -> None:
    remote = UpdateComponent(
        "app-core",
        "1.0.1",
        "https://example.invalid/app.zip",
        "a" * 64,
        12_000_000,
    )

    plan = plan_component_update(_state(), _manifest(remote))

    assert plan.patch_available is True
    assert tuple(item.component_id for item in plan.components) == ("app-core",)
    assert plan.total_size_bytes == 12_000_000


def test_patch_plan_falls_back_to_full_installer_without_installed_state() -> None:
    remote = UpdateComponent(
        "app-core",
        "1.0.1",
        "https://example.invalid/app.zip",
        "a" * 64,
        100,
    )

    plan = plan_component_update(None, _manifest(remote))

    assert plan.full_installer_required is True
    assert plan.patch_available is False


def test_component_patch_replaces_and_deletes_owned_files(tmp_path: Path) -> None:
    install = tmp_path / "install"
    (install / "_internal").mkdir(parents=True)
    (install / "VideoEditingAgent.exe").write_bytes(b"old-exe")
    (install / "_internal/app.txt").write_bytes(b"old-app")
    state_path = install / "_internal/resources/packaging/update-state.json"
    save_update_state(state_path, _state())

    archive = tmp_path / "app.zip"
    archive_sha = _write_patch(
        archive,
        component_id="app-core",
        version="1.0.1",
        files={"VideoEditingAgent.exe": b"new-exe"},
    )
    remote = UpdateComponent(
        "app-core",
        "1.0.1",
        "https://example.invalid/app.zip",
        archive_sha,
        archive.stat().st_size,
    )
    manifest = _manifest(remote)

    updated = apply_component_archives(
        install_root=install,
        state_path=state_path,
        target_application_version="1.0.1",
        manifest=manifest,
        archives=((remote, archive),),
    )

    assert (install / "VideoEditingAgent.exe").read_bytes() == b"new-exe"
    assert not (install / "_internal/app.txt").exists()
    assert updated.application_version == "1.0.1"
    assert updated.component("app-core") is not None
    assert updated.component("app-core").version == "1.0.1"  # type: ignore[union-attr]


def test_component_patch_rolls_back_after_partial_replace_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install = tmp_path / "install"
    (install / "_internal").mkdir(parents=True)
    (install / "VideoEditingAgent.exe").write_bytes(b"old-exe")
    (install / "_internal/app.txt").write_bytes(b"old-app")
    state_path = install / "_internal/resources/packaging/update-state.json"
    save_update_state(state_path, _state())

    archive = tmp_path / "app.zip"
    archive_sha = _write_patch(
        archive,
        component_id="app-core",
        version="1.0.1",
        files={
            "VideoEditingAgent.exe": b"new-exe",
            "_internal/app.txt": b"new-app",
        },
    )
    remote = UpdateComponent(
        "app-core",
        "1.0.1",
        "https://example.invalid/app.zip",
        archive_sha,
        archive.stat().st_size,
    )
    real_replace = component_update.os.replace
    replacements = 0

    def fail_second_replace(source: Path, target: Path) -> None:
        nonlocal replacements
        if str(source).endswith(".update-new"):
            replacements += 1
            if replacements == 2:
                raise OSError("simulated replacement failure")
        real_replace(source, target)

    monkeypatch.setattr(component_update.os, "replace", fail_second_replace)

    with pytest.raises(OSError, match="simulated replacement failure"):
        apply_component_archives(
            install_root=install,
            state_path=state_path,
            target_application_version="1.0.1",
            manifest=_manifest(remote),
            archives=((remote, archive),),
        )

    assert (install / "VideoEditingAgent.exe").read_bytes() == b"old-exe"
    assert (install / "_internal/app.txt").read_bytes() == b"old-app"


class _RejectProductExe:
    def publisher_of(self, path: Path) -> str | None:
        del path
        return None


def test_component_patch_rejects_unsigned_product_exe_and_rolls_back(tmp_path: Path) -> None:
    install = tmp_path / "install"
    (install / "_internal").mkdir(parents=True)
    (install / "VideoEditingAgent.exe").write_bytes(b"MZ-old")
    (install / "_internal/app.txt").write_bytes(b"old-app")
    state_path = install / "_internal/resources/packaging/update-state.json"
    save_update_state(state_path, _state())

    archive = tmp_path / "app.zip"
    archive_sha = _write_patch(
        archive,
        component_id="app-core",
        version="1.0.1",
        files={"VideoEditingAgent.exe": b"MZ-new"},
    )
    remote = UpdateComponent(
        "app-core",
        "1.0.1",
        "https://example.invalid/app.zip",
        archive_sha,
        archive.stat().st_size,
    )

    with pytest.raises(ValueError, match="Authenticode-signed"):
        apply_component_archives(
            install_root=install,
            state_path=state_path,
            target_application_version="1.0.1",
            manifest=_manifest(remote),
            archives=((remote, archive),),
            trust=_RejectProductExe(),
        )

    assert (install / "VideoEditingAgent.exe").read_bytes() == b"MZ-old"
    assert (install / "_internal/app.txt").read_bytes() == b"old-app"

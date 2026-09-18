from __future__ import annotations

import hashlib
import json
import os
import shutil
import zipfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath

from video_editing_agent.adapters.product.update_check import UpdateComponent, UpdateManifest
from video_editing_agent.adapters.product.update_state import (
    UPDATE_LAYOUT_VERSION,
    UPDATER_PROTOCOL_VERSION,
    InstalledComponentState,
    InstalledUpdateState,
    UpdateFileRecord,
    load_update_state,
    save_update_state,
)
from video_editing_agent.adapters.product.update_trust import (
    ReplacementTrust,
    default_replacement_trust,
    enforce_replacement_trust,
)

PATCH_SCHEMA = "video-editing-agent/component-patch/v1"
_FORBIDDEN_PATCH_TARGETS = {
    "VideoEditingAgent-updater.exe",
    "_internal/resources/packaging/update-state.json",
}


@dataclass(frozen=True, slots=True)
class ComponentUpdatePlan:
    components: tuple[UpdateComponent, ...]
    total_size_bytes: int
    full_installer_required: bool = False
    reason: str | None = None

    @property
    def patch_available(self) -> bool:
        return bool(self.components) and not self.full_installer_required


@dataclass(frozen=True, slots=True)
class ComponentPatchManifest:
    component_id: str
    version: str
    layout_version: int
    files: tuple[UpdateFileRecord, ...]


def plan_component_update(
    installed: InstalledUpdateState | None,
    manifest: UpdateManifest,
) -> ComponentUpdatePlan:
    if installed is None:
        return ComponentUpdatePlan((), 0, True, "installed component state is unavailable")
    if not manifest.components:
        return ComponentUpdatePlan((), 0, True, "release does not publish component patches")
    if installed.layout_version != manifest.layout_version:
        return ComponentUpdatePlan((), 0, True, "component layout changed")
    if manifest.layout_version != UPDATE_LAYOUT_VERSION:
        return ComponentUpdatePlan((), 0, True, "updater does not support target layout")
    if manifest.minimum_updater_version > UPDATER_PROTOCOL_VERSION:
        return ComponentUpdatePlan((), 0, True, "release requires a newer updater")

    selected: list[UpdateComponent] = []
    for remote in manifest.components:
        local = installed.component(remote.component_id)
        if local is None:
            return ComponentUpdatePlan(
                (),
                0,
                True,
                f"installed state does not own component {remote.component_id}",
            )
        if local.version != remote.version:
            selected.append(remote)

    if not selected and installed.application_version != manifest.version:
        return ComponentUpdatePlan(
            (),
            0,
            True,
            "application version changed without a matching component patch",
        )
    return ComponentUpdatePlan(
        tuple(selected),
        sum(item.size_bytes for item in selected),
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_component_patch(
    archive: Path,
    *,
    expected: UpdateComponent,
    expected_layout_version: int,
) -> ComponentPatchManifest:
    if sha256_file(archive) != expected.sha256:
        raise ValueError(f"component archive SHA-256 mismatch: {expected.component_id}")
    try:
        with zipfile.ZipFile(archive) as package:
            try:
                root = json.loads(package.read("patch.json").decode("utf-8"))
            except (KeyError, UnicodeError, json.JSONDecodeError) as exc:
                raise ValueError("component patch.json is missing or invalid") from exc
            if not isinstance(root, dict) or root.get("schema") != PATCH_SCHEMA:
                raise ValueError("unsupported component patch schema")
            component_id = _required_string(root, "component_id")
            version = _required_string(root, "version")
            layout_version = _required_int(root, "layout_version")
            if component_id != expected.component_id or version != expected.version:
                raise ValueError("component patch identity does not match update manifest")
            if layout_version != expected_layout_version:
                raise ValueError("component patch layout version does not match release")

            raw_files = root.get("files")
            if not isinstance(raw_files, list):
                raise ValueError("component patch files must be a list")
            files: list[UpdateFileRecord] = []
            for raw_file in raw_files:
                if not isinstance(raw_file, dict):
                    raise ValueError("component patch file must be an object")
                record = UpdateFileRecord(
                    PurePosixPath(_required_string(raw_file, "path")),
                    _required_string(raw_file, "sha256"),
                    _required_int(raw_file, "size_bytes"),
                )
                if str(record.relative_path) in _FORBIDDEN_PATCH_TARGETS:
                    raise ValueError(
                        f"component patch targets protected updater state: {record.relative_path}"
                    )
                member_name = f"payload/{record.relative_path.as_posix()}"
                try:
                    info = package.getinfo(member_name)
                except KeyError as exc:
                    raise ValueError(
                        f"component payload is missing: {record.relative_path}"
                    ) from exc
                if info.file_size != record.size_bytes:
                    raise ValueError(f"component payload size mismatch: {record.relative_path}")
                digest = hashlib.sha256(package.read(member_name)).hexdigest()
                if digest != record.sha256:
                    raise ValueError(f"component payload SHA-256 mismatch: {record.relative_path}")
                files.append(record)
    except zipfile.BadZipFile as exc:
        raise ValueError("component patch archive is not a valid ZIP") from exc

    return ComponentPatchManifest(component_id, version, layout_version, tuple(files))


def apply_component_archives(
    *,
    install_root: Path,
    state_path: Path,
    target_application_version: str,
    manifest: UpdateManifest,
    archives: Sequence[tuple[UpdateComponent, Path]],
    progress: Callable[[str, int, int], None] | None = None,
    trust: ReplacementTrust | None = None,
) -> InstalledUpdateState:
    install_root = install_root.resolve()
    previous = load_update_state(state_path)
    if previous.layout_version != manifest.layout_version:
        raise ValueError("installed component layout does not match update release")

    backup_root = install_root / ".update-backup"
    if backup_root.exists():
        shutil.rmtree(backup_root)
    backup_root.mkdir(parents=True)
    original_existence: dict[str, bool] = {}
    touched_paths: set[str] = set()
    current = previous
    replacement_trust = trust if trust is not None else default_replacement_trust()

    try:
        for remote, archive in archives:
            patch = load_component_patch(
                archive,
                expected=remote,
                expected_layout_version=manifest.layout_version,
            )
            old_component = current.component(remote.component_id)
            if old_component is None:
                raise ValueError(f"installed state is missing component {remote.component_id}")
            new_paths = {str(item.relative_path): item for item in patch.files}
            old_paths = {str(item.relative_path): item for item in old_component.files}
            managed_paths = set(old_paths) | set(new_paths)

            with zipfile.ZipFile(archive) as package:
                total = max(len(patch.files), 1)
                for index, record in enumerate(patch.files, start=1):
                    relative = str(record.relative_path)
                    target = _bounded_target(install_root, record.relative_path)
                    _backup_once(
                        install_root,
                        backup_root,
                        target,
                        relative,
                        original_existence,
                    )
                    touched_paths.add(relative)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    temporary = target.with_name(target.name + ".update-new")
                    with package.open(f"payload/{record.relative_path.as_posix()}") as source:
                        with temporary.open("wb") as destination:
                            shutil.copyfileobj(source, destination)
                    if sha256_file(temporary) != record.sha256:
                        temporary.unlink(missing_ok=True)
                        raise ValueError(f"staged component file failed SHA-256: {relative}")
                    previous_publisher = (
                        replacement_trust.publisher_of(target) if target.is_file() else None
                    )
                    enforce_replacement_trust(
                        temporary,
                        destination=target,
                        previous_publisher=previous_publisher,
                        trust=replacement_trust,
                    )
                    os.replace(temporary, target)
                    if progress is not None:
                        progress(remote.component_id, index, total)

            for relative in sorted(managed_paths - set(new_paths)):
                target = _bounded_target(install_root, PurePosixPath(relative))
                _backup_once(
                    install_root,
                    backup_root,
                    target,
                    relative,
                    original_existence,
                )
                touched_paths.add(relative)
                target.unlink(missing_ok=True)

            replacement = InstalledComponentState(
                remote.component_id,
                remote.version,
                patch.files,
            )
            current = replace(
                current,
                components=tuple(
                    replacement if item.component_id == remote.component_id else item
                    for item in current.components
                ),
            )

        current = replace(current, application_version=target_application_version)
        save_update_state(state_path, current)
        shutil.rmtree(backup_root, ignore_errors=True)
        return current
    except Exception:
        _rollback(
            install_root=install_root,
            backup_root=backup_root,
            touched_paths=touched_paths,
            original_existence=original_existence,
        )
        save_update_state(state_path, previous)
        shutil.rmtree(backup_root, ignore_errors=True)
        raise


def _backup_once(
    install_root: Path,
    backup_root: Path,
    target: Path,
    relative: str,
    original_existence: dict[str, bool],
) -> None:
    if relative in original_existence:
        return
    existed = target.is_file()
    original_existence[relative] = existed
    if existed:
        backup = _bounded_target(backup_root, PurePosixPath(relative))
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, backup)


def _rollback(
    *,
    install_root: Path,
    backup_root: Path,
    touched_paths: set[str],
    original_existence: dict[str, bool],
) -> None:
    for relative in sorted(touched_paths, reverse=True):
        target = _bounded_target(install_root, PurePosixPath(relative))
        if original_existence.get(relative, False):
            backup = _bounded_target(backup_root, PurePosixPath(relative))
            if backup.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                temporary = target.with_name(target.name + ".rollback-new")
                shutil.copy2(backup, temporary)
                os.replace(temporary, target)
        else:
            target.unlink(missing_ok=True)


def _bounded_target(root: Path, relative: PurePosixPath) -> Path:
    candidate = (root / Path(*relative.parts)).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"update path escapes install root: {relative}") from exc
    return candidate


def _required_string(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"component patch {key} must be a non-empty string")
    return value.strip()


def _required_int(payload: dict[str, object], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"component patch {key} must be a non-negative integer")
    return value

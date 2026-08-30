from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

UPDATE_STATE_SCHEMA = "video-editing-agent/update-state/v1"
UPDATE_LAYOUT_VERSION = 1
UPDATER_PROTOCOL_VERSION = 1
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class UpdateFileRecord:
    relative_path: PurePosixPath
    sha256: str
    size_bytes: int

    def __post_init__(self) -> None:
        _validate_relative_path(self.relative_path)
        if _SHA256.fullmatch(self.sha256) is None:
            raise ValueError("update file sha256 must be 64 lowercase hex characters")
        if self.size_bytes < 0:
            raise ValueError("update file size must be >= 0")


@dataclass(frozen=True, slots=True)
class InstalledComponentState:
    component_id: str
    version: str
    files: tuple[UpdateFileRecord, ...]

    def __post_init__(self) -> None:
        if not self.component_id.strip() or not self.version.strip():
            raise ValueError("component id and version must not be blank")
        paths = tuple(str(item.relative_path) for item in self.files)
        if len(paths) != len(set(paths)):
            raise ValueError("component file paths must be unique")


@dataclass(frozen=True, slots=True)
class InstalledUpdateState:
    application_version: str
    components: tuple[InstalledComponentState, ...]
    layout_version: int = UPDATE_LAYOUT_VERSION
    updater_version: int = UPDATER_PROTOCOL_VERSION
    schema: str = UPDATE_STATE_SCHEMA

    def __post_init__(self) -> None:
        if self.schema != UPDATE_STATE_SCHEMA:
            raise ValueError("unsupported update-state schema")
        if self.layout_version < 1 or self.updater_version < 1:
            raise ValueError("update-state versions must be >= 1")
        if not self.application_version.strip():
            raise ValueError("application version must not be blank")
        ids = tuple(item.component_id for item in self.components)
        if len(ids) != len(set(ids)):
            raise ValueError("installed component ids must be unique")

    def component(self, component_id: str) -> InstalledComponentState | None:
        return next((item for item in self.components if item.component_id == component_id), None)


def default_update_state_path(install_root: Path) -> Path:
    return install_root / "_internal" / "resources" / "packaging" / "update-state.json"


def load_update_state(path: Path) -> InstalledUpdateState:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"update state could not be loaded: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("update-state root must be an object")
    if payload.get("schema") != UPDATE_STATE_SCHEMA:
        raise ValueError("unsupported update-state schema")
    components = payload.get("components")
    if not isinstance(components, list):
        raise ValueError("update-state components must be a list")
    parsed_components: list[InstalledComponentState] = []
    for raw_component in components:
        if not isinstance(raw_component, dict):
            raise ValueError("update-state component must be an object")
        raw_files = raw_component.get("files")
        if not isinstance(raw_files, list):
            raise ValueError("update-state component files must be a list")
        files: list[UpdateFileRecord] = []
        for raw_file in raw_files:
            if not isinstance(raw_file, dict):
                raise ValueError("update-state file must be an object")
            files.append(
                UpdateFileRecord(
                    PurePosixPath(_string(raw_file, "path")),
                    _string(raw_file, "sha256"),
                    _integer(raw_file, "size_bytes"),
                )
            )
        parsed_components.append(
            InstalledComponentState(
                _string(raw_component, "id"),
                _string(raw_component, "version"),
                tuple(files),
            )
        )
    return InstalledUpdateState(
        application_version=_string(payload, "application_version"),
        layout_version=_integer(payload, "layout_version"),
        updater_version=_integer(payload, "updater_version"),
        components=tuple(parsed_components),
    )


def save_update_state(path: Path, state: InstalledUpdateState) -> None:
    payload = {
        "schema": state.schema,
        "application_version": state.application_version,
        "layout_version": state.layout_version,
        "updater_version": state.updater_version,
        "components": [
            {
                "id": component.component_id,
                "version": component.version,
                "files": [
                    {
                        "path": str(item.relative_path),
                        "sha256": item.sha256,
                        "size_bytes": item.size_bytes,
                    }
                    for item in component.files
                ],
            }
            for component in state.components
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _validate_relative_path(path: PurePosixPath) -> None:
    value = str(path)
    if not value or value == "." or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe update path: {value!r}")
    if path.parts[0].casefold() in {".git", "build", "dist"}:
        raise ValueError(f"developer-only update path is forbidden: {value!r}")


def _string(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"update-state {key} must be a non-empty string")
    return value.strip()


def _integer(payload: dict[str, object], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"update-state {key} must be an integer")
    return value

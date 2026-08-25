from __future__ import annotations

import ctypes
import os
import shutil
import sys
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from video_editing_agent.adapters.bootstrap.runtime_manifest import (
    InclusionPolicy,
    RuntimeManifest,
    load_runtime_manifest,
)

_DLL_DIRECTORY_HANDLES: list[object] = []


class RuntimeLayout(StrEnum):
    DEVELOPMENT = "development"
    FROZEN = "frozen"


@dataclass(frozen=True, slots=True)
class ResourceRuntimeLocator:
    layout: RuntimeLayout
    install_root: Path
    manifest: RuntimeManifest
    repository_root: Path | None = None
    managed_root: Path | None = None
    path_locator: Callable[[str], str | None] = shutil.which

    def component_path(self, component_id: str) -> Path | None:
        component = self.manifest.component(component_id)
        if component is None:
            return None
        if component.relative_path is None:
            return None
        root = (
            self.managed_root
            if component.inclusion is InclusionPolicy.EXTERNAL and self.managed_root is not None
            else self.install_root
        ).resolve()
        candidate = (root / Path(*component.relative_path.parts)).resolve()
        if not candidate.is_relative_to(root):
            raise ValueError(f"runtime component escaped install root: {component_id}")
        return candidate

    def existing_component_path(self, component_id: str) -> Path | None:
        candidate = self.component_path(component_id)
        return candidate if candidate is not None and candidate.exists() else None

    def executable(self, component_id: str, *, development_name: str | None = None) -> str | None:
        packaged = self.existing_component_path(component_id)
        if packaged is not None:
            return str(packaged)
        if self.layout is RuntimeLayout.FROZEN or development_name is None:
            return None
        path_value = self.path_locator(development_name)
        if path_value is not None:
            return path_value
        if self.repository_root is None or development_name not in {"ffmpeg", "ffprobe"}:
            return None
        candidate = (
            self.repository_root
            / ".tools/ffmpeg-8.1/ffmpeg-8.1-full_build/bin"
            / f"{development_name}.exe"
        )
        return str(candidate) if candidate.is_file() else None

    def activate_managed_python_runtime(self, component_id: str) -> bool:
        if component_id != "python-stdlib-managed":
            self._activate_runtime_path("python-stdlib-managed")
        return self._activate_runtime_path(component_id)

    def _activate_runtime_path(self, component_id: str) -> bool:
        component = self.manifest.component(component_id)
        path = self.existing_component_path(component_id)
        if (
            component is None
            or component.inclusion not in {InclusionPolicy.EXTERNAL, InclusionPolicy.INCLUDE}
            or path is None
            or not path.is_dir()
        ):
            return False
        value = str(path)
        if value not in sys.path:
            sys.path.insert(0, value)
        if component_id == "python-stdlib-managed":
            ctypes_path = str(path / "ctypes")
            if ctypes_path not in ctypes.__path__:
                ctypes.__path__.append(ctypes_path)
        if hasattr(os, "add_dll_directory"):
            for candidate in (path, path / "torch/lib", path / "ctranslate2", path / "av.libs"):
                if candidate.is_dir():
                    _DLL_DIRECTORY_HANDLES.append(os.add_dll_directory(str(candidate)))
        return True


def default_runtime_locator(
    *,
    executable: Path | None = None,
    frozen: bool | None = None,
    repository_root: Path | None = None,
    managed_root: Path | None = None,
) -> ResourceRuntimeLocator:
    is_frozen = bool(getattr(sys, "frozen", False)) if frozen is None else frozen
    repo = Path(__file__).resolve().parents[4] if repository_root is None else repository_root
    candidates: tuple[Path, ...]
    if is_frozen:
        install_root = (Path(sys.executable) if executable is None else executable).resolve().parent
        candidates = (
            install_root / "resources/packaging/runtime-manifest.json",
            install_root / "_internal/resources/packaging/runtime-manifest.json",
        )
    else:
        install_root = repo
        candidates = (repo / "resources/packaging/runtime-manifest.json",)
    manifest_path = next((item for item in candidates if item.is_file()), None)
    if manifest_path is None:
        raise ValueError("product runtime manifest is missing from the expected resource layout")
    managed = (
        Path.home() / "AppData/Local/Video Editing Agent/Components"
        if managed_root is None
        else managed_root
    )
    return ResourceRuntimeLocator(
        RuntimeLayout.FROZEN if is_frozen else RuntimeLayout.DEVELOPMENT,
        install_root,
        load_runtime_manifest(manifest_path),
        repository_root=None if is_frozen else repo,
        managed_root=managed,
    )

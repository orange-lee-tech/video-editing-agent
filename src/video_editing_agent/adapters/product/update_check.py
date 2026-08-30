from __future__ import annotations

import json
import re
from dataclasses import dataclass
from urllib.request import Request, urlopen

from video_editing_agent.version import APP_VERSION

DEFAULT_UPDATE_MANIFEST_URL = (
    "https://orange-lee-tech.github.io/homepages/video-editing-agent/stable/latest.json"
)
_MAX_MANIFEST_BYTES = 128 * 1024
_COMPONENT_ID = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


@dataclass(frozen=True, slots=True)
class UpdateComponent:
    component_id: str
    version: str
    url: str
    sha256: str
    size_bytes: int

    def __post_init__(self) -> None:
        if _COMPONENT_ID.fullmatch(self.component_id) is None:
            raise ValueError("update component id is invalid")
        if not self.version.strip() or not self.url.strip():
            raise ValueError("update component version/url must not be blank")
        _validate_sha256(self.sha256)
        if self.size_bytes < 1:
            raise ValueError("update component size must be >= 1")


@dataclass(frozen=True, slots=True)
class UpdateManifest:
    version: str
    published_at: str
    release_notes_url: str
    download_url: str
    installer_sha256: str
    mandatory: bool
    layout_version: int = 1
    minimum_updater_version: int = 1
    components: tuple[UpdateComponent, ...] = ()

    def __post_init__(self) -> None:
        if self.layout_version < 1 or self.minimum_updater_version < 1:
            raise ValueError("update layout/updater versions must be >= 1")
        ids = tuple(item.component_id for item in self.components)
        if len(ids) != len(set(ids)):
            raise ValueError("update component ids must be unique")


@dataclass(frozen=True, slots=True)
class UpdateCheckResult:
    current_version: str
    manifest: UpdateManifest | None
    error: str | None = None

    @property
    def update_available(self) -> bool:
        return self.manifest is not None and _version_tuple(self.manifest.version) > _version_tuple(
            self.current_version
        )


def _version_tuple(value: str) -> tuple[int, int, int]:
    parts = value.strip().split(".")
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        raise ValueError("version must be semantic major.minor.patch")
    return int(parts[0]), int(parts[1]), int(parts[2])


def _non_empty_string(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"update manifest {key} must be a non-empty string")
    return value.strip()


def _integer(payload: dict[str, object], key: str, default: int) -> int:
    value = payload.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"update manifest {key} must be an integer >= 1")
    return value


def _validate_sha256(value: str) -> str:
    normalized = value.strip().lower()
    if len(normalized) != 64 or any(ch not in "0123456789abcdef" for ch in normalized):
        raise ValueError("update sha256 must be a SHA-256 hex digest")
    return normalized


def _parse_components(payload: dict[str, object]) -> tuple[UpdateComponent, ...]:
    raw = payload.get("components", [])
    if not isinstance(raw, list):
        raise ValueError("update manifest components must be a list")
    components: list[UpdateComponent] = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("update manifest component must be an object")
        size = item.get("size_bytes")
        if isinstance(size, bool) or not isinstance(size, int):
            raise ValueError("update component size_bytes must be an integer")
        components.append(
            UpdateComponent(
                component_id=_non_empty_string(item, "id"),
                version=_non_empty_string(item, "version"),
                url=_non_empty_string(item, "url"),
                sha256=_validate_sha256(_non_empty_string(item, "sha256")),
                size_bytes=size,
            )
        )
    return tuple(components)


def parse_update_manifest(content: str) -> UpdateManifest:
    root = json.loads(content)
    if not isinstance(root, dict):
        raise ValueError("update manifest root must be an object")
    mandatory = root.get("mandatory", False)
    if not isinstance(mandatory, bool):
        raise ValueError("update manifest mandatory must be a bool")
    version = _non_empty_string(root, "version")
    _version_tuple(version)
    sha256 = _validate_sha256(_non_empty_string(root, "installer_sha256"))
    return UpdateManifest(
        version=version,
        published_at=_non_empty_string(root, "published_at"),
        release_notes_url=_non_empty_string(root, "release_notes_url"),
        download_url=_non_empty_string(root, "download_url"),
        installer_sha256=sha256,
        mandatory=mandatory,
        layout_version=_integer(root, "layout_version", 1),
        minimum_updater_version=_integer(root, "minimum_updater_version", 1),
        components=_parse_components(root),
    )


def check_for_update(
    *,
    current_version: str = APP_VERSION,
    manifest_url: str = DEFAULT_UPDATE_MANIFEST_URL,
    timeout_seconds: float = 4.0,
) -> UpdateCheckResult:
    try:
        _version_tuple(current_version)
        request = Request(
            manifest_url,
            headers={"User-Agent": f"VideoEditingAgent/{current_version}"},
        )
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = response.read(_MAX_MANIFEST_BYTES + 1)
        if len(payload) > _MAX_MANIFEST_BYTES:
            raise ValueError("update manifest exceeds size limit")
        manifest = parse_update_manifest(payload.decode("utf-8"))
        return UpdateCheckResult(current_version, manifest)
    except Exception as exc:
        return UpdateCheckResult(current_version, None, f"{type(exc).__name__}: {exc}")

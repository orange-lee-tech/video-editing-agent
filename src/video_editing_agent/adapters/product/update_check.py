from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.request import Request, urlopen

from video_editing_agent.version import APP_VERSION

DEFAULT_UPDATE_MANIFEST_URL = (
    "https://orange-lee-tech.github.io/homepages/video-editing-agent/stable/latest.json"
)
_MAX_MANIFEST_BYTES = 64 * 1024


@dataclass(frozen=True, slots=True)
class UpdateManifest:
    version: str
    published_at: str
    release_notes_url: str
    download_url: str
    installer_sha256: str
    mandatory: bool


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


def parse_update_manifest(content: str) -> UpdateManifest:
    root = json.loads(content)
    if not isinstance(root, dict):
        raise ValueError("update manifest root must be an object")
    mandatory = root.get("mandatory", False)
    if not isinstance(mandatory, bool):
        raise ValueError("update manifest mandatory must be a bool")
    version = _non_empty_string(root, "version")
    _version_tuple(version)
    sha256 = _non_empty_string(root, "installer_sha256").lower()
    if len(sha256) != 64 or any(ch not in "0123456789abcdef" for ch in sha256):
        raise ValueError("update manifest installer_sha256 must be a SHA-256 hex digest")
    return UpdateManifest(
        version=version,
        published_at=_non_empty_string(root, "published_at"),
        release_notes_url=_non_empty_string(root, "release_notes_url"),
        download_url=_non_empty_string(root, "download_url"),
        installer_sha256=sha256,
        mandatory=mandatory,
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

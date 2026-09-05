from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from video_editing_agent.adapters.product import update_check, update_ed25519
from video_editing_agent.adapters.product.update_check import (
    UpdateCheckResult,
    check_for_update,
    parse_update_manifest,
)
from video_editing_agent.adapters.product.update_signature import signed_manifest_text
from video_editing_agent.adapters.product.update_url import UpdateOriginPolicy
from video_editing_agent.version import APP_VERSION

_TEST_ORIGIN = UpdateOriginPolicy(
    pages_host="example.invalid",
    pages_prefix="/",
    github_host="example.invalid",
    github_prefix="/",
)


def _unsigned_payload(version: str = "1.0.1") -> dict[str, object]:
    return {
        "version": version,
        "published_at": "2026-08-29T00:00:00Z",
        "release_notes_url": "https://example.invalid/notes",
        "download_url": "https://example.invalid/download",
        "installer_sha256": "a" * 64,
        "mandatory": False,
    }


def _signed_manifest(
    version: str = "1.0.1", extra: dict[str, object] | None = None
) -> tuple[str, bytes]:
    seed = update_ed25519.generate_seed()
    public = update_ed25519.public_key_from_seed(seed)
    payload = _unsigned_payload(version)
    if extra:
        payload.update(extra)
    return signed_manifest_text(payload, seed), public


def test_release_version_identity_is_1_0_0_and_packaging_mirrors_it() -> None:
    assert APP_VERSION == "1.0.0"

    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["version"] == APP_VERSION

    runtime_manifest = json.loads(
        Path("resources/packaging/runtime-manifest.json").read_text(encoding="utf-8")
    )
    assert runtime_manifest["application_version"] == APP_VERSION

    installer = Path("packaging/windows/VideoEditingAgent.iss").read_text(encoding="utf-8")
    match = re.search(r'#define AppVersion "([^"]+)"', installer)
    assert match is not None and match.group(1) == APP_VERSION

    workflow = Path(".github/workflows/windows-release-candidate.yml").read_text(encoding="utf-8")
    assert "steps.source.outputs.version" in workflow
    assert "VideoEditingAgent-Setup-0.1.0.exe" not in workflow

    desktop = Path("src/video_editing_agent/adapters/product/tkinter_app.py").read_text(
        encoding="utf-8"
    )
    assert "APP_VERSION" in desktop
    assert "check_updates" in desktop


def test_update_manifest_parses_and_reports_newer_version() -> None:
    text, public = _signed_manifest("1.0.1")
    manifest = parse_update_manifest(text, public_key=public, origin_policy=_TEST_ORIGIN)
    result = UpdateCheckResult("1.0.0", manifest)

    assert result.update_available is True
    assert manifest.installer_sha256 == "a" * 64
    assert manifest.mandatory is False


def test_update_check_is_fail_open_and_does_not_raise(monkeypatch) -> None:
    def fail(*_args, **_kwargs):
        raise OSError("offline")

    monkeypatch.setattr(update_check, "fetch_https_bytes", fail)

    result = check_for_update(
        current_version="1.0.0",
        manifest_url="https://example.invalid/stable/latest.json",
        origin_policy=_TEST_ORIGIN,
    )

    assert result.update_available is False
    assert result.manifest is None
    assert result.error is not None
    assert "offline" in result.error


def test_update_check_accepts_valid_public_manifest_without_credentials(monkeypatch) -> None:
    text, public = _signed_manifest("1.0.1")
    captured: dict[str, object] = {}

    def fake_fetch(url: str, **kwargs: object) -> bytes:
        captured["url"] = url
        captured["timeout"] = kwargs["timeout_seconds"]
        captured["user_agent"] = kwargs["user_agent"]
        return text.encode("utf-8")

    monkeypatch.setattr(update_check, "fetch_https_bytes", fake_fetch)

    result = check_for_update(
        current_version="1.0.0",
        timeout_seconds=1.5,
        manifest_url="https://example.invalid/stable/latest.json",
        public_key=public,
        origin_policy=_TEST_ORIGIN,
    )

    assert result.error is None
    assert result.update_available is True
    assert captured["timeout"] == 1.5
    assert "Authorization" not in str(captured["user_agent"])


def test_update_manifest_parses_component_patches() -> None:
    text, public = _signed_manifest(
        "1.0.1",
        extra={
            "layout_version": 1,
            "minimum_updater_version": 1,
            "components": [
                {
                    "id": "app-core",
                    "version": "1.0.1",
                    "url": "https://example.invalid/app-core.zip",
                    "sha256": "b" * 64,
                    "size_bytes": 123456,
                }
            ],
        },
    )

    manifest = parse_update_manifest(text, public_key=public, origin_policy=_TEST_ORIGIN)

    assert manifest.layout_version == 1
    assert manifest.minimum_updater_version == 1
    assert len(manifest.components) == 1
    assert manifest.components[0].component_id == "app-core"
    assert manifest.components[0].size_bytes == 123456


def test_installer_requires_bilingual_user_agreement_and_eta() -> None:
    installer = Path("packaging/windows/VideoEditingAgent.iss").read_text(encoding="utf-8")

    assert 'LicenseFile: "..\\..\\resources\\legal\\USER_AGREEMENT_en.txt"' in installer
    assert 'LicenseFile: "..\\..\\resources\\legal\\USER_AGREEMENT_zh-CN.txt"' in installer
    assert "CurInstallProgressChanged" in installer
    assert "InstallEtaRemaining" in installer
    assert Path("resources/legal/USER_AGREEMENT_en.txt").is_file()
    assert Path("resources/legal/USER_AGREEMENT_zh-CN.txt").is_file()

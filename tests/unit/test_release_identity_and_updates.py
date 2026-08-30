from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from video_editing_agent.adapters.product import update_check
from video_editing_agent.adapters.product.update_check import (
    UpdateCheckResult,
    check_for_update,
    parse_update_manifest,
)
from video_editing_agent.version import APP_VERSION


def _manifest(version: str = "0.1.5") -> str:
    return json.dumps(
        {
            "version": version,
            "published_at": "2026-08-29T00:00:00Z",
            "release_notes_url": "https://example.invalid/notes",
            "download_url": "https://example.invalid/download",
            "installer_sha256": "a" * 64,
            "mandatory": False,
        }
    )


def test_release_version_identity_is_0_1_4_and_packaging_mirrors_it() -> None:
    assert APP_VERSION == "0.1.4"

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
    manifest = parse_update_manifest(_manifest("0.1.5"))
    result = UpdateCheckResult("0.1.4", manifest)

    assert result.update_available is True
    assert manifest.installer_sha256 == "a" * 64
    assert manifest.mandatory is False


def test_update_check_is_fail_open_and_does_not_raise(monkeypatch) -> None:
    def fail(*_args, **_kwargs):
        raise OSError("offline")

    monkeypatch.setattr(update_check, "urlopen", fail)

    result = check_for_update(current_version="0.1.4")

    assert result.update_available is False
    assert result.manifest is None
    assert result.error is not None
    assert "offline" in result.error


def test_update_check_accepts_valid_public_manifest_without_credentials(monkeypatch) -> None:
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

        def read(self, _limit: int) -> bytes:
            return _manifest("0.1.4").encode("utf-8")

    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr(update_check, "urlopen", fake_urlopen)

    result = check_for_update(current_version="0.1.4", timeout_seconds=1.5)

    assert result.error is None
    assert result.update_available is True
    assert captured["timeout"] == 1.5
    assert captured["request"].get_header("Authorization") is None

from __future__ import annotations

import json
from pathlib import Path

import pytest

from video_editing_agent.adapters.product import update_check, update_ed25519
from video_editing_agent.adapters.product.component_update import apply_component_archives
from video_editing_agent.adapters.product.update_check import check_for_update, parse_update_manifest
from video_editing_agent.adapters.product.update_signature import (
    UPDATE_MANIFEST_PUBLIC_KEY,
    signed_manifest_text,
)
from video_editing_agent.adapters.product.update_trust import enforce_replacement_trust
from video_editing_agent.adapters.product.update_url import (
    UpdateOriginPolicy,
    assert_allowed_update_url,
)

TEST_ORIGIN = UpdateOriginPolicy(
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


def _signed_manifest(version: str = "1.0.1") -> tuple[str, bytes]:
    seed = update_ed25519.generate_seed()
    public = update_ed25519.public_key_from_seed(seed)
    return signed_manifest_text(_unsigned_payload(version), seed), public


def test_rfc8032_empty_message_vector() -> None:
    seed = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
    public = update_ed25519.public_key_from_seed(seed)
    assert public.hex() == "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
    update_ed25519.verify(public, b"", update_ed25519.sign(seed, b""))


def test_parse_update_manifest_requires_valid_signature() -> None:
    text, public = _signed_manifest("1.0.1")
    manifest = parse_update_manifest(text, public_key=public, origin_policy=TEST_ORIGIN)
    assert manifest.version == "1.0.1"
    with pytest.raises(ValueError, match="signature is missing"):
        parse_update_manifest(json.dumps(_unsigned_payload()), public_key=public)


def test_parse_update_manifest_rejects_wrong_key() -> None:
    text, _public = _signed_manifest("1.0.1")
    other = update_ed25519.public_key_from_seed(update_ed25519.generate_seed())
    with pytest.raises(ValueError, match="signature is invalid"):
        parse_update_manifest(text, public_key=other, origin_policy=TEST_ORIGIN)


def test_component_urls_must_be_https_release_assets() -> None:
    assert_allowed_update_url(
        "https://github.com/orange-lee-tech/video-editing-agent/releases/download/v1.0.1/app.zip",
        role="component",
    )
    with pytest.raises(ValueError, match="HTTPS"):
        assert_allowed_update_url("http://example.invalid/app.zip", role="component")
    with pytest.raises(ValueError, match="Release asset"):
        assert_allowed_update_url(
            "https://github.com/orange-lee-tech/video-editing-agent/archive/refs/heads/main.zip",
            role="component",
        )
    with pytest.raises(ValueError, match="allowed release origin"):
        assert_allowed_update_url("https://evil.example/payload.zip", role="component")


def test_production_public_key_is_configured() -> None:
    assert len(UPDATE_MANIFEST_PUBLIC_KEY) == 32
    assert UPDATE_MANIFEST_PUBLIC_KEY != bytes(32)


def test_check_for_update_rejects_unsigned_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        update_check,
        "fetch_https_bytes",
        lambda *_args, **_kwargs: json.dumps(_unsigned_payload()).encode("utf-8"),
    )
    result = check_for_update(
        current_version="1.0.0",
        manifest_url="https://example.invalid/stable/latest.json",
        origin_policy=TEST_ORIGIN,
        public_key=update_ed25519.public_key_from_seed(update_ed25519.generate_seed()),
    )
    assert result.manifest is None
    assert result.error is not None
    assert "signature" in result.error


def test_check_for_update_accepts_signed_allowlisted_manifest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    text, public = _signed_manifest("1.0.1")
    captured: dict[str, object] = {}

    def fake_fetch(url: str, **kwargs: object) -> bytes:
        captured["url"] = url
        captured["timeout"] = kwargs["timeout_seconds"]
        return text.encode("utf-8")

    monkeypatch.setattr(update_check, "fetch_https_bytes", fake_fetch)
    result = check_for_update(
        current_version="1.0.0",
        manifest_url="https://example.invalid/stable/latest.json",
        timeout_seconds=1.5,
        public_key=public,
        origin_policy=TEST_ORIGIN,
    )
    assert result.error is None
    assert result.update_available is True
    assert captured["timeout"] == 1.5


class _PublisherMap:
    def __init__(self, names: dict[str, str | None]) -> None:
        self._names = names

    def publisher_of(self, path: Path) -> str | None:
        return self._names.get(path.name)


def test_unsigned_product_exe_replacement_is_rejected(tmp_path: Path) -> None:
    staged = tmp_path / "VideoEditingAgent.exe.update-new"
    destination = tmp_path / "VideoEditingAgent.exe"
    staged.write_bytes(b"MZ-unsigned")
    with pytest.raises(ValueError, match="Authenticode-signed"):
        enforce_replacement_trust(
            staged,
            destination=destination,
            previous_publisher=None,
            trust=_PublisherMap({staged.name: None}),
        )


def test_product_exe_publisher_mismatch_is_rejected(tmp_path: Path) -> None:
    staged = tmp_path / "VideoEditingAgent.exe.update-new"
    destination = tmp_path / "VideoEditingAgent.exe"
    staged.write_bytes(b"MZ-signed")
    with pytest.raises(ValueError, match="does not match"):
        enforce_replacement_trust(
            staged,
            destination=destination,
            previous_publisher="Pyrsys B.V.",
            trust=_PublisherMap({staged.name: "Attacker Inc."}),
        )


def test_matching_publisher_is_accepted(tmp_path: Path) -> None:
    staged = tmp_path / "VideoEditingAgent.exe.update-new"
    destination = tmp_path / "VideoEditingAgent.exe"
    staged.write_bytes(b"MZ-signed")
    enforce_replacement_trust(
        staged,
        destination=destination,
        previous_publisher="Pyrsys B.V.",
        trust=_PublisherMap({staged.name: "Pyrsys B.V."}),
    )

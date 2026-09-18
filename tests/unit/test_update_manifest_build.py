from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.maintenance import build_update_channel_manifest as builder
from video_editing_agent.adapters.product import update_ed25519
from video_editing_agent.adapters.product.update_signature import verify_manifest_signature


def test_build_signed_update_channel_manifest_binds_release_assets(
    tmp_path: Path,
    monkeypatch,
) -> None:
    seed = update_ed25519.generate_seed()
    public = update_ed25519.public_key_from_seed(seed)
    monkeypatch.setattr(builder, "UPDATE_MANIFEST_PUBLIC_KEY", public)

    installer = tmp_path / "VideoEditingAgent-Setup-1.0.1.exe"
    installer.write_bytes(b"installer")
    component_root = tmp_path / "components"
    component_root.mkdir()
    archive = component_root / "VideoEditingAgent-Update-app-core-1.0.1.zip"
    archive.write_bytes(b"component")
    metadata = {
        "schema": "video-editing-agent/update-release-components/v1",
        "application_version": "1.0.1",
        "layout_version": 1,
        "minimum_updater_version": 2,
        "components": [
            {
                "id": "app-core",
                "version": "1.0.1",
                "filename": archive.name,
                "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                "size_bytes": archive.stat().st_size,
            }
        ],
    }
    metadata_path = tmp_path / "update-release-components.json"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    manifest = builder.build_signed_manifest(
        version="1.0.1",
        published_at="2026-09-15T00:00:00Z",
        installer=installer,
        component_metadata=metadata_path,
        component_root=component_root,
        repository_slug="orange-lee-tech/video-editing-agent",
        release_notes_url=(
            "https://orange-lee-tech.github.io/homepages/video-editing-agent/stable/1.0.1.html"
        ),
        seed=seed,
    )

    verify_manifest_signature(manifest, public_key=public)
    assert manifest["installer_sha256"] == hashlib.sha256(installer.read_bytes()).hexdigest()
    assert manifest["download_url"] == (
        "https://github.com/orange-lee-tech/video-editing-agent/releases/download/v1.0.1/"
        "VideoEditingAgent-Setup-1.0.1.exe"
    )
    assert manifest["components"] == [
        {
            "id": "app-core",
            "version": "1.0.1",
            "url": (
                "https://github.com/orange-lee-tech/video-editing-agent/releases/download/v1.0.1/"
                "VideoEditingAgent-Update-app-core-1.0.1.zip"
            ),
            "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "size_bytes": archive.stat().st_size,
        }
    ]

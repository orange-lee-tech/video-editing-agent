from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.storage.asset.repository_media import RepositoryLocalAssetMediaResolver


class StaticAssetRepository:
    def __init__(self, asset: Asset) -> None:
        self._asset = asset

    def load(self, asset_ref: EntityRevisionRef) -> Asset:
        actual_ref = EntityRevisionRef(self._asset.envelope.id, self._asset.envelope.revision)
        if asset_ref != actual_ref:
            raise KeyError(asset_ref)
        return self._asset

    def save(self, asset: Asset) -> None:
        self._asset = asset


def make_asset(storage_ref: str) -> Asset:
    now = datetime(2026, 8, 10, 9, 45, tzinfo=UTC)
    return Asset(
        envelope=EntityEnvelope(
            id="ast_media_resolver",
            revision=1,
            schema_version="0.1.1",
            status=EntityStatus.VALID,
            created_at=now,
            created_by="test",
        ),
        media_kind="video",
        origin="local",
        storage_ref=storage_ref,
        content_hash="sha256:" + "1" * 64,
        byte_size=1,
        provenance=AssetProvenance(origin_type="local"),
        imported_at=now,
        duration_ms=1_000,
    )


def test_repository_media_resolver_restores_local_file_uri_with_spaces(tmp_path: Path) -> None:
    media_path = tmp_path / "folder with spaces" / "clip with spaces.mp4"
    media_path.parent.mkdir()
    media_path.write_bytes(b"x")
    asset = make_asset(media_path.resolve().as_uri())
    asset_ref = EntityRevisionRef(asset.envelope.id, asset.envelope.revision)

    resolved = RepositoryLocalAssetMediaResolver(StaticAssetRepository(asset)).resolve_local(
        asset_ref
    )

    assert resolved.asset_ref == asset_ref
    assert resolved.path == media_path.resolve()


def test_repository_media_resolver_rejects_non_file_storage_ref() -> None:
    asset = make_asset("https://example.invalid/media.mp4")
    asset_ref = EntityRevisionRef(asset.envelope.id, asset.envelope.revision)

    with pytest.raises(ValueError, match="not local file media"):
        RepositoryLocalAssetMediaResolver(StaticAssetRepository(asset)).resolve_local(asset_ref)

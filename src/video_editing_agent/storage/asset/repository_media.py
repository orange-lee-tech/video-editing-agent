from __future__ import annotations

import pathlib
import urllib.parse
import urllib.request

from video_editing_agent.application.ports.asset_media import (
    AssetMediaResolver,
    ResolvedLocalAssetMedia,
)
from video_editing_agent.application.ports.asset_repository import AssetRepository
from video_editing_agent.domain.common.entity import EntityRevisionRef


class RepositoryLocalAssetMediaResolver(AssetMediaResolver):
    """Resolve exact persisted Asset revisions whose storage_ref is a local file URI."""

    def __init__(self, repository: AssetRepository) -> None:
        self._repository = repository

    def resolve_local(self, asset_ref: EntityRevisionRef) -> ResolvedLocalAssetMedia:
        asset = self._repository.load(asset_ref)
        actual_ref = EntityRevisionRef(asset.envelope.id, asset.envelope.revision)
        if actual_ref != asset_ref:
            raise RuntimeError(
                f"AssetRepository returned {actual_ref.entity_id}@{actual_ref.revision} "
                f"for requested {asset_ref.entity_id}@{asset_ref.revision}"
            )

        parsed = urllib.parse.urlsplit(asset.storage_ref)
        if parsed.scheme.lower() != "file":
            raise ValueError(
                f"Asset {asset_ref.entity_id}@{asset_ref.revision} is not local file media"
            )
        if parsed.query or parsed.fragment:
            raise ValueError("local Asset file URI must not contain query or fragment components")

        path_text = urllib.request.url2pathname(urllib.parse.unquote(parsed.path))
        if parsed.netloc and parsed.netloc.lower() != "localhost":
            path_text = f"//{parsed.netloc}{path_text}"
        path = pathlib.Path(path_text).expanduser().resolve(strict=True)
        if not path.is_file():
            raise ValueError(f"Asset storage_ref must resolve to a file: {path}")

        return ResolvedLocalAssetMedia(asset_ref=asset_ref, path=path)

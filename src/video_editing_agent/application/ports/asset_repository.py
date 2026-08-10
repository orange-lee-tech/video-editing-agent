from __future__ import annotations

from typing import Protocol

from video_editing_agent.domain.asset.model import Asset
from video_editing_agent.domain.common.entity import EntityRevisionRef


class AssetRepository(Protocol):
    """Persistence seam for exact revisioned Asset records; no semantic authority."""

    def load(self, asset_ref: EntityRevisionRef) -> Asset: ...

    def save(self, asset: Asset) -> None: ...

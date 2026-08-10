from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef


@dataclass(frozen=True, slots=True)
class ResolvedLocalAssetMedia:
    asset_ref: EntityRevisionRef
    path: pathlib.Path


class AssetMediaResolver(Protocol):
    """Resolve an exact Asset revision to local media without exposing storage layout."""

    def resolve_local(self, asset_ref: EntityRevisionRef) -> ResolvedLocalAssetMedia: ...

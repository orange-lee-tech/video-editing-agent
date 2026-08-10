from __future__ import annotations

import pathlib
from dataclasses import dataclass

from video_editing_agent.domain.asset.model import AssetProvenance


@dataclass(frozen=True, slots=True)
class LocalMediaSource:
    """Local-first MediaSource accepted by the first AssetIngest implementation."""

    path: pathlib.Path
    origin: str
    provenance: AssetProvenance

    def __post_init__(self) -> None:
        if not self.origin.strip():
            raise ValueError("origin must not be empty")
        if self.origin != self.provenance.origin_type:
            raise ValueError("origin must match provenance.origin_type")

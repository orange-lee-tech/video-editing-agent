from __future__ import annotations

import pathlib
from dataclasses import dataclass

from video_editing_agent.domain.asset.model import AssetProvenance
from video_editing_agent.domain.asset.policy import AssetUsageRole


@dataclass(frozen=True, slots=True)
class LocalMediaSource:
    """Local-first MediaSource with optional explicit v0.2 usage declaration."""

    path: pathlib.Path
    origin: str
    provenance: AssetProvenance
    usage_role: AssetUsageRole | None = None

    def __post_init__(self) -> None:
        if not self.origin.strip():
            raise ValueError("origin must not be empty")
        if self.origin != self.provenance.origin_type:
            raise ValueError("origin must match provenance.origin_type")

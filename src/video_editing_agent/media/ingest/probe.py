from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class MediaTechnicalMetadata:
    media_kind: str
    duration_ms: int | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    codec: str | None = None
    audio_channels: int | None = None
    sample_rate_hz: int | None = None

    def __post_init__(self) -> None:
        if not self.media_kind.strip():
            raise ValueError("media_kind must not be empty")


class MediaProbe(Protocol):
    def probe(self, path: pathlib.Path) -> MediaTechnicalMetadata: ...

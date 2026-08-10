from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from video_editing_agent.domain.common.entity import EntityEnvelope


@dataclass(frozen=True, slots=True)
class AssetProvenance:
    origin_type: str
    provider: str | None = None
    provider_asset_id: str | None = None
    source_page: str | None = None
    creator: str | None = None
    retrieved_at: datetime | None = None
    license_information: str | None = None
    attribution: str | None = None

    def __post_init__(self) -> None:
        if not self.origin_type.strip():
            raise ValueError("origin_type must not be empty")


@dataclass(frozen=True, slots=True)
class Asset:
    envelope: EntityEnvelope
    media_kind: str
    origin: str
    storage_ref: str
    content_hash: str
    byte_size: int
    provenance: AssetProvenance
    imported_at: datetime
    duration_ms: int | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    codec: str | None = None
    audio_channels: int | None = None
    sample_rate_hz: int | None = None
    user_labels: tuple[str, ...] = ()
    collection_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("media_kind", self.media_kind),
            ("origin", self.origin),
            ("storage_ref", self.storage_ref),
            ("content_hash", self.content_hash),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")

        if self.origin != self.provenance.origin_type:
            raise ValueError("origin must match provenance.origin_type")
        if isinstance(self.byte_size, bool) or not isinstance(self.byte_size, int):
            raise TypeError("byte_size must be an int")
        if self.byte_size < 0:
            raise ValueError("byte_size must be >= 0")

        for name, value in (
            ("duration_ms", self.duration_ms),
            ("width", self.width),
            ("height", self.height),
            ("audio_channels", self.audio_channels),
            ("sample_rate_hz", self.sample_rate_hz),
        ):
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an int or None")
            if value < 0:
                raise ValueError(f"{name} must be >= 0")

        if self.fps is not None:
            if isinstance(self.fps, bool) or not isinstance(self.fps, (int, float)):
                raise TypeError("fps must be a number or None")
            if float(self.fps) <= 0:
                raise ValueError("fps must be > 0")

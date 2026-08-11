from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from video_editing_agent.domain.asset.policy import AssetUsageRole, default_asset_usage_role
from video_editing_agent.domain.common.entity import EntityEnvelope
from video_editing_agent.domain.common.media_time import MediaTime


def _validate_optional_non_negative_int(name: str, value: int | None) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int or None")
    if value < 0:
        raise ValueError(f"{name} must be >= 0")


def _resolve_duration(
    *,
    duration: MediaTime | None,
    duration_ms: int | None,
) -> MediaTime | None:
    if duration is not None:
        if duration_ms is not None:
            raise ValueError("provide duration or legacy duration_ms, not both")
        resolved = duration
    elif duration_ms is not None:
        resolved = MediaTime.from_milliseconds(duration_ms)
    else:
        return None

    if resolved.as_fraction() < 0:
        raise ValueError("duration must be >= 0")
    return resolved


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


@dataclass(frozen=True, slots=True, init=False)
class Asset:
    envelope: EntityEnvelope
    media_kind: str
    origin: str
    usage_role: AssetUsageRole
    storage_ref: str
    content_hash: str
    byte_size: int
    provenance: AssetProvenance
    imported_at: datetime
    duration: MediaTime | None
    width: int | None
    height: int | None
    fps: float | None
    codec: str | None
    audio_channels: int | None
    sample_rate_hz: int | None
    user_labels: tuple[str, ...]
    collection_refs: tuple[str, ...]

    def __init__(
        self,
        envelope: EntityEnvelope,
        media_kind: str,
        origin: str,
        storage_ref: str,
        content_hash: str,
        byte_size: int,
        provenance: AssetProvenance,
        imported_at: datetime,
        duration_ms: int | None = None,
        width: int | None = None,
        height: int | None = None,
        fps: float | None = None,
        codec: str | None = None,
        audio_channels: int | None = None,
        sample_rate_hz: int | None = None,
        user_labels: tuple[str, ...] = (),
        collection_refs: tuple[str, ...] = (),
        *,
        duration: MediaTime | None = None,
        usage_role: AssetUsageRole | None = None,
    ) -> None:
        resolved_duration = _resolve_duration(duration=duration, duration_ms=duration_ms)
        resolved_usage_role = usage_role or default_asset_usage_role(
            media_kind=media_kind,
            origin=origin,
        )

        for name, value in (
            ("media_kind", media_kind),
            ("origin", origin),
            ("storage_ref", storage_ref),
            ("content_hash", content_hash),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")

        if origin != provenance.origin_type:
            raise ValueError("origin must match provenance.origin_type")
        if isinstance(byte_size, bool) or not isinstance(byte_size, int):
            raise TypeError("byte_size must be an int")
        if byte_size < 0:
            raise ValueError("byte_size must be >= 0")

        _validate_optional_non_negative_int("width", width)
        _validate_optional_non_negative_int("height", height)
        _validate_optional_non_negative_int("audio_channels", audio_channels)
        _validate_optional_non_negative_int("sample_rate_hz", sample_rate_hz)

        if fps is not None:
            if isinstance(fps, bool) or not isinstance(fps, (int, float)):
                raise TypeError("fps must be a number or None")
            if float(fps) <= 0:
                raise ValueError("fps must be > 0")

        object.__setattr__(self, "envelope", envelope)
        object.__setattr__(self, "media_kind", media_kind)
        object.__setattr__(self, "origin", origin)
        object.__setattr__(self, "usage_role", resolved_usage_role)
        object.__setattr__(self, "storage_ref", storage_ref)
        object.__setattr__(self, "content_hash", content_hash)
        object.__setattr__(self, "byte_size", byte_size)
        object.__setattr__(self, "provenance", provenance)
        object.__setattr__(self, "imported_at", imported_at)
        object.__setattr__(self, "duration", resolved_duration)
        object.__setattr__(self, "width", width)
        object.__setattr__(self, "height", height)
        object.__setattr__(self, "fps", None if fps is None else float(fps))
        object.__setattr__(self, "codec", codec)
        object.__setattr__(self, "audio_channels", audio_channels)
        object.__setattr__(self, "sample_rate_hz", sample_rate_hz)
        object.__setattr__(self, "user_labels", user_labels)
        object.__setattr__(self, "collection_refs", collection_refs)

    @property
    def duration_ms(self) -> int | None:
        """Legacy exact-ms adapter. Raises instead of rounding finer canonical time."""

        if self.duration is None:
            return None
        return self.duration.to_milliseconds_exact()

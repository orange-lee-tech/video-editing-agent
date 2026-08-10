from __future__ import annotations

import hashlib
import pathlib
import uuid
from collections.abc import Callable
from datetime import datetime, timezone

from video_editing_agent.domain.asset.model import Asset
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityStatus
from video_editing_agent.media.ingest.probe import MediaProbe
from video_editing_agent.media.ingest.source import LocalMediaSource

ASSET_SCHEMA_VERSION = "0.1.1"
HASH_CHUNK_SIZE = 1024 * 1024


def _default_asset_id() -> str:
    return f"ast_{uuid.uuid4().hex}"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(HASH_CHUNK_SIZE):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


class AssetIngestService:
    """Create immutable Asset identity from an already available local media source."""

    def __init__(
        self,
        probe: MediaProbe,
        *,
        asset_id_factory: Callable[[], str] = _default_asset_id,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._probe = probe
        self._asset_id_factory = asset_id_factory
        self._clock = clock

    def ingest(self, source: LocalMediaSource, *, created_by: str = "system") -> Asset:
        path = source.path.expanduser().resolve(strict=True)
        if not path.is_file():
            raise ValueError(f"media source must be a file: {path}")

        metadata = self._probe.probe(path)
        imported_at = self._clock()
        asset_id = self._asset_id_factory()
        if not asset_id.startswith("ast_"):
            raise ValueError("asset_id_factory must return an ast_* identifier")

        return Asset(
            envelope=EntityEnvelope(
                id=asset_id,
                revision=1,
                schema_version=ASSET_SCHEMA_VERSION,
                status=EntityStatus.VALID,
                created_at=imported_at,
                created_by=created_by,
            ),
            media_kind=metadata.media_kind,
            origin=source.origin,
            storage_ref=path.as_uri(),
            content_hash=_sha256_file(path),
            byte_size=path.stat().st_size,
            provenance=source.provenance,
            imported_at=imported_at,
            duration_ms=metadata.duration_ms,
            width=metadata.width,
            height=metadata.height,
            fps=metadata.fps,
            codec=metadata.codec,
            audio_channels=metadata.audio_channels,
            sample_rate_hz=metadata.sample_rate_hz,
        )

from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.media.ingest.ffprobe import parse_ffprobe_metadata
from video_editing_agent.media.ingest.probe import MediaTechnicalMetadata
from video_editing_agent.media.ingest.service import AssetIngestService
from video_editing_agent.media.ingest.source import LocalMediaSource

NOW = datetime(2026, 8, 11, 2, 40, tzinfo=UTC)


def envelope() -> EntityEnvelope:
    return EntityEnvelope(
        id="ast_exact_duration",
        revision=1,
        schema_version="0.2",
        status=EntityStatus.VALID,
        created_at=NOW,
        created_by="test",
    )


def test_ffprobe_duration_string_becomes_exact_rational_time() -> None:
    metadata = parse_ffprobe_metadata(
        '{"streams":[{"codec_type":"video","codec_name":"h264"}],"format":{"duration":"2.5025"}}'
    )

    assert metadata.duration == MediaTime(1001, 400)
    with pytest.raises(ValueError, match="exact integer millisecond"):
        _ = metadata.duration_ms


def test_asset_keeps_submillisecond_duration_without_rounding() -> None:
    asset = Asset(
        envelope=envelope(),
        media_kind="video",
        origin="local",
        storage_ref="file:///tmp/exact.mp4",
        content_hash="sha256:" + "3" * 64,
        byte_size=10,
        provenance=AssetProvenance(origin_type="local"),
        imported_at=NOW,
        duration=MediaTime(1001, 400),
    )

    assert asset.duration == MediaTime(1001, 400)
    with pytest.raises(ValueError, match="exact integer millisecond"):
        _ = asset.duration_ms


def test_legacy_millisecond_asset_construction_remains_exact() -> None:
    asset = Asset(
        envelope=envelope(),
        media_kind="video",
        origin="local",
        storage_ref="file:///tmp/legacy.mp4",
        content_hash="sha256:" + "4" * 64,
        byte_size=10,
        provenance=AssetProvenance(origin_type="local"),
        imported_at=NOW,
        duration_ms=2_502,
    )

    assert asset.duration == MediaTime(1251, 500)
    assert asset.duration_ms == 2_502


class ExactProbe:
    def probe(self, path: Path) -> MediaTechnicalMetadata:
        assert path.is_file()
        return MediaTechnicalMetadata(
            media_kind="video",
            duration=MediaTime(1001, 400),
            codec="h264",
        )


def test_asset_ingest_preserves_exact_probe_duration(tmp_path: Path) -> None:
    media = tmp_path / "exact.mp4"
    media.write_bytes(b"media")
    service = AssetIngestService(
        ExactProbe(),
        asset_id_factory=lambda: "ast_exact_duration",
        clock=lambda: NOW,
    )

    asset = service.ingest(
        LocalMediaSource(
            path=media,
            origin="local",
            provenance=AssetProvenance(origin_type="local"),
        )
    )

    assert asset.duration == MediaTime(1001, 400)

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from video_editing_agent.domain.asset.model import AssetProvenance
from video_editing_agent.media.ingest.probe import MediaTechnicalMetadata
from video_editing_agent.media.ingest.service import AssetIngestService
from video_editing_agent.media.ingest.source import LocalMediaSource


class StaticProbe:
    def probe(self, path: Path) -> MediaTechnicalMetadata:
        assert path.is_file()
        return MediaTechnicalMetadata(
            media_kind="video",
            duration_ms=2_000,
            width=1920,
            height=1080,
            fps=25.0,
            codec="h264",
            audio_channels=2,
            sample_rate_hz=48_000,
        )


def test_local_ingest_creates_valid_asset_with_hash_and_metadata(tmp_path: Path) -> None:
    media = tmp_path / "clip.mp4"
    payload = b"test-media-payload"
    media.write_bytes(payload)
    now = datetime(2026, 8, 10, 7, 40, tzinfo=timezone.utc)
    service = AssetIngestService(
        StaticProbe(),
        asset_id_factory=lambda: "ast_test",
        clock=lambda: now,
    )

    asset = service.ingest(
        LocalMediaSource(
            path=media,
            origin="captured",
            provenance=AssetProvenance(origin_type="captured"),
        ),
        created_by="user",
    )

    assert asset.envelope.id == "ast_test"
    assert asset.envelope.revision == 1
    assert asset.envelope.created_at == now
    assert asset.envelope.created_by == "user"
    assert asset.storage_ref == media.resolve().as_uri()
    assert asset.byte_size == len(payload)
    assert asset.content_hash == f"sha256:{hashlib.sha256(payload).hexdigest()}"
    assert asset.duration_ms == 2_000
    assert asset.width == 1920
    assert asset.height == 1080
    assert asset.fps == 25.0
    assert asset.codec == "h264"


def test_ingest_rejects_non_asset_identifier(tmp_path: Path) -> None:
    media = tmp_path / "clip.mp4"
    media.write_bytes(b"x")
    service = AssetIngestService(StaticProbe(), asset_id_factory=lambda: "wrong")

    try:
        service.ingest(
            LocalMediaSource(
                path=media,
                origin="imported",
                provenance=AssetProvenance(origin_type="imported"),
            )
        )
    except ValueError as exc:
        assert "ast_*" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_source_origin_must_match_provenance(tmp_path: Path) -> None:
    try:
        LocalMediaSource(
            path=tmp_path / "clip.mp4",
            origin="captured",
            provenance=AssetProvenance(origin_type="remote"),
        )
    except ValueError as exc:
        assert "provenance.origin_type" in str(exc)
    else:
        raise AssertionError("expected ValueError")

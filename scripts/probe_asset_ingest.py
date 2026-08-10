from __future__ import annotations

import argparse
import pathlib

from video_editing_agent.domain.asset.model import AssetProvenance
from video_editing_agent.media.ingest.ffprobe import FfprobeMediaProbe
from video_editing_agent.media.ingest.service import AssetIngestService
from video_editing_agent.media.ingest.source import LocalMediaSource


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe real ffprobe metadata extraction and local Asset ingestion."
    )
    parser.add_argument("video", type=pathlib.Path)
    parser.add_argument("--expected-duration-ms", type=int, required=True)
    parser.add_argument("--duration-tolerance-ms", type=int, default=100)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    video_path = args.video.expanduser().resolve()
    if not video_path.is_file():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    service = AssetIngestService(FfprobeMediaProbe(), asset_id_factory=lambda: "ast_probe")
    asset = service.ingest(
        LocalMediaSource(
            path=video_path,
            origin="imported",
            provenance=AssetProvenance(origin_type="imported"),
        )
    )

    if asset.media_kind != "video":
        raise RuntimeError(f"Expected video Asset, got {asset.media_kind}")
    if asset.duration_ms is None:
        raise RuntimeError("ffprobe did not provide duration")
    if abs(asset.duration_ms - args.expected_duration_ms) > args.duration_tolerance_ms:
        raise RuntimeError(
            f"Unexpected duration: expected about {args.expected_duration_ms} ms, "
            f"got {asset.duration_ms} ms"
        )
    if (asset.width, asset.height) != (320, 180):
        raise RuntimeError(f"Unexpected dimensions: {asset.width}x{asset.height}")
    if asset.fps is None or abs(asset.fps - 25.0) > 0.01:
        raise RuntimeError(f"Unexpected frame rate: {asset.fps}")
    if asset.audio_channels != 1:
        raise RuntimeError(f"Unexpected audio channel count: {asset.audio_channels}")
    if asset.sample_rate_hz != 48_000:
        raise RuntimeError(f"Unexpected sample rate: {asset.sample_rate_hz}")
    if not asset.content_hash.startswith("sha256:") or len(asset.content_hash) != 71:
        raise RuntimeError("Asset content hash is not a canonical SHA-256 value")

    print("Asset ingest probe: PASS")
    print(f"asset_id={asset.envelope.id}")
    print(f"media_kind={asset.media_kind}")
    print(f"duration_ms={asset.duration_ms}")
    print(f"dimensions={asset.width}x{asset.height}")
    print(f"fps={asset.fps}")
    print(f"codec={asset.codec}")
    print(f"audio_channels={asset.audio_channels}")
    print(f"sample_rate_hz={asset.sample_rate_hz}")
    print(f"content_hash={asset.content_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

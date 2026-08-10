from __future__ import annotations

import argparse
import pathlib

from video_editing_agent.application.ports.shot_detector import ShotDetectionOptions
from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.media.ingest.ffprobe import FfprobeMediaProbe
from video_editing_agent.media.ingest.service import AssetIngestService
from video_editing_agent.media.ingest.source import LocalMediaSource
from video_editing_agent.media.shot_detection.catalog import ShotCatalog
from video_editing_agent.media.shot_detection.detector import PolicyDrivenShotDetector
from video_editing_agent.media.shot_detection.transnet_backend import (
    ResolvedVideoAsset,
    TransNetV2SceneBoundaryBackend,
)
from video_editing_agent.media.shot_detection.transnet_runtime import (
    TorchTransNetV2Config,
    TorchTransNetV2WindowPredictor,
)


class IngestedAssetVideoResolver:
    def __init__(self, asset: Asset, source_path: pathlib.Path) -> None:
        self._asset = asset
        self._source_path = source_path

    def resolve_video(self, asset_ref: EntityRevisionRef) -> ResolvedVideoAsset:
        expected_ref = EntityRevisionRef(self._asset.envelope.id, self._asset.envelope.revision)
        if asset_ref != expected_ref:
            raise ValueError(f"Unknown Asset revision: {asset_ref}")
        if self._asset.duration_ms is None:
            raise ValueError("Asset has no probed duration")
        return ResolvedVideoAsset(
            path=self._source_path,
            duration_ms=self._asset.duration_ms,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe real local media from Asset ingest through committed Shot identities."
    )
    parser.add_argument("video", type=pathlib.Path)
    parser.add_argument("--expected-shots", type=int, required=True)
    parser.add_argument(
        "--device",
        default="cpu",
        choices=("auto", "cpu", "cuda", "mps"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    video_path = args.video.expanduser().resolve()
    if not video_path.is_file():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if args.expected_shots <= 0:
        raise ValueError("expected-shots must be > 0")

    ingest = AssetIngestService(FfprobeMediaProbe(), asset_id_factory=lambda: "ast_pipeline_probe")
    asset = ingest.ingest(
        LocalMediaSource(
            path=video_path,
            origin="imported",
            provenance=AssetProvenance(origin_type="imported"),
        )
    )
    asset_ref = EntityRevisionRef(asset.envelope.id, asset.envelope.revision)

    backend = TransNetV2SceneBoundaryBackend(
        IngestedAssetVideoResolver(asset, video_path),
        TorchTransNetV2WindowPredictor(TorchTransNetV2Config(device=args.device)),
    )
    proposals = PolicyDrivenShotDetector(backend).detect(asset_ref, ShotDetectionOptions())
    shots = ShotCatalog().commit_boundaries(proposals)

    if len(shots) != args.expected_shots:
        raise RuntimeError(f"Expected {args.expected_shots} Shots, got {len(shots)}")
    if asset.duration_ms is None:
        raise RuntimeError("Asset duration disappeared after shot detection")
    if shots[0].source_start_ms != 0 or shots[-1].source_end_ms != asset.duration_ms:
        raise RuntimeError("Committed Shots do not cover the complete Asset duration")
    if any(shot.asset_ref != asset_ref for shot in shots):
        raise RuntimeError("Committed Shot references changed Asset identity")

    for previous, current in zip(shots, shots[1:], strict=False):
        if previous.source_end_ms != current.source_start_ms:
            raise RuntimeError("Committed Shots contain a gap or overlap")
        if previous.next_shot_ref != EntityRevisionRef(current.envelope.id, current.envelope.revision):
            raise RuntimeError("Forward Shot neighbor reference is inconsistent")
        if current.previous_shot_ref != EntityRevisionRef(
            previous.envelope.id, previous.envelope.revision
        ):
            raise RuntimeError("Backward Shot neighbor reference is inconsistent")

    print("Asset-to-Shots pipeline probe: PASS")
    print(f"asset_ref={asset_ref.entity_id}@{asset_ref.revision}")
    print(f"asset_duration_ms={asset.duration_ms}")
    print(f"proposal_count={len(proposals)}")
    print(f"shot_count={len(shots)}")
    print(f"shot_ranges_ms={[(shot.source_start_ms, shot.source_end_ms) for shot in shots]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

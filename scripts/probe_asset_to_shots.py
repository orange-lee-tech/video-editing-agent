from __future__ import annotations

import argparse
import pathlib

from video_editing_agent.application.ports.shot_detector import ShotDetectionOptions
from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.media.ingest.ffprobe import FfprobeMediaProbe
from video_editing_agent.media.ingest.service import AssetIngestService
from video_editing_agent.media.ingest.source import LocalMediaSource
from video_editing_agent.media.shot_detection.catalog import ShotCatalog
from video_editing_agent.media.shot_detection.transnet_runtime import (
    TorchTransNetV2Config,
    TorchTransNetV2WindowPredictor,
)
from video_editing_agent.media.shot_detection.v02_exact import (
    ExactPolicyDrivenShotDetector,
    ExactResolvedVideoAsset,
    ExactTransNetV2SceneBoundaryBackend,
)


class IngestedAssetVideoResolver:
    def __init__(self, asset: Asset, source_path: pathlib.Path) -> None:
        self._asset = asset
        self._source_path = source_path

    def resolve_video(self, asset_ref: EntityRevisionRef) -> ExactResolvedVideoAsset:
        expected_ref = EntityRevisionRef(self._asset.envelope.id, self._asset.envelope.revision)
        if asset_ref != expected_ref:
            raise ValueError(f"Unknown Asset revision: {asset_ref}")
        if self._asset.duration is None:
            raise ValueError("Asset has no probed duration")
        return ExactResolvedVideoAsset(
            path=self._source_path,
            duration=self._asset.duration,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Probe local media from Asset ingest through exact-time TransNetV2 boundaries "
            "and committed Shot identities."
        )
    )
    parser.add_argument("video", type=pathlib.Path)
    parser.add_argument(
        "--expected-shots",
        type=int,
        default=None,
        help="Optional fixed expectation for deterministic engineering fixtures.",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        choices=("auto", "cpu", "cuda", "mps"),
    )
    return parser.parse_args()


def _format_time(value: MediaTime) -> str:
    return f"{value.value}/{value.scale}s"


def main() -> int:
    args = parse_args()
    video_path = args.video.expanduser().resolve()
    if not video_path.is_file():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if args.expected_shots is not None and args.expected_shots <= 0:
        raise ValueError("expected-shots must be > 0 when provided")

    ingest = AssetIngestService(FfprobeMediaProbe(), asset_id_factory=lambda: "ast_pipeline_probe")
    asset = ingest.ingest(
        LocalMediaSource(
            path=video_path,
            origin="imported",
            provenance=AssetProvenance(origin_type="imported"),
        )
    )
    asset_ref = EntityRevisionRef(asset.envelope.id, asset.envelope.revision)
    if asset.duration is None:
        raise RuntimeError("Asset duration disappeared after ingest")

    backend = ExactTransNetV2SceneBoundaryBackend(
        IngestedAssetVideoResolver(asset, video_path),
        TorchTransNetV2WindowPredictor(TorchTransNetV2Config(device=args.device)),
    )
    proposals = ExactPolicyDrivenShotDetector(backend).detect(asset_ref, ShotDetectionOptions())
    shots = ShotCatalog().commit_boundaries(proposals)

    if args.expected_shots is not None and len(shots) != args.expected_shots:
        raise RuntimeError(f"Expected {args.expected_shots} Shots, got {len(shots)}")
    if not shots:
        raise RuntimeError("Positive-duration media produced no committed Shots")
    if shots[0].source_range.start != MediaTime(0, 1):
        raise RuntimeError("Committed Shots do not begin at authoritative source time 0")
    if shots[-1].source_range.end != asset.duration:
        raise RuntimeError("Committed Shots do not cover the complete authoritative Asset duration")
    if any(shot.asset_ref != asset_ref for shot in shots):
        raise RuntimeError("Committed Shot references changed Asset identity")

    for previous, current in zip(shots, shots[1:], strict=False):
        if previous.source_range.end != current.source_range.start:
            raise RuntimeError("Committed Shots contain a gap or overlap")
        if previous.next_shot_ref != EntityRevisionRef(
            current.envelope.id, current.envelope.revision
        ):
            raise RuntimeError("Forward Shot neighbor reference is inconsistent")
        if current.previous_shot_ref != EntityRevisionRef(
            previous.envelope.id, previous.envelope.revision
        ):
            raise RuntimeError("Backward Shot neighbor reference is inconsistent")

    print("Asset-to-Shots exact-time pipeline probe: PASS")
    print(f"asset_ref={asset_ref.entity_id}@{asset_ref.revision}")
    print(f"asset_duration={_format_time(asset.duration)}")
    print(f"asset_duration_decimal={asset.duration.to_decimal_seconds_string()}s")
    print(f"proposal_count={len(proposals)}")
    print(f"shot_count={len(shots)}")
    print(
        "shot_ranges="
        + repr(
            [
                (_format_time(shot.source_range.start), _format_time(shot.source_range.end))
                for shot in shots
            ]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

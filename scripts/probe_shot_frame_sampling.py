from __future__ import annotations

import argparse
import pathlib
import struct
from datetime import UTC, datetime

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.understanding.frame_extraction import (
    PNG_SIGNATURE,
    FfmpegPngFrameExtractor,
)
from video_editing_agent.media.understanding.sampling import (
    FrameSamplingOptions,
    plan_uniform_frame_samples,
)


def _png_dimensions(content: bytes) -> tuple[int, int]:
    if not content.startswith(PNG_SIGNATURE) or len(content) < 24:
        raise RuntimeError("Extracted frame is not a complete PNG header")
    return struct.unpack(">II", content[16:24])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe deterministic Shot frame planning and real FFmpeg PNG extraction."
    )
    parser.add_argument("video", type=pathlib.Path)
    parser.add_argument("--duration-ms", type=int, required=True)
    parser.add_argument("--max-frames", type=int, default=3)
    parser.add_argument("--expected-width", type=int, required=True)
    parser.add_argument("--expected-height", type=int, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    video_path = args.video.expanduser().resolve()
    if not video_path.is_file():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if args.duration_ms <= 0:
        raise ValueError("duration-ms must be > 0")

    shot = Shot(
        envelope=EntityEnvelope(
            id="sht_sampling_probe",
            revision=2,
            schema_version="0.1.1",
            status=EntityStatus.VALID,
            created_at=datetime.now(UTC),
            created_by="probe",
        ),
        asset_ref=EntityRevisionRef("ast_sampling_probe", 1),
        source_start_ms=0,
        source_end_ms=args.duration_ms,
        boundary_method="probe",
    )
    plan = plan_uniform_frame_samples(
        shot,
        FrameSamplingOptions(max_frames=args.max_frames),
    )
    frames = FfmpegPngFrameExtractor().extract(video_path, plan)

    if len(frames) != len(plan.samples):
        raise RuntimeError("Frame extractor changed the sampling-plan cardinality")
    for planned, extracted in zip(plan.samples, frames, strict=True):
        if extracted.sample != planned:
            raise RuntimeError("Frame extractor changed sampling identity")
        dimensions = _png_dimensions(extracted.content)
        if dimensions != (args.expected_width, args.expected_height):
            raise RuntimeError(
                f"Unexpected PNG dimensions at {planned.source_timestamp_ms} ms: {dimensions}"
            )

    print("Shot frame sampling probe: PASS")
    print(f"shot_ref={plan.shot_ref.entity_id}@{plan.shot_ref.revision}")
    print(f"timestamps_ms={[sample.source_timestamp_ms for sample in plan.samples]}")
    print(f"frame_sizes_bytes={[len(frame.content) for frame in frames]}")
    print(f"dimensions={args.expected_width}x{args.expected_height}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

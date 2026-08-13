from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import time
from datetime import UTC, datetime

from video_editing_agent.application.ports.asset_media import ResolvedLocalAssetMedia
from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.temporal.visual_events import (
    MotionEventPolicy,
    VisualMotionEventService,
)
from video_editing_agent.media.temporal.visual_motion import VisualMotionEvidenceService
from video_editing_agent.media.temporal.visual_motion_codec import decode_visual_motion
from video_editing_agent.media.temporal.visual_refinement import (
    VisualMotionRefinementService,
    VisualRefinementPolicy,
)
from video_editing_agent.providers.vision.opencv_motion import (
    OpenCvMotionConfig,
    OpenCvVisualMotionPort,
)
from video_editing_agent.storage.artifact.lifecycle_repository import (
    LocalArtifactLifecycleRepository,
)
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase
from video_editing_agent.storage.repositories.sqlite_repositories import (
    SqliteAssetRepository,
    SqliteShotRepository,
)
from video_editing_agent.storage.repositories.temporal_evidence_repository import (
    SqliteTemporalEvidenceRepository,
)


class Resolver:
    def __init__(self, path: pathlib.Path) -> None:
        self.path = path

    def resolve_local(self, asset_ref: EntityRevisionRef) -> ResolvedLocalAssetMedia:
        return ResolvedLocalAssetMedia(asset_ref, self.path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--ffmpeg", required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("fresh output required")
    output.mkdir(parents=True, exist_ok=True)
    import cv2
    import numpy as np

    media = output / "between_grid.mp4"
    rng = np.random.default_rng(8081)
    background = rng.integers(20, 220, (180, 320, 3), dtype=np.uint8)
    writer = cv2.VideoWriter(str(media), cv2.VideoWriter_fourcc(*"mp4v"), 30, (320, 180))
    x = 50
    for frame in range(150):
        image = background.copy()
        if 38 <= frame < 68:
            x += 9 if frame == 52 else 3
        for row in range(4):
            for col in range(4):
                cv2.rectangle(
                    image,
                    (x + col * 9, 70 + row * 9),
                    (x + col * 9 + 8, 70 + row * 9 + 8),
                    (250, 20, 20) if (row + col) % 2 else (20, 250, 250),
                    -1,
                )
        writer.write(image)
    writer.release()
    db = SqliteProjectDatabase(output / "project.sqlite3")
    db.initialize()
    now = datetime(2026, 8, 13, tzinfo=UTC)
    asset_ref = EntityRevisionRef("ast_refine", 1)
    shot_ref = EntityRevisionRef("sht_refine", 1)

    def envelope(identity: str):
        return EntityEnvelope(identity, 1, "0.2", EntityStatus.VALID, now, "r0.8e-probe")

    assets = SqliteAssetRepository(db)
    shots = SqliteShotRepository(db)
    assets.save(
        Asset(
            envelope(asset_ref.entity_id),
            "video",
            "local",
            media.as_uri(),
            "sha256:" + hashlib.sha256(media.read_bytes()).hexdigest(),
            media.stat().st_size,
            AssetProvenance("local"),
            now,
            duration=MediaTime(5, 1),
        )
    )
    shots.save(
        Shot(
            envelope(shot_ref.entity_id),
            asset_ref,
            source_range=MediaTimeRange(MediaTime(1, 1), MediaTime(3, 1)),
            boundary_method="probe",
        )
    )
    repository = SqliteTemporalEvidenceRepository(db)
    store = LocalArtifactStore(output / "artifacts")
    lifecycle = LocalArtifactLifecycleRepository(output / "artifacts")
    policy = MotionEventPolicy("r0.8e-controlled-v1", 0.03, 0.02, 0.03, 0.02, 2, 0)
    coarse_owner = VisualMotionEvidenceService(
        shot_repository=shots,
        asset_media_resolver=Resolver(media),
        temporal_evidence_repository=repository,
        artifact_store=store,
        artifact_lifecycle_repository=lifecycle,
        motion_port=OpenCvVisualMotionPort(
            OpenCvMotionConfig(ffmpeg_executable=args.ffmpeg, frames_per_second=10)
        ),
    )
    started = time.perf_counter()
    coarse_measure = coarse_owner.measure(shot_ref)[0]
    coarse_regions, coarse_anchors = VisualMotionEventService(
        shot_repository=shots, temporal_evidence_repository=repository, artifact_store=store
    ).reduce(shot_ref, coarse_measure.evidence_id, policy)
    coarse_wall = time.perf_counter() - started
    coarse_region = next(x for x in coarse_regions if x.kind == "residual_motion_region")
    fine_owner = VisualMotionEvidenceService(
        shot_repository=shots,
        asset_media_resolver=Resolver(media),
        temporal_evidence_repository=repository,
        artifact_store=store,
        artifact_lifecycle_repository=lifecycle,
        motion_port=OpenCvVisualMotionPort(
            OpenCvMotionConfig(ffmpeg_executable=args.ffmpeg, frames_per_second=30)
        ),
    )
    refine = VisualMotionRefinementService(
        shot_repository=shots,
        temporal_evidence_repository=repository,
        motion_evidence_service=fine_owner,
        event_service=VisualMotionEventService(
            shot_repository=shots, temporal_evidence_repository=repository, artifact_store=store
        ),
    )
    started = time.perf_counter()
    fine_regions, fine_anchors = refine.refine(
        shot_ref,
        coarse_region.evidence_id,
        VisualRefinementPolicy("r0.8e-fine-v1", MediaTime(1, 5), policy),
    )
    fine_wall = time.perf_counter() - started

    def residual(anchors):
        return {
            x.kind.removeprefix("residual_motion_"): x.source_time.as_fraction()
            for x in anchors
            if x.kind.startswith("residual_motion_")
        }

    coarse = residual(coarse_anchors)
    fine = residual(fine_anchors)
    truth = {
        "onset": MediaTime(38, 30).as_fraction(),
        "peak": MediaTime(52, 30).as_fraction(),
        "settle": MediaTime(68, 30).as_fraction(),
    }
    coarse_error = {k: float(abs(coarse[k] - v)) for k, v in truth.items()}
    fine_error = {k: float(abs(fine[k] - v)) for k, v in truth.items()}
    measurement_sets = [
        x for x in repository.list_evidence(shot_ref) if x.kind == "visual_motion_measurement_set"
    ]
    fine_measure = next(x for x in measurement_sets if x.evidence_id != coarse_measure.evidence_id)
    decoded = decode_visual_motion(store.get_by_id(fine_measure.artifact_refs[0]))
    reopened = SqliteTemporalEvidenceRepository(SqliteProjectDatabase(output / "project.sqlite3"))
    repeat_regions, repeat_anchors = refine.refine(
        shot_ref,
        coarse_region.evidence_id,
        VisualRefinementPolicy("r0.8e-fine-v1", MediaTime(1, 5), policy),
    )
    regression = __import__("subprocess").run(
        [
            "uv",
            "run",
            "pytest",
            "-q",
            "tests/unit/test_visual_refinement.py",
            "tests/unit/test_visual_motion_codec_v2.py",
            "tests/unit/test_visual_motion_events.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    gates = {
        "REFINED_WITHIN_ONE_FRAME": max(fine_error.values()) <= 1 / 30,
        "REFINED_NOT_WORSE": all(fine_error[k] <= coarse_error[k] for k in truth),
        "NON_ZERO_SHOT_OFFSET": decoded.analyzed_source_range is not None
        and decoded.analyzed_source_range.start.as_fraction() >= 1,
        "SUBRANGE_INSIDE_SHOT": decoded.analyzed_source_range is not None
        and decoded.analyzed_source_range.end.as_fraction() <= 4,
        "RESTART_EQUALITY": reopened.list_evidence(shot_ref) == repository.list_evidence(shot_ref)
        and reopened.list_anchors(shot_ref) == repository.list_anchors(shot_ref),
        "ARTIFACT_REOPEN": decode_visual_motion(
            LocalArtifactStore(output / "artifacts").get_by_id(fine_measure.artifact_refs[0])
        )
        == decoded,
        "DETERMINISTIC_IDS": [x.evidence_id for x in repeat_regions]
        == [x.evidence_id for x in fine_regions]
        and [x.anchor_id for x in repeat_anchors] == [x.anchor_id for x in fine_anchors],
        "PAN_ONLY_NO_RESIDUAL_EVENT": regression.returncode == 0,
        "UNAVAILABLE_FAIL_CLOSED": regression.returncode == 0,
        "V1_BACKWARD_READ": regression.returncode == 0,
    }
    result = {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "gates": {k: "PASS" if v else "FAIL" for k, v in gates.items()},
        "truth_seconds": {k: float(v) for k, v in truth.items()},
        "coarse_seconds": {k: float(v) for k, v in coarse.items()},
        "refined_seconds": {k: float(v) for k, v in fine.items()},
        "coarse_error_seconds": coarse_error,
        "refined_error_seconds": fine_error,
        "analyzed_source_range": {
            "start": [
                decoded.analyzed_source_range.start.value,
                decoded.analyzed_source_range.start.scale,
            ],
            "duration": [
                decoded.analyzed_source_range.duration.value,
                decoded.analyzed_source_range.duration.scale,
            ],
        },
        "measurement_counts": {"coarse": 10 * 3 - 1, "refined": len(decoded.measurements)},
        "performance": {
            "coarse_wall": coarse_wall,
            "coarse_rtf": coarse_wall / 3,
            "refined_wall": fine_wall,
            "refined_rtf": fine_wall / float(decoded.analyzed_source_range.duration.as_fraction()),
        },
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

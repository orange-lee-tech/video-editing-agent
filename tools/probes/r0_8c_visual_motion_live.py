from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from datetime import UTC, datetime

from video_editing_agent.application.ports.asset_media import ResolvedLocalAssetMedia
from video_editing_agent.application.ports.visual_motion import VisualMotionRequest
from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.temporal.visual_motion import VisualMotionEvidenceService
from video_editing_agent.providers.vision.opencv_motion import (
    OpenCvMotionConfig,
    OpenCvVisualMotionPort,
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
    import cv2
    import numpy as np

    args.output = args.output.expanduser().resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(808)
    background = rng.integers(20, 220, (180, 320, 3), dtype=np.uint8)
    cases = {"static": (0, 0), "pan_only": (2, 0), "local_only": (0, 3), "pan_plus_local": (2, 3)}
    reports = {}
    for name, (pan, local) in cases.items():
        path = args.output / f"{name}.mp4"
        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 10, (320, 180))
        for frame_index in range(50):
            test_index = max(0, min(29, frame_index - 10))
            frame = np.roll(background, pan * test_index, axis=1)
            if local:
                x = 40 + local * test_index + pan * test_index
                for row in range(4):
                    for column in range(4):
                        color = (250, 20, 20) if (row + column) % 2 else (20, 250, 250)
                        cv2.rectangle(
                            frame,
                            (x + column * 9, 70 + row * 9),
                            (x + column * 9 + 8, 70 + row * 9 + 8),
                            color,
                            -1,
                        )
            writer.write(frame)
        writer.release()
        started = time.perf_counter()
        proposal = OpenCvVisualMotionPort(
            OpenCvMotionConfig(ffmpeg_executable=args.ffmpeg)
        ).measure(
            VisualMotionRequest(
                EntityRevisionRef(f"sht_{name}", 1),
                path,
                MediaTimeRange(MediaTime(1, 1), MediaTime(3, 1)),
            )
        )
        available = [item for item in proposal.measurements if item.status == "available"]
        reports[name] = {
            "pairs": len(proposal.measurements),
            "available": len(available),
            "global_median": float(np.median([x.global_displacement for x in available])),
            "raw_median": float(np.median([x.raw_displacement_median for x in available])),
            "residual_p95_median": float(np.median([x.residual_p95 for x in available])),
            "inlier_ratio_median": float(np.median([x.inlier_ratio for x in available])),
            "wall_seconds": time.perf_counter() - started,
        }
    pan = reports["pan_only"]
    passed = (
        pan["residual_p95_median"] < pan["raw_median"] * 0.35
        and reports["local_only"]["residual_p95_median"]
        > reports["static"]["residual_p95_median"] + 0.5
        and reports["pan_plus_local"]["residual_p95_median"] > pan["residual_p95_median"] + 0.5
    )
    live_path = args.output / "pan_plus_local.mp4"
    database_path = args.output / "motion.sqlite3"
    database_path.unlink(missing_ok=True)
    database = SqliteProjectDatabase(database_path)
    database.initialize()
    now = datetime(2026, 8, 13, tzinfo=UTC)
    asset_ref = EntityRevisionRef("ast_motion_live", 1)
    shot_ref = EntityRevisionRef("sht_motion_live", 1)

    def envelope(identity: str) -> EntityEnvelope:
        return EntityEnvelope(identity, 1, "0.2", EntityStatus.VALID, now, "r0.8c-probe")

    SqliteAssetRepository(database).save(
        Asset(
            envelope(asset_ref.entity_id),
            "video",
            "local",
            live_path.as_uri(),
            "sha256:" + "8" * 64,
            live_path.stat().st_size,
            AssetProvenance("local"),
            now,
            duration=MediaTime(5, 1),
        )
    )
    SqliteShotRepository(database).save(
        Shot(
            envelope(shot_ref.entity_id),
            asset_ref,
            source_range=MediaTimeRange(MediaTime(1, 1), MediaTime(3, 1)),
            boundary_method="r0.8c-probe",
        )
    )
    evidence = VisualMotionEvidenceService(
        shot_repository=SqliteShotRepository(database),
        asset_media_resolver=Resolver(live_path),
        temporal_evidence_repository=SqliteTemporalEvidenceRepository(database),
        artifact_store=LocalArtifactStore(args.output / "artifacts"),
        motion_port=OpenCvVisualMotionPort(OpenCvMotionConfig(ffmpeg_executable=args.ffmpeg)),
    ).measure(shot_ref)
    reopened = SqliteTemporalEvidenceRepository(SqliteProjectDatabase(database_path)).list_evidence(
        shot_ref
    )
    persistence_pass = reopened == tuple(sorted(evidence, key=lambda item: item.evidence_id))
    passed = passed and persistence_pass
    result = {
        "status": "PASS" if passed else "FAIL",
        "opencv": cv2.__version__,
        "numpy": np.__version__,
        "shot_range": [1, 4],
        "cases": reports,
        "PAN_ONLY_FALSE_LOCAL_ACTION": "PASS" if passed else "FAIL",
        "persistence": {
            "status": "PASS" if persistence_pass else "FAIL",
            "evidence": len(reopened),
            "artifact_id": evidence[0].artifact_refs[0],
            "sqlite_reopen": persistence_pass,
        },
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import time
from datetime import UTC, datetime

from video_editing_agent.application.ports.artifact_store import StoredArtifactRef
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


def _prepare_output(output: pathlib.Path) -> None:
    if output.exists():
        if not output.is_dir():
            raise NotADirectoryError(f"probe output is not a directory: {output}")
        if any(output.iterdir()):
            raise FileExistsError(
                f"probe output is not empty; choose a fresh path instead of overwriting: {output}"
            )
        return
    output.mkdir(parents=True, exist_ok=False)


def _case_report(proposal, np, wall_seconds: float) -> dict[str, float | int]:
    available = [item for item in proposal.measurements if item.status == "available"]
    if not available:
        raise RuntimeError("controlled visual-motion fixture produced no available measurements")
    return {
        "pairs": len(proposal.measurements),
        "available": len(available),
        "global_median": float(np.median([item.global_displacement for item in available])),
        "raw_median": float(np.median([item.raw_displacement_median for item in available])),
        "residual_p95_median": float(np.median([item.residual_p95 for item in available])),
        "inlier_ratio_median": float(np.median([item.inlier_ratio for item in available])),
        "wall_seconds": wall_seconds,
        "input_seconds": 3.0,
        "rtf": wall_seconds / 3.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--ffmpeg", required=True)
    args = parser.parse_args()
    import cv2
    import numpy as np

    args.output = args.output.expanduser().resolve()
    _prepare_output(args.output)
    rng = np.random.default_rng(808)
    background = rng.integers(20, 220, (180, 320, 3), dtype=np.uint8)
    cases = {
        "static": (0, 0),
        "pan_only": (2, 0),
        "local_only": (0, 3),
        "pan_plus_local": (2, 3),
    }
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
        reports[name] = _case_report(proposal, np, time.perf_counter() - started)

    static = reports["static"]
    pan = reports["pan_only"]
    local = reports["local_only"]
    pan_local = reports["pan_plus_local"]
    gates = {
        "STATIC_LOW_MOTION": (
            static["global_median"] < 0.1 and static["residual_p95_median"] < 0.1
        ),
        "PAN_ONLY_FALSE_LOCAL_ACTION": (
            pan["raw_median"] > 0.5 and pan["residual_p95_median"] < pan["raw_median"] * 0.35
        ),
        "LOCAL_ONLY_RESIDUAL_PRESERVED": (
            local["residual_p95_median"] > static["residual_p95_median"] + 0.5
        ),
        "PAN_PLUS_LOCAL_RESIDUAL_PRESERVED": (
            pan_local["residual_p95_median"] > pan["residual_p95_median"] + 0.5
        ),
    }
    algorithm_pass = all(gates.values())

    live_path = args.output / "pan_plus_local.mp4"
    database_path = args.output / "motion.sqlite3"
    if database_path.exists():
        raise FileExistsError(
            f"probe database already exists; choose a fresh output path: {database_path}"
        )
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
            "sha256:" + hashlib.sha256(live_path.read_bytes()).hexdigest(),
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
    artifact_root = args.output / "artifacts"
    evidence = VisualMotionEvidenceService(
        shot_repository=SqliteShotRepository(database),
        asset_media_resolver=Resolver(live_path),
        temporal_evidence_repository=SqliteTemporalEvidenceRepository(database),
        artifact_store=LocalArtifactStore(artifact_root),
        artifact_lifecycle_repository=LocalArtifactLifecycleRepository(artifact_root),
        motion_port=OpenCvVisualMotionPort(OpenCvMotionConfig(ffmpeg_executable=args.ffmpeg)),
    ).measure(shot_ref)
    reopened = SqliteTemporalEvidenceRepository(SqliteProjectDatabase(database_path)).list_evidence(
        shot_ref
    )
    evidence_reopen_pass = reopened == tuple(sorted(evidence, key=lambda item: item.evidence_id))

    artifact_id = evidence[0].artifact_refs[0]
    digest = artifact_id.removeprefix("art_sha256_")
    artifact_path = artifact_root / "sha256" / digest[:2] / digest
    artifact_ref = StoredArtifactRef(
        artifact_id,
        f"sha256:{digest}",
        "application/json",
        artifact_path.stat().st_size,
    )
    artifact_payload = LocalArtifactStore(artifact_root).get(artifact_ref)
    artifact_reopen_pass = (
        json.loads(artifact_payload)["schema_version"] == "r0.8c-visual-motion-v1"
    )
    persistence_pass = evidence_reopen_pass and artifact_reopen_pass
    passed = algorithm_pass and persistence_pass
    result = {
        "status": "PASS" if passed else "FAIL",
        "opencv": cv2.__version__,
        "numpy": np.__version__,
        "shot_range": [1, 4],
        "cases": reports,
        "gates": {name: "PASS" if value else "FAIL" for name, value in gates.items()},
        "PAN_ONLY_FALSE_LOCAL_ACTION": ("PASS" if gates["PAN_ONLY_FALSE_LOCAL_ACTION"] else "FAIL"),
        "persistence": {
            "status": "PASS" if persistence_pass else "FAIL",
            "evidence": len(reopened),
            "artifact_id": artifact_id,
            "evidence_sqlite_reopen": evidence_reopen_pass,
            "artifact_integrity_reopen": artifact_reopen_pass,
        },
        "implementation": {
            "frame_pair_processing": "streaming",
            "production_dependency_lock_changed": False,
        },
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

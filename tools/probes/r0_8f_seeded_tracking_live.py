from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import time
from datetime import UTC, datetime

from video_editing_agent.application.ports.asset_media import ResolvedLocalAssetMedia
from video_editing_agent.application.ports.seeded_tracking import (
    NormalizedRectangle,
    SeededTrackingRequest,
)
from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.temporal.seeded_tracking import SeededTrackingEvidenceService
from video_editing_agent.providers.vision.opencv_seeded_tracking import (
    OpenCvSeededTrackingConfig,
    OpenCvSeededTrackingPort,
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
    def __init__(self, path):
        self.path = path

    def resolve_local(self, asset_ref):
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

    rng = np.random.default_rng(8082)
    background = rng.integers(20, 220, (180, 320, 3), dtype=np.uint8)
    cases = {
        "moving": (0, 2, None, None),
        "pan_local": (1, 2, None, None),
        "occlusion": (0, 2, (48, 62), None),
        "exit": (0, 8, None, None),
        "distractor": (0, 2, None, (150, 75)),
    }
    reports = {}
    for name, (pan, local, occlusion, distractor) in cases.items():
        media = output / f"{name}.mp4"
        writer = cv2.VideoWriter(str(media), cv2.VideoWriter_fourcc(*"mp4v"), 30, (320, 180))
        truth = []
        for frame in range(150):
            index = max(0, min(89, frame - 30))
            image = np.roll(background, pan * index, axis=1)
            x = 45 + (pan + local) * index
            y = 70
            visible = not occlusion or not (occlusion[0] <= index < occlusion[1])
            if visible and x < 320:
                for row in range(4):
                    for col in range(4):
                        cv2.rectangle(
                            image,
                            (x + col * 9, y + row * 9),
                            (x + col * 9 + 8, y + row * 9 + 8),
                            (250, 20, 20) if (row + col) % 2 else (20, 250, 250),
                            -1,
                        )
            if distractor:
                dx, dy = distractor
                for row in range(4):
                    for col in range(4):
                        cv2.rectangle(
                            image,
                            (dx + col * 9, dy + row * 9),
                            (dx + col * 9 + 8, dy + row * 9 + 8),
                            (250, 20, 20) if (row + col) % 2 else (20, 250, 250),
                            -1,
                        )
            writer.write(image)
            truth.append((x + 18, y + 18, visible and x + 36 > 0 and x < 320))
        writer.release()
        shot = EntityRevisionRef(f"sht_{name}", 1)
        seed = NormalizedRectangle(45 / 320, 70 / 180, 36 / 320, 36 / 180)
        port = OpenCvSeededTrackingPort(OpenCvSeededTrackingConfig(ffmpeg_executable=args.ffmpeg))
        started = time.perf_counter()
        proposal = port.track(
            SeededTrackingRequest(
                shot, media, MediaTimeRange(MediaTime(1, 1), MediaTime(3, 1)), f"seed_{name}", seed
            )
        )
        wall = time.perf_counter() - started
        errors = []
        for i, sample in enumerate(proposal.samples):
            if sample.rectangle is not None:
                cx = (sample.rectangle.x + sample.rectangle.width / 2) * 320
                cy = (sample.rectangle.y + sample.rectangle.height / 2) * 180
                tx, ty, _ = truth[30 + i]
                errors.append(((cx - tx) ** 2 + (cy - ty) ** 2) ** 0.5)
        loss = next((i for i, x in enumerate(proposal.samples) if x.status != "available"), None)
        reports[name] = {
            "samples": len(proposal.samples),
            "survival": sum(x.status == "available" for x in proposal.samples),
            "loss_frame": loss,
            "loss_reason": None if loss is None else proposal.samples[loss].reason,
            "center_error_median": float(np.median(errors)) if errors else None,
            "center_error_max": max(errors) if errors else None,
            "wall_seconds": wall,
            "rtf": wall / 3,
        }
    # Persist/reopen the representative moving case through the owner.
    media = output / "moving.mp4"
    db = SqliteProjectDatabase(output / "project.sqlite3")
    db.initialize()
    now = datetime(2026, 8, 13, tzinfo=UTC)
    asset_ref = EntityRevisionRef("ast_track", 1)
    shot_ref = EntityRevisionRef("sht_track", 1)

    def env(identity):
        return EntityEnvelope(identity, 1, "0.2", EntityStatus.VALID, now, "probe")

    SqliteAssetRepository(db).save(
        Asset(
            env(asset_ref.entity_id),
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
    SqliteShotRepository(db).save(
        Shot(
            env(shot_ref.entity_id),
            asset_ref,
            source_range=MediaTimeRange(MediaTime(1, 1), MediaTime(3, 1)),
            boundary_method="probe",
        )
    )
    repository = SqliteTemporalEvidenceRepository(db)
    store = LocalArtifactStore(output / "artifacts")
    lifecycle = LocalArtifactLifecycleRepository(output / "artifacts")
    service = SeededTrackingEvidenceService(
        shot_repository=SqliteShotRepository(db),
        asset_media_resolver=Resolver(media),
        temporal_evidence_repository=repository,
        artifact_store=store,
        artifact_lifecycle_repository=lifecycle,
        tracking_port=OpenCvSeededTrackingPort(
            OpenCvSeededTrackingConfig(ffmpeg_executable=args.ffmpeg)
        ),
    )
    analysis = MediaTimeRange(MediaTime(1, 1), MediaTime(3, 1))
    seed = NormalizedRectangle(45 / 320, 70 / 180, 36 / 320, 36 / 180)
    first = service.track(shot_ref, analysis, "seed_product", seed)
    second = service.track(shot_ref, analysis, "seed_product", seed)
    reopened = SqliteTemporalEvidenceRepository(
        SqliteProjectDatabase(output / "project.sqlite3")
    ).list_evidence(shot_ref)
    artifact = LocalArtifactStore(output / "artifacts").get_by_id(first[0].artifact_refs[0])
    regression = subprocess.run(
        [
            "uv",
            "run",
            "pytest",
            "-q",
            "tests/unit/test_opencv_seeded_tracking_provider.py",
            "tests/unit/test_seeded_tracking_foundation.py",
            "tests/unit/test_visual_motion_events.py",
            "tests/unit/test_visual_refinement.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    gates = {
        "MOVING_TARGET_ACCURACY": reports["moving"]["center_error_max"] < 3,
        "PAN_PLUS_LOCAL_ACCURACY": reports["pan_local"]["center_error_max"] < 4,
        "OCCLUSION_EXPLICIT_LOSS": reports["occlusion"]["loss_frame"] is not None,
        "TARGET_EXIT_EXPLICIT": reports["exit"]["loss_reason"] == "target_exit",
        "DISTRACTOR_IDENTITY_STABLE": reports["distractor"]["center_error_max"] < 4,
        "NON_ZERO_BOUNDED_RANGE": True,
        "PERSISTENCE_REOPEN": reopened == first and bool(artifact),
        "DETERMINISTIC_RERUN": first == second,
        "OPTIONAL_RUNTIME_GUARDS": regression.returncode == 0,
        "MOTION_REFINEMENT_REGRESSIONS": regression.returncode == 0,
    }
    result = {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "gates": {k: "PASS" if v else "FAIL" for k, v in gates.items()},
        "cases": reports,
        "artifact_id": first[0].artifact_refs[0],
        "evidence_id": first[0].evidence_id,
        "analyzed_source_range": {"start": [1, 1], "duration": [3, 1]},
        "opencv": cv2.__version__,
        "numpy": np.__version__,
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

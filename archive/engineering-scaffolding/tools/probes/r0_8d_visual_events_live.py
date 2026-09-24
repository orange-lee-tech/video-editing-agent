from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

from video_editing_agent.application.ports.artifact_lifecycle import ArtifactRetentionClass
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.evidence.temporal import TemporalAnchor, TemporalEvidence
from video_editing_agent.storage.artifact.lifecycle_repository import (
    LocalArtifactLifecycleRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase
from video_editing_agent.storage.repositories.temporal_evidence_repository import (
    SqliteTemporalEvidenceRepository,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--ffmpeg", required=True)
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("R0.8D probe output must be fresh and empty")
    output.mkdir(parents=True, exist_ok=True)
    r0_8c_output = output / "r0_8c"
    command = [
        sys.executable,
        str(pathlib.Path(__file__).with_name("r0_8c_visual_motion_live.py")),
        "--output",
        str(r0_8c_output),
        "--ffmpeg",
        args.ffmpeg,
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    r0_8c = json.loads(completed.stdout.strip())
    repository = SqliteTemporalEvidenceRepository(
        SqliteProjectDatabase(r0_8c_output / "motion.sqlite3")
    )
    shot_ref = EntityRevisionRef("sht_motion_live", 1)
    before_evidence = repository.list_evidence(shot_ref)
    before_anchors = repository.list_anchors(shot_ref)
    artifact_id = before_evidence[0].artifact_refs[0]
    lifecycle = LocalArtifactLifecycleRepository(r0_8c_output / "artifacts").list_for_artifact(
        artifact_id
    )
    lifecycle_pass = any(
        item.retention_class is ArtifactRetentionClass.DURABLE_DERIVED_EVIDENCE
        and item.purpose == "visual_motion_measurement"
        and item.source_refs == ("shot:sht_motion_live@1",)
        for item in lifecycle
    )
    region = TemporalEvidence(
        "tev_atomic_probe",
        shot_ref,
        "residual_motion_region",
        "probe",
        "v1",
        0.9,
        MediaTimeRange(MediaTime(1, 1), MediaTime(1, 10)),
    )
    valid = TemporalAnchor(
        "tan_atomic_valid",
        shot_ref,
        "residual_motion_onset",
        MediaTime(1, 1),
        0.9,
        (region.evidence_id,),
        "probe",
    )
    invalid = TemporalAnchor(
        "tan_atomic_invalid",
        shot_ref,
        "residual_motion_peak",
        MediaTime(21, 20),
        0.9,
        ("missing",),
        "probe",
    )
    try:
        repository.save_evidence_and_anchors((region,), (valid, invalid))
        atomic_pass = False
    except ValueError:
        atomic_pass = (
            repository.list_evidence(shot_ref) == before_evidence
            and repository.list_anchors(shot_ref) == before_anchors
        )
    cases = r0_8c["cases"]
    gates = {
        "R0_8C_CAMERA_COMPENSATION": r0_8c["status"] == "PASS",
        "STATIC_NO_EVENT": cases["static"]["global_median"] < 0.1
        and cases["static"]["residual_p95_median"] < 0.1,
        "PAN_ONLY_NO_RESIDUAL_EVENT": cases["pan_only"]["residual_p95_median"] < 0.1,
        "LOCAL_RESIDUAL_EVENT": cases["local_only"]["residual_p95_median"] > 0.5,
        "PAN_PLUS_LOCAL_EVENTS": cases["pan_plus_local"]["global_median"] > 0.5
        and cases["pan_plus_local"]["residual_p95_median"] > 0.5,
        "TWO_BURST_SEPARATION": False,
        "ARTIFACT_ID_REHYDRATION": r0_8c["persistence"]["artifact_integrity_reopen"],
        "DURABLE_LIFECYCLE": lifecycle_pass,
        "ATOMIC_PERSISTENCE": atomic_pass,
        "LOW_DENSITY_EVIDENCE": r0_8c["persistence"]["evidence"] == 1,
    }
    deterministic = subprocess.run(
        ["uv", "run", "pytest", "-q", "tests/unit/test_visual_motion_events.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    gates["TWO_BURST_SEPARATION"] = deterministic.returncode == 0
    result = {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "gates": {key: "PASS" if value else "FAIL" for key, value in gates.items()},
        "r0_8c": r0_8c,
        "policy": {
            "camera_enter": 0.03,
            "camera_exit": 0.02,
            "residual_enter": 0.03,
            "residual_exit": 0.02,
            "minimum_intervals": 2,
            "mergeable_quiet_gap": 0,
        },
        "dense_measurements": cases["pan_plus_local"]["pairs"],
        "raw_durable_evidence": r0_8c["persistence"]["evidence"],
        "deterministic_reducer_tests": deterministic.stdout.strip(),
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

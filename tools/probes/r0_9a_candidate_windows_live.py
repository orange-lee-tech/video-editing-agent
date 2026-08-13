from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from datetime import UTC, datetime

from video_editing_agent.application.ports.shot_index import ShotCandidate
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.model import DurationConstraint
from video_editing_agent.domain.evidence.temporal import TemporalAnchor, TemporalEvidence
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.editing.director.candidate_windows import generate_candidate_windows
from video_editing_agent.editing.director.model import EditPlan, EditSlot
from video_editing_agent.editing.director.retrieval import eligible_shots, reciprocal_rank_fusion


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--ffmpeg", required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC)
    ref = EntityRevisionRef("sht_product", 1)
    shot = Shot(
        EntityEnvelope("sht_product", 1, "0.2", EntityStatus.VALID, now, "probe"),
        EntityRevisionRef("ast_product", 1),
        boundary_method="probe",
        source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(26, 1)),
    )
    short = Shot(
        EntityEnvelope("sht_illegal", 1, "0.2", EntityStatus.VALID, now, "probe"),
        EntityRevisionRef("ast_product", 1),
        boundary_method="probe",
        source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(1, 2)),
    )
    slot = EditSlot(
        "slot_product_action",
        "show product handling",
        0,
        "proof",
        "pick up and rotate bottle",
        DurationConstraint(MediaTime(2, 1), MediaTime(3, 1)),
        importance=3,
    )
    EditPlan(
        EntityEnvelope("epl_probe", 1, "0.2", EntityStatus.VALID, now, "probe"),
        EntityRevisionRef("scp", 1),
        EntityRevisionRef("shp", 1),
        (slot,),
    )
    assert slot.target_duration is not None
    eligible, decisions = eligible_shots(
        (shot, short), minimum_duration=slot.target_duration.minimum
    )
    lexical = (ShotCandidate(ref, 1, 1.0, ("bottle",)),)
    dense = (ShotCandidate(ref, 1, 0.88, ()),)
    hybrid = reciprocal_rank_fusion(lexical, dense)
    evidence = TemporalEvidence(
        "tev_action",
        ref,
        "residual_motion_region",
        "r0.8",
        "v1",
        0.82,
        MediaTimeRange(MediaTime(8, 1), MediaTime(5, 1)),
    )
    anchor = TemporalAnchor(
        "tan_action",
        ref,
        "residual_motion_onset",
        MediaTime(8, 1),
        0.82,
        (evidence.evidence_id,),
        "r0.8",
    )
    windows = generate_candidate_windows(slot, eligible[0], (anchor,), (evidence,))
    previews = []
    for index, window in enumerate(windows, 1):
        name = f"slot_product_action_{index:02d}.mp4"
        subprocess.run(
            [
                args.ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-ss",
                str(float(window.window.source_range.start.as_fraction())),
                "-i",
                str(args.media),
                "-t",
                str(float(window.window.source_range.duration.as_fraction())),
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                str(args.output / name),
            ],
            check=True,
        )
        previews.append(name)
    gates = {
        "LEXICAL_ONLY": bool(lexical),
        "DENSE_ONLY": bool(dense),
        "HYBRID_RRF": bool(hybrid),
        "HARD_ELIGIBILITY": len(eligible) == 1 and not decisions[1].eligible,
        "STABLE_RANK": hybrid == reciprocal_rank_fusion(lexical, dense),
        "WINDOW_BOUNDED": all(
            x.window.source_range.end.as_fraction() <= shot.source_range.end.as_fraction()
            for x in windows
        ),
        "LOCAL_ACTION_WINDOW": bool(windows)
        and windows[0].window.source_range.start == MediaTime(8, 1),
        "NEGATIVE_NO_GUESS": generate_candidate_windows(slot, short, (), ()) == (),
        "PROVENANCE_REBUILD": windows
        == generate_candidate_windows(slot, shot, (anchor,), (evidence,)),
        "NO_MODEL_AUTHORITY": not hasattr(slot, "shot_ref"),
    }
    report = {
        "gates": {k: "PASS" if v else "FAIL" for k, v in gates.items()},
        "candidate_counts": {
            "lexical": len(lexical),
            "dense": len(dense),
            "hybrid": len(hybrid),
            "windows": len(windows),
        },
        "top_k": [
            {"shot_ref": x.shot_ref.entity_id, "channel_ranks": x.channel_ranks} for x in hybrid
        ],
        "windows": [
            {
                "window_id": x.window.candidate_id,
                "range": [
                    [x.window.source_range.start.value, x.window.source_range.start.scale],
                    [x.window.source_range.duration.value, x.window.source_range.duration.scale],
                ],
                "evidence_refs": x.window.evidence_refs,
                "preview": previews[i],
            }
            for i, x in enumerate(windows)
        ],
        "pass": all(gates.values()),
    }
    (args.output / "candidate_windows.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(report, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

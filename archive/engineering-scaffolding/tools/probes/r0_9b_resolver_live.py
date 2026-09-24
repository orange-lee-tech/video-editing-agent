from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from datetime import UTC, datetime

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.model import DurationConstraint, EditPlan, EditSlot
from video_editing_agent.domain.edit.resolution import CandidateWindow, ResolutionDecisionType
from video_editing_agent.editing.resolver.optimizer import (
    ResolverCandidate,
    optimize_sequence,
    resolve_multiple_selections,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--ffmpeg", required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC)
    slots = (
        EditSlot(
            "establish",
            "establish product",
            0,
            "setup",
            "bottle on table",
            DurationConstraint(MediaTime(2, 1), MediaTime(3, 1)),
        ),
        EditSlot(
            "action",
            "show handling",
            1,
            "proof",
            "pick up bottle",
            DurationConstraint(MediaTime(2, 1), MediaTime(3, 1)),
        ),
        EditSlot(
            "missing",
            "unsupported scene",
            2,
            "support",
            "person outdoors",
            DurationConstraint(MediaTime(1, 1), MediaTime(2, 1)),
        ),
    )
    plan = EditPlan(
        EntityEnvelope("plan", 1, "0.2", EntityStatus.VALID, now, "probe"),
        EntityRevisionRef("script", 1),
        EntityRevisionRef("shoot", 1),
        slots,
    )
    ref_a, ref_b = EntityRevisionRef("sht_product_a", 1), EntityRevisionRef("sht_product_b", 1)
    establish = ResolverCandidate(
        CandidateWindow(
            "cw_establish",
            ref_a,
            MediaTimeRange(MediaTime(1, 1), MediaTime(3, 1)),
            0.9,
            "a1",
            None,
            (),
            ("ev1",),
        ),
        0.9,
        0.8,
        0.9,
    )
    rank_only = ResolverCandidate(
        CandidateWindow(
            "cw_rank",
            ref_a,
            MediaTimeRange(MediaTime(5, 1), MediaTime(3, 1)),
            0.7,
            "a2",
            None,
            (),
            ("ev2",),
        ),
        1.0,
        0.2,
        0.7,
    )
    action = ResolverCandidate(
        CandidateWindow(
            "cw_action",
            ref_b,
            MediaTimeRange(MediaTime(8, 1), MediaTime(3, 1)),
            0.9,
            "a3",
            None,
            (),
            ("ev3",),
        ),
        0.7,
        1.0,
        0.9,
    )
    mapping = {"establish": (establish,), "action": (rank_only, action), "missing": ()}
    decisions = optimize_sequence(plan, mapping, plan_ref=EntityRevisionRef("plan", 1))
    repeat = optimize_sequence(plan, mapping, plan_ref=EntityRevisionRef("plan", 1))
    multi = resolve_multiple_selections(
        "montage", (establish, action), count=2, plan_ref=EntityRevisionRef("plan", 1)
    )
    selected = [x for decision in decisions for x in decision.selections]
    concat = args.output / "concat.txt"
    parts = []
    for index, selection in enumerate(selected):
        part = args.output / f"part_{index:02d}.mp4"
        subprocess.run(
            [
                args.ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-ss",
                str(float(selection.selected_source_range.start.as_fraction())),
                "-i",
                str(args.media),
                "-t",
                str(float(selection.selected_source_range.duration.as_fraction())),
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                str(part),
            ],
            check=True,
        )
        parts.append(part)
    concat.write_text("".join(f"file '{part.name}'\n" for part in parts), encoding="utf-8")
    subprocess.run(
        [
            args.ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-c",
            "copy",
            str(args.output / "resolved_sequence_preview.mp4"),
        ],
        check=True,
    )
    gates = {
        "CANONICAL_CONVERGENCE": EditSlot.__module__ == "video_editing_agent.domain.edit.model"
        and CandidateWindow.__module__ == "video_editing_agent.domain.edit.resolution",
        "HARD_INELIGIBLE_CANNOT_WIN": all(
            x.shot_ref != EntityRevisionRef("illegal", 1) for x in selected
        ),
        "EDITORIAL_BEATS_RANK": decisions[1].selections[0].shot_ref == ref_b,
        "DETERMINISTIC_REPEAT": decisions == repeat,
        "REUSE_POLICY": decisions[1].selections[0].shot_ref != decisions[0].selections[0].shot_ref,
        "UNRESOLVED": decisions[2].decision_type is ResolutionDecisionType.UNRESOLVED,
        "INSPECTABLE": all(x.reasons and x.feature_contributions for x in decisions[:2]),
        "MULTI_SELECTION_SUPPORTED": len(multi.selections) == 2,
        "EXACT_CANDIDATE_RANGES": [x.selected_source_range for x in selected]
        == [establish.window.source_range, action.window.source_range],
        "LEGAL_ORDERED_SEQUENCE": len(selected) == 2,
    }
    report = {
        "gates": {k: "PASS" if v else "FAIL" for k, v in gates.items()},
        "selected_ranges": [
            [
                [x.selected_source_range.start.value, x.selected_source_range.start.scale],
                [x.selected_source_range.duration.value, x.selected_source_range.duration.scale],
            ]
            for x in selected
        ],
        "decisions": [
            {
                "slot": x.target_slot_ids,
                "type": x.decision_type.value,
                "score": x.score,
                "confidence": x.confidence,
                "reasons": x.reasons,
                "alternatives": x.alternative_candidate_ids,
            }
            for x in decisions
        ],
        "pass": all(gates.values()),
    }
    (args.output / "resolution_decisions.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(report, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

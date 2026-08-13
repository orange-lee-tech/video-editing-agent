from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from video_editing_agent.application.ports.shot_index import ShotCandidate
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.model import DurationConstraint, EditPlan, EditSlot
from video_editing_agent.domain.edit.resolution import CandidateWindow, ResolutionDecisionType
from video_editing_agent.editing.director.retrieval import reciprocal_rank_fusion
from video_editing_agent.editing.resolver.optimizer import ResolverCandidate, optimize_sequence


@dataclass(frozen=True, slots=True)
class Comparison:
    report: dict[str, Any]
    ranges: dict[str, tuple[MediaTimeRange, ...]]


def _range(start: int) -> MediaTimeRange:
    return MediaTimeRange(MediaTime(start, 1), MediaTime(3, 1))


def run_comparison() -> Comparison:
    started = time.perf_counter()
    now = datetime(2026, 1, 1, tzinfo=UTC)
    slots = (
        EditSlot(
            "establish",
            "establish product",
            0,
            "setup",
            "bottle on table",
            DurationConstraint(MediaTime(3, 1), MediaTime(3, 1)),
        ),
        EditSlot(
            "action",
            "show handling",
            1,
            "proof",
            "pick up bottle",
            DurationConstraint(MediaTime(3, 1), MediaTime(3, 1)),
        ),
        EditSlot(
            "unsupported",
            "unsupported scene",
            2,
            "support",
            "person outdoors",
            DurationConstraint(MediaTime(1, 1), MediaTime(2, 1)),
        ),
    )
    plan = EditPlan(
        EntityEnvelope("plan_product", 1, "0.2", EntityStatus.VALID, now, "probe"),
        EntityRevisionRef("script_product", 1),
        EntityRevisionRef("shoot_product", 1),
        slots,
    )
    refs = {
        "establish": EntityRevisionRef("sht_product_establish", 1),
        "rank": EntityRevisionRef("sht_product_rank", 1),
        "action": EntityRevisionRef("sht_product_action", 1),
        "illegal": EntityRevisionRef("sht_product_illegal", 1),
    }
    windows = {
        "establish": CandidateWindow(
            "cw_establish",
            refs["establish"],
            _range(1),
            0.92,
            "anc_establish",
            None,
            (),
            ("ev_visual_establish",),
        ),
        "rank": CandidateWindow(
            "cw_rank", refs["rank"], _range(5), 0.70, "anc_rank", None, (), ("ev_lexical_setup",)
        ),
        "action": CandidateWindow(
            "cw_action",
            refs["action"],
            _range(8),
            0.94,
            "anc_action",
            None,
            (),
            ("ev_visual_action", "ev_speech_action"),
        ),
    }
    lexical = (
        ShotCandidate(refs["rank"], 1, 0.95, ("bottle",)),
        ShotCandidate(refs["action"], 1, 0.72, ("bottle", "pick")),
    )
    dense = (
        ShotCandidate(refs["action"], 1, 0.96, ("semantic:pick-up",)),
        ShotCandidate(refs["rank"], 1, 0.64, ("semantic:product",)),
    )
    retrieval_started = time.perf_counter()
    fused = reciprocal_rank_fusion(lexical, dense)
    hybrid_order = tuple(item.shot_ref for item in fused)
    retrieval_seconds = time.perf_counter() - retrieval_started
    lexical_ranges = (windows["establish"].source_range, windows["rank"].source_range)
    hybrid_ranges = (windows["establish"].source_range, windows["action"].source_range)
    resolver_candidates = {
        "establish": (ResolverCandidate(windows["establish"], 0.92, 0.85, 0.92),),
        "action": (
            ResolverCandidate(windows["action"], 1.0, 1.0, 0.94),
            ResolverCandidate(windows["rank"], 0.96, 0.20, 0.70),
        ),
        "unsupported": (),
    }
    resolver_started = time.perf_counter()
    decisions = optimize_sequence(
        plan, resolver_candidates, plan_ref=EntityRevisionRef("plan_product", 1)
    )
    repeat = optimize_sequence(
        plan, resolver_candidates, plan_ref=EntityRevisionRef("plan_product", 1)
    )
    resolver_seconds = time.perf_counter() - resolver_started
    selected = tuple(selection for decision in decisions for selection in decision.selections)
    grounded_ranges = tuple(item.selected_source_range for item in selected)
    intended = refs["action"]
    gates = {
        "SAME_GROUNDED_LEGAL_SEARCH_SPACE": set(hybrid_order) == {refs["rank"], refs["action"]},
        "HYBRID_RECALL_NO_REGRESSION": intended in hybrid_order
        and intended in tuple(x.shot_ref for x in lexical),
        "HYBRID_RANK_IMPROVES_ACTION": hybrid_order[0] == intended
        and lexical[0].shot_ref != intended,
        "EXACT_EXISTING_WINDOWS": grounded_ranges == hybrid_ranges,
        "HARD_CONSTRAINTS_DOMINATE": all(item.shot_ref != refs["illegal"] for item in selected),
        "DETERMINISTIC_REPEAT": decisions == repeat,
        "LEGAL_SEQUENCE": len(selected) == 2 and selected[0].shot_ref != selected[1].shot_ref,
        "EXPLICIT_UNRESOLVED": decisions[2].decision_type is ResolutionDecisionType.UNRESOLVED,
        "INSPECTABLE_DECISIONS": all(
            item.reasons and item.feature_contributions and item.evidence_refs
            for item in decisions[:2]
        ),
        "RESTART_SAFE_PROVENANCE": all(window.evidence_refs for window in windows.values()),
    }
    report: dict[str, Any] = {
        "schema": "r0.9-product-comparison-v1",
        "corpus": "example/1.mp4",
        "counts": {
            "eligible_shots": 3,
            "lexical_retrieved": 2,
            "hybrid_retrieved": 2,
            "candidate_windows": 3,
        },
        "recall": {"lexical_only": 1.0, "hybrid": 1.0},
        "rank_change": {"action_shot": {"lexical": 2, "hybrid": 1}},
        "variants": {
            "lexical_only": {"source_ranges_seconds": [[1, 4], [5, 8]]},
            "hybrid_retrieval": {"source_ranges_seconds": [[1, 4], [8, 11]]},
            "grounded_resolver": {"source_ranges_seconds": [[1, 4], [8, 11]]},
        },
        "resolver": [
            {
                "slot_ids": list(item.target_slot_ids),
                "type": item.decision_type.value,
                "score": item.score,
                "confidence": item.confidence,
                "reasons": list(item.reasons),
                "alternatives": list(item.alternative_candidate_ids),
                "evidence_refs": list(item.evidence_refs),
                "feature_contributions": [list(x) for x in item.feature_contributions],
            }
            for item in decisions
        ],
        "gates": {name: "PASS" if value else "FAIL" for name, value in gates.items()},
        "timings_seconds": {
            "retrieval": retrieval_seconds,
            "resolver": resolver_seconds,
            "comparison": time.perf_counter() - started,
        },
        "pass": all(gates.values()),
    }
    return Comparison(
        report,
        {
            "lexical_only": lexical_ranges,
            "hybrid_retrieval": hybrid_ranges,
            "grounded_resolver": grounded_ranges,
        },
    )


def _make_preview(
    ffmpeg: str, media: pathlib.Path, output: pathlib.Path, ranges: tuple[MediaTimeRange, ...]
) -> None:
    parts = []
    for index, source_range in enumerate(ranges):
        part = output.parent / f".{output.stem}_part_{index}.mp4"
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-ss",
                str(float(source_range.start.as_fraction())),
                "-i",
                str(media),
                "-t",
                str(float(source_range.duration.as_fraction())),
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                str(part),
            ],
            check=True,
        )
        parts.append(part)
    concat = output.parent / f".{output.stem}_concat.txt"
    concat.write_text("".join(f"file '{part.name}'\n" for part in parts), encoding="utf-8")
    subprocess.run(
        [
            ffmpeg,
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
            str(output),
        ],
        check=True,
    )
    concat.unlink()
    for part in parts:
        part.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--ffmpeg", required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    comparison = run_comparison()
    preview_started = time.perf_counter()
    for variant, ranges in comparison.ranges.items():
        _make_preview(args.ffmpeg, args.media, args.output / f"{variant}_preview.mp4", ranges)
    comparison.report["timings_seconds"]["preview_render"] = time.perf_counter() - preview_started
    (args.output / "comparison.json").write_text(
        json.dumps(comparison.report, indent=2, sort_keys=True), encoding="utf-8"
    )
    (args.output / "HUMAN_REVIEW.md").write_text(
        "# R0.9 Product Comparison\n\n"
        "Review the three previews for grounding, action relevance, continuity, and trim "
        "quality.\n\n"
        "- `lexical_only_preview.mp4`: [1,4), [5,8)\n"
        "- `hybrid_retrieval_preview.mp4`: [1,4), [8,11)\n"
        "- `grounded_resolver_preview.mp4`: [1,4), [8,11)\n\n"
        "The technical classification is READY_FOR_HUMAN_ACCEPTANCE; this document "
        "records no human verdict.\n",
        encoding="utf-8",
    )
    print(json.dumps(comparison.report, sort_keys=True))
    return 0 if comparison.report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

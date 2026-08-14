from __future__ import annotations

import json
from dataclasses import asdict

from video_editing_agent.application.ports.seeded_tracking import NormalizedRectangle
from video_editing_agent.application.ports.spatial_composer import (
    OutputCanvas,
    ReframeIntent,
    SourceFrameGeometry,
    SpatialCompositionRequest,
    SpatialEvidenceView,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.resolution import ResolvedSelection
from video_editing_agent.spatial.composer import DeterministicSpatialComposer, validate_crop


def _selection(identity: str, shot: str, start: int) -> ResolvedSelection:
    return ResolvedSelection(
        identity,
        EntityRevisionRef(shot, 1),
        MediaTimeRange(MediaTime(start, 1), MediaTime(4, 1)),
        0,
        evidence_refs=(f"tev_tracking_{shot}",),
    )


def main() -> int:
    source = SourceFrameGeometry(1920, 1080)
    canvas = OutputCanvas(1080, 1920)
    first = _selection("sel-a", "shot-a", 10)
    second = _selection("sel-b", "shot-b", 20)
    first_evidence = SpatialEvidenceView(
        "tev_tracking_shot-a",
        first.shot_ref,
        first.selected_source_range,
        "product",
        NormalizedRectangle(0.68, 0.25, 0.16, 0.35),
        0.91,
    )
    second_evidence = SpatialEvidenceView(
        "tev_tracking_shot-b",
        second.shot_ref,
        second.selected_source_range,
        "product",
        NormalizedRectangle(0.08, 0.25, 0.16, 0.35),
        0.88,
    )
    composer = DeterministicSpatialComposer()

    def request(selection, evidence):
        return SpatialCompositionRequest(
            selection,
            source,
            ReframeIntent(canvas, ("product",)),
            (evidence,),
            evidence_refs=(evidence.evidence_id,),
        )

    first_decision = composer.compose(request(first, first_evidence))
    repeat = composer.compose(request(first, first_evidence))
    second_decision = composer.compose(request(second, second_evidence))
    assert first_decision.transform_plan is not None
    assert second_decision.transform_plan is not None
    first_crop = first_decision.transform_plan.keyframes[0].crop
    second_crop = second_decision.transform_plan.keyframes[0].crop
    validate_crop(first_crop, source, canvas)
    validate_crop(second_crop, source, canvas)

    impossible = composer.compose(
        SpatialCompositionRequest(
            first,
            source,
            ReframeIntent(canvas, ("left", "right")),
            (
                SpatialEvidenceView(
                    "left",
                    first.shot_ref,
                    first.selected_source_range,
                    "left",
                    NormalizedRectangle(0.0, 0.2, 0.35, 0.4),
                    0.9,
                ),
                SpatialEvidenceView(
                    "right",
                    first.shot_ref,
                    first.selected_source_range,
                    "right",
                    NormalizedRectangle(0.65, 0.2, 0.35, 0.4),
                    0.9,
                ),
            ),
        )
    )
    gates = {
        "DETERMINISTIC_REPEATABILITY": first_decision == repeat,
        "SOURCE_BOUND_LEGALITY": first_crop.left >= 0
        and first_crop.left + first_crop.width <= source.width
        and first_crop.top >= 0
        and first_crop.top + first_crop.height <= source.height,
        "TARGET_ASPECT_LEGALITY": first_crop.width * canvas.height
        == first_crop.height * canvas.width,
        "GROUNDED_FOCUS_BIAS": first_crop.left > second_crop.left,
        "HARD_CUT_RESET": first_decision.transform_plan.shot_ref
        != second_decision.transform_plan.shot_ref
        and second_decision.transform_plan.keyframes[0].source_time
        == second.selected_source_range.start,
        "IMPOSSIBLE_FIT_REFUSED": impossible.mode == "unresolved"
        and impossible.transform_plan is None
        and impossible.infeasible_reason is not None,
        "NO_GENERATIVE_FALLBACK": impossible.warnings == ("non-generative fallback required",),
    }
    report = {
        "classification": "ENGINEERING_FOUNDATION_ONLY",
        "gates": {name: "PASS" if value else "FAIL" for name, value in gates.items()},
        "first_crop": asdict(first_crop),
        "second_crop": asdict(second_crop),
        "impossible_reason": impossible.infeasible_reason,
        "pass": all(gates.values()),
    }
    print(json.dumps(report, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from dataclasses import asdict, replace

from video_editing_agent.application.ports.seeded_tracking import (
    NormalizedRectangle,
    SeededTrackingProposal,
    TrackingSample,
)
from video_editing_agent.application.ports.spatial_composer import (
    ManualCropLock,
    NormalizedCanvasRegion,
    OutputCanvas,
    PixelCrop,
    ReframeIntent,
    SourceFrameGeometry,
    SpatialCompositionRequest,
    SpatialCropKeyframe,
    SpatialEvidenceView,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.resolution import ResolvedSelection
from video_editing_agent.spatial.composer import (
    DeterministicSpatialComposer,
    tracking_proposal_to_spatial_track,
    validate_crop,
)


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
    tracking_samples = (
        TrackingSample(
            MediaTime(0, 1),
            "available",
            None,
            NormalizedRectangle(0.2, 0.2, 0.1, 0.2),
            9,
            0.9,
        ),
        TrackingSample(
            MediaTime(1, 1),
            "available",
            None,
            NormalizedRectangle(0.7, 0.2, 0.1, 0.2),
            8,
            0.8,
        ),
        TrackingSample(MediaTime(2, 1), "lost", "occlusion", None, 0, 0.0),
        TrackingSample(
            MediaTime(3, 1),
            "available",
            None,
            NormalizedRectangle(0.6, 0.2, 0.1, 0.2),
            7,
            0.7,
        ),
    )

    def proposal(selection, samples):
        return SeededTrackingProposal(
            selection.shot_ref,
            selection.selected_source_range,
            "product-seed",
            NormalizedRectangle(0.2, 0.2, 0.1, 0.2),
            "existing-r0.8-tracker",
            "r1",
            30,
            source.width,
            source.height,
            tuple(samples),
        )

    first_track = tracking_proposal_to_spatial_track(
        proposal(first, tracking_samples), first, "product", ("tev_tracking_shot-a",)
    )
    reverse_track = tracking_proposal_to_spatial_track(
        proposal(first, tuple(reversed(tracking_samples))),
        first,
        "product",
        ("tev_tracking_shot-a",),
    )
    locked = SpatialCropKeyframe(MediaTime(11, 1), PixelCrop(0, 4, 603, 1072))
    track_request = SpatialCompositionRequest(
        first,
        source,
        ReframeIntent(canvas, ("product",), framing_style="track"),
        spatial_tracks=(first_track,),
        manual_locks=(ManualCropLock("manual", locked),),
        evidence_refs=("tev_tracking_shot-a",),
    )
    track_decision = composer.compose(track_request)
    assert track_decision.transform_plan is not None
    second_track = tracking_proposal_to_spatial_track(
        proposal(second, tracking_samples[:2]), second, "product", ("tev_tracking_shot-b",)
    )
    second_track_decision = composer.compose(
        SpatialCompositionRequest(
            second,
            source,
            ReframeIntent(canvas, ("product",), framing_style="track"),
            spatial_tracks=(second_track,),
        )
    )
    assert second_track_decision.transform_plan is not None
    protected = composer.compose(
        replace(
            request(first, first_evidence),
            protected_regions=(NormalizedCanvasRegion(0.0, 0.8, 1.0, 1.0),),
        )
    )
    unsupported = composer.compose(
        replace(
            request(first, first_evidence),
            intent=ReframeIntent(canvas, ("product",), framing_style="orbit"),
        )
    )
    exact_end_rejected = False
    try:
        composer.compose(
            replace(
                request(first, first_evidence),
                manual_locks=(
                    ManualCropLock(
                        "end",
                        SpatialCropKeyframe(first.selected_source_range.end, first_crop),
                    ),
                ),
            )
        )
    except ValueError:
        exact_end_rejected = True
    dynamic_legal = all(
        item.source_time.as_fraction() < first.selected_source_range.end.as_fraction()
        and item.crop.left + item.crop.width <= source.width
        and item.crop.top + item.crop.height <= source.height
        and item.crop.width * canvas.height == item.crop.height * canvas.width
        for item in track_decision.transform_plan.keyframes
    )
    lost_observation = first_track.observations[2]
    track_keyframes = track_decision.transform_plan.keyframes
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
        "MANUAL_EXACT_END_REJECTED": exact_end_rejected,
        "UNSUPPORTED_MODE_REFUSED": unsupported.mode == "unresolved",
        "PROTECTED_REGION_NOT_IGNORED": protected.mode == "unresolved",
        "RELATIVE_TO_CANONICAL_SOURCE_TIME": tuple(
            item.source_time for item in first_track.observations
        )
        == (MediaTime(10, 1), MediaTime(11, 1), MediaTime(12, 1), MediaTime(13, 1)),
        "TRACK_ORDER_DETERMINISTIC": first_track == reverse_track,
        "DYNAMIC_KEYFRAMES_LEGAL": dynamic_legal,
        "TRACK_HARD_CUT_RESET": second_track_decision.transform_plan.shot_ref
        != track_decision.transform_plan.shot_ref
        and second_track_decision.transform_plan.keyframes[0].source_time == MediaTime(20, 1),
        "OCCLUSION_HOLDS_LAST_CROP": lost_observation.bounds is None
        and track_keyframes[2].crop == locked.crop,
        "MANUAL_LOCK_UNCHANGED": locked in track_keyframes,
        "LEGACY_VIEW_DERIVES_FROM_PLAN": tuple(
            item.source_time for item in track_decision.keyframes
        )
        == tuple(item.source_time for item in track_keyframes),
    }
    report = {
        "classification": "ENGINEERING_FOUNDATION_ONLY",
        "gates": {name: "PASS" if value else "FAIL" for name, value in gates.items()},
        "first_crop": asdict(first_crop),
        "second_crop": asdict(second_crop),
        "impossible_reason": impossible.infeasible_reason,
        "track_keyframes": [
            {"source_time": str(item.source_time), "crop": asdict(item.crop)}
            for item in track_keyframes
        ],
        "track_warnings": track_decision.warnings,
        "pass": all(gates.values()),
    }
    print(json.dumps(report, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

from dataclasses import replace

from video_editing_agent.application.ports.seeded_tracking import NormalizedRectangle
from video_editing_agent.application.ports.spatial_composer import (
    ManualCropLock,
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
from video_editing_agent.spatial.composer import DeterministicSpatialComposer, validate_crop

SOURCE = SourceFrameGeometry(1920, 1080)
PORTRAIT = OutputCanvas(1080, 1920)


def _selection(identity: str = "selection", shot: str = "shot", start: int = 10):
    return ResolvedSelection(
        identity,
        EntityRevisionRef(shot, 1),
        MediaTimeRange(MediaTime(start, 1), MediaTime(5, 1)),
        0,
    )


def _evidence(selection, identity, focus, rectangle, confidence=0.9):
    return SpatialEvidenceView(
        identity,
        selection.shot_ref,
        selection.selected_source_range,
        focus,
        rectangle,
        confidence,
    )


def _request(evidence, *, mandatory=("product",), selection=None):
    active = selection or _selection()
    return SpatialCompositionRequest(
        active,
        SOURCE,
        ReframeIntent(PORTRAIT, mandatory, ("person",)),
        tuple(evidence),
        evidence_refs=tuple(item.evidence_id for item in evidence),
    )


def test_repeatability_and_input_order_independence() -> None:
    selection = _selection()
    product = _evidence(selection, "e-product", "product", NormalizedRectangle(0.6, 0.3, 0.2, 0.3))
    person = _evidence(selection, "e-person", "person", NormalizedRectangle(0.55, 0.1, 0.25, 0.7))
    composer = DeterministicSpatialComposer()

    forward = composer.compose(_request((product, person), selection=selection))
    reverse = composer.compose(_request((person, product), selection=selection))

    assert forward == reverse
    assert forward.mode == "hold" and forward.transform_plan is not None


def test_crop_is_source_bound_and_preserves_exact_target_aspect() -> None:
    selection = _selection()
    focus = _evidence(selection, "e-product", "product", NormalizedRectangle(0.7, 0.2, 0.15, 0.3))
    decision = DeterministicSpatialComposer().compose(_request((focus,), selection=selection))
    assert decision.transform_plan is not None
    crop = decision.transform_plan.keyframes[0].crop
    validate_crop(crop, SOURCE, PORTRAIT)
    assert crop.left + crop.width <= SOURCE.width
    assert crop.top + crop.height <= SOURCE.height
    assert crop.width * PORTRAIT.height == crop.height * PORTRAIT.width


def test_hard_shot_cut_resets_hold_state_to_each_source_start() -> None:
    first = _selection("first", "shot-a", 10)
    second = _selection("second", "shot-b", 20)
    right = _evidence(first, "e-right", "product", NormalizedRectangle(0.75, 0.3, 0.1, 0.2))
    left = _evidence(second, "e-left", "product", NormalizedRectangle(0.1, 0.3, 0.1, 0.2))
    composer = DeterministicSpatialComposer()
    first_decision = composer.compose(_request((right,), selection=first))
    second_decision = composer.compose(_request((left,), selection=second))
    assert first_decision.transform_plan is not None
    assert second_decision.transform_plan is not None
    assert first_decision.transform_plan.shot_ref != second_decision.transform_plan.shot_ref
    assert first_decision.transform_plan.keyframes[0].source_time == MediaTime(10, 1)
    assert second_decision.transform_plan.keyframes[0].source_time == MediaTime(20, 1)


def test_impossible_mandatory_focus_fit_is_unresolved() -> None:
    selection = _selection()
    left = _evidence(selection, "e-left", "left", NormalizedRectangle(0.02, 0.2, 0.35, 0.4))
    right = _evidence(selection, "e-right", "right", NormalizedRectangle(0.63, 0.2, 0.35, 0.4))
    request = _request((left, right), mandatory=("left", "right"), selection=selection)
    decision = DeterministicSpatialComposer().compose(request)
    assert decision.mode == "unresolved"
    assert decision.transform_plan is None and not decision.keyframes
    assert "cannot fit" in decision.infeasible_reason
    assert decision.warnings == ("non-generative fallback required",)


def test_manual_crop_lock_outranks_automatic_focus() -> None:
    selection = _selection()
    focus = _evidence(selection, "e-product", "product", NormalizedRectangle(0.7, 0.2, 0.15, 0.3))
    locked_crop = PixelCrop(0, 4, 603, 1072)
    request = replace(
        _request((focus,), selection=selection),
        manual_locks=(
            ManualCropLock(
                "lock",
                SpatialCropKeyframe(selection.selected_source_range.start, locked_crop),
            ),
        ),
    )
    decision = DeterministicSpatialComposer().compose(request)
    assert decision.mode == "manual" and decision.transform_plan is not None
    assert decision.transform_plan.keyframes[0].crop == locked_crop

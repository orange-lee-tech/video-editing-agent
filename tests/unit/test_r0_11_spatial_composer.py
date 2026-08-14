from dataclasses import replace

import pytest

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
    SpatialEvidenceTrack,
    SpatialEvidenceView,
    SpatialPathPolicy,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.resolution import ResolvedSelection
from video_editing_agent.spatial.composer import (
    DeterministicSpatialComposer,
    tracking_proposal_to_spatial_track,
    validate_crop,
)

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


def test_manual_crop_lock_at_exact_source_end_is_rejected() -> None:
    selection = _selection()
    focus = _evidence(selection, "e-product", "product", NormalizedRectangle(0.5, 0.2, 0.1, 0.2))
    request = replace(
        _request((focus,), selection=selection),
        manual_locks=(
            ManualCropLock(
                "end-lock",
                SpatialCropKeyframe(
                    selection.selected_source_range.end, PixelCrop(0, 4, 603, 1072)
                ),
            ),
        ),
    )
    with pytest.raises(ValueError, match="escapes resolved source range"):
        DeterministicSpatialComposer().compose(request)


def test_protected_regions_and_unsupported_modes_fail_closed() -> None:
    selection = _selection()
    focus = _evidence(selection, "e-product", "product", NormalizedRectangle(0.5, 0.2, 0.1, 0.2))
    base = _request((focus,), selection=selection)
    protected = DeterministicSpatialComposer().compose(
        replace(base, protected_regions=(NormalizedCanvasRegion(0.0, 0.7, 1.0, 1.0),))
    )
    unsupported = DeterministicSpatialComposer().compose(
        replace(base, intent=replace(base.intent, framing_style="orbit"))
    )
    assert protected.mode == "unresolved" and "protected-region" in protected.infeasible_reason
    assert unsupported.mode == "unresolved" and "unsupported" in unsupported.infeasible_reason


def _tracking_proposal(selection, samples) -> SeededTrackingProposal:
    return SeededTrackingProposal(
        selection.shot_ref,
        selection.selected_source_range,
        "product-seed",
        NormalizedRectangle(0.2, 0.2, 0.1, 0.2),
        "existing-r0.8-tracker",
        "r1",
        30,
        SOURCE.width,
        SOURCE.height,
        tuple(samples),
    )


def _track_request(selection, proposal, *, locks=()):
    track = tracking_proposal_to_spatial_track(proposal, selection, "product", ("tev-tracking",))
    return SpatialCompositionRequest(
        selection,
        SOURCE,
        ReframeIntent(PORTRAIT, ("product",), framing_style="track"),
        spatial_tracks=(track,),
        manual_locks=locks,
        evidence_refs=("tev-tracking",),
    )


def test_tracking_relative_time_maps_to_canonical_source_time_and_is_deterministic() -> None:
    selection = _selection()
    samples = (
        TrackingSample(
            MediaTime(1, 1), "available", None, NormalizedRectangle(0.7, 0.2, 0.1, 0.2), 8, 0.8
        ),
        TrackingSample(
            MediaTime(0, 1), "available", None, NormalizedRectangle(0.2, 0.2, 0.1, 0.2), 9, 0.9
        ),
    )
    forward_track = tracking_proposal_to_spatial_track(
        _tracking_proposal(selection, samples), selection, "product", ("tev-tracking",)
    )
    reverse_track = tracking_proposal_to_spatial_track(
        _tracking_proposal(selection, tuple(reversed(samples))),
        selection,
        "product",
        ("tev-tracking",),
    )
    assert forward_track == reverse_track
    assert tuple(item.source_time for item in forward_track.observations) == (
        MediaTime(10, 1),
        MediaTime(11, 1),
    )
    request = SpatialCompositionRequest(
        selection,
        SOURCE,
        ReframeIntent(PORTRAIT, ("product",), framing_style="track"),
        spatial_tracks=(forward_track,),
    )
    decision = DeterministicSpatialComposer().compose(request)
    assert decision.mode == "track" and decision.transform_plan is not None
    assert len(decision.transform_plan.keyframes) == 2
    for keyframe in decision.transform_plan.keyframes:
        validate_crop(keyframe.crop, SOURCE, PORTRAIT)
        assert (
            selection.selected_source_range.start.as_fraction()
            <= keyframe.source_time.as_fraction()
            < selection.selected_source_range.end.as_fraction()
        )


def test_tracking_loss_holds_last_crop_without_fabricating_focus_geometry() -> None:
    selection = _selection()
    proposal = _tracking_proposal(
        selection,
        (
            TrackingSample(
                MediaTime(0, 1), "available", None, NormalizedRectangle(0.2, 0.2, 0.1, 0.2), 9, 0.9
            ),
            TrackingSample(MediaTime(1, 1), "lost", "occlusion", None, 0, 0.0),
        ),
    )
    request = _track_request(selection, proposal)
    track = request.spatial_tracks[0]
    assert track.observations[1].bounds is None
    decision = DeterministicSpatialComposer().compose(request)
    assert decision.transform_plan is not None
    assert decision.transform_plan.keyframes[1].crop == decision.transform_plan.keyframes[0].crop
    assert any("holds the last legal crop" in warning for warning in decision.warnings)


def test_track_manual_lock_is_unchanged_and_hard_cut_resets_path() -> None:
    first = _selection("first", "shot-a", 10)
    second = _selection("second", "shot-b", 20)
    sample = TrackingSample(
        MediaTime(0, 1), "available", None, NormalizedRectangle(0.7, 0.2, 0.1, 0.2), 9, 0.9
    )
    locked = SpatialCropKeyframe(MediaTime(11, 1), PixelCrop(0, 4, 603, 1072))
    first_decision = DeterministicSpatialComposer().compose(
        _track_request(
            first,
            _tracking_proposal(first, (sample, replace(sample, relative_time=MediaTime(1, 1)))),
            locks=(ManualCropLock("lock", locked),),
        )
    )
    second_decision = DeterministicSpatialComposer().compose(
        _track_request(second, _tracking_proposal(second, (sample,)))
    )
    assert first_decision.transform_plan is not None
    assert second_decision.transform_plan is not None
    assert locked in first_decision.transform_plan.keyframes
    assert second_decision.transform_plan.keyframes[0].source_time == MediaTime(20, 1)
    assert first_decision.transform_plan.shot_ref != second_decision.transform_plan.shot_ref


def test_analyzed_range_is_half_open_in_converter_and_track_contract() -> None:
    selection = _selection()
    base = _tracking_proposal(
        selection,
        (
            TrackingSample(
                MediaTime(0, 1),
                "available",
                None,
                NormalizedRectangle(0.2, 0.2, 0.1, 0.2),
                9,
                0.9,
            ),
        ),
    )
    short_range = MediaTimeRange(MediaTime(10, 1), MediaTime(2, 1))
    exact_end = replace(
        base,
        analyzed_source_range=short_range,
        samples=(replace(base.samples[0], relative_time=MediaTime(2, 1)),),
    )
    before_start = replace(
        base,
        analyzed_source_range=short_range,
        samples=(replace(base.samples[0], relative_time=MediaTime(-1, 1)),),
    )
    with pytest.raises(ValueError, match="escapes analyzed source range"):
        tracking_proposal_to_spatial_track(exact_end, selection, "product", ("e",))
    with pytest.raises(ValueError, match="escapes analyzed source range"):
        tracking_proposal_to_spatial_track(before_start, selection, "product", ("e",))

    valid = tracking_proposal_to_spatial_track(base, selection, "product", ("e",))
    with pytest.raises(ValueError, match="half-open analyzed source range"):
        SpatialEvidenceTrack(
            valid.track_id,
            valid.selection_id,
            valid.shot_ref,
            short_range,
            valid.source_geometry,
            valid.focus_ref,
            valid.provider_id,
            valid.provider_revision,
            valid.sampling_fps,
            (replace(valid.observations[0], source_time=short_range.end),),
            valid.evidence_refs,
        )


def _compose_positions(positions, *, policy=None, lost=()):
    selection = _selection()
    samples = [
        TrackingSample(
            MediaTime(index, 1),
            "available",
            None,
            NormalizedRectangle(position, 0.2, 0.05, 0.2),
            9,
            0.9,
        )
        for index, position in enumerate(positions)
    ]
    samples.extend(
        TrackingSample(MediaTime(time, 1), "lost", "occlusion", None, 0, 0.0) for time in lost
    )
    request = replace(
        _track_request(selection, _tracking_proposal(selection, samples)),
        path_policy=policy or SpatialPathPolicy(),
    )
    return DeterministicSpatialComposer().compose(request)


def test_dead_zone_suppresses_jitter_but_real_movement_remains() -> None:
    jitter = _compose_positions((0.2, 0.202, 0.199))
    movement = _compose_positions((0.2, 0.4))
    assert jitter.transform_plan is not None and jitter.spatial_qc is not None
    assert movement.transform_plan is not None
    assert len(jitter.transform_plan.keyframes) == 1
    assert jitter.spatial_qc.suppressed_keyframe_count == 2
    assert len(movement.transform_plan.keyframes) == 2
    assert movement.transform_plan.keyframes[0].crop != movement.transform_plan.keyframes[1].crop


def test_velocity_limit_is_deterministic_and_preserves_focus() -> None:
    policy = SpatialPathPolicy(max_center_velocity_pixels_per_second=100)
    first = _compose_positions((0.2, 0.3), policy=policy)
    second = _compose_positions((0.2, 0.3), policy=policy)
    assert first == second and first.transform_plan is not None and first.spatial_qc is not None
    crops = first.transform_plan.keyframes
    assert crops[1].crop.left - crops[0].crop.left == 100
    assert first.spatial_qc.contained_focus_count == first.spatial_qc.focus_observation_count
    assert first.spatial_qc.max_center_velocity_pixels_per_second == 100.0


def test_loss_gap_policy_holds_short_and_refuses_over_limit() -> None:
    short = _compose_positions((0.2,), lost=(1,))
    over = _compose_positions((0.2,), lost=(2,))
    assert short.mode == "track" and short.spatial_qc is not None
    assert short.spatial_qc.held_loss_count == 1
    assert short.spatial_qc.held_loss_duration_seconds == 1.0
    assert over.mode == "unresolved" and "max_lost_hold_gap" in over.infeasible_reason

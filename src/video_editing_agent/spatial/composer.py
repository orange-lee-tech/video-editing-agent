from __future__ import annotations

import hashlib
import math
from fractions import Fraction

from video_editing_agent.application.ports.seeded_tracking import (
    NormalizedRectangle,
    SeededTrackingProposal,
)
from video_editing_agent.application.ports.spatial_composer import (
    OutputCanvas,
    PixelCrop,
    ReframeDecision,
    SourceFrameGeometry,
    SpatialCompositionRequest,
    SpatialCropKeyframe,
    SpatialEvidenceTrack,
    SpatialFocusObservation,
    SpatialPathQc,
    SpatialTransformKeyframe,
    SpatialTransformPlan,
)
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.edit.resolution import ResolvedSelection


def _fraction(value: float) -> Fraction:
    return Fraction(str(value))


def _bounds(rectangle: NormalizedRectangle, source: SourceFrameGeometry) -> PixelCrop:
    left = math.floor(_fraction(rectangle.x) * source.width)
    top = math.floor(_fraction(rectangle.y) * source.height)
    right = math.ceil((_fraction(rectangle.x) + _fraction(rectangle.width)) * source.width)
    bottom = math.ceil((_fraction(rectangle.y) + _fraction(rectangle.height)) * source.height)
    return PixelCrop(left, top, right - left, bottom - top)


def _crop_dimensions(source: SourceFrameGeometry, canvas: OutputCanvas) -> tuple[int, int]:
    divisor = math.gcd(canvas.width, canvas.height)
    aspect_width, aspect_height = canvas.width // divisor, canvas.height // divisor
    multiplier = min(source.width // aspect_width, source.height // aspect_height)
    if multiplier <= 0:
        raise ValueError("target aspect ratio has no positive integer crop inside source geometry")
    return aspect_width * multiplier, aspect_height * multiplier


def validate_crop(crop: PixelCrop, source: SourceFrameGeometry, canvas: OutputCanvas) -> None:
    if crop.left + crop.width > source.width or crop.top + crop.height > source.height:
        raise ValueError("crop escapes source bounds")
    if crop.width * canvas.height != crop.height * canvas.width:
        raise ValueError("crop does not preserve target aspect ratio")


def _contains(crop: PixelCrop, focus: PixelCrop) -> bool:
    return (
        crop.left <= focus.left
        and crop.top <= focus.top
        and crop.left + crop.width >= focus.left + focus.width
        and crop.top + crop.height >= focus.top + focus.height
    )


def _centered_crop(
    center_x: Fraction,
    center_y: Fraction,
    width: int,
    height: int,
    source: SourceFrameGeometry,
) -> PixelCrop:
    left = math.floor(center_x - Fraction(width, 2))
    top = math.floor(center_y - Fraction(height, 2))
    left = min(max(left, 0), source.width - width)
    top = min(max(top, 0), source.height - height)
    return PixelCrop(left, top, width, height)


def _legacy_keyframe(
    source_time: MediaTime, crop: PixelCrop, source: SourceFrameGeometry
) -> SpatialTransformKeyframe:
    return SpatialTransformKeyframe(
        source_time,
        (crop.left + crop.width / 2) / source.width,
        (crop.top + crop.height / 2) / source.height,
        source.width / crop.width,
    )


def tracking_proposal_to_spatial_track(
    proposal: SeededTrackingProposal,
    selection: ResolvedSelection,
    focus_ref: str,
    evidence_refs: tuple[str, ...],
) -> SpatialEvidenceTrack:
    if proposal.shot_ref != selection.shot_ref:
        raise ValueError("tracking proposal belongs to a different Shot")
    if (
        proposal.analyzed_source_range.start.as_fraction()
        < selection.selected_source_range.start.as_fraction()
        or proposal.analyzed_source_range.end.as_fraction()
        > selection.selected_source_range.end.as_fraction()
    ):
        raise ValueError("tracking proposal escapes resolved source range")
    samples = tuple(sorted(proposal.samples, key=lambda item: item.relative_time.as_fraction()))
    observations = tuple(
        SpatialFocusObservation(
            proposal.analyzed_source_range.start + sample.relative_time,
            sample.status,
            sample.rectangle,
            sample.support_ratio,
            sample.reason,
        )
        for sample in samples
    )
    if any(
        item.source_time.as_fraction() < proposal.analyzed_source_range.start.as_fraction()
        or item.source_time.as_fraction() >= proposal.analyzed_source_range.end.as_fraction()
        for item in observations
    ):
        raise ValueError("tracking observation escapes analyzed source range")
    identity = (
        selection.selection_id,
        proposal.shot_ref,
        proposal.analyzed_source_range,
        proposal.width,
        proposal.height,
        proposal.seed_id,
        proposal.provider_id,
        proposal.provider_revision,
        proposal.frames_per_second,
        observations,
        tuple(sorted(evidence_refs)),
    )
    digest = hashlib.sha256(repr(identity).encode()).hexdigest()
    return SpatialEvidenceTrack(
        f"spt_{digest}",
        selection.selection_id,
        selection.shot_ref,
        proposal.analyzed_source_range,
        SourceFrameGeometry(proposal.width, proposal.height),
        focus_ref,
        proposal.provider_id,
        proposal.provider_revision,
        proposal.frames_per_second,
        observations,
        tuple(sorted(evidence_refs)),
    )


class DeterministicSpatialComposer:
    """Own legal static/hold crop decisions; observations never become commands directly."""

    policy_version = "r0.11-static-track-v2"
    track_loss_policy = "hold-last-legal-crop-v1"

    def compose(self, request: SpatialCompositionRequest) -> ReframeDecision:
        if request.protected_regions:
            return self._unresolved(
                request, "protected-region overlap policy is not defined for deterministic solve"
            )
        if request.intent.framing_style not in {"hold", "track"}:
            return self._unresolved(
                request, f"unsupported framing style: {request.intent.framing_style}"
            )
        if request.intent.framing_style == "track":
            return self._track(request)
        selection = request.selection
        evidence = tuple(
            sorted(
                request.spatial_evidence,
                key=lambda item: (item.focus_ref, item.evidence_id),
            )
        )
        for item in evidence:
            if item.shot_ref != selection.shot_ref:
                raise ValueError("spatial evidence belongs to a different Shot")
            if (
                item.source_range.start.as_fraction()
                < selection.selected_source_range.start.as_fraction()
                or item.source_range.end.as_fraction()
                > selection.selected_source_range.end.as_fraction()
            ):
                raise ValueError("spatial evidence escapes the resolved source range")

        evidence_by_focus = {item.focus_ref: item for item in evidence}
        missing = tuple(
            sorted(
                ref for ref in request.intent.mandatory_focus_refs if ref not in evidence_by_focus
            )
        )
        if missing:
            return self._unresolved(request, f"mandatory focus evidence unavailable: {missing}")

        if request.manual_locks:
            return self._manual(request)

        try:
            crop_width, crop_height = _crop_dimensions(
                request.source_geometry, request.intent.output_canvas
            )
        except ValueError as exc:
            return self._unresolved(request, str(exc))
        focus_bounds = {
            item.focus_ref: _bounds(item.bounds, request.source_geometry) for item in evidence
        }
        mandatory = tuple(focus_bounds[ref] for ref in request.intent.mandatory_focus_refs)
        if mandatory:
            union_left = min(item.left for item in mandatory)
            union_top = min(item.top for item in mandatory)
            union_right = max(item.left + item.width for item in mandatory)
            union_bottom = max(item.top + item.height for item in mandatory)
            if union_right - union_left > crop_width or union_bottom - union_top > crop_height:
                return self._unresolved(
                    request, "mandatory focus cannot fit legal target-aspect crop"
                )

        centers = {
            (
                Fraction(request.source_geometry.width, 2),
                Fraction(request.source_geometry.height, 2),
            )
        }
        for bounds in focus_bounds.values():
            centers.add(
                (
                    Fraction(2 * bounds.left + bounds.width, 2),
                    Fraction(2 * bounds.top + bounds.height, 2),
                )
            )
        if mandatory:
            centers.add(
                (
                    Fraction(union_left + union_right, 2),
                    Fraction(union_top + union_bottom, 2),
                )
            )
        candidates = tuple(
            sorted(
                {
                    _centered_crop(x, y, crop_width, crop_height, request.source_geometry)
                    for x, y in centers
                },
                key=lambda item: (item.left, item.top, item.width, item.height),
            )
        )
        legal = tuple(
            crop for crop in candidates if all(_contains(crop, bounds) for bounds in mandatory)
        )
        if not legal:
            return self._unresolved(request, "no legal crop contains every mandatory focus")

        preferred = set(request.intent.preferred_focus_refs)

        def rank(crop: PixelCrop) -> tuple[float, Fraction, int, int]:
            coverage = sum(
                item.confidence
                for item in evidence
                if (
                    item.focus_ref in preferred
                    or item.focus_ref in request.intent.mandatory_focus_refs
                )
                and _contains(crop, focus_bounds[item.focus_ref])
            )
            center_distance = abs(
                Fraction(2 * crop.left + crop.width, 2) - Fraction(request.source_geometry.width, 2)
            ) + abs(
                Fraction(2 * crop.top + crop.height, 2)
                - Fraction(request.source_geometry.height, 2)
            )
            return (-coverage, center_distance, crop.left, crop.top)

        selected = min(legal, key=rank)
        validate_crop(selected, request.source_geometry, request.intent.output_canvas)
        source_time = selection.selected_source_range.start
        plan = SpatialTransformPlan(
            selection.selection_id,
            selection.shot_ref,
            selection.selected_source_range,
            request.source_geometry,
            request.intent.output_canvas,
            (SpatialCropKeyframe(source_time, selected),),
        )
        confidence = max((item.confidence for item in evidence), default=0.5)
        return self._decision(request, "hold", plan, confidence, ())

    def _manual(self, request: SpatialCompositionRequest) -> ReframeDecision:
        locks = tuple(
            sorted(
                request.manual_locks,
                key=lambda item: (item.keyframe.source_time.as_fraction(), item.lock_id),
            )
        )
        for lock in locks:
            if not (
                request.selection.selected_source_range.start.as_fraction()
                <= lock.keyframe.source_time.as_fraction()
                < request.selection.selected_source_range.end.as_fraction()
            ):
                raise ValueError("manual crop lock escapes resolved source range")
            validate_crop(lock.keyframe.crop, request.source_geometry, request.intent.output_canvas)
        plan = SpatialTransformPlan(
            request.selection.selection_id,
            request.selection.shot_ref,
            request.selection.selected_source_range,
            request.source_geometry,
            request.intent.output_canvas,
            tuple(lock.keyframe for lock in locks),
        )
        return self._decision(
            request, "manual", plan, 1.0, ("manual crop locks override auto solve",)
        )

    def _track(self, request: SpatialCompositionRequest) -> ReframeDecision:
        tracks = tuple(
            sorted(
                request.spatial_tracks,
                key=lambda item: (item.focus_ref, item.track_id),
            )
        )
        if not tracks:
            return self._unresolved(request, "track framing requires grounded tracking evidence")
        if len(request.intent.mandatory_focus_refs) > 1:
            return self._unresolved(request, "multi-focus dynamic tracking is not supported")
        focus_ref = (
            request.intent.mandatory_focus_refs[0]
            if request.intent.mandatory_focus_refs
            else tracks[0].focus_ref
        )
        matching = tuple(item for item in tracks if item.focus_ref == focus_ref)
        if not matching:
            return self._unresolved(request, "mandatory focus tracking evidence unavailable")
        track = matching[0]
        selection = request.selection
        if track.selection_id != selection.selection_id or track.shot_ref != selection.shot_ref:
            raise ValueError("spatial track provenance disagrees with resolved selection")
        if track.source_geometry != request.source_geometry:
            raise ValueError("spatial track geometry disagrees with source geometry")
        if (
            track.analyzed_source_range.start.as_fraction()
            < selection.selected_source_range.start.as_fraction()
            or track.analyzed_source_range.end.as_fraction()
            > selection.selected_source_range.end.as_fraction()
        ):
            raise ValueError("spatial track escapes resolved source range")
        try:
            crop_width, crop_height = _crop_dimensions(
                request.source_geometry, request.intent.output_canvas
            )
        except ValueError as exc:
            return self._unresolved(request, str(exc))
        keyframes: list[SpatialCropKeyframe] = []
        last_crop: PixelCrop | None = None
        last_observation_time: MediaTime | None = None
        last_available_time: MediaTime | None = None
        lost_seen = False
        lost_times: set[Fraction] = set()
        available_confidence: list[float] = []
        held_loss_count = 0
        held_loss_duration = Fraction(0)
        suppressed_keyframes = 0
        policy = request.path_policy
        for observation in track.observations:
            if (
                observation.source_time.as_fraction()
                >= selection.selected_source_range.end.as_fraction()
            ):
                continue
            if (
                observation.source_time.as_fraction()
                < selection.selected_source_range.start.as_fraction()
            ):
                raise ValueError("spatial observation precedes resolved source range")
            if observation.status == "lost":
                lost_seen = True
                if last_crop is None or last_available_time is None:
                    return self._unresolved(
                        request, "tracking begins lost; no legal crop exists to hold"
                    )
                loss_gap = (observation.source_time - last_available_time).as_fraction()
                if loss_gap > policy.max_lost_hold_gap.as_fraction():
                    return self._unresolved(
                        request,
                        f"tracking loss exceeds policy={policy.version} max_lost_hold_gap",
                    )
                if last_observation_time is not None:
                    held_loss_duration += (
                        observation.source_time - last_observation_time
                    ).as_fraction()
                held_loss_count += 1
                keyframes.append(SpatialCropKeyframe(observation.source_time, last_crop))
                lost_times.add(observation.source_time.as_fraction())
                last_observation_time = observation.source_time
                continue
            assert observation.bounds is not None
            focus = _bounds(observation.bounds, request.source_geometry)
            if focus.width > crop_width or focus.height > crop_height:
                return self._unresolved(request, "tracked mandatory focus cannot fit legal crop")
            center_x = Fraction(2 * focus.left + focus.width, 2)
            center_y = Fraction(2 * focus.top + focus.height, 2)
            proposed = _centered_crop(
                center_x,
                center_y,
                crop_width,
                crop_height,
                request.source_geometry,
            )
            if not _contains(proposed, focus):
                return self._unresolved(request, "no legal crop contains tracked mandatory focus")
            validate_crop(proposed, request.source_geometry, request.intent.output_canvas)
            stabilized = proposed
            if last_crop is not None and last_observation_time is not None:
                delta_left = proposed.left - last_crop.left
                delta_top = proposed.top - last_crop.top
                if (
                    abs(delta_left) <= policy.center_dead_zone_pixels
                    and abs(delta_top) <= policy.center_dead_zone_pixels
                    and _contains(last_crop, focus)
                ):
                    stabilized = last_crop
                else:
                    elapsed = (observation.source_time - last_observation_time).as_fraction()
                    maximum = math.floor(policy.max_center_velocity_pixels_per_second * elapsed)
                    limited_left = last_crop.left + min(max(delta_left, -maximum), maximum)
                    limited_top = last_crop.top + min(max(delta_top, -maximum), maximum)
                    limited = PixelCrop(
                        limited_left,
                        limited_top,
                        proposed.width,
                        proposed.height,
                    )
                    validate_crop(limited, request.source_geometry, request.intent.output_canvas)
                    if not _contains(limited, focus):
                        return self._unresolved(
                            request,
                            "velocity limit would crop mandatory focus; refusing path",
                        )
                    stabilized = limited
            if (
                last_crop is not None
                and stabilized == last_crop
                and policy.suppress_redundant_keyframes
            ):
                suppressed_keyframes += 1
            else:
                keyframes.append(SpatialCropKeyframe(observation.source_time, stabilized))
            last_crop = stabilized
            last_observation_time = observation.source_time
            last_available_time = observation.source_time
            available_confidence.append(observation.confidence)
        if not keyframes:
            return self._unresolved(request, "tracking evidence has no in-range observations")

        by_time = {item.source_time.as_fraction(): item for item in keyframes}
        manual_used = False
        lock_times: set[Fraction] = set()
        for lock in sorted(
            request.manual_locks,
            key=lambda item: (item.keyframe.source_time.as_fraction(), item.lock_id),
        ):
            if not (
                selection.selected_source_range.start.as_fraction()
                <= lock.keyframe.source_time.as_fraction()
                < selection.selected_source_range.end.as_fraction()
            ):
                raise ValueError("manual crop lock escapes resolved source range")
            validate_crop(lock.keyframe.crop, request.source_geometry, request.intent.output_canvas)
            by_time[lock.keyframe.source_time.as_fraction()] = lock.keyframe
            lock_times.add(lock.keyframe.source_time.as_fraction())
            manual_used = True
        canonical_items: list[SpatialCropKeyframe] = []
        for key in sorted(by_time):
            item = by_time[key]
            if key in lost_times and key not in lock_times and canonical_items:
                item = SpatialCropKeyframe(item.source_time, canonical_items[-1].crop)
            canonical_items.append(item)
        canonical = tuple(canonical_items)
        plan = SpatialTransformPlan(
            selection.selection_id,
            selection.shot_ref,
            selection.selected_source_range,
            request.source_geometry,
            request.intent.output_canvas,
            canonical,
        )
        warnings = tuple(
            message
            for condition, message in (
                (
                    lost_seen,
                    "tracking loss holds the last legal crop; "
                    f"policy={self.track_loss_policy} is mechanism-level and uncalibrated",
                ),
                (manual_used, "manual crop locks override track solve at locked source times"),
            )
            if condition
        )
        confidence = (
            sum(available_confidence) / len(available_confidence) if available_confidence else 0.0
        )
        qc = self._track_qc(
            request,
            track,
            plan,
            held_loss_count,
            float(held_loss_duration),
            suppressed_keyframes,
        )
        return self._decision(request, "track", plan, confidence, warnings, qc)

    def _decision(
        self,
        request: SpatialCompositionRequest,
        mode: str,
        plan: SpatialTransformPlan,
        confidence: float,
        warnings: tuple[str, ...],
        spatial_qc: SpatialPathQc | None = None,
    ) -> ReframeDecision:
        evidence_refs = self._evidence_refs(request)
        identity = (
            request.selection,
            request.source_geometry,
            request.intent.output_canvas,
            tuple(sorted(request.intent.mandatory_focus_refs)),
            tuple(sorted(request.intent.preferred_focus_refs)),
            plan,
            evidence_refs,
            self.policy_version,
            request.path_policy,
        )
        digest = hashlib.sha256(repr(identity).encode()).hexdigest()
        legacy = tuple(
            _legacy_keyframe(item.source_time, item.crop, plan.source_geometry)
            for item in plan.keyframes
        )
        return ReframeDecision(
            f"rfd_{digest}",
            request.selection.selection_id,
            mode,
            legacy,
            confidence,
            evidence_refs,
            warnings,
            transform_plan=plan,
            spatial_qc=spatial_qc,
        )

    def _unresolved(self, request: SpatialCompositionRequest, reason: str) -> ReframeDecision:
        evidence_refs = self._evidence_refs(request)
        identity = (
            request.selection,
            request.source_geometry,
            request.intent.output_canvas,
            tuple(sorted(request.intent.mandatory_focus_refs)),
            tuple(sorted(request.intent.preferred_focus_refs)),
            evidence_refs,
            reason,
            self.policy_version,
            request.path_policy,
        )
        digest = hashlib.sha256(repr(identity).encode()).hexdigest()
        return ReframeDecision(
            f"rfd_{digest}",
            request.selection.selection_id,
            "unresolved",
            (),
            0.0,
            evidence_refs,
            ("non-generative fallback required",),
            reason,
            spatial_qc=SpatialPathQc(0, 0, 0, 0, 0.0, 0.0, 0, 0, 0.0, 0, reason),
        )

    @staticmethod
    def _track_qc(
        request: SpatialCompositionRequest,
        track: SpatialEvidenceTrack,
        plan: SpatialTransformPlan,
        held_loss_count: int,
        held_loss_duration: float,
        suppressed_keyframes: int,
    ) -> SpatialPathQc:
        keyframes = plan.keyframes
        displacements: list[float] = []
        velocities: list[float] = []
        directions: list[tuple[int, int]] = []
        for left, right in zip(keyframes, keyframes[1:], strict=False):
            dx = right.crop.left - left.crop.left
            dy = right.crop.top - left.crop.top
            displacement = math.hypot(dx, dy)
            elapsed = float((right.source_time - left.source_time).as_fraction())
            displacements.append(displacement)
            velocities.append(0.0 if elapsed == 0 else displacement / elapsed)
            directions.append(((dx > 0) - (dx < 0), (dy > 0) - (dy < 0)))
        direction_changes = sum(
            current != previous and current != (0, 0) and previous != (0, 0)
            for previous, current in zip(directions, directions[1:], strict=False)
        )
        available = tuple(item for item in track.observations if item.status == "available")
        contained = 0
        for observation in available:
            assert observation.bounds is not None
            active = max(
                (
                    item
                    for item in keyframes
                    if item.source_time.as_fraction() <= observation.source_time.as_fraction()
                ),
                key=lambda item: item.source_time.as_fraction(),
                default=None,
            )
            if active is not None and _contains(
                active.crop, _bounds(observation.bounds, request.source_geometry)
            ):
                contained += 1
        return SpatialPathQc(
            len(available),
            contained,
            0,
            0,
            max(displacements, default=0.0),
            max(velocities, default=0.0),
            direction_changes,
            held_loss_count,
            held_loss_duration,
            suppressed_keyframes,
        )

    @staticmethod
    def _evidence_refs(request: SpatialCompositionRequest) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    *(item.evidence_id for item in request.spatial_evidence),
                    *(item.track_id for item in request.spatial_tracks),
                    *(ref for item in request.spatial_tracks for ref in item.evidence_refs),
                    *request.evidence_refs,
                }
            )
        )

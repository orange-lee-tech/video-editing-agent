from __future__ import annotations

import hashlib
import math
from fractions import Fraction

from video_editing_agent.application.ports.seeded_tracking import NormalizedRectangle
from video_editing_agent.application.ports.spatial_composer import (
    OutputCanvas,
    PixelCrop,
    ReframeDecision,
    SourceFrameGeometry,
    SpatialCompositionRequest,
    SpatialCropKeyframe,
    SpatialTransformKeyframe,
    SpatialTransformPlan,
)
from video_editing_agent.domain.common.media_time import MediaTime


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


class DeterministicSpatialComposer:
    """Own legal static/hold crop decisions; observations never become commands directly."""

    policy_version = "r0.11-static-hold-v1"

    def compose(self, request: SpatialCompositionRequest) -> ReframeDecision:
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
                <= request.selection.selected_source_range.end.as_fraction()
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

    def _decision(
        self,
        request: SpatialCompositionRequest,
        mode: str,
        plan: SpatialTransformPlan,
        confidence: float,
        warnings: tuple[str, ...],
    ) -> ReframeDecision:
        evidence_refs = tuple(sorted(item.evidence_id for item in request.spatial_evidence))
        identity = (
            request.selection,
            request.source_geometry,
            request.intent.output_canvas,
            tuple(sorted(request.intent.mandatory_focus_refs)),
            tuple(sorted(request.intent.preferred_focus_refs)),
            plan,
            evidence_refs,
            self.policy_version,
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
        )

    def _unresolved(self, request: SpatialCompositionRequest, reason: str) -> ReframeDecision:
        evidence_refs = tuple(sorted(item.evidence_id for item in request.spatial_evidence))
        identity = (
            request.selection,
            request.source_geometry,
            request.intent.output_canvas,
            tuple(sorted(request.intent.mandatory_focus_refs)),
            tuple(sorted(request.intent.preferred_focus_refs)),
            evidence_refs,
            reason,
            self.policy_version,
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
        )

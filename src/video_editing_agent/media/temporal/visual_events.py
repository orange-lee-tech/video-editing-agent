from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

from video_editing_agent.application.ports.artifact_store import ArtifactStore
from video_editing_agent.application.ports.shot_repository import ShotRepository
from video_editing_agent.application.ports.temporal_evidence_repository import (
    TemporalEvidenceRepository,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.evidence.temporal import TemporalAnchor, TemporalEvidence
from video_editing_agent.media.temporal.visual_motion import VISUAL_MOTION_MEASUREMENT_SET_KIND
from video_editing_agent.media.temporal.visual_motion_codec import decode_visual_motion

CAMERA_REGION_KIND = "camera_motion_region"
RESIDUAL_REGION_KIND = "residual_motion_region"
LEGACY_KINDS = frozenset({"camera_motion_measurement", "residual_motion_measurement"})
REDUCER_VERSION = "visual-motion-event-reducer@r0.8d-v1"


@dataclass(frozen=True, slots=True)
class MotionEventPolicy:
    policy_id: str
    camera_enter_threshold: float
    camera_exit_threshold: float
    residual_enter_threshold: float
    residual_exit_threshold: float
    minimum_region_intervals: int
    maximum_mergeable_quiet_gap: int

    def __post_init__(self) -> None:
        if not self.policy_id.strip():
            raise ValueError("policy_id must not be empty")
        if (
            self.camera_exit_threshold > self.camera_enter_threshold
            or self.residual_exit_threshold > self.residual_enter_threshold
        ):
            raise ValueError("exit thresholds must not exceed enter thresholds")
        if self.minimum_region_intervals < 1 or self.maximum_mergeable_quiet_gap < 0:
            raise ValueError("invalid motion event interval policy")


@dataclass(frozen=True, slots=True)
class _Sample:
    interval: MediaTimeRange
    signal: float | None
    reliability: float


def _regions(
    samples: tuple[_Sample, ...], enter: float, exit: float, policy: MotionEventPolicy
) -> tuple[tuple[int, int], ...]:
    found: list[tuple[int, int]] = []
    start: int | None = None
    last_active = -1
    quiet = 0
    for index, sample in enumerate(samples):
        if sample.signal is None:
            if start is not None and last_active - start + 1 >= policy.minimum_region_intervals:
                found.append((start, last_active))
            start = None
            quiet = 0
            continue
        threshold = enter if start is None else exit
        if sample.signal >= threshold:
            if start is None:
                start = index
            last_active = index
            quiet = 0
        elif start is not None:
            quiet += 1
            if quiet > policy.maximum_mergeable_quiet_gap:
                if last_active - start + 1 >= policy.minimum_region_intervals:
                    found.append((start, last_active))
                start = None
                quiet = 0
    if start is not None and last_active - start + 1 >= policy.minimum_region_intervals:
        found.append((start, last_active))
    return tuple(found)


class VisualMotionEventService:
    def __init__(
        self,
        *,
        shot_repository: ShotRepository,
        temporal_evidence_repository: TemporalEvidenceRepository,
        artifact_store: ArtifactStore,
    ) -> None:
        self._shots = shot_repository
        self._repository = temporal_evidence_repository
        self._artifacts = artifact_store

    def reduce(
        self, shot_ref: EntityRevisionRef, measurement_evidence_id: str, policy: MotionEventPolicy
    ) -> tuple[tuple[TemporalEvidence, ...], tuple[TemporalAnchor, ...]]:
        shot = self._shots.load(shot_ref)
        selected = next(
            (
                item
                for item in self._repository.list_evidence(shot_ref)
                if item.evidence_id == measurement_evidence_id
            ),
            None,
        )
        if selected is None:
            raise KeyError(measurement_evidence_id)
        if (
            selected.kind != VISUAL_MOTION_MEASUREMENT_SET_KIND
            and selected.kind not in LEGACY_KINDS
        ):
            raise ValueError("unsupported visual motion measurement evidence kind")
        if len(selected.artifact_refs) != 1:
            raise ValueError("motion measurement evidence must reference one Artifact")
        proposal = decode_visual_motion(self._artifacts.get_by_id(selected.artifact_refs[0]))
        if (
            proposal.shot_ref != shot_ref
            or proposal.provider_id != selected.method
            or proposal.provider_revision != selected.producer_version
        ):
            raise ValueError("motion Artifact provenance disagrees with selected evidence")
        diagonal = math.hypot(proposal.width, proposal.height)
        analysis_range = proposal.analyzed_source_range or shot.source_range
        if (
            analysis_range.start.as_fraction() < shot.source_range.start.as_fraction()
            or analysis_range.end.as_fraction() > shot.source_range.end.as_fraction()
        ):
            raise ValueError("motion Artifact analyzed range escapes exact Shot")
        camera: list[_Sample] = []
        residual: list[_Sample] = []
        for item in proposal.measurements:
            absolute = MediaTimeRange(
                analysis_range.start + item.relative_range.start, item.relative_range.duration
            )
            seconds = float(item.relative_range.duration.as_fraction())
            available = item.status == "available"
            camera.append(
                _Sample(
                    absolute,
                    None
                    if not available or item.global_displacement is None
                    else item.global_displacement / diagonal / seconds,
                    item.inlier_ratio,
                )
            )
            residual.append(
                _Sample(
                    absolute,
                    None
                    if not available or item.residual_p95 is None
                    else item.residual_p95 / diagonal / seconds,
                    item.inlier_ratio,
                )
            )
        output_evidence: list[TemporalEvidence] = []
        anchors: list[TemporalAnchor] = []
        for kind, samples, enter, exit in (
            (
                CAMERA_REGION_KIND,
                tuple(camera),
                policy.camera_enter_threshold,
                policy.camera_exit_threshold,
            ),
            (
                RESIDUAL_REGION_KIND,
                tuple(residual),
                policy.residual_enter_threshold,
                policy.residual_exit_threshold,
            ),
        ):
            for region_index, (first, last) in enumerate(_regions(samples, enter, exit, policy)):
                region_range = MediaTimeRange(
                    samples[first].interval.start,
                    samples[last].interval.end - samples[first].interval.start,
                )
                identity = (
                    f"{shot_ref.entity_id}:{shot_ref.revision}:{selected.evidence_id}:"
                    f"{selected.artifact_refs[0]}:{REDUCER_VERSION}:{policy.policy_id}:"
                    f"{kind}:{region_index}"
                )
                evidence_id = "tev_motion_region_" + hashlib.sha256(identity.encode()).hexdigest()
                reliability = sorted(sample.reliability for sample in samples[first : last + 1])[
                    ((last - first + 1) - 1) // 2
                ]
                region = TemporalEvidence(
                    evidence_id,
                    shot_ref,
                    kind,
                    REDUCER_VERSION,
                    policy.policy_id,
                    reliability,
                    region_range,
                    selected.artifact_refs,
                    (selected.evidence_id,),
                )
                output_evidence.append(region)
                peak_index = max(
                    range(first, last + 1),
                    key=lambda index: (samples[index].signal or -1.0, -index),
                )
                points = (
                    ("onset", region_range.start),
                    (
                        "peak",
                        samples[peak_index].interval.start
                        + MediaTime(
                            samples[peak_index].interval.duration.value,
                            samples[peak_index].interval.duration.scale * 2,
                        ),
                    ),
                    ("settle", region_range.end),
                )
                prefix = "camera_motion" if kind == CAMERA_REGION_KIND else "residual_motion"
                for suffix, point in points:
                    anchor_kind = f"{prefix}_{suffix}"
                    anchor_id = (
                        "tan_motion_"
                        + hashlib.sha256(f"{identity}:{anchor_kind}".encode()).hexdigest()
                    )
                    anchors.append(
                        TemporalAnchor(
                            anchor_id,
                            shot_ref,
                            anchor_kind,
                            point,
                            reliability,
                            (evidence_id,),
                            REDUCER_VERSION,
                        )
                    )
        result_evidence = tuple(output_evidence)
        result_anchors = tuple(anchors)
        self._repository.save_evidence_and_anchors(result_evidence, result_anchors)
        return result_evidence, result_anchors

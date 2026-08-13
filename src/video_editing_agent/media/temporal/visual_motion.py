from __future__ import annotations

import hashlib
import math
from dataclasses import asdict

from video_editing_agent.application.ports.artifact_lifecycle import (
    ArtifactLifecycleDescriptor,
    ArtifactLifecycleRepository,
    ArtifactRetentionClass,
)
from video_editing_agent.application.ports.artifact_store import ArtifactPayload, ArtifactStore
from video_editing_agent.application.ports.asset_media import AssetMediaResolver
from video_editing_agent.application.ports.shot_repository import ShotRepository
from video_editing_agent.application.ports.temporal_evidence_repository import (
    TemporalEvidenceRepository,
)
from video_editing_agent.application.ports.visual_motion import (
    VisualMotionMeasurement,
    VisualMotionPort,
    VisualMotionRequest,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.evidence.temporal import TemporalEvidence
from video_editing_agent.media.temporal.visual_motion_codec import encode_visual_motion

VISUAL_MOTION_MEASUREMENT_SET_KIND = "visual_motion_measurement_set"


def _validate(measurement: VisualMotionMeasurement, duration: MediaTime) -> None:
    if (
        measurement.relative_range.start.as_fraction() < 0
        or measurement.relative_range.end.as_fraction() > duration.as_fraction()
    ):
        raise ValueError("visual motion measurement must stay inside exact Shot")
    numeric = asdict(measurement)
    for value in numeric.values():
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("visual motion measurements must be finite")
    if measurement.status != "available" and any(
        value is not None
        for value in (
            measurement.translation_x,
            measurement.translation_y,
            measurement.global_displacement,
            measurement.residual_median,
        )
    ):
        raise ValueError("unavailable visual motion must not masquerade as zero motion")


class VisualMotionEvidenceService:
    def __init__(
        self,
        *,
        shot_repository: ShotRepository,
        asset_media_resolver: AssetMediaResolver,
        temporal_evidence_repository: TemporalEvidenceRepository,
        artifact_store: ArtifactStore,
        artifact_lifecycle_repository: ArtifactLifecycleRepository,
        motion_port: VisualMotionPort,
    ) -> None:
        self._shots = shot_repository
        self._media = asset_media_resolver
        self._evidence = temporal_evidence_repository
        self._artifacts = artifact_store
        self._lifecycle = artifact_lifecycle_repository
        self._port = motion_port

    def measure(self, shot_ref: EntityRevisionRef) -> tuple[TemporalEvidence, ...]:
        shot = self._shots.load(shot_ref)
        actual = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
        if actual != shot_ref:
            raise RuntimeError("ShotRepository returned a different Shot revision")
        media = self._media.resolve_local(shot.asset_ref)
        proposal = self._port.measure(VisualMotionRequest(shot_ref, media.path, shot.source_range))
        if proposal.shot_ref != shot_ref:
            raise ValueError("visual motion proposal returned a different Shot revision")
        if not proposal.provider_id.strip() or not proposal.provider_revision.strip():
            raise ValueError("visual motion provider identity must not be empty")
        previous_end = None
        for measurement in proposal.measurements:
            _validate(measurement, shot.source_range.duration)
            start = measurement.relative_range.start.as_fraction()
            if previous_end is not None and start < previous_end:
                raise ValueError("visual motion measurements must be ordered and non-overlapping")
            previous_end = measurement.relative_range.end.as_fraction()
        payload = encode_visual_motion(proposal)
        artifact = self._artifacts.put(ArtifactPayload("application/json", payload))
        source_ref = f"shot:{shot_ref.entity_id}@{shot_ref.revision}"
        self._lifecycle.add(
            ArtifactLifecycleDescriptor(
                artifact.artifact_id,
                ArtifactRetentionClass.DURABLE_DERIVED_EVIDENCE,
                "visual_motion_measurement",
                (source_ref,),
            )
        )
        available = sum(item.status == "available" for item in proposal.measurements)
        completeness = available / len(proposal.measurements) if proposal.measurements else 0.0
        digest = hashlib.sha256(
            f"{shot_ref.entity_id}:{shot_ref.revision}:{artifact.artifact_id}".encode()
        ).hexdigest()
        result = (
            TemporalEvidence(
                f"tev_motion_set_{digest}",
                shot_ref,
                VISUAL_MOTION_MEASUREMENT_SET_KIND,
                proposal.provider_id,
                proposal.provider_revision,
                completeness,
                shot.source_range,
                (artifact.artifact_id,),
            ),
        )
        self._evidence.save_evidence_batch(result)
        return result

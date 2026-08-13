from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict

from video_editing_agent.application.ports.artifact_store import ArtifactPayload, ArtifactStore
from video_editing_agent.application.ports.asset_media import AssetMediaResolver
from video_editing_agent.application.ports.shot_repository import ShotRepository
from video_editing_agent.application.ports.temporal_evidence_repository import (
    TemporalEvidenceRepository,
)
from video_editing_agent.application.ports.visual_motion import (
    VisualMotionMeasurement,
    VisualMotionPort,
    VisualMotionProposal,
    VisualMotionRequest,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.evidence.temporal import TemporalEvidence

CAMERA_MOTION_KIND = "camera_motion_measurement"
RESIDUAL_MOTION_KIND = "residual_motion_measurement"


def _canonical_payload(proposal: VisualMotionProposal) -> bytes:
    return json.dumps(
        {"schema_version": "r0.8c-visual-motion-v1", "proposal": asdict(proposal)},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()


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
        motion_port: VisualMotionPort,
    ) -> None:
        self._shots = shot_repository
        self._media = asset_media_resolver
        self._evidence = temporal_evidence_repository
        self._artifacts = artifact_store
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
        payload = _canonical_payload(proposal)
        artifact = self._artifacts.put(ArtifactPayload("application/json", payload))
        evidence = []
        for index, measurement in enumerate(proposal.measurements):
            if measurement.status != "available":
                continue
            absolute = MediaTimeRange(
                shot.source_range.start + measurement.relative_range.start,
                measurement.relative_range.duration,
            )
            for kind in (CAMERA_MOTION_KIND, RESIDUAL_MOTION_KIND):
                digest = hashlib.sha256(
                    f"{shot_ref.entity_id}:{shot_ref.revision}:{index}:{kind}:{artifact.artifact_id}".encode()
                ).hexdigest()
                evidence.append(
                    TemporalEvidence(
                        f"tev_motion_{digest}",
                        shot_ref,
                        kind,
                        proposal.provider_id,
                        proposal.provider_revision,
                        measurement.inlier_ratio,
                        absolute,
                        (artifact.artifact_id,),
                    )
                )
        result = tuple(evidence)
        self._evidence.save_evidence_batch(result)
        return result

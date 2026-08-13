from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict

from video_editing_agent.application.ports.artifact_lifecycle import (
    ArtifactLifecycleDescriptor,
    ArtifactLifecycleRepository,
    ArtifactRetentionClass,
)
from video_editing_agent.application.ports.artifact_store import ArtifactPayload, ArtifactStore
from video_editing_agent.application.ports.asset_media import AssetMediaResolver
from video_editing_agent.application.ports.seeded_tracking import (
    NormalizedRectangle,
    SeededTrackingPort,
    SeededTrackingProposal,
    SeededTrackingRequest,
)
from video_editing_agent.application.ports.shot_repository import ShotRepository
from video_editing_agent.application.ports.temporal_evidence_repository import (
    TemporalEvidenceRepository,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTimeRange
from video_editing_agent.domain.evidence.temporal import TemporalEvidence

TRACKING_MEASUREMENT_SET_KIND = "seeded_tracking_measurement_set"
_STATUSES = frozenset({"available", "lost"})
_LOSS_REASONS = frozenset(
    {
        "insufficient_features",
        "tracking_failure",
        "round_trip_failure",
        "insufficient_support",
        "insufficient_target_support",
        "occlusion",
        "target_exit",
    }
)


def _validate_rectangle(rectangle: NormalizedRectangle) -> None:
    values = (rectangle.x, rectangle.y, rectangle.width, rectangle.height)
    if (
        any(not math.isfinite(x) for x in values)
        or rectangle.width <= 0
        or rectangle.height <= 0
        or rectangle.x < 0
        or rectangle.y < 0
        or rectangle.x + rectangle.width > 1
        or rectangle.y + rectangle.height > 1
    ):
        raise ValueError("tracking rectangle must be finite and normalized inside the frame")


def encode_seeded_tracking(proposal: SeededTrackingProposal) -> bytes:
    return json.dumps(
        {"schema_version": "r0.8f-seeded-tracking-v1", "proposal": asdict(proposal)},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()


class SeededTrackingEvidenceService:
    def __init__(
        self,
        *,
        shot_repository: ShotRepository,
        asset_media_resolver: AssetMediaResolver,
        temporal_evidence_repository: TemporalEvidenceRepository,
        artifact_store: ArtifactStore,
        artifact_lifecycle_repository: ArtifactLifecycleRepository,
        tracking_port: SeededTrackingPort,
    ) -> None:
        self._shots = shot_repository
        self._media = asset_media_resolver
        self._repository = temporal_evidence_repository
        self._artifacts = artifact_store
        self._lifecycle = artifact_lifecycle_repository
        self._port = tracking_port

    def track(
        self,
        shot_ref: EntityRevisionRef,
        analyzed_source_range: MediaTimeRange,
        seed_id: str,
        seed_rectangle: NormalizedRectangle,
    ) -> tuple[TemporalEvidence, ...]:
        shot = self._shots.load(shot_ref)
        _validate_rectangle(seed_rectangle)
        if not seed_id.strip():
            raise ValueError("seed_id must not be empty")
        if (
            analyzed_source_range.start.as_fraction() < shot.source_range.start.as_fraction()
            or analyzed_source_range.end.as_fraction() > shot.source_range.end.as_fraction()
        ):
            raise ValueError("tracking analyzed range must stay inside exact Shot")
        media = self._media.resolve_local(shot.asset_ref)
        proposal = self._port.track(
            SeededTrackingRequest(
                shot_ref, media.path, analyzed_source_range, seed_id, seed_rectangle
            )
        )
        if (
            proposal.shot_ref != shot_ref
            or proposal.analyzed_source_range != analyzed_source_range
            or proposal.seed_id != seed_id
            or proposal.seed_rectangle != seed_rectangle
        ):
            raise ValueError("tracking proposal provenance disagrees with request")
        if not proposal.provider_id.strip() or not proposal.provider_revision.strip():
            raise ValueError("tracking provider identity must not be empty")
        for name, value in (
            ("frames_per_second", proposal.frames_per_second),
            ("width", proposal.width),
            ("height", proposal.height),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"tracking {name} must be a positive int")
        if not proposal.samples or proposal.samples[0].relative_time.as_fraction() != 0:
            raise ValueError("tracking samples must be non-empty and begin at relative zero")
        previous = None
        for sample in proposal.samples:
            if (
                sample.relative_time.as_fraction() < 0
                or sample.relative_time.as_fraction() > analyzed_source_range.duration.as_fraction()
            ):
                raise ValueError("tracking sample escapes analyzed range")
            if previous is not None and sample.relative_time.as_fraction() <= previous:
                raise ValueError("tracking samples must be strictly ordered")
            previous = sample.relative_time.as_fraction()
            if sample.status not in _STATUSES:
                raise ValueError("unsupported tracking sample status")
            if (
                isinstance(sample.support_count, bool)
                or not isinstance(sample.support_count, int)
                or sample.support_count < 0
            ):
                raise ValueError("tracking support_count must be a non-negative int")
            if (
                isinstance(sample.support_ratio, bool)
                or not isinstance(sample.support_ratio, (int, float))
                or not math.isfinite(float(sample.support_ratio))
                or not 0 <= float(sample.support_ratio) <= 1
            ):
                raise ValueError("tracking support_ratio must be finite and between 0 and 1")
            if sample.status == "available":
                if sample.reason is not None:
                    raise ValueError("available tracking sample must not have a loss reason")
                if sample.rectangle is None:
                    raise ValueError("available tracking sample requires rectangle")
                _validate_rectangle(sample.rectangle)
            else:
                if sample.reason not in _LOSS_REASONS:
                    raise ValueError("lost tracking sample requires a supported reason")
                if sample.rectangle is not None:
                    raise ValueError("unavailable tracking sample must not contain geometry")
        payload = encode_seeded_tracking(proposal)
        artifact = self._artifacts.put(ArtifactPayload("application/json", payload))
        source_ref = f"shot:{shot_ref.entity_id}@{shot_ref.revision}"
        self._lifecycle.add(
            ArtifactLifecycleDescriptor(
                artifact.artifact_id,
                ArtifactRetentionClass.DURABLE_DERIVED_EVIDENCE,
                "seeded_tracking_measurement",
                (source_ref, seed_id),
            )
        )
        available = sum(x.status == "available" for x in proposal.samples)
        confidence = available / len(proposal.samples) if proposal.samples else 0.0
        digest = hashlib.sha256(
            f"{shot_ref.entity_id}:{shot_ref.revision}:{seed_id}:{artifact.artifact_id}".encode()
        ).hexdigest()
        evidence = (
            TemporalEvidence(
                f"tev_tracking_set_{digest}",
                shot_ref,
                TRACKING_MEASUREMENT_SET_KIND,
                proposal.provider_id,
                proposal.provider_revision,
                confidence,
                analyzed_source_range,
                (artifact.artifact_id,),
                (seed_id,),
            ),
        )
        self._repository.save_evidence_batch(evidence)
        return evidence

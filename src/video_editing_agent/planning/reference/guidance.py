from __future__ import annotations

from video_editing_agent.application.ports.preproduction_planning import ReferenceStyleGuidance
from video_editing_agent.planning.reference.service import ReferenceStyleEvidenceResult


def to_reference_style_guidance(result: ReferenceStyleEvidenceResult) -> ReferenceStyleGuidance:
    """Project derived evidence into provider-neutral planning context."""

    return ReferenceStyleGuidance(
        reference_asset_ref=result.evidence.reference_asset_ref,
        evidence_artifact_id=result.artifact_ref.artifact_id,
        observations=result.planning_guidance,
        unavailable_dimensions=result.evidence.unavailable_dimensions,
    )

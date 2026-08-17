from __future__ import annotations

import hashlib

from video_editing_agent.application.ports.audio_editorial import (
    AudioMixDecision,
    SourceAudioPolicy,
    SourceAudioTreatment,
    VoiceTreatment,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.edit.model import EditPlan
from video_editing_agent.domain.edit.resolution import ResolutionDecision, ResolutionDecisionType


def build_conservative_source_audio_mix(
    edit_plan: EditPlan,
    decisions: tuple[ResolutionDecision, ...],
) -> AudioMixDecision:
    """Preserve grounded original audio unless an explicit later policy decides otherwise."""

    plan_ref = EntityRevisionRef(edit_plan.envelope.id, edit_plan.envelope.revision)
    selection_ids = tuple(
        selection.selection_id
        for decision in decisions
        if decision.decision_type is ResolutionDecisionType.RESOLVED
        for selection in decision.selections
    )
    payload = (
        f"{plan_ref.entity_id}@{plan_ref.revision}:"
        f"{'|'.join(selection_ids)}:preserve-v1"
    )
    decision_id = f"amx_{hashlib.sha256(payload.encode()).hexdigest()}"
    treatments = tuple(
        SourceAudioTreatment(
            selection_id,
            SourceAudioPolicy.PRESERVE,
            VoiceTreatment.PRESERVE,
            reason="product default preserves grounded original source audio",
        )
        for selection_id in selection_ids
    )
    return AudioMixDecision(
        decision_id,
        plan_ref,
        None,
        SourceAudioPolicy.PRESERVE,
        source_treatments=treatments,
    )

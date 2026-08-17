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
    """Preserve Resolver-grounded original audio until a later policy explicitly changes it."""

    plan_ref = EntityRevisionRef(edit_plan.envelope.id, edit_plan.envelope.revision)
    selections = tuple(
        selection
        for decision in decisions
        if decision.decision_type is ResolutionDecisionType.RESOLVED
        for selection in decision.selections
    )
    payload = (
        f"{plan_ref.entity_id}@{plan_ref.revision}:"
        f"{'|'.join(selection.selection_id for selection in selections)}:preserve-v1"
    )
    decision_id = f"amx_{hashlib.sha256(payload.encode()).hexdigest()}"
    treatments = tuple(
        SourceAudioTreatment(
            selection.selection_id,
            selection.selected_source_range,
            SourceAudioPolicy.PRESERVE,
            VoiceTreatment.PRESERVE,
        )
        for selection in selections
    )
    return AudioMixDecision(
        decision_id,
        plan_ref,
        SourceAudioPolicy.PRESERVE,
        source_treatments=treatments,
    )

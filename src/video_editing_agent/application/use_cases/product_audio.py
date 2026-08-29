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
    *,
    source_audio_selection_ids: frozenset[str] | None = None,
) -> AudioMixDecision:
    """Preserve Resolver-grounded original audio until a later policy explicitly changes it."""

    plan_ref = EntityRevisionRef(edit_plan.envelope.id, edit_plan.envelope.revision)
    selections = tuple(
        selection
        for decision in decisions
        if decision.decision_type is ResolutionDecisionType.RESOLVED
        for selection in decision.selections
    )
    source_audio_ids = (
        frozenset(selection.selection_id for selection in selections)
        if source_audio_selection_ids is None
        else source_audio_selection_ids
    )
    unknown = source_audio_ids - frozenset(selection.selection_id for selection in selections)
    if unknown:
        raise ValueError("source-audio selection ids must belong to resolved selections")
    payload = (
        f"{plan_ref.entity_id}@{plan_ref.revision}:"
        f"{'|'.join(selection.selection_id for selection in selections)}:"
        f"{'|'.join(sorted(source_audio_ids))}:preserve-available-v2"
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
        if selection.selection_id in source_audio_ids
    )
    return AudioMixDecision(
        decision_id,
        plan_ref,
        SourceAudioPolicy.MUTE,
        source_treatments=treatments,
    )

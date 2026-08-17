from __future__ import annotations

from datetime import UTC, datetime

from video_editing_agent.application.ports.audio_editorial import (
    SourceAudioPolicy,
    VoiceTreatment,
)
from video_editing_agent.application.use_cases.product_audio import (
    build_conservative_source_audio_mix,
)
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.model import EditPlan, EditSlot
from video_editing_agent.domain.edit.resolution import (
    ResolutionDecision,
    ResolutionDecisionType,
    ResolvedSelection,
)

NOW = datetime(2026, 8, 17, 14, 0, tzinfo=UTC)


def _envelope(identity: str) -> EntityEnvelope:
    return EntityEnvelope(identity, 1, "0.2", EntityStatus.VALID, NOW, "test")


def test_conservative_product_audio_preserves_grounded_selection_ranges() -> None:
    plan = EditPlan(
        _envelope("epl_audio_product"),
        None,
        None,
        (
            EditSlot("slot_a", "show first", 0),
            EditSlot("slot_b", "show second", 1),
        ),
        EntityRevisionRef("brf_audio_product", 1),
    )
    plan_ref = EntityRevisionRef(plan.envelope.id, plan.envelope.revision)
    first_range = MediaTimeRange(MediaTime(1, 2), MediaTime(2, 1))
    second_range = MediaTimeRange(MediaTime(7, 2), MediaTime(3, 2))
    decisions = (
        ResolutionDecision(
            "res_a",
            plan_ref,
            ("slot_a",),
            ResolutionDecisionType.RESOLVED,
            (ResolvedSelection("sel_a", EntityRevisionRef("sht_a", 1), first_range, 0),),
        ),
        ResolutionDecision(
            "res_b",
            plan_ref,
            ("slot_b",),
            ResolutionDecisionType.RESOLVED,
            (ResolvedSelection("sel_b", EntityRevisionRef("sht_b", 1), second_range, 0),),
        ),
    )

    first = build_conservative_source_audio_mix(plan, decisions)
    second = build_conservative_source_audio_mix(plan, decisions)

    assert first == second
    assert first.edit_plan_ref == plan_ref
    assert first.source_audio_policy is SourceAudioPolicy.PRESERVE
    assert first.automation_intents == ()
    assert tuple(item.selection_id for item in first.source_treatments) == ("sel_a", "sel_b")
    assert tuple(item.source_range for item in first.source_treatments) == (
        first_range,
        second_range,
    )
    assert all(
        item.source_audio_policy is SourceAudioPolicy.PRESERVE
        and item.voice_treatment is VoiceTreatment.PRESERVE
        for item in first.source_treatments
    )

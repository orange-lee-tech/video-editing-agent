from __future__ import annotations

from datetime import UTC, datetime

from video_editing_agent.application.ports.preproduction_planning import (
    NarrativeSectionProposal,
    ScriptPlanProposal,
)
from video_editing_agent.application.ports.preproduction_review import (
    ScriptProposalReview,
    ScriptProposalViolation,
)
from video_editing_agent.domain.brief.model import AuthoritativeFact, Brief
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityStatus
from video_editing_agent.planning.script.workflow import _deterministic_claim_fallback

NOW = datetime(2026, 8, 26, tzinfo=UTC)


def _brief() -> Brief:
    return Brief(
        EntityEnvelope("brf_gate2", 1, "0.2", EntityStatus.VALID, NOW, "test"),
        "通勤水杯",
        "展示日常通勤场景",
        "年轻上班族",
        "短视频",
        "便携、日常使用方便",
        authoritative_facts=(AuthoritativeFact("fact_capacity", "The bottle capacity is 350ml."),),
    )


def _claim_review(*section_ids: str) -> ScriptProposalReview:
    return ScriptProposalReview(
        False,
        tuple(
            ScriptProposalViolation(
                "unsupported_claim",
                "The planned section asserts an unsupported product property.",
                section_id,
            )
            for section_id in section_ids
        ),
    )


def test_deterministic_claim_fallback_keeps_only_exact_verified_fact() -> None:
    proposal = ScriptPlanProposal(
        (
            NarrativeSectionProposal(
                "demonstration",
                "proof",
                "Show that the bottle is portable.",
                spoken_content="It fits in a bag and can be held in one hand.",
                visual_requirement="Put it in a bag and hold it in one hand.",
                on_screen_text_intent="Easy to carry",
                editing_intent="Emphasize portability",
                protected_fact_ids=("fact_capacity",),
            ),
        )
    )

    fallback = _deterministic_claim_fallback(
        _brief(),
        proposal,
        _claim_review("demonstration"),
        current_script=None,
    )

    assert fallback is not None
    section = fallback.sections[0]
    assert section.spoken_content == "The bottle capacity is 350ml."
    assert section.on_screen_text_intent is None
    assert section.visual_requirement == (
        "Show close or medium detail coverage of visible product form. Do not stage a fit, "
        "ease, performance, or outcome demonstration."
    )
    assert section.editing_intent is None
    joined = " ".join(
        value
        for value in (
            section.information_goal,
            section.spoken_content,
            section.visual_requirement,
            section.on_screen_text_intent,
        )
        if value is not None
    ).casefold()
    assert "fits in a bag" not in joined
    assert "held in one hand" not in joined
    assert "easy to carry" not in joined


def test_deterministic_fallback_assigns_repeated_fact_to_one_narrative_role() -> None:
    proposal = ScriptPlanProposal(
        tuple(
            NarrativeSectionProposal(
                section_id,
                narrative_role,
                "Unsupported convenience claim.",
                spoken_content="Convenient everywhere.",
                visual_requirement="Demonstrate easy use.",
                on_screen_text_intent="Convenient",
                protected_fact_ids=("fact_capacity",),
            )
            for section_id, narrative_role in (
                ("hook", "hook"),
                ("demonstration", "demonstration"),
                ("closing", "closing"),
            )
        )
    )

    fallback = _deterministic_claim_fallback(
        _brief(),
        proposal,
        _claim_review("hook", "demonstration", "closing"),
        current_script=None,
    )

    assert fallback is not None
    fact_text = "The bottle capacity is 350ml."
    presentations = sum(
        value == fact_text
        for section in fallback.sections
        for value in (section.spoken_content, section.on_screen_text_intent)
    )
    assert presentations == 1
    assert fallback.sections[1].spoken_content == fact_text
    assert fallback.sections[0].visual_requirement != fallback.sections[1].visual_requirement
    assert fallback.sections[1].visual_requirement != fallback.sections[2].visual_requirement
    assert all(section.editing_intent is None for section in fallback.sections)


def test_deterministic_fallback_never_handles_non_claim_policy_veto() -> None:
    proposal = ScriptPlanProposal((NarrativeSectionProposal("hook", "hook", "Show the product."),))
    review = ScriptProposalReview(
        False,
        (
            ScriptProposalViolation(
                "prohibited_content",
                "The proposal violates a prohibited-content rule.",
                "hook",
            ),
        ),
    )

    assert (
        _deterministic_claim_fallback(
            _brief(),
            proposal,
            review,
            current_script=None,
        )
        is None
    )

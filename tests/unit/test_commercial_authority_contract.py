from datetime import UTC, datetime

from video_editing_agent.application.ports.preproduction_planning import ScriptPlanProposal
from video_editing_agent.application.ports.preproduction_review import ScriptProposalReviewRequest
from video_editing_agent.domain.brief.model import AuthoritativeFact, Brief
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityStatus
from video_editing_agent.planning.authority.commercial import (
    COMMERCIAL_AUTHORITY_SYSTEM_RULES,
    CONCRETE_CLAIM_CATEGORIES,
    commercial_authority_payload,
)
from video_editing_agent.providers.llm.deepseek_chat import _brief_payload
from video_editing_agent.providers.llm.deepseek_preproduction_review import _brief_review_payload


def _brief() -> Brief:
    return Brief(
        envelope=EntityEnvelope(
            id="brf_authority",
            revision=1,
            schema_version="0.2",
            status=EntityStatus.DRAFT,
            created_at=datetime(2026, 8, 12, tzinfo=UTC),
            created_by="test",
        ),
        title="500 mL bottle commute-scene ad",
        objective="Create a short product ad.",
        audience="commuters",
        platform="generic vertical short-form",
        core_message="Show the bottle in a commute-preparation context.",
        product_topic="500 mL bottle",
        authoritative_facts=(
            AuthoritativeFact("fact_capacity", "Bottle capacity is 500 mL."),
            AuthoritativeFact("fact_lid", "Bottle has a screw-on lid."),
        ),
        prohibited_content=("Do not claim leak resistance.",),
        brand_constraints=("Keep factual claims auditable.",),
    )


def test_commercial_authority_separates_positioning_from_factual_support() -> None:
    payload = commercial_authority_payload(_brief())

    assert payload["positioning_intent"] == "Show the bottle in a commute-preparation context."
    assert payload["positioning_intent_is_factual_authority"] is False
    assert payload["concrete_claim_requires_authoritative_fact"] is True
    assert payload["supported_mechanism_description_mode"] == "neutral_observable_action_or_state"
    assert payload["mechanism_fact_does_not_authorize"] == [
        "ease",
        "convenience",
        "simplicity",
        "sufficiency",
        "result",
    ]
    assert payload["successful_demonstration_outcome_requires_authoritative_support"] is True
    assert payload["unsupported_claim_handling"] == "unresolved_or_nonclaim_framing"
    assert payload["concrete_claim_categories"] == [
        item.value for item in CONCRETE_CLAIM_CATEGORIES
    ]
    assert payload["authoritative_facts"] == [
        {"fact_id": "fact_capacity", "statement": "Bottle capacity is 500 mL."},
        {"fact_id": "fact_lid", "statement": "Bottle has a screw-on lid."},
    ]


def test_shared_rules_require_neutral_observable_mechanical_description() -> None:
    assert "observable mechanism, action, or state" in COMMERCIAL_AUTHORITY_SYSTEM_RULES
    assert "evaluative or sufficiency meaning" in COMMERCIAL_AUTHORITY_SYSTEM_RULES
    assert "'just/only do X'" in COMMERCIAL_AUTHORITY_SYSTEM_RULES
    assert "spoken copy" in COMMERCIAL_AUTHORITY_SYSTEM_RULES
    assert "shooting instructions" in COMMERCIAL_AUTHORITY_SYSTEM_RULES


def test_generation_and_semantic_review_share_the_exact_brief_projection() -> None:
    brief = _brief()
    generation_payload = _brief_payload(brief)
    review_payload = _brief_review_payload(
        ScriptProposalReviewRequest(brief=brief, proposal=ScriptPlanProposal(()))
    )

    assert review_payload == generation_payload
    assert review_payload["commercial_authority"] == commercial_authority_payload(brief)
    assert review_payload["title"] == brief.title
    assert review_payload["platform"] == brief.platform
    assert review_payload["target_duration"] is None
    assert review_payload["references"] == []

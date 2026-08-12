from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from video_editing_agent.domain.brief.model import Brief


class ConcreteClaimCategory(StrEnum):
    PROPERTY = "property"
    PERFORMANCE = "performance"
    FIT = "fit"
    ADEQUACY = "adequacy"
    OPERABILITY = "operability"
    MATERIAL = "material"
    RELIABILITY = "reliability"
    OUTCOME = "outcome"


CONCRETE_CLAIM_CATEGORIES = tuple(ConcreteClaimCategory)

# This is the single provider-neutral semantic rule text for commercial pre-production.
# Providers may add stage-specific constraints, but they must not redefine this authority model.
COMMERCIAL_AUTHORITY_SYSTEM_RULES = (
    "Use brief.commercial_authority as the shared commercial semantic contract. "
    "Its positioning_intent describes desired narrative or marketing framing and is not factual "
    "evidence. Objective and audience are also context, not evidence. Concrete product claims "
    "about property, performance, fit, adequacy, operability, material, reliability, or outcome "
    "require direct support from the listed authoritative_facts. A structural or mechanical "
    "feature does not imply a performance property or outcome. Examples: 500 mL does not prove "
    "that an amount is enough for a commute or that a product fits easily in a backpack; a "
    "screw-on lid does not prove one-hand operation or leak resistance. A structural or "
    "mechanical feature establishes only its stated structure or mechanism; it does not establish "
    "ease of use, convenience, performance, reliability, or outcomes. A screw-on lid does not "
    "establish easy, simple, or convenient opening or closing. A planned successful visual "
    "demonstration can itself imply a concrete claim, including fit or adequacy, and therefore "
    "follows the same support rule. When concrete support is absent, keep the claim unresolved or "
    "use non-claim framing; never convert positioning intent, reviewer diagnostics, or a desired "
    "demonstration into fact."
)


@dataclass(frozen=True, slots=True)
class CommercialAuthoritySnapshot:
    positioning_intent: str
    authoritative_facts: tuple[tuple[str, str], ...]
    prohibited_content: tuple[str, ...]
    brand_constraints: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "positioning_intent": self.positioning_intent,
            "positioning_intent_is_factual_authority": False,
            "authoritative_facts": [
                {"fact_id": fact_id, "statement": statement}
                for fact_id, statement in self.authoritative_facts
            ],
            "concrete_claim_categories": [
                item.value for item in CONCRETE_CLAIM_CATEGORIES
            ],
            "concrete_claim_requires_authoritative_fact": True,
            "successful_demonstration_outcome_requires_authoritative_support": True,
            "unsupported_claim_handling": "unresolved_or_nonclaim_framing",
            "prohibited_content": list(self.prohibited_content),
            "brand_constraints": list(self.brand_constraints),
        }


def commercial_authority_snapshot(brief: Brief) -> CommercialAuthoritySnapshot:
    """Project a Brief into the one shared commercial authority view used by model stages."""

    return CommercialAuthoritySnapshot(
        positioning_intent=brief.core_message,
        authoritative_facts=tuple(
            (fact.fact_id, fact.statement) for fact in brief.authoritative_facts
        ),
        prohibited_content=brief.prohibited_content,
        brand_constraints=brief.brand_constraints,
    )


def commercial_authority_payload(brief: Brief) -> dict[str, Any]:
    return commercial_authority_snapshot(brief).to_payload()

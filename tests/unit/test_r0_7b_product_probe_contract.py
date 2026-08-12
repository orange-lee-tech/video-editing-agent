from __future__ import annotations

import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from video_editing_agent.domain.brief.model import AuthoritativeFact, Brief
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityStatus
from video_editing_agent.planning.authority.commercial import (
    COMMERCIAL_AUTHORITY_SYSTEM_RULES,
    commercial_authority_payload,
)
from video_editing_agent.storage.repositories.preproduction_codec import encode_brief

sys.path.insert(0, str(Path(__file__).parents[2]))
probe = importlib.import_module("tools.probes.r0_7b_product_probe")


def _brief() -> Brief:
    return Brief(
        envelope=EntityEnvelope(
            id="brf_probe_contract",
            revision=1,
            schema_version="0.2",
            status=EntityStatus.DRAFT,
            created_at=datetime(2026, 8, 12, tzinfo=UTC),
            created_by="test",
        ),
        title="500 mL water bottle commute-scene ad",
        objective="Create a short product ad.",
        audience="commuters",
        platform="generic vertical short-form",
        core_message="Show 500 mL capacity and screw-on lid in a commute-preparation context.",
        product_topic="500 mL bottle",
        authoritative_facts=(
            AuthoritativeFact("fact_capacity", "Bottle capacity is 500 mL."),
            AuthoritativeFact("fact_lid", "Bottle has a screw-on lid."),
        ),
    )


def test_product_ad_fixture_uses_commute_as_framing_not_fit_authority() -> None:
    case = probe.product_ad_case()

    assert case.brief_content.product_topic == "500 mL 水杯"
    assert "方便日常通勤携带" not in case.brief_content.core_message
    assert "500 mL 容量和旋拧式杯盖" in case.brief_content.core_message
    assert (
        "通勤场景只作为叙事定位，不构成具体的携带适配性或产品性能事实。"
        in case.brief_content.success_criteria
    )
    assert [fact.statement for fact in case.brief_content.authoritative_facts] == [
        "水杯容量为 500 mL。",
        "水杯使用旋拧式杯盖。",
    ]


def test_product_review_prompt_reuses_shared_commercial_authority_contract() -> None:
    assert COMMERCIAL_AUTHORITY_SYSTEM_RULES in probe.PRODUCT_REVIEW_SYSTEM_PROMPT
    assert "planned successful visual demonstration" in probe.PRODUCT_REVIEW_SYSTEM_PROMPT


def test_product_review_context_receives_structured_commercial_authority() -> None:
    brief = _brief()
    context = {"brief": json.loads(encode_brief(brief)), "case_id": "product_ad"}

    patched = probe._context_with_commercial_authority(context)
    authority = patched["brief"]["commercial_authority"]

    assert patched is not context
    assert patched["brief"] is not context["brief"]
    assert authority == commercial_authority_payload(brief)
    assert authority["positioning_intent_is_factual_authority"] is False

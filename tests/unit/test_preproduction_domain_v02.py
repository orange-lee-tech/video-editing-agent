from datetime import UTC, datetime

import pytest

from video_editing_agent.domain.brief.model import AuthoritativeFact, Brief, BriefReference
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.script.model import NarrativeSection, ScriptPlan
from video_editing_agent.domain.shooting.model import (
    CoveragePriority,
    ProductionConstraints,
    ShotRequirement,
    ShootingPlan,
)

NOW = datetime(2026, 8, 11, 18, 0, tzinfo=UTC)


def envelope(entity_id: str) -> EntityEnvelope:
    return EntityEnvelope(
        id=entity_id,
        revision=1,
        schema_version="0.2",
        status=EntityStatus.DRAFT,
        created_at=NOW,
        created_by="test",
    )


def test_brief_supports_commercial_facts_and_references() -> None:
    brief = Brief(
        envelope=envelope("brf_product"),
        title="Launch clip",
        objective="Drive product consideration",
        audience="First-time buyers",
        platform="short-form vertical",
        core_message="The product is simple to use.",
        product_topic="Example product",
        target_duration=MediaTime(30, 1),
        authoritative_facts=(
            AuthoritativeFact("fact_price", "Launch price is 99 USD", "approved offer sheet"),
        ),
        references=(
            BriefReference(
                "ref_style",
                "video",
                "Use the reference for pacing and structure only.",
                EntityRevisionRef("ast_reference", 1),
            ),
        ),
    )

    assert brief.target_duration == MediaTime(30, 1)
    assert brief.authoritative_facts[0].fact_id == "fact_price"
    assert brief.references[0].asset_ref == EntityRevisionRef("ast_reference", 1)


def test_brief_keeps_bootstrap_constructor_compatible() -> None:
    brief = Brief(
        envelope("brf_legacy"),
        "Title",
        "Objective",
        "Audience",
        "Platform",
        "Core message",
    )

    assert brief.product_topic is None
    assert brief.references == ()


def test_brief_rejects_duplicate_authoritative_fact_ids() -> None:
    with pytest.raises(ValueError, match="unique fact_id"):
        Brief(
            envelope("brf_duplicate"),
            "Title",
            "Objective",
            "Audience",
            "Platform",
            "Core message",
            authoritative_facts=(
                AuthoritativeFact("fact_1", "First"),
                AuthoritativeFact("fact_1", "Second"),
            ),
        )


def test_script_plan_derives_duration_and_locked_sections() -> None:
    script = ScriptPlan(
        envelope=envelope("scp_product"),
        brief_ref=EntityRevisionRef("brf_product", 1),
        sections=(
            NarrativeSection(
                section_id="hook",
                narrative_role="hook",
                information_goal="Earn attention",
                target_duration=MediaTime(3, 1),
                protected_fact_ids=("fact_price",),
                locked=True,
            ),
            NarrativeSection(
                section_id="proof",
                narrative_role="proof",
                information_goal="Demonstrate the product",
                target_duration=MediaTime(7, 1),
            ),
        ),
    )

    assert script.estimated_duration == MediaTime(10, 1)
    assert script.locked_section_ids == ("hook",)


def test_script_plan_duration_is_unknown_when_a_section_has_no_budget() -> None:
    script = ScriptPlan(
        envelope=envelope("scp_unknown"),
        brief_ref=EntityRevisionRef("brf_product", 1),
        sections=(
            NarrativeSection(
                "hook",
                "hook",
                "Earn attention",
                target_duration=MediaTime(3, 1),
            ),
            NarrativeSection("body", "body", "Explain value"),
        ),
    )

    assert script.estimated_duration is None


def test_script_plan_rejects_duplicate_section_ids() -> None:
    with pytest.raises(ValueError, match="unique section_id"):
        ScriptPlan(
            envelope=envelope("scp_duplicate"),
            brief_ref=EntityRevisionRef("brf_product", 1),
            sections=(
                NarrativeSection("same", "hook", "A"),
                NarrativeSection("same", "proof", "B"),
            ),
        )


def test_shot_requirement_models_practical_capture_guidance() -> None:
    requirement = ShotRequirement(
        requirement_id="req_demo",
        script_section_ref="proof",
        purpose="Show the product in use",
        subject="Product and hand",
        action="Operate the main control",
        framing="close",
        camera_motion="static",
        target_duration=MediaTime(4, 1),
        minimum_duration=MediaTime(2, 1),
        priority=CoveragePriority.REQUIRED,
        capture_instruction="Move close, start recording, then operate the control once.",
        alternate_coverage=("Repeat from a wider angle",),
        handle_before=MediaTime(1, 1),
        handle_after=MediaTime(1, 1),
    )

    assert requirement.priority is CoveragePriority.REQUIRED
    assert requirement.minimum_duration == MediaTime(2, 1)


def test_shot_requirement_rejects_target_shorter_than_minimum() -> None:
    with pytest.raises(ValueError, match="shorter than minimum"):
        ShotRequirement(
            "req_bad",
            "proof",
            "Show proof",
            "Product",
            target_duration=MediaTime(1, 1),
            minimum_duration=MediaTime(2, 1),
        )


def test_shooting_plan_captures_production_constraints_and_unique_requirements() -> None:
    requirement = ShotRequirement("req_1", "hook", "Show product", "Product")
    plan = ShootingPlan(
        envelope=envelope("shp_product"),
        script_plan_ref=EntityRevisionRef("scp_product", 1),
        requirements=(requirement,),
        constraints=ProductionConstraints(
            camera_or_phone="phone",
            stabilizer="tripod",
            people_count=1,
            locations=("desk",),
            user_skill_level="ordinary user",
        ),
    )

    assert plan.constraints.camera_or_phone == "phone"
    assert plan.requirements[0].priority is CoveragePriority.RECOMMENDED


def test_shooting_plan_rejects_duplicate_requirement_ids() -> None:
    with pytest.raises(ValueError, match="unique requirement_id"):
        ShootingPlan(
            envelope=envelope("shp_duplicate"),
            script_plan_ref=EntityRevisionRef("scp_product", 1),
            requirements=(
                ShotRequirement("req_same", "hook", "A", "Product"),
                ShotRequirement("req_same", "proof", "B", "Product"),
            ),
        )

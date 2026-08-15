from __future__ import annotations

from datetime import UTC, datetime

import pytest

from video_editing_agent.domain.common.entity import (
    EntityEnvelope,
    EntityRevisionRef,
    EntityStatus,
)
from video_editing_agent.domain.edit.model import EditPlan, EditSlot

NOW = datetime(2026, 8, 15, tzinfo=UTC)
BRIEF_REF = EntityRevisionRef("brief", 1)
SCRIPT_REF = EntityRevisionRef("script", 2)
SHOOTING_REF = EntityRevisionRef("shooting", 3)


def _envelope() -> EntityEnvelope:
    return EntityEnvelope("edit-plan", 1, "0.2", EntityStatus.VALID, NOW, "test")


def _slot(identity: str = "intro", order: int = 0) -> EditSlot:
    return EditSlot(identity, "show product value", order)


def test_editing_only_requires_brief_but_not_planning_artifacts() -> None:
    plan = EditPlan(
        _envelope(),
        None,
        None,
        (_slot(),),
        brief_ref=BRIEF_REF,
    )

    assert plan.brief_ref == BRIEF_REF
    assert plan.script_plan_ref is None
    assert plan.shooting_plan_ref is None


def test_brief_rooted_plan_can_keep_script_context_without_shooting_plan() -> None:
    plan = EditPlan(
        _envelope(),
        SCRIPT_REF,
        None,
        (_slot(),),
        brief_ref=BRIEF_REF,
    )

    assert plan.brief_ref == BRIEF_REF
    assert plan.script_plan_ref == SCRIPT_REF
    assert plan.shooting_plan_ref is None


def test_combined_plan_retains_exact_planning_provenance() -> None:
    plan = EditPlan(
        _envelope(),
        SCRIPT_REF,
        SHOOTING_REF,
        (_slot(),),
        brief_ref=BRIEF_REF,
    )

    assert plan.brief_ref == BRIEF_REF
    assert plan.script_plan_ref == SCRIPT_REF
    assert plan.shooting_plan_ref == SHOOTING_REF


def test_legacy_combined_shape_remains_compatible() -> None:
    plan = EditPlan(
        _envelope(),
        SCRIPT_REF,
        SHOOTING_REF,
        (_slot(),),
    )

    assert plan.brief_ref is None
    assert plan.script_plan_ref == SCRIPT_REF
    assert plan.shooting_plan_ref == SHOOTING_REF


@pytest.mark.parametrize(
    ("brief_ref", "script_ref", "shooting_ref", "message"),
    (
        (None, None, None, "requires Brief provenance"),
        (None, SCRIPT_REF, None, "requires Brief provenance"),
        (BRIEF_REF, None, SHOOTING_REF, "without ScriptPlan"),
    ),
)
def test_broken_provenance_shapes_fail_closed(
    brief_ref: EntityRevisionRef | None,
    script_ref: EntityRevisionRef | None,
    shooting_ref: EntityRevisionRef | None,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        EditPlan(
            _envelope(),
            script_ref,
            shooting_ref,
            (_slot(),),
            brief_ref=brief_ref,
        )


def test_existing_slot_identity_and_order_guards_remain_active() -> None:
    with pytest.raises(ValueError, match="unique slots"):
        EditPlan(
            _envelope(),
            None,
            None,
            (_slot("same", 0), _slot("same", 1)),
            brief_ref=BRIEF_REF,
        )

    with pytest.raises(ValueError, match="ordered"):
        EditPlan(
            _envelope(),
            None,
            None,
            (_slot("later", 1), _slot("earlier", 0)),
            brief_ref=BRIEF_REF,
        )

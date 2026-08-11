from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.script.model import NarrativeSection, ScriptPlan
from video_editing_agent.domain.shooting.model import ProductionConstraints, ShotRequirement
from video_editing_agent.planning.shooting.service import ShootingPlanner

NOW = datetime(2026, 8, 11, 22, 45, tzinfo=UTC)
SCRIPT_REF = EntityRevisionRef("scp_locations", 1)


class ScriptRepo:
    def load(self, script_plan_ref: EntityRevisionRef) -> ScriptPlan:
        if script_plan_ref != SCRIPT_REF:
            raise KeyError(script_plan_ref)
        return ScriptPlan(
            envelope=EntityEnvelope(
                id="scp_locations",
                revision=1,
                schema_version="0.2",
                status=EntityStatus.DRAFT,
                created_at=NOW,
                created_by="test",
            ),
            brief_ref=EntityRevisionRef("brf_locations", 1),
            sections=(NarrativeSection("hook", "hook", "Open the video"),),
        )

    def save(self, script_plan: ScriptPlan) -> None:
        raise AssertionError("ShootingPlanner must not save ScriptPlan")


class ShootingRepo:
    def __init__(self) -> None:
        self.saved: list[Any] = []

    def load(self, shooting_plan_ref: EntityRevisionRef) -> Any:
        for item in self.saved:
            if EntityRevisionRef(item.envelope.id, item.envelope.revision) == shooting_plan_ref:
                return item
        raise KeyError(shooting_plan_ref)

    def save(self, shooting_plan: Any) -> None:
        self.saved.append(shooting_plan)


def planner(repository: ShootingRepo) -> ShootingPlanner:
    return ShootingPlanner(
        script_plan_repository=ScriptRepo(),
        shooting_plan_repository=repository,
        shooting_plan_id_factory=lambda: "shp_locations",
        clock=lambda: NOW,
    )


def requirement(environment: str | None) -> ShotRequirement:
    return ShotRequirement(
        requirement_id="req_hook",
        script_section_ref="hook",
        purpose="Capture the opening",
        subject="person",
        environment=environment,
    )


def test_exact_declared_location_is_accepted() -> None:
    repository = ShootingRepo()
    constraints = ProductionConstraints(locations=("家中书桌", "门口/玄关"))

    result = planner(repository).create(
        SCRIPT_REF,
        (requirement("家中书桌"),),
        constraints=constraints,
    )

    assert result.requirements[0].environment == "家中书桌"
    assert repository.saved == [result]


def test_undeclared_or_combined_location_is_rejected_before_save() -> None:
    repository = ShootingRepo()
    constraints = ProductionConstraints(locations=("家中书桌", "门口/玄关"))

    with pytest.raises(ValueError, match="must exactly match"):
        planner(repository).create(
            SCRIPT_REF,
            (requirement("家中书桌或厨房水槽"),),
            constraints=constraints,
        )

    assert repository.saved == []


def test_missing_environment_is_rejected_when_locations_are_declared() -> None:
    repository = ShootingRepo()
    constraints = ProductionConstraints(locations=("家中书桌",))

    with pytest.raises(ValueError, match="must exactly match"):
        planner(repository).create(
            SCRIPT_REF,
            (requirement(None),),
            constraints=constraints,
        )

    assert repository.saved == []


def test_empty_location_constraints_do_not_invent_location_authority() -> None:
    repository = ShootingRepo()

    result = planner(repository).create(
        SCRIPT_REF,
        (requirement("临时场景"),),
        constraints=ProductionConstraints(),
    )

    assert result.requirements[0].environment == "临时场景"
    assert repository.saved == [result]


def test_revise_validates_against_effective_updated_constraints() -> None:
    repository = ShootingRepo()
    initial = planner(repository).create(
        SCRIPT_REF,
        (requirement("家中书桌"),),
        constraints=ProductionConstraints(locations=("家中书桌",)),
    )
    current_ref = EntityRevisionRef(initial.envelope.id, initial.envelope.revision)

    with pytest.raises(ValueError, match="must exactly match"):
        planner(repository).revise(
            current_ref,
            (requirement("家中书桌"),),
            constraints=ProductionConstraints(locations=("门口/玄关",)),
        )

    assert repository.saved == [initial]

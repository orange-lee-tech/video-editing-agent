from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from video_editing_agent.application.ports.script_plan_repository import ScriptPlanRepository
from video_editing_agent.application.ports.shooting_plan_repository import ShootingPlanRepository
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.script.model import ScriptPlan
from video_editing_agent.domain.shooting.model import (
    ProductionConstraints,
    ShootingPlan,
    ShotRequirement,
)

PREPRODUCTION_SCHEMA_VERSION = "0.2"


def _default_shooting_plan_id() -> str:
    return f"shp_{uuid.uuid4().hex}"


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _validate_requirement_sections(
    script_plan: ScriptPlan,
    requirements: tuple[ShotRequirement, ...],
) -> None:
    section_ids = {section.section_id for section in script_plan.sections}
    for requirement in requirements:
        if requirement.script_section_ref not in section_ids:
            raise ValueError(
                f"ShotRequirement {requirement.requirement_id!r} references unknown Script section "
                f"{requirement.script_section_ref!r}"
            )


def _validate_requirement_locations(
    constraints: ProductionConstraints,
    requirements: tuple[ShotRequirement, ...],
) -> None:
    location_ids = {location.location_id for location in constraints.locations}
    for requirement in requirements:
        if requirement.location_ref is not None and requirement.location_ref not in location_ids:
            raise ValueError(
                f"ShotRequirement {requirement.requirement_id!r} references unknown production "
                f"location {requirement.location_ref!r}"
            )
        if (
            constraints.locations
            and requirement.environment_description is not None
            and requirement.location_ref is None
        ):
            raise ValueError(
                f"ShotRequirement {requirement.requirement_id!r} has an environment description "
                "but no structured location_ref"
            )


def _validate_requirements(
    script_plan: ScriptPlan,
    constraints: ProductionConstraints,
    requirements: tuple[ShotRequirement, ...],
) -> None:
    _validate_requirement_sections(script_plan, requirements)
    _validate_requirement_locations(constraints, requirements)


def _derived_refs(
    current_ref: EntityRevisionRef,
    script_plan_ref: EntityRevisionRef,
) -> tuple[EntityRevisionRef, ...]:
    if current_ref == script_plan_ref:
        return (current_ref,)
    return (current_ref, script_plan_ref)


class ShootingPlanner:
    """Semantic owner for ShootingPlan creation and structured revision."""

    def __init__(
        self,
        *,
        script_plan_repository: ScriptPlanRepository,
        shooting_plan_repository: ShootingPlanRepository,
        shooting_plan_id_factory: Callable[[], str] = _default_shooting_plan_id,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._script_plan_repository = script_plan_repository
        self._shooting_plan_repository = shooting_plan_repository
        self._shooting_plan_id_factory = shooting_plan_id_factory
        self._clock = clock

    def create(
        self,
        script_plan_ref: EntityRevisionRef,
        requirements: tuple[ShotRequirement, ...],
        *,
        constraints: ProductionConstraints | None = None,
        notes: tuple[str, ...] = (),
        created_by: str = "system",
    ) -> ShootingPlan:
        script_plan = self._script_plan_repository.load(script_plan_ref)
        effective_constraints = ProductionConstraints() if constraints is None else constraints
        _validate_requirements(script_plan, effective_constraints, requirements)
        shooting_plan_id = self._shooting_plan_id_factory()
        if not shooting_plan_id.startswith("shp_"):
            raise ValueError("shooting_plan_id_factory must return an shp_* identifier")
        shooting_plan = ShootingPlan(
            envelope=EntityEnvelope(
                id=shooting_plan_id,
                revision=1,
                schema_version=PREPRODUCTION_SCHEMA_VERSION,
                status=EntityStatus.DRAFT,
                created_at=self._clock(),
                created_by=created_by,
                derived_from=(script_plan_ref,),
            ),
            script_plan_ref=script_plan_ref,
            requirements=requirements,
            constraints=effective_constraints,
            notes=notes,
        )
        self._shooting_plan_repository.save(shooting_plan)
        return shooting_plan

    def revise(
        self,
        current_ref: EntityRevisionRef,
        requirements: tuple[ShotRequirement, ...],
        *,
        script_plan_ref: EntityRevisionRef | None = None,
        constraints: ProductionConstraints | None = None,
        notes: tuple[str, ...] | None = None,
        created_by: str = "system",
    ) -> ShootingPlan:
        current = self._shooting_plan_repository.load(current_ref)
        actual_ref = EntityRevisionRef(current.envelope.id, current.envelope.revision)
        if actual_ref != current_ref:
            raise RuntimeError("ShootingPlanRepository returned a different exact revision")
        target_script_ref = script_plan_ref or current.script_plan_ref
        script_plan = self._script_plan_repository.load(target_script_ref)
        effective_constraints = current.constraints if constraints is None else constraints
        _validate_requirements(script_plan, effective_constraints, requirements)
        revised = ShootingPlan(
            envelope=EntityEnvelope(
                id=current.envelope.id,
                revision=current.envelope.revision + 1,
                schema_version=PREPRODUCTION_SCHEMA_VERSION,
                status=EntityStatus.DRAFT,
                created_at=self._clock(),
                created_by=created_by,
                derived_from=_derived_refs(current_ref, target_script_ref),
            ),
            script_plan_ref=target_script_ref,
            requirements=requirements,
            constraints=effective_constraints,
            notes=current.notes if notes is None else notes,
        )
        self._shooting_plan_repository.save(revised)
        return revised

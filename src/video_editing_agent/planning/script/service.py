from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime

from video_editing_agent.application.ports.brief_repository import BriefRepository
from video_editing_agent.application.ports.script_plan_repository import ScriptPlanRepository
from video_editing_agent.domain.brief.model import Brief
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.script.model import NarrativeSection, ScriptPlan

PREPRODUCTION_SCHEMA_VERSION = "0.2"


def _default_script_plan_id() -> str:
    return f"scp_{uuid.uuid4().hex}"


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _validate_protected_facts(brief: Brief, sections: tuple[NarrativeSection, ...]) -> None:
    available_fact_ids = {fact.fact_id for fact in brief.authoritative_facts}
    for section in sections:
        missing = tuple(
            fact_id for fact_id in section.protected_fact_ids if fact_id not in available_fact_ids
        )
        if missing:
            raise ValueError(
                f"section {section.section_id!r} references unknown protected facts: {missing!r}"
            )


def _validate_locked_sections(
    current: ScriptPlan,
    proposed_sections: tuple[NarrativeSection, ...],
    *,
    allow_locked_changes: bool,
) -> None:
    if allow_locked_changes:
        return
    proposed_by_id = {section.section_id: section for section in proposed_sections}
    for section in current.sections:
        if section.locked and proposed_by_id.get(section.section_id) != section:
            raise ValueError(
                f"locked section {section.section_id!r} cannot change without explicit override"
            )


def _derived_refs(
    current_ref: EntityRevisionRef,
    brief_ref: EntityRevisionRef,
) -> tuple[EntityRevisionRef, ...]:
    if current_ref == brief_ref:
        return (current_ref,)
    return (current_ref, brief_ref)


class ScriptPlanner:
    """Semantic owner for ScriptPlan creation and structured revision."""

    def __init__(
        self,
        *,
        brief_repository: BriefRepository,
        script_plan_repository: ScriptPlanRepository,
        script_plan_id_factory: Callable[[], str] = _default_script_plan_id,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._brief_repository = brief_repository
        self._script_plan_repository = script_plan_repository
        self._script_plan_id_factory = script_plan_id_factory
        self._clock = clock

    def create(
        self,
        brief_ref: EntityRevisionRef,
        sections: tuple[NarrativeSection, ...],
        *,
        created_by: str = "system",
    ) -> ScriptPlan:
        brief = self._brief_repository.load(brief_ref)
        _validate_protected_facts(brief, sections)
        script_plan_id = self._script_plan_id_factory()
        if not script_plan_id.startswith("scp_"):
            raise ValueError("script_plan_id_factory must return an scp_* identifier")
        script_plan = ScriptPlan(
            envelope=EntityEnvelope(
                id=script_plan_id,
                revision=1,
                schema_version=PREPRODUCTION_SCHEMA_VERSION,
                status=EntityStatus.DRAFT,
                created_at=self._clock(),
                created_by=created_by,
                derived_from=(brief_ref,),
            ),
            brief_ref=brief_ref,
            sections=sections,
        )
        self._script_plan_repository.save(script_plan)
        return script_plan

    def revise(
        self,
        current_ref: EntityRevisionRef,
        sections: tuple[NarrativeSection, ...],
        *,
        brief_ref: EntityRevisionRef | None = None,
        allow_locked_changes: bool = False,
        created_by: str = "system",
    ) -> ScriptPlan:
        current = self._script_plan_repository.load(current_ref)
        actual_ref = EntityRevisionRef(current.envelope.id, current.envelope.revision)
        if actual_ref != current_ref:
            raise RuntimeError("ScriptPlanRepository returned a different exact revision")
        target_brief_ref = brief_ref or current.brief_ref
        brief = self._brief_repository.load(target_brief_ref)
        _validate_locked_sections(
            current,
            sections,
            allow_locked_changes=allow_locked_changes,
        )
        _validate_protected_facts(brief, sections)
        revised = ScriptPlan(
            envelope=EntityEnvelope(
                id=current.envelope.id,
                revision=current.envelope.revision + 1,
                schema_version=PREPRODUCTION_SCHEMA_VERSION,
                status=EntityStatus.DRAFT,
                created_at=self._clock(),
                created_by=created_by,
                derived_from=_derived_refs(current_ref, target_brief_ref),
            ),
            brief_ref=target_brief_ref,
            sections=sections,
        )
        self._script_plan_repository.save(revised)
        return revised

    def set_section_lock(
        self,
        current_ref: EntityRevisionRef,
        section_id: str,
        *,
        locked: bool,
        created_by: str = "user",
    ) -> ScriptPlan:
        if not section_id.strip():
            raise ValueError("section_id must not be empty")
        current = self._script_plan_repository.load(current_ref)
        matching = tuple(
            section for section in current.sections if section.section_id == section_id
        )
        if not matching:
            raise ValueError(f"unknown Script section: {section_id!r}")
        section = matching[0]
        if section.locked is locked:
            return current
        revised_sections = tuple(
            replace(item, locked=locked) if item.section_id == section_id else item
            for item in current.sections
        )
        return self.revise(
            current_ref,
            revised_sections,
            allow_locked_changes=True,
            created_by=created_by,
        )

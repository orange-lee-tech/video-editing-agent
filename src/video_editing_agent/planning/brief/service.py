from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from video_editing_agent.application.ports.brief_repository import BriefRepository
from video_editing_agent.domain.brief.model import AuthoritativeFact, Brief, BriefReference
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime

PREPRODUCTION_SCHEMA_VERSION = "0.2"


def _default_brief_id() -> str:
    return f"brf_{uuid.uuid4().hex}"


def _utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class BriefContent:
    title: str
    objective: str
    audience: str
    platform: str
    core_message: str
    product_topic: str | None = None
    target_duration: MediaTime | None = None
    authoritative_facts: tuple[AuthoritativeFact, ...] = ()
    style_emotion: tuple[str, ...] = ()
    success_criteria: tuple[str, ...] = ()
    prohibited_content: tuple[str, ...] = ()
    brand_constraints: tuple[str, ...] = ()
    user_notes: str | None = None
    references: tuple[BriefReference, ...] = ()

    @classmethod
    def from_brief(cls, brief: Brief) -> BriefContent:
        return cls(
            title=brief.title,
            objective=brief.objective,
            audience=brief.audience,
            platform=brief.platform,
            core_message=brief.core_message,
            product_topic=brief.product_topic,
            target_duration=brief.target_duration,
            authoritative_facts=brief.authoritative_facts,
            style_emotion=brief.style_emotion,
            success_criteria=brief.success_criteria,
            prohibited_content=brief.prohibited_content,
            brand_constraints=brief.brand_constraints,
            user_notes=brief.user_notes,
            references=brief.references,
        )

    def build(self, envelope: EntityEnvelope) -> Brief:
        return Brief(
            envelope=envelope,
            title=self.title,
            objective=self.objective,
            audience=self.audience,
            platform=self.platform,
            core_message=self.core_message,
            product_topic=self.product_topic,
            target_duration=self.target_duration,
            authoritative_facts=self.authoritative_facts,
            style_emotion=self.style_emotion,
            success_criteria=self.success_criteria,
            prohibited_content=self.prohibited_content,
            brand_constraints=self.brand_constraints,
            user_notes=self.user_notes,
            references=self.references,
        )


class BriefService:
    """Semantic owner for creating and revising Brief entities."""

    def __init__(
        self,
        repository: BriefRepository,
        *,
        brief_id_factory: Callable[[], str] = _default_brief_id,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._repository = repository
        self._brief_id_factory = brief_id_factory
        self._clock = clock

    def create(self, content: BriefContent, *, created_by: str = "system") -> Brief:
        brief_id = self._brief_id_factory()
        if not brief_id.startswith("brf_"):
            raise ValueError("brief_id_factory must return a brf_* identifier")
        brief = content.build(
            EntityEnvelope(
                id=brief_id,
                revision=1,
                schema_version=PREPRODUCTION_SCHEMA_VERSION,
                status=EntityStatus.DRAFT,
                created_at=self._clock(),
                created_by=created_by,
            )
        )
        self._repository.save(brief)
        return brief

    def revise(
        self,
        current_ref: EntityRevisionRef,
        content: BriefContent,
        *,
        created_by: str = "system",
    ) -> Brief:
        current = self._repository.load(current_ref)
        actual_ref = EntityRevisionRef(current.envelope.id, current.envelope.revision)
        if actual_ref != current_ref:
            raise RuntimeError("BriefRepository returned a different exact revision")
        revised = content.build(
            EntityEnvelope(
                id=current.envelope.id,
                revision=current.envelope.revision + 1,
                schema_version=PREPRODUCTION_SCHEMA_VERSION,
                status=EntityStatus.DRAFT,
                created_at=self._clock(),
                created_by=created_by,
                derived_from=(current_ref,),
            )
        )
        self._repository.save(revised)
        return revised

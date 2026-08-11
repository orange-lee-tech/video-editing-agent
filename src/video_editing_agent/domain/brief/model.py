from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime


def _require_nonempty(name: str, value: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} must not be empty")


def _require_positive_time(name: str, value: MediaTime | None) -> None:
    if value is not None and value.value <= 0:
        raise ValueError(f"{name} must be > 0")


def _require_nonempty_items(name: str, values: tuple[str, ...]) -> None:
    if any(not value.strip() for value in values):
        raise ValueError(f"{name} must not contain empty values")


@dataclass(frozen=True, slots=True)
class AuthoritativeFact:
    fact_id: str
    statement: str
    source_note: str | None = None

    def __post_init__(self) -> None:
        _require_nonempty("fact_id", self.fact_id)
        _require_nonempty("statement", self.statement)
        if self.source_note is not None:
            _require_nonempty("source_note", self.source_note)


@dataclass(frozen=True, slots=True)
class BriefReference:
    reference_id: str
    kind: str
    description: str
    asset_ref: EntityRevisionRef | None = None

    def __post_init__(self) -> None:
        _require_nonempty("reference_id", self.reference_id)
        _require_nonempty("kind", self.kind)
        _require_nonempty("description", self.description)


@dataclass(frozen=True, slots=True)
class Brief:
    envelope: EntityEnvelope
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

    def __post_init__(self) -> None:
        for name, value in (
            ("title", self.title),
            ("objective", self.objective),
            ("audience", self.audience),
            ("platform", self.platform),
            ("core_message", self.core_message),
        ):
            _require_nonempty(name, value)
        if self.product_topic is not None:
            _require_nonempty("product_topic", self.product_topic)
        if self.user_notes is not None:
            _require_nonempty("user_notes", self.user_notes)
        _require_positive_time("target_duration", self.target_duration)
        for name, values in (
            ("style_emotion", self.style_emotion),
            ("success_criteria", self.success_criteria),
            ("prohibited_content", self.prohibited_content),
            ("brand_constraints", self.brand_constraints),
        ):
            _require_nonempty_items(name, values)

        fact_ids = tuple(fact.fact_id for fact in self.authoritative_facts)
        if len(set(fact_ids)) != len(fact_ids):
            raise ValueError("authoritative_facts must have unique fact_id values")
        reference_ids = tuple(reference.reference_id for reference in self.references)
        if len(set(reference_ids)) != len(reference_ids):
            raise ValueError("references must have unique reference_id values")

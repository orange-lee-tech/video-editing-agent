from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class EntityStatus(StrEnum):
    DRAFT = "draft"
    VALID = "valid"
    STALE = "stale"
    ARCHIVED = "archived"


@dataclass(frozen=True, slots=True)
class EntityRevisionRef:
    entity_id: str
    revision: int

    def __post_init__(self) -> None:
        if not self.entity_id:
            raise ValueError("entity_id must not be empty")
        if self.revision < 1:
            raise ValueError("revision must be >= 1")


@dataclass(frozen=True, slots=True)
class EntityEnvelope:
    id: str
    revision: int
    schema_version: str
    status: EntityStatus
    created_at: datetime
    created_by: str
    derived_from: tuple[EntityRevisionRef, ...] = ()

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("id must not be empty")
        if self.revision < 1:
            raise ValueError("revision must be >= 1")
        if not self.schema_version:
            raise ValueError("schema_version must not be empty")
        if not self.created_by:
            raise ValueError("created_by must not be empty")
        if len(set(self.derived_from)) != len(self.derived_from):
            raise ValueError("derived_from must not contain duplicate exact revision refs")

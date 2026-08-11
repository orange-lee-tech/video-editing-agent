from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class ArtifactRetentionClass(StrEnum):
    REBUILDABLE_CACHE = "rebuildable_cache"
    DURABLE_DERIVED_EVIDENCE = "durable_derived_evidence"
    PROJECT_OUTPUT = "project_output"


_RETENTION_PRIORITY = {
    ArtifactRetentionClass.REBUILDABLE_CACHE: 0,
    ArtifactRetentionClass.DURABLE_DERIVED_EVIDENCE: 1,
    ArtifactRetentionClass.PROJECT_OUTPUT: 2,
}


@dataclass(frozen=True, slots=True)
class ArtifactLifecycleDescriptor:
    """Lifecycle metadata kept above content-addressed binary identity."""

    artifact_id: str
    retention_class: ArtifactRetentionClass
    purpose: str
    source_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.artifact_id.startswith("art_sha256_"):
            raise ValueError("artifact_id must use the art_sha256_* content-addressed form")
        if not self.purpose.strip():
            raise ValueError("purpose must not be empty")
        if any(not value.strip() for value in self.source_refs):
            raise ValueError("source_refs must not contain blank values")


class ArtifactLifecycleRepository(Protocol):
    """Persist references/retention semantics independently of binary content identity."""

    def add(self, descriptor: ArtifactLifecycleDescriptor) -> None: ...

    def list_for_artifact(self, artifact_id: str) -> tuple[ArtifactLifecycleDescriptor, ...]: ...

    def remove_all_for_artifact(self, artifact_id: str) -> None: ...


def strongest_retention_class(
    values: Iterable[ArtifactRetentionClass],
) -> ArtifactRetentionClass:
    """Choose the strongest lifecycle when the same binary serves multiple roles."""

    materialized = tuple(values)
    if not materialized:
        raise ValueError("at least one retention class is required")
    return max(materialized, key=_RETENTION_PRIORITY.__getitem__)

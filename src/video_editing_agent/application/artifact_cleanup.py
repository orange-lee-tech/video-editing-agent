from __future__ import annotations

from video_editing_agent.application.ports.artifact_lifecycle import (
    ArtifactLifecycleRepository,
    ArtifactRetentionClass,
    strongest_retention_class,
)
from video_editing_agent.application.ports.artifact_store import ArtifactStore, StoredArtifactRef


class ArtifactCleanupService:
    """Delete binaries only when all known references classify them as rebuildable cache."""

    def __init__(
        self,
        *,
        artifact_store: ArtifactStore,
        lifecycle_repository: ArtifactLifecycleRepository,
    ) -> None:
        self._artifact_store = artifact_store
        self._lifecycle_repository = lifecycle_repository

    def delete_rebuildable(self, ref: StoredArtifactRef) -> bool:
        descriptors = self._lifecycle_repository.list_for_artifact(ref.artifact_id)
        if not descriptors:
            return False
        strongest = strongest_retention_class(
            descriptor.retention_class for descriptor in descriptors
        )
        if strongest is not ArtifactRetentionClass.REBUILDABLE_CACHE:
            return False

        deleted = self._artifact_store.delete(ref)
        if deleted:
            self._lifecycle_repository.remove_all_for_artifact(ref.artifact_id)
        return deleted

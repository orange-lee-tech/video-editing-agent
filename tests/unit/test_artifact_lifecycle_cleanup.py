from pathlib import Path

from video_editing_agent.application.artifact_cleanup import ArtifactCleanupService
from video_editing_agent.application.ports.artifact_lifecycle import (
    ArtifactLifecycleDescriptor,
    ArtifactRetentionClass,
)
from video_editing_agent.application.ports.artifact_store import ArtifactPayload
from video_editing_agent.storage.artifact.lifecycle_repository import (
    LocalArtifactLifecycleRepository,
)
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore


def test_lifecycle_metadata_survives_repository_reopen(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "artifacts")
    ref = store.put(ArtifactPayload(media_type="image/png", content=b"frame"))
    repository = LocalArtifactLifecycleRepository(tmp_path / "artifacts")
    descriptor = ArtifactLifecycleDescriptor(
        artifact_id=ref.artifact_id,
        retention_class=ArtifactRetentionClass.DURABLE_DERIVED_EVIDENCE,
        purpose="visual-understanding-evidence",
        source_refs=("sht_1@1",),
    )
    repository.add(descriptor)

    reopened = LocalArtifactLifecycleRepository(tmp_path / "artifacts")

    assert reopened.list_for_artifact(ref.artifact_id) == (descriptor,)


def test_cleanup_refuses_binary_still_referenced_as_durable_evidence(tmp_path: Path) -> None:
    root = tmp_path / "artifacts"
    store = LocalArtifactStore(root)
    ref = store.put(ArtifactPayload(media_type="image/png", content=b"shared-frame"))
    lifecycle = LocalArtifactLifecycleRepository(root)
    lifecycle.add(
        ArtifactLifecycleDescriptor(
            artifact_id=ref.artifact_id,
            retention_class=ArtifactRetentionClass.REBUILDABLE_CACHE,
            purpose="preview-frame",
        )
    )
    lifecycle.add(
        ArtifactLifecycleDescriptor(
            artifact_id=ref.artifact_id,
            retention_class=ArtifactRetentionClass.DURABLE_DERIVED_EVIDENCE,
            purpose="provider-evidence",
            source_refs=("analysis-1",),
        )
    )
    cleanup = ArtifactCleanupService(
        artifact_store=store,
        lifecycle_repository=lifecycle,
    )

    assert not cleanup.delete_rebuildable(ref)
    assert store.get(ref) == b"shared-frame"
    assert len(lifecycle.list_for_artifact(ref.artifact_id)) == 2


def test_cleanup_deletes_cache_only_binary_and_metadata(tmp_path: Path) -> None:
    root = tmp_path / "artifacts"
    store = LocalArtifactStore(root)
    ref = store.put(ArtifactPayload(media_type="image/png", content=b"cache-only"))
    lifecycle = LocalArtifactLifecycleRepository(root)
    lifecycle.add(
        ArtifactLifecycleDescriptor(
            artifact_id=ref.artifact_id,
            retention_class=ArtifactRetentionClass.REBUILDABLE_CACHE,
            purpose="thumbnail",
        )
    )
    cleanup = ArtifactCleanupService(
        artifact_store=store,
        lifecycle_repository=lifecycle,
    )

    assert cleanup.delete_rebuildable(ref)
    assert lifecycle.list_for_artifact(ref.artifact_id) == ()


def test_cleanup_fails_closed_without_lifecycle_metadata(tmp_path: Path) -> None:
    root = tmp_path / "artifacts"
    store = LocalArtifactStore(root)
    ref = store.put(ArtifactPayload(media_type="image/png", content=b"unknown-role"))
    lifecycle = LocalArtifactLifecycleRepository(root)
    cleanup = ArtifactCleanupService(
        artifact_store=store,
        lifecycle_repository=lifecycle,
    )

    assert not cleanup.delete_rebuildable(ref)
    assert store.get(ref) == b"unknown-role"

import pytest

from video_editing_agent.application.ports.artifact_lifecycle import (
    ArtifactLifecycleDescriptor,
    ArtifactRetentionClass,
    strongest_retention_class,
)


def test_strongest_retention_prevents_cache_cleanup_from_dropping_evidence() -> None:
    assert (
        strongest_retention_class(
            (
                ArtifactRetentionClass.REBUILDABLE_CACHE,
                ArtifactRetentionClass.DURABLE_DERIVED_EVIDENCE,
            )
        )
        is ArtifactRetentionClass.DURABLE_DERIVED_EVIDENCE
    )


def test_project_output_has_stronger_retention_than_derived_evidence() -> None:
    assert (
        strongest_retention_class(
            (
                ArtifactRetentionClass.DURABLE_DERIVED_EVIDENCE,
                ArtifactRetentionClass.PROJECT_OUTPUT,
            )
        )
        is ArtifactRetentionClass.PROJECT_OUTPUT
    )


def test_artifact_lifecycle_requires_semantic_purpose() -> None:
    with pytest.raises(ValueError, match="purpose"):
        ArtifactLifecycleDescriptor(
            artifact_id="art_sha256_test",
            retention_class=ArtifactRetentionClass.REBUILDABLE_CACHE,
            purpose=" ",
        )

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.asset.policy import AssetUsageRole, is_visual_resolver_eligible
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.shot.analysis import (
    AnalysisProfile,
    ShotAnalysis,
    VisualSemantics,
)
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.planning.reference.service import ReferenceStyleEvidenceService
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore

NOW = datetime(2026, 8, 11, 21, 15, tzinfo=UTC)


def envelope(entity_id: str) -> EntityEnvelope:
    return EntityEnvelope(
        id=entity_id,
        revision=1,
        schema_version="0.2",
        status=EntityStatus.VALID,
        created_at=NOW,
        created_by="test",
    )


def reference_asset(*, usage_role: AssetUsageRole) -> Asset:
    return Asset(
        envelope=envelope("ast_reference"),
        media_kind="video",
        origin="imported_local",
        usage_role=usage_role,
        storage_ref="asset://reference.mp4",
        content_hash="sha256:reference",
        byte_size=1_024,
        provenance=AssetProvenance(origin_type="imported_local"),
        imported_at=NOW,
        duration=MediaTime(9, 2),
        width=1080,
        height=1920,
        fps=30.0,
        codec="h264",
    )


def reference_shots() -> tuple[Shot, ...]:
    asset_ref = EntityRevisionRef("ast_reference", 1)
    return (
        Shot(
            envelope=envelope("sht_ref_1"),
            asset_ref=asset_ref,
            source_start_ms=0,
            source_end_ms=1_000,
            boundary_method="test",
        ),
        Shot(
            envelope=envelope("sht_ref_2"),
            asset_ref=asset_ref,
            source_start_ms=1_000,
            source_end_ms=2_500,
            boundary_method="test",
        ),
        Shot(
            envelope=envelope("sht_ref_3"),
            asset_ref=asset_ref,
            source_start_ms=2_500,
            source_end_ms=4_500,
            boundary_method="test",
        ),
    )


def reference_analyses() -> tuple[ShotAnalysis, ...]:
    visuals = (
        VisualSemantics(
            framing="close",
            camera_motion="static",
            actions=("lift bottle",),
            subjects=("bottle",),
            environment="desk",
        ),
        VisualSemantics(
            framing="medium",
            camera_motion="pan",
            actions=("rotate bottle",),
            subjects=("bottle", "hand"),
            environment="desk",
        ),
        VisualSemantics(
            framing="close",
            camera_motion="static",
            actions=("lift bottle",),
            subjects=("bottle",),
            environment="entryway",
        ),
    )
    return tuple(
        ShotAnalysis(
            shot_ref=EntityRevisionRef(f"sht_ref_{index}", 1),
            revision=1,
            profile=AnalysisProfile.EDITORIAL,
            analyzed_at=NOW,
            visual=visual,
        )
        for index, visual in enumerate(visuals, start=1)
    )


def test_reference_style_evidence_is_abstract_cacheable_and_not_resolver_eligible(
    tmp_path: Path,
) -> None:
    asset = reference_asset(usage_role=AssetUsageRole.REFERENCE_ANALYSIS_ONLY)
    shots = reference_shots()
    analyses = reference_analyses()
    store = LocalArtifactStore(tmp_path / "artifacts")

    result = ReferenceStyleEvidenceService(store).analyze(asset, shots, analyses)

    evidence = result.evidence
    assert evidence.reference_asset_ref == EntityRevisionRef("ast_reference", 1)
    assert evidence.shot_count == 3
    assert evidence.total_duration == MediaTime(9, 2)
    assert evidence.minimum_shot_duration == MediaTime(1, 1)
    assert evidence.median_shot_duration == MediaTime(3, 2)
    assert evidence.maximum_shot_duration == MediaTime(2, 1)
    assert evidence.opening_framing == "close"
    assert evidence.opening_camera_motion == "static"
    assert evidence.framing_sequence == ("close", "medium", "close")
    assert evidence.camera_motion_sequence == ("static", "pan", "static")
    assert [(item.value, item.count) for item in evidence.framing_patterns] == [
        ("close", 2),
        ("medium", 1),
    ]
    assert [(item.value, item.count) for item in evidence.action_patterns] == [
        ("lift bottle", 2),
        ("rotate bottle", 1),
    ]
    assert "music_cut_relationship" in evidence.unavailable_dimensions
    assert any("do not copy" in item.lower() for item in result.planning_guidance)
    assert any("do not infer" in item.lower() for item in result.planning_guidance)

    payload = json.loads(store.get(result.artifact_ref).decode("utf-8"))
    assert payload["artifact_type"] == "reference_style_evidence"
    assert payload["reference_asset_ref"] == {"entity_id": "ast_reference", "revision": 1}
    assert payload["duration"]["median_shot"] == {"value": 3, "scale": 2}
    assert payload["unavailable_dimensions"] == list(evidence.unavailable_dimensions)

    assert not is_visual_resolver_eligible(
        media_kind=asset.media_kind,
        origin=asset.origin,
        usage_role=asset.usage_role,
    )


def test_reference_style_evidence_rejects_editable_visual_asset(tmp_path: Path) -> None:
    asset = reference_asset(usage_role=AssetUsageRole.EDITABLE_VISUAL_FOOTAGE)

    with pytest.raises(ValueError, match="reference_analysis_only"):
        ReferenceStyleEvidenceService(LocalArtifactStore(tmp_path / "artifacts")).analyze(
            asset,
            reference_shots(),
            reference_analyses(),
        )


def test_reference_style_evidence_requires_exact_analysis_coverage(tmp_path: Path) -> None:
    asset = reference_asset(usage_role=AssetUsageRole.REFERENCE_ANALYSIS_ONLY)

    with pytest.raises(ValueError, match="exactly cover"):
        ReferenceStyleEvidenceService(LocalArtifactStore(tmp_path / "artifacts")).analyze(
            asset,
            reference_shots(),
            reference_analyses()[:-1],
        )


def test_reference_style_evidence_requires_visual_observation(tmp_path: Path) -> None:
    asset = reference_asset(usage_role=AssetUsageRole.REFERENCE_ANALYSIS_ONLY)
    analyses = tuple(
        ShotAnalysis(
            shot_ref=EntityRevisionRef(f"sht_ref_{index}", 1),
            revision=1,
            profile=AnalysisProfile.BASIC,
            analyzed_at=NOW,
        )
        for index in range(1, 4)
    )

    with pytest.raises(ValueError, match="at least one visual"):
        ReferenceStyleEvidenceService(LocalArtifactStore(tmp_path / "artifacts")).analyze(
            asset,
            reference_shots(),
            analyses,
        )

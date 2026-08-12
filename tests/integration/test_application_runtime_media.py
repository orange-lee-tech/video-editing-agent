from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest

from video_editing_agent.application.ports.shot_detector import (
    ShotBoundaryProposal,
    ShotDetectionOptions,
)
from video_editing_agent.application.use_cases.runtime import AssetIngestRequest
from video_editing_agent.domain.asset.model import AssetProvenance
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shot.analysis import AnalysisProfile
from video_editing_agent.media.ingest.probe import MediaTechnicalMetadata
from video_editing_agent.storage.project import ProjectWorkspace


class Probe:
    def probe(self, path: Path) -> MediaTechnicalMetadata:
        assert path.is_file()
        return MediaTechnicalMetadata("video", duration_ms=2_000, width=16, height=9)


class Detector:
    def detect(self, asset_ref: EntityRevisionRef, options: ShotDetectionOptions):
        del options
        return (
            ShotBoundaryProposal(asset_ref, 0, 1_000, "fake"),
            ShotBoundaryProposal(asset_ref, 1_000, 2_000, "fake"),
        )


class FailingDetector:
    def detect(self, asset_ref: EntityRevisionRef, options: ShotDetectionOptions):
        del asset_ref, options
        raise RuntimeError("detector failed")


class Understanding:
    def __init__(self) -> None:
        self.calls: list[tuple[EntityRevisionRef, AnalysisProfile]] = []

    def analyze(self, shot_ref: EntityRevisionRef, profile: AnalysisProfile):
        self.calls.append((shot_ref, profile))
        raise RuntimeError("visual provider failed")

    def reanalyze(self, shot_ref: EntityRevisionRef, profile: AnalysisProfile):
        raise AssertionError((shot_ref, profile))


def runtime(workspace: ProjectWorkspace, understanding: Understanding):
    unused = cast(Any, object())
    return workspace.runtime(
        script_planning=unused,
        script_review=unused,
        shooting_planning=unused,
        shooting_review=unused,
        media_probe=Probe(),
        understanding=understanding,
    )


def test_injected_runtime_ingest_detect_and_failure_atomicity(tmp_path: Path) -> None:
    workspace = ProjectWorkspace.open(tmp_path / "project")
    understanding = Understanding()
    operations = runtime(workspace, understanding).media
    assert operations is not None
    media = tmp_path / "clip.mp4"
    media.write_bytes(b"deterministic fixture")

    asset = operations.ingest(AssetIngestRequest(media, "captured", AssetProvenance("captured")))
    asset_ref = EntityRevisionRef(asset.envelope.id, asset.envelope.revision)
    shots = operations.detect(asset_ref, Detector(), ShotDetectionOptions())
    assert len(shots) == 2
    assert workspace.status()["counts"]["assets"] == 1
    assert workspace.status()["counts"]["shots"] == 2

    with pytest.raises(RuntimeError, match="detector failed"):
        operations.detect(asset_ref, FailingDetector(), ShotDetectionOptions())
    assert workspace.status()["counts"]["shots"] == 2

    shot_ref = EntityRevisionRef(shots[0].envelope.id, 1)
    with pytest.raises(RuntimeError, match="visual provider failed"):
        operations.analyze(shot_ref, AnalysisProfile.SEMANTIC)
    assert understanding.calls == [(shot_ref, AnalysisProfile.SEMANTIC)]
    assert workspace.status()["counts"]["shot_analyses"] == 0


def test_runtime_invalid_boundary_batch_commits_no_shots(tmp_path: Path) -> None:
    workspace = ProjectWorkspace.open(tmp_path / "project")
    operations = runtime(workspace, Understanding()).media
    assert operations is not None
    media = tmp_path / "clip.mp4"
    media.write_bytes(b"fixture")
    asset = operations.ingest(AssetIngestRequest(media, "captured", AssetProvenance("captured")))
    asset_ref = EntityRevisionRef(asset.envelope.id, 1)

    class InvalidDetector:
        def detect(self, ref: EntityRevisionRef, options: ShotDetectionOptions):
            del options
            return (
                ShotBoundaryProposal(ref, 0, 900, "fake"),
                ShotBoundaryProposal(ref, 1_000, 2_000, "fake"),
            )

    with pytest.raises(ValueError, match="contiguous"):
        operations.detect(asset_ref, InvalidDetector(), ShotDetectionOptions())
    assert workspace.status()["counts"]["shots"] == 0

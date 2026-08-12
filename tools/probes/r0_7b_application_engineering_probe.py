from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, cast

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


class DeterministicProbe:
    calls = 0

    def probe(self, path: Path) -> MediaTechnicalMetadata:
        self.calls += 1
        if not path.is_file():
            raise FileNotFoundError(path)
        return MediaTechnicalMetadata("video", duration_ms=2_000, width=16, height=9)


class DeterministicDetector:
    calls = 0

    def detect(self, asset_ref: EntityRevisionRef, options: ShotDetectionOptions):
        self.calls += 1
        del options
        return (
            ShotBoundaryProposal(asset_ref, 0, 1_000, "probe-fake"),
            ShotBoundaryProposal(asset_ref, 1_000, 2_000, "probe-fake"),
        )


class ObservedVisualFailure:
    calls = 0

    def analyze(self, shot_ref: EntityRevisionRef, profile: AnalysisProfile):
        self.calls += 1
        raise RuntimeError(f"observed fake visual failure: {shot_ref} {profile.value}")

    def reanalyze(self, shot_ref: EntityRevisionRef, profile: AnalysisProfile):
        raise AssertionError((shot_ref, profile))


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="r0_7b_engineering_") as directory:
        root = Path(directory)
        fixture = root / "fixture.mp4"
        fixture.write_bytes(b"deterministic local fixture")
        workspace = ProjectWorkspace.open(root / "project")
        probe = DeterministicProbe()
        detector = DeterministicDetector()
        understanding = ObservedVisualFailure()
        unused = cast(Any, object())
        runtime = workspace.runtime(
            script_planning=unused,
            script_review=unused,
            shooting_planning=unused,
            shooting_review=unused,
            media_probe=probe,
            understanding=understanding,
        )
        assert runtime.media is not None
        asset = runtime.media.ingest(
            AssetIngestRequest(fixture, "captured", AssetProvenance("captured"))
        )
        asset_ref = EntityRevisionRef(asset.envelope.id, 1)
        shots = runtime.media.detect(asset_ref, detector, ShotDetectionOptions())
        assert tuple(shot.source_start_ms for shot in shots) == (0, 1_000)
        assert tuple(shot.source_end_ms for shot in shots) == (1_000, 2_000)
        reopened = ProjectWorkspace.open(root / "project")
        assert reopened.assets.load(asset_ref) == asset
        persisted_shots = tuple(sorted(reopened.shots.list_all(), key=lambda shot: shot.source_start_ms))
        assert tuple(
            (shot.envelope.id, shot.envelope.revision, shot.source_range)
            for shot in persisted_shots
        ) == tuple((shot.envelope.id, shot.envelope.revision, shot.source_range) for shot in shots)
        assert probe.calls == detector.calls == 1
        evidence = {
            "probe": "r0.7b-application-engineering",
            "classification": "engineering_partial",
            "asset_ingest_observed": True,
            "shot_detection_observed": True,
            "cross_process_persistence_observed": True,
            "media_probe_calls": probe.calls,
            "shot_detector_calls": detector.calls,
            "external_provider_invoked": False,
            "external_provider_calls": understanding.calls,
            "persisted_counts": reopened.status()["counts"],
            "remaining_direct_scenario": [
                "visual-understanding success",
                "preproduction bounded repair and locks",
                "coverage and temporal reopen",
            ],
        }
        print(json.dumps(evidence, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

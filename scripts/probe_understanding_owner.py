from __future__ import annotations

import argparse
import pathlib
from datetime import UTC, datetime

from video_editing_agent.application.ports.asset_media import ResolvedLocalAssetMedia
from video_editing_agent.application.ports.visual_understanding import (
    VisualSemanticsProposal,
    VisualUnderstandingRequest,
)
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.shot.analysis import AnalysisProfile, ShotAnalysis
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.understanding.frame_extraction import FfmpegPngFrameExtractor
from video_editing_agent.media.understanding.service import (
    ProviderNeutralVisualUnderstandingService,
)
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore


class StaticShotRepository:
    def __init__(self, shot: Shot) -> None:
        self._shot = shot

    def load(self, shot_ref: EntityRevisionRef) -> Shot:
        expected = EntityRevisionRef(self._shot.envelope.id, self._shot.envelope.revision)
        if shot_ref != expected:
            raise KeyError(shot_ref)
        return self._shot


class StaticMediaResolver:
    def __init__(self, resolved: ResolvedLocalAssetMedia) -> None:
        self._resolved = resolved

    def resolve_local(self, asset_ref: EntityRevisionRef) -> ResolvedLocalAssetMedia:
        if asset_ref != self._resolved.asset_ref:
            raise KeyError(asset_ref)
        return self._resolved


class MemoryAnalysisRepository:
    def __init__(self) -> None:
        self.saved: list[ShotAnalysis] = []

    def latest(self, shot_ref: EntityRevisionRef) -> ShotAnalysis | None:
        matches = [analysis for analysis in self.saved if analysis.shot_ref == shot_ref]
        return matches[-1] if matches else None

    def save(self, analysis: ShotAnalysis) -> None:
        self.saved.append(analysis)


class DeterministicVisualProvider:
    def __init__(self) -> None:
        self.requests: list[VisualUnderstandingRequest] = []

    def analyze(self, request: VisualUnderstandingRequest) -> VisualSemanticsProposal:
        self.requests.append(request)
        return VisualSemanticsProposal(
            summary=f"  Synthetic moving test pattern with {len(request.frames)} sampled frames.  ",
            tags=("synthetic", " test-pattern ", "synthetic"),
            subjects=("test pattern",),
            actions=("moving",),
            environment=" generated ",
            framing=" full frame ",
            camera_motion=" static ",
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe UnderstandingService ownership with real frames and a fake visual provider."
    )
    parser.add_argument("video", type=pathlib.Path)
    parser.add_argument("--duration-ms", type=int, required=True)
    parser.add_argument("--artifact-root", type=pathlib.Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    video_path = args.video.expanduser().resolve()
    if not video_path.is_file():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    shot = Shot(
        envelope=EntityEnvelope(
            id="sht_understanding_probe",
            revision=3,
            schema_version="0.1.1",
            status=EntityStatus.VALID,
            created_at=datetime.now(UTC),
            created_by="probe",
        ),
        asset_ref=EntityRevisionRef("ast_understanding_probe", 1),
        source_start_ms=0,
        source_end_ms=args.duration_ms,
        boundary_method="probe",
    )
    shot_ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
    repository = MemoryAnalysisRepository()
    visual_provider = DeterministicVisualProvider()
    service = ProviderNeutralVisualUnderstandingService(
        shot_repository=StaticShotRepository(shot),
        asset_media_resolver=StaticMediaResolver(
            ResolvedLocalAssetMedia(asset_ref=shot.asset_ref, path=video_path)
        ),
        analysis_repository=repository,
        frame_extractor=FfmpegPngFrameExtractor(),
        artifact_store=LocalArtifactStore(args.artifact_root),
        visual_port=visual_provider,
    )

    first = service.analyze(shot_ref, AnalysisProfile.SEMANTIC)
    second = service.reanalyze(shot_ref, AnalysisProfile.EDITORIAL)

    if (first.revision, second.revision) != (1, 2):
        raise RuntimeError(f"Unexpected analysis revisions: {first.revision}, {second.revision}")
    if first.shot_ref != shot_ref or second.shot_ref != shot_ref:
        raise RuntimeError("UnderstandingService changed Shot identity")
    if len(first.artifact_refs) != 3 or len(second.artifact_refs) != 5:
        raise RuntimeError("Analysis frame budgets did not match semantic/editorial profiles")
    if len(visual_provider.requests) != 2:
        raise RuntimeError("Visual provider invocation count is incorrect")
    if [len(request.frames) for request in visual_provider.requests] != [3, 5]:
        raise RuntimeError("Visual provider received incorrect frame budgets")
    if first.visual is None or first.visual.tags != ("synthetic", "test-pattern"):
        raise RuntimeError("Visual proposal normalization did not run before analysis commit")
    if repository.saved != [first, second]:
        raise RuntimeError("ShotAnalysisRepository did not preserve committed revision order")

    print("UnderstandingService ownership probe: PASS")
    print(f"shot_ref={shot_ref.entity_id}@{shot_ref.revision}")
    print(f"analysis_revisions={[analysis.revision for analysis in repository.saved]}")
    print(f"profiles={[analysis.profile.value for analysis in repository.saved]}")
    print(f"provider_frame_counts={[len(request.frames) for request in visual_provider.requests]}")
    print(f"artifact_counts={[len(first.artifact_refs), len(second.artifact_refs)]}")
    print(f"normalized_tags={first.visual.tags}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

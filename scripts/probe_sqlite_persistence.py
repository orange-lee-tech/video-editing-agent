from __future__ import annotations

import argparse
import pathlib

from video_editing_agent.application.ports.shot_detector import ShotBoundaryProposal
from video_editing_agent.application.ports.visual_understanding import (
    VisualQualityScoreProposal,
    VisualSemanticsProposal,
    VisualUnderstandingRequest,
)
from video_editing_agent.domain.asset.model import AssetProvenance
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shot.analysis import AnalysisProfile
from video_editing_agent.media.ingest.ffprobe import FfprobeMediaProbe
from video_editing_agent.media.ingest.service import AssetIngestService
from video_editing_agent.media.ingest.source import LocalMediaSource
from video_editing_agent.media.shot_detection.catalog import ShotCatalog
from video_editing_agent.media.understanding.frame_extraction import FfmpegPngFrameExtractor
from video_editing_agent.media.understanding.service import (
    ProviderNeutralVisualUnderstandingService,
)
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore
from video_editing_agent.storage.asset.repository_media import RepositoryLocalAssetMediaResolver
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase
from video_editing_agent.storage.repositories.sqlite_repositories import (
    SqliteAssetRepository,
    SqliteShotAnalysisRepository,
    SqliteShotRepository,
)

ASSET_ID = "ast_sqlite_persistence_probe"
SHOT_ID = "sht_sqlite_persistence_probe"


class DeterministicVisualProvider:
    """Keep the persistence probe independent from any external visual-model service."""

    def analyze(self, request: VisualUnderstandingRequest) -> VisualSemanticsProposal:
        return VisualSemanticsProposal(
            summary=f"Synthetic persistence probe using {len(request.frames)} real frame samples.",
            tags=("synthetic", "persistence-probe"),
            subjects=("test pattern",),
            actions=("moving",),
            environment="generated",
            framing="full frame",
            camera_motion="static",
            quality_scores=(VisualQualityScoreProposal("aesthetic", 0.8),),
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prove SQLite Asset/Shot/ShotAnalysis recovery across separate Python processes."
        )
    )
    parser.add_argument("phase", choices=("seed", "resume"))
    parser.add_argument("video", type=pathlib.Path)
    parser.add_argument("--database", type=pathlib.Path, required=True)
    parser.add_argument("--artifact-root", type=pathlib.Path, required=True)
    return parser.parse_args()


def open_repositories(database_path: pathlib.Path):
    database = SqliteProjectDatabase(database_path)
    database.initialize()
    return (
        database,
        SqliteAssetRepository(database),
        SqliteShotRepository(database),
        SqliteShotAnalysisRepository(database),
    )


def make_understanding_service(
    *,
    asset_repository: SqliteAssetRepository,
    shot_repository: SqliteShotRepository,
    analysis_repository: SqliteShotAnalysisRepository,
    artifact_root: pathlib.Path,
) -> ProviderNeutralVisualUnderstandingService:
    return ProviderNeutralVisualUnderstandingService(
        shot_repository=shot_repository,
        asset_media_resolver=RepositoryLocalAssetMediaResolver(asset_repository),
        analysis_repository=analysis_repository,
        frame_extractor=FfmpegPngFrameExtractor(),
        artifact_store=LocalArtifactStore(artifact_root),
        visual_port=DeterministicVisualProvider(),
    )


def seed(
    video_path: pathlib.Path, database_path: pathlib.Path, artifact_root: pathlib.Path
) -> None:
    database, asset_repository, shot_repository, analysis_repository = open_repositories(
        database_path
    )
    ingest = AssetIngestService(
        FfprobeMediaProbe(),
        repository=asset_repository,
        asset_id_factory=lambda: ASSET_ID,
    )
    asset = ingest.ingest(
        LocalMediaSource(
            path=video_path,
            origin="local",
            provenance=AssetProvenance(origin_type="local"),
        ),
        created_by="sqlite-persistence-probe",
    )
    if asset.duration_ms is None or asset.duration_ms <= 0:
        raise RuntimeError("ffprobe did not provide a positive video duration")

    asset_ref = EntityRevisionRef(asset.envelope.id, asset.envelope.revision)
    shots = ShotCatalog(
        repository=shot_repository,
        shot_id_factory=lambda: SHOT_ID,
    ).commit_boundaries(
        (
            ShotBoundaryProposal(
                asset_ref=asset_ref,
                source_start_ms=0,
                source_end_ms=asset.duration_ms,
                detection_method="sqlite-persistence-probe",
            ),
        ),
        created_by="sqlite-persistence-probe",
    )
    if len(shots) != 1:
        raise RuntimeError(f"expected one persisted Shot, got {len(shots)}")

    shot_ref = EntityRevisionRef(shots[0].envelope.id, shots[0].envelope.revision)
    service = make_understanding_service(
        asset_repository=asset_repository,
        shot_repository=shot_repository,
        analysis_repository=analysis_repository,
        artifact_root=artifact_root,
    )
    first = service.analyze(shot_ref, AnalysisProfile.SEMANTIC)
    if first.revision != 1:
        raise RuntimeError(f"expected ShotAnalysis@1, got @{first.revision}")
    if len(first.artifact_refs) != 3:
        raise RuntimeError("semantic profile did not persist three sampled frame artifacts")
    if analysis_repository.latest(shot_ref) != first:
        raise RuntimeError("ShotAnalysis@1 was not readable before seed process exit")

    print("SQLite persistence seed: PASS")
    print(f"schema_version={database.schema_version()}")
    print(f"asset_ref={asset_ref.entity_id}@{asset_ref.revision}")
    print(f"shot_ref={shot_ref.entity_id}@{shot_ref.revision}")
    print(f"analysis_revision={first.revision}")
    print(f"artifact_count={len(first.artifact_refs)}")


def resume(
    video_path: pathlib.Path, database_path: pathlib.Path, artifact_root: pathlib.Path
) -> None:
    database, asset_repository, shot_repository, analysis_repository = open_repositories(
        database_path
    )
    asset_ref = EntityRevisionRef(ASSET_ID, 1)
    shot_ref = EntityRevisionRef(SHOT_ID, 1)

    asset = asset_repository.load(asset_ref)
    shot = shot_repository.load(shot_ref)
    if shot.asset_ref != asset_ref:
        raise RuntimeError("reopened Shot no longer references the exact persisted Asset revision")

    resolved = RepositoryLocalAssetMediaResolver(asset_repository).resolve_local(asset_ref)
    if resolved.path != video_path.resolve(strict=True):
        raise RuntimeError(
            "reopened Asset storage_ref did not recover the original local video path"
        )
    if asset.storage_ref != resolved.path.as_uri():
        raise RuntimeError("reopened Asset storage_ref changed during local media resolution")

    first = analysis_repository.latest(shot_ref)
    if first is None or first.revision != 1:
        raise RuntimeError("resume process could not recover ShotAnalysis@1")

    service = make_understanding_service(
        asset_repository=asset_repository,
        shot_repository=shot_repository,
        analysis_repository=analysis_repository,
        artifact_root=artifact_root,
    )
    second = service.reanalyze(shot_ref, AnalysisProfile.EDITORIAL)
    if second.revision != 2:
        raise RuntimeError(f"expected ShotAnalysis@2 after restart, got @{second.revision}")
    if len(second.artifact_refs) != 5:
        raise RuntimeError("editorial profile did not persist five sampled frame artifacts")
    if analysis_repository.latest(shot_ref) != second:
        raise RuntimeError("ShotAnalysis@2 was not persisted after restart")

    print("SQLite persistence resume: PASS")
    print(f"schema_version={database.schema_version()}")
    print(f"asset_ref={asset_ref.entity_id}@{asset_ref.revision}")
    print(f"shot_ref={shot_ref.entity_id}@{shot_ref.revision}")
    print(f"analysis_revisions={[first.revision, second.revision]}")
    print(f"artifact_counts={[len(first.artifact_refs), len(second.artifact_refs)]}")


def main() -> int:
    args = parse_args()
    video_path = args.video.expanduser().resolve(strict=True)
    database_path = args.database.expanduser().resolve()
    artifact_root = args.artifact_root.expanduser().resolve()

    if args.phase == "seed":
        seed(video_path, database_path, artifact_root)
    else:
        resume(video_path, database_path, artifact_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

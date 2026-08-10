from __future__ import annotations

import argparse
import os
import pathlib

from video_editing_agent.application.ports.shot_detector import ShotBoundaryProposal
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
from video_editing_agent.providers.vision.openai_responses import (
    OpenAIResponsesVisualConfig,
    OpenAIResponsesVisualUnderstanding,
    UrllibOpenAIResponsesTransport,
)
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore
from video_editing_agent.storage.asset.repository_media import RepositoryLocalAssetMediaResolver
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase
from video_editing_agent.storage.repositories.sqlite_repositories import (
    SqliteAssetRepository,
    SqliteShotAnalysisRepository,
    SqliteShotRepository,
)

ASSET_ID = "ast_openai_visual_live_probe"
SHOT_ID = "sht_openai_visual_live_probe"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one real OpenAI visual-understanding request through the owner chain."
    )
    parser.add_argument("video", type=pathlib.Path)
    parser.add_argument("--database", type=pathlib.Path, required=True)
    parser.add_argument("--artifact-root", type=pathlib.Path, required=True)
    parser.add_argument("--model", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    video_path = args.video.expanduser().resolve(strict=True)
    database = SqliteProjectDatabase(args.database.expanduser().resolve())
    database.initialize()
    asset_repository = SqliteAssetRepository(database)
    shot_repository = SqliteShotRepository(database)
    analysis_repository = SqliteShotAnalysisRepository(database)
    artifact_store = LocalArtifactStore(args.artifact_root.expanduser().resolve())

    asset = AssetIngestService(
        FfprobeMediaProbe(),
        repository=asset_repository,
        asset_id_factory=lambda: ASSET_ID,
    ).ingest(
        LocalMediaSource(
            path=video_path,
            origin="local",
            provenance=AssetProvenance(origin_type="local"),
        ),
        created_by="openai-visual-live-probe",
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
                detection_method="openai-visual-live-probe",
            ),
        ),
        created_by="openai-visual-live-probe",
    )
    if len(shots) != 1:
        raise RuntimeError(f"expected exactly one Shot, got {len(shots)}")
    shot_ref = EntityRevisionRef(shots[0].envelope.id, shots[0].envelope.revision)

    visual_port = OpenAIResponsesVisualUnderstanding(
        artifact_store=artifact_store,
        transport=UrllibOpenAIResponsesTransport(api_key=api_key),
        config=OpenAIResponsesVisualConfig(
            model=args.model,
            image_detail="low",
            max_output_tokens=1_200,
        ),
    )
    service = ProviderNeutralVisualUnderstandingService(
        shot_repository=shot_repository,
        asset_media_resolver=RepositoryLocalAssetMediaResolver(asset_repository),
        analysis_repository=analysis_repository,
        frame_extractor=FfmpegPngFrameExtractor(),
        artifact_store=artifact_store,
        visual_port=visual_port,
    )

    analysis = service.analyze(shot_ref, AnalysisProfile.SEMANTIC)
    if analysis.revision != 1:
        raise RuntimeError(f"expected ShotAnalysis@1, got @{analysis.revision}")
    if len(analysis.artifact_refs) != 3:
        raise RuntimeError("semantic profile did not preserve three sampled frame artifacts")
    if analysis.visual is None:
        raise RuntimeError("OpenAI provider did not produce visual semantics")
    visual = analysis.visual
    if not (visual.summary or visual.tags or visual.subjects or visual.actions):
        raise RuntimeError("OpenAI provider returned no searchable visual semantics")
    if analysis_repository.latest(shot_ref) != analysis:
        raise RuntimeError("UnderstandingService did not persist the committed ShotAnalysis")

    print("OpenAI visual provider live probe: PASS")
    print(f"model={args.model}")
    print(f"asset_ref={asset_ref.entity_id}@{asset_ref.revision}")
    print(f"shot_ref={shot_ref.entity_id}@{shot_ref.revision}")
    print(f"analysis_revision={analysis.revision}")
    print(f"artifact_count={len(analysis.artifact_refs)}")
    print(f"summary_present={visual.summary is not None}")
    print(f"tag_count={len(visual.tags)}")
    print(f"subject_count={len(visual.subjects)}")
    print(f"action_count={len(visual.actions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

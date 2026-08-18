from __future__ import annotations

from pathlib import Path

from video_editing_agent.adapters.cli.media_config import (
    transnetv2_detector,
    visual_understanding_port,
)
from video_editing_agent.adapters.cli.provider_config import (
    deepseek_director_port,
    deepseek_preproduction_ports,
)
from video_editing_agent.adapters.product.runtime import ProductRuntimeConfig
from video_editing_agent.application.ports.shot_detector import ShotDetectionOptions, ShotDetector
from video_editing_agent.application.ports.understanding import UnderstandingService
from video_editing_agent.application.use_cases.product_flow import (
    EditingProductFlow,
    PlanningProductFlow,
)
from video_editing_agent.media.ingest.ffprobe import FfprobeMediaProbe
from video_editing_agent.media.understanding.frame_extraction import FfmpegPngFrameExtractor
from video_editing_agent.media.understanding.service import (
    ProviderNeutralVisualUnderstandingService,
)
from video_editing_agent.providers.reference.direct_https import DirectHttpsReferenceAcquirer
from video_editing_agent.providers.review.ffmpeg_pcm import FFmpegPcmRenderedMediaQc
from video_editing_agent.render.edl_ffmpeg import FFmpegEDLRenderer
from video_editing_agent.storage.asset.repository_media import RepositoryLocalAssetMediaResolver
from video_editing_agent.storage.project.product_flow import (
    EditingProductCapabilities,
    PlanningProductCapabilities,
    PlanningReferenceCapabilities,
    build_editing_product_flow,
    build_planning_product_flow,
)
from video_editing_agent.storage.project.workspace import ProjectWorkspace


def _media_capabilities(
    workspace: ProjectWorkspace, config: ProductRuntimeConfig
) -> tuple[ShotDetector, UnderstandingService]:
    if not all(
        (
            config.ffmpeg,
            config.ffprobe,
            config.transnet_weights,
            config.visual_provider,
            config.visual_model,
        )
    ):
        raise RuntimeError("mandatory media runtime capability is unavailable; run Doctor")
    assert config.ffmpeg and config.ffprobe and config.transnet_weights
    assert config.visual_provider and config.visual_model
    visual = visual_understanding_port(
        config.visual_provider, model=config.visual_model, artifacts=workspace.artifacts
    )
    understanding = ProviderNeutralVisualUnderstandingService(
        shot_repository=workspace.shots,
        asset_media_resolver=RepositoryLocalAssetMediaResolver(workspace.assets),
        analysis_repository=workspace.analyses,
        frame_extractor=FfmpegPngFrameExtractor(config.ffmpeg),
        artifact_store=workspace.artifacts,
        visual_port=visual,
    )
    detector = transnetv2_detector(
        workspace.assets,
        model_path=config.transnet_weights,
        device=config.device,
        ffmpeg_executable=config.ffmpeg,
    )
    return detector, understanding


def planning_flow(
    project: Path, config: ProductRuntimeConfig, *, reference: bool
) -> PlanningProductFlow:
    workspace = ProjectWorkspace.open(project)
    ports = deepseek_preproduction_ports(model=config.deepseek_model)
    reference_capabilities = None
    if reference:
        detector, understanding = _media_capabilities(workspace, config)
        assert config.ffprobe is not None
        reference_capabilities = PlanningReferenceCapabilities(
            FfprobeMediaProbe(config.ffprobe),
            detector,
            ShotDetectionOptions(),
            understanding,
            DirectHttpsReferenceAcquirer(workspace.root / "reference-media"),
        )
    return build_planning_product_flow(
        workspace,
        PlanningProductCapabilities(
            ports.script_planning,
            ports.script_review,
            ports.shooting_planning,
            ports.shooting_review,
            reference_capabilities,
        ),
    )


def editing_flow(project: Path, config: ProductRuntimeConfig) -> EditingProductFlow:
    workspace = ProjectWorkspace.open(project)
    detector, understanding = _media_capabilities(workspace, config)
    assert config.ffmpeg is not None and config.ffprobe is not None
    return build_editing_product_flow(
        workspace,
        EditingProductCapabilities(
            FfprobeMediaProbe(config.ffprobe),
            detector,
            ShotDetectionOptions(),
            understanding,
            deepseek_director_port(model=config.deepseek_model),
            FFmpegEDLRenderer(config.ffmpeg, config.ffprobe),
            FFmpegPcmRenderedMediaQc(config.ffmpeg, config.ffprobe),
        ),
    )

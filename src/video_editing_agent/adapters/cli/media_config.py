from __future__ import annotations

import os
from pathlib import Path

from video_editing_agent.application.ports.asset_repository import AssetRepository
from video_editing_agent.application.ports.visual_understanding import VisualUnderstandingPort
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.media.shot_detection.transnet_backend import TransNetV2BackendConfig
from video_editing_agent.media.shot_detection.transnet_runtime import (
    TorchTransNetV2Config,
    TorchTransNetV2WindowPredictor,
)
from video_editing_agent.media.shot_detection.v02_exact import (
    ExactPolicyDrivenShotDetector,
    ExactResolvedVideoAsset,
    ExactTransNetV2SceneBoundaryBackend,
)
from video_editing_agent.providers.vision.gemini_generate_content import (
    GeminiGenerateContentVisualUnderstanding,
    GeminiVisualConfig,
    UrllibGeminiGenerateContentTransport,
)
from video_editing_agent.providers.vision.openai_responses import (
    OpenAIResponsesVisualConfig,
    OpenAIResponsesVisualUnderstanding,
    UrllibOpenAIResponsesTransport,
)
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore
from video_editing_agent.storage.asset.repository_media import RepositoryLocalAssetMediaResolver

from .provider_config import ProviderConfigurationError


class RepositoryExactVideoResolver:
    def __init__(self, repository: AssetRepository) -> None:
        self._repository = repository
        self._local = RepositoryLocalAssetMediaResolver(repository)

    def resolve_video(self, asset_ref: EntityRevisionRef) -> ExactResolvedVideoAsset:
        asset = self._repository.load(asset_ref)
        if asset.duration is None:
            raise ValueError("Asset must have an exact duration for shot detection")
        return ExactResolvedVideoAsset(self._local.resolve_local(asset_ref).path, asset.duration)


def transnetv2_detector(
    repository: AssetRepository,
    *,
    model_path: Path,
    device: str,
    ffmpeg_executable: str,
) -> ExactPolicyDrivenShotDetector:
    resolved_model = model_path.expanduser().resolve(strict=True)
    if not resolved_model.is_file():
        raise ValueError(f"TransNetV2 model must be a file: {resolved_model}")
    predictor = TorchTransNetV2WindowPredictor(
        TorchTransNetV2Config(device=device, weights_path=resolved_model)
    )
    backend = ExactTransNetV2SceneBoundaryBackend(
        RepositoryExactVideoResolver(repository),
        predictor,
        config=TransNetV2BackendConfig(ffmpeg_executable=ffmpeg_executable),
    )
    return ExactPolicyDrivenShotDetector(backend)


def visual_understanding_port(
    provider: str,
    *,
    model: str,
    artifacts: LocalArtifactStore,
) -> VisualUnderstandingPort:
    if provider == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key.strip():
            raise ProviderConfigurationError("GEMINI_API_KEY is required for provider=gemini")
        return GeminiGenerateContentVisualUnderstanding(
            artifact_store=artifacts,
            transport=UrllibGeminiGenerateContentTransport(api_key=api_key),
            config=GeminiVisualConfig(model=model),
        )
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key.strip():
            raise ProviderConfigurationError("OPENAI_API_KEY is required for provider=openai")
        return OpenAIResponsesVisualUnderstanding(
            artifact_store=artifacts,
            transport=UrllibOpenAIResponsesTransport(api_key=api_key),
            config=OpenAIResponsesVisualConfig(model=model),
        )
    raise ProviderConfigurationError(f"unsupported visual provider: {provider}")

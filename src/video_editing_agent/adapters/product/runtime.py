from __future__ import annotations

import importlib.util
import os
import shutil
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from importlib.machinery import ModuleSpec
from pathlib import Path

from video_editing_agent.media.shot_detection.transnet_runtime import (
    TRANSNETV2_WEIGHTS_FILENAME,
)


@dataclass(frozen=True, slots=True)
class ProductRuntimeConfig:
    ffmpeg: str | None = None
    ffprobe: str | None = None
    transnet_weights: Path | None = None
    visual_provider: str | None = None
    visual_model: str | None = None
    deepseek_model: str = "deepseek-v4-flash"
    device: str = "cpu"


@dataclass(frozen=True, slots=True)
class ProductRuntimeResolution:
    config: ProductRuntimeConfig | None
    diagnostics: tuple[str, ...]

    @property
    def is_ready(self) -> bool:
        return self.config is not None and not self.diagnostics


def resolve_product_runtime(
    *,
    mode: str = "editing",
    reference_required: bool = False,
    environment: Mapping[str, str] | None = None,
    executable_locator: Callable[[str], str | None] = shutil.which,
    module_finder: Callable[[str], ModuleSpec | None] = importlib.util.find_spec,
) -> ProductRuntimeResolution:
    env = os.environ if environment is None else environment
    diagnostics: list[str] = []
    if mode not in {"planning", "editing"}:
        raise ValueError("mode must be planning or editing")
    media_required = mode == "editing" or reference_required
    visual_provider: str | None = None
    visual_model: str | None = None
    ffmpeg, ffprobe = executable_locator("ffmpeg"), executable_locator("ffprobe")
    if media_required and (ffmpeg is None or ffprobe is None):
        diagnostics.append(
            "FFmpeg/ffprobe are required for Editing but are not resolvable; run Doctor."
        )
    try:
        spec = module_finder("transnetv2_pytorch")
    except (ImportError, ModuleNotFoundError, ValueError):
        spec = None
    weights = None
    if spec is not None and spec.origin is not None:
        candidate = Path(spec.origin).resolve().parent / TRANSNETV2_WEIGHTS_FILENAME
        if candidate.is_file():
            weights = candidate
    if media_required and weights is None:
        diagnostics.append(
            "Reviewed TransNetV2 runtime/weights were not auto-resolved; run Doctor."
        )
    if env.get("GEMINI_API_KEY", "").strip():
        visual_provider, visual_model = "gemini", "gemini-2.5-flash"
    elif env.get("OPENAI_API_KEY", "").strip():
        visual_provider, visual_model = "openai", "gpt-5-mini"
    elif media_required:
        visual_provider, visual_model = "", ""
        diagnostics.append(
            "Editing requires one configured visual provider (GEMINI_API_KEY or OPENAI_API_KEY)."
        )
    if not env.get("DEEPSEEK_API_KEY", "").strip():
        diagnostics.append("Planning/Director requires DEEPSEEK_API_KEY to be configured.")
    if diagnostics:
        return ProductRuntimeResolution(None, tuple(diagnostics))
    return ProductRuntimeResolution(
        ProductRuntimeConfig(ffmpeg, ffprobe, weights, visual_provider, visual_model), ()
    )

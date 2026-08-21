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

_APPROVED_WINDOWS_FFMPEG_BIN = Path(".tools/ffmpeg-8.1/ffmpeg-8.1-full_build/bin")


def locate_media_executable(
    name: str,
    *,
    path_locator: Callable[[str], str | None] = shutil.which,
    repository_root: Path | None = None,
) -> str | None:
    """Resolve PATH first, then the approved repository-local Windows runtime."""
    resolved = path_locator(name)
    if resolved is not None:
        return resolved
    if name not in {"ffmpeg", "ffprobe"}:
        return None
    root = Path(__file__).resolve().parents[4] if repository_root is None else repository_root
    candidate = root / _APPROVED_WINDOWS_FFMPEG_BIN / f"{name}.exe"
    return str(candidate) if candidate.is_file() else None


@dataclass(frozen=True, slots=True)
class ProductRuntimeConfig:
    ffmpeg: str | None = None
    ffprobe: str | None = None
    transnet_weights: Path | None = None
    visual_provider: str | None = None
    visual_model: str | None = None
    deepseek_model: str = "deepseek-v4-flash"
    device: str = "cpu"
    speech_recognition_available: bool = False


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
    executable_locator: Callable[[str], str | None] | None = None,
    module_finder: Callable[[str], ModuleSpec | None] = importlib.util.find_spec,
) -> ProductRuntimeResolution:
    env = os.environ if environment is None else environment
    diagnostics: list[str] = []
    if mode not in {"planning", "editing"}:
        raise ValueError("mode must be planning or editing")
    media_required = mode == "editing" or reference_required
    visual_provider: str | None = None
    visual_model: str | None = None
    locator = locate_media_executable if executable_locator is None else executable_locator
    ffmpeg, ffprobe = locator("ffmpeg"), locator("ffprobe")
    if media_required and (ffmpeg is None or ffprobe is None):
        purpose = "Editing" if mode == "editing" else "Planning reference-video analysis"
        diagnostics.append(
            f"FFmpeg/ffprobe are required for {purpose} but are not resolvable; run Doctor."
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
        purpose = "Editing" if mode == "editing" else "Planning reference-video analysis"
        diagnostics.append(
            f"Reviewed TransNetV2 runtime/weights required for {purpose} were not "
            "auto-resolved; run Doctor."
        )
    if env.get("GEMINI_API_KEY", "").strip():
        visual_provider, visual_model = "gemini", "gemini-3.6-flash"
    elif env.get("OPENAI_API_KEY", "").strip():
        visual_provider, visual_model = "openai", "gpt-5-mini"
    elif media_required:
        visual_provider, visual_model = "", ""
        purpose = "Editing" if mode == "editing" else "Planning reference-video analysis"
        diagnostics.append(
            f"{purpose} requires one configured visual provider (GEMINI_API_KEY or OPENAI_API_KEY)."
        )
    if not env.get("DEEPSEEK_API_KEY", "").strip():
        diagnostics.append("Planning/Director requires DEEPSEEK_API_KEY to be configured.")
    try:
        speech_recognition_available = module_finder("faster_whisper") is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        speech_recognition_available = False
    if diagnostics:
        return ProductRuntimeResolution(None, tuple(diagnostics))
    return ProductRuntimeResolution(
        ProductRuntimeConfig(
            ffmpeg,
            ffprobe,
            weights,
            visual_provider,
            visual_model,
            speech_recognition_available=speech_recognition_available,
        ),
        (),
    )

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from video_editing_agent.application.ports.asset_media import ResolvedLocalAssetMedia
from video_editing_agent.application.ports.executor import DeterministicToolInvocation
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.edl.model import EDL


@dataclass(frozen=True, slots=True)
class OutputSpec:
    path: Path
    width: int
    height: int
    frames_per_second: int
    container: str = "mp4"
    video_codec: str = "libx264"
    audio_codec: str = "aac"

    def __post_init__(self) -> None:
        for name, numeric_value in (
            ("width", self.width),
            ("height", self.height),
            ("frames_per_second", self.frames_per_second),
        ):
            if (
                isinstance(numeric_value, bool)
                or not isinstance(numeric_value, int)
                or numeric_value <= 0
            ):
                raise ValueError(f"{name} must be a positive int")
        for name, text_value in (
            ("container", self.container),
            ("video_codec", self.video_codec),
            ("audio_codec", self.audio_codec),
        ):
            if not text_value.strip():
                raise ValueError(f"{name} must not be empty")


class RenderDiagnosticCode(StrEnum):
    INVALID_EDL = "invalid_edl"
    UNSUPPORTED_TRACK = "unsupported_track"
    UNSUPPORTED_AUTOMATION = "unsupported_automation"
    UNSUPPORTED_OUTPUT = "unsupported_output"
    TIMELINE_NOT_CONTIGUOUS = "timeline_not_contiguous"
    MISSING_ASSET_MEDIA = "missing_asset_media"
    AMBIGUOUS_ASSET_MEDIA = "ambiguous_asset_media"
    OUTPUT_CONFLICT = "output_conflict"
    SUBTITLE_TIMING_UNREPRESENTABLE = "subtitle_timing_unrepresentable"
    SUBTITLE_LAYER_UNSUPPORTED = "subtitle_layer_unsupported"
    EXECUTION_FAILED = "execution_failed"
    OUTPUT_VERIFICATION_FAILED = "output_verification_failed"


@dataclass(frozen=True, slots=True)
class RenderDiagnostic:
    code: RenderDiagnosticCode
    message: str
    segment_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RenderRequest:
    edl: EDL
    asset_media: tuple[ResolvedLocalAssetMedia, ...]
    output_spec: OutputSpec


@dataclass(frozen=True, slots=True)
class RenderArtifact:
    path: Path
    edl_ref: EntityRevisionRef
    output_spec: OutputSpec
    ffmpeg_invocation: DeterministicToolInvocation
    ffprobe_invocation: DeterministicToolInvocation


@dataclass(frozen=True, slots=True)
class RenderResult:
    artifact: RenderArtifact | None
    diagnostics: tuple[RenderDiagnostic, ...]

    @property
    def is_rendered(self) -> bool:
        return self.artifact is not None and not self.diagnostics


class Renderer(Protocol):
    """Execute canonical EDL; no alternate editorial authority is available here."""

    def render(self, request: RenderRequest) -> RenderResult: ...

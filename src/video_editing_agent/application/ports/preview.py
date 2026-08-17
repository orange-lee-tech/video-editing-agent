from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from video_editing_agent.domain.common.media_time import MediaTime


class PreviewDecodeMode(StrEnum):
    AUTO = "auto"
    SOFTWARE_VIDEO = "software_video"


class PreviewPlaybackState(StrEnum):
    NEW = "new"
    READY = "ready"
    LOADED = "loaded"
    BUFFERING = "buffering"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    RELEASED = "released"
    FAILED = "failed"


class PreviewDiagnosticCode(StrEnum):
    RUNTIME_NOT_FOUND = "runtime_not_found"
    RUNTIME_INVALID = "runtime_invalid"
    LIBRARY_LOAD_FAILED = "library_load_failed"
    INITIALIZATION_FAILED = "initialization_failed"
    MEDIA_NOT_FOUND = "media_not_found"
    MEDIA_NOT_LOCAL_FILE = "media_not_local_file"
    NOT_INITIALIZED = "not_initialized"
    NO_MEDIA_LOADED = "no_media_loaded"
    INVALID_SEEK = "invalid_seek"
    MISSING_PLUGIN = "missing_plugin"
    PLAYBACK_FAILED = "playback_failed"
    BACKEND_FAILURE = "backend_failure"
    RELEASED = "released"


@dataclass(frozen=True, slots=True)
class PreviewDiagnostic:
    code: PreviewDiagnosticCode
    message: str
    retryable: bool = False


@dataclass(frozen=True, slots=True)
class PreviewStatus:
    backend: str
    state: PreviewPlaybackState
    decode_mode: PreviewDecodeMode
    runtime_root: Path | None = None
    runtime_version: str | None = None
    runtime_provenance: str | None = None
    media_path: Path | None = None
    position: MediaTime | None = None
    disabled_hardware_features: tuple[str, ...] = ()
    diagnostics: tuple[PreviewDiagnostic, ...] = ()

    @property
    def is_usable(self) -> bool:
        return self.state not in {PreviewPlaybackState.FAILED, PreviewPlaybackState.RELEASED}


class PreviewBackend(Protocol):
    """Playback-only boundary. Canonical EDL and editorial decisions live elsewhere."""

    def initialize(self) -> PreviewStatus: ...

    def load(self, path: Path) -> PreviewStatus: ...

    def play(self) -> PreviewStatus: ...

    def pause(self) -> PreviewStatus: ...

    def seek(self, position: MediaTime) -> PreviewStatus: ...

    def status(self) -> PreviewStatus: ...

    def stop(self) -> PreviewStatus: ...

    def release(self) -> PreviewStatus: ...

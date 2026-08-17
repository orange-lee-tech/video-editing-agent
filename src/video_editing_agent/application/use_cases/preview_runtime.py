from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from video_editing_agent.application.ports.preview import PreviewBackend, PreviewStatus
from video_editing_agent.domain.common.media_time import MediaTime


@dataclass(frozen=True, slots=True)
class PreviewOperations:
    initialize: Callable[[], PreviewStatus]
    load: Callable[[Path], PreviewStatus]
    play: Callable[[], PreviewStatus]
    pause: Callable[[], PreviewStatus]
    seek: Callable[[MediaTime], PreviewStatus]
    status: Callable[[], PreviewStatus]
    stop: Callable[[], PreviewStatus]
    release: Callable[[], PreviewStatus]


@dataclass(frozen=True, slots=True)
class PreviewApplicationRuntime:
    """Independent playback surface; it has no EDL or editorial mutation operation."""

    preview: PreviewOperations

    @classmethod
    def from_backend(cls, backend: PreviewBackend) -> PreviewApplicationRuntime:
        return cls(
            preview=PreviewOperations(
                initialize=backend.initialize,
                load=backend.load,
                play=backend.play,
                pause=backend.pause,
                seek=backend.seek,
                status=backend.status,
                stop=backend.stop,
                release=backend.release,
            )
        )

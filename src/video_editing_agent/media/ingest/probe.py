from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.domain.common.media_time import MediaTime


@dataclass(frozen=True, slots=True, init=False)
class MediaTechnicalMetadata:
    media_kind: str
    duration: MediaTime | None
    width: int | None
    height: int | None
    fps: float | None
    codec: str | None
    audio_channels: int | None
    sample_rate_hz: int | None

    def __init__(
        self,
        media_kind: str,
        duration_ms: int | None = None,
        width: int | None = None,
        height: int | None = None,
        fps: float | None = None,
        codec: str | None = None,
        audio_channels: int | None = None,
        sample_rate_hz: int | None = None,
        *,
        duration: MediaTime | None = None,
    ) -> None:
        if duration is not None:
            if duration_ms is not None:
                raise ValueError("provide duration or legacy duration_ms, not both")
            resolved_duration = duration
        elif duration_ms is not None:
            resolved_duration = MediaTime.from_milliseconds(duration_ms)
        else:
            resolved_duration = None

        if not media_kind.strip():
            raise ValueError("media_kind must not be empty")
        if resolved_duration is not None and resolved_duration.as_fraction() < 0:
            raise ValueError("duration must be >= 0")

        object.__setattr__(self, "media_kind", media_kind)
        object.__setattr__(self, "duration", resolved_duration)
        object.__setattr__(self, "width", width)
        object.__setattr__(self, "height", height)
        object.__setattr__(self, "fps", fps)
        object.__setattr__(self, "codec", codec)
        object.__setattr__(self, "audio_channels", audio_channels)
        object.__setattr__(self, "sample_rate_hz", sample_rate_hz)

    @property
    def duration_ms(self) -> int | None:
        """Legacy exact-ms adapter; finer probe precision is never silently rounded."""

        if self.duration is None:
            return None
        return self.duration.to_milliseconds_exact()


class MediaProbe(Protocol):
    def probe(self, path: pathlib.Path) -> MediaTechnicalMetadata: ...

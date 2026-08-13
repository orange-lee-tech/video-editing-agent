from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange


@dataclass(frozen=True, slots=True)
class BeatPoint:
    source_time: MediaTime
    energy: float
    confidence: float

    def __post_init__(self) -> None:
        if self.source_time.as_fraction() < 0:
            raise ValueError("beat source time must be >= 0")
        if not 0.0 <= self.energy <= 1.0 or not 0.0 <= self.confidence <= 1.0:
            raise ValueError("beat energy/confidence must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class BeatMap:
    envelope: EntityEnvelope
    audio_asset_ref: EntityRevisionRef
    analyzed_source_range: MediaTimeRange
    beats: tuple[BeatPoint, ...]
    tempo_bpm: float | None
    provider_id: str
    provider_revision: str
    confidence: float = 0.0
    energy_envelope: tuple[BeatPoint, ...] = ()

    def __post_init__(self) -> None:
        if not self.provider_id.strip() or not self.provider_revision.strip():
            raise ValueError("BeatMap provider identity must not be empty")
        if self.tempo_bpm is not None and self.tempo_bpm <= 0:
            raise ValueError("tempo_bpm must be > 0")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("BeatMap confidence must be between 0 and 1")
        if tuple(x.source_time.as_fraction() for x in self.beats) != tuple(
            sorted(x.source_time.as_fraction() for x in self.beats)
        ):
            raise ValueError("beats must be ordered")
        if any(
            beat.source_time.as_fraction() < self.analyzed_source_range.start.as_fraction()
            or beat.source_time.as_fraction() >= self.analyzed_source_range.end.as_fraction()
            for beat in self.beats
        ):
            raise ValueError("beats must stay inside analyzed source range")
        if any(
            point.source_time.as_fraction() < self.analyzed_source_range.start.as_fraction()
            or point.source_time.as_fraction() >= self.analyzed_source_range.end.as_fraction()
            for point in self.energy_envelope
        ):
            raise ValueError("energy envelope must stay inside analyzed source range")

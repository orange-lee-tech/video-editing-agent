from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import gcd

from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange


class EDLInterpolation(StrEnum):
    HOLD = "hold"
    LINEAR = "linear"


@dataclass(frozen=True, slots=True)
class ExactRational:
    """Exact dimensionless or pixel-space value; never binary-float authority."""

    value: int
    scale: int = 1

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            raise TypeError("value must be an int")
        if isinstance(self.scale, bool) or not isinstance(self.scale, int):
            raise TypeError("scale must be an int")
        if self.scale <= 0:
            raise ValueError("scale must be > 0")
        divisor = gcd(abs(self.value), self.scale)
        object.__setattr__(self, "value", self.value // divisor)
        object.__setattr__(self, "scale", self.scale // divisor)


@dataclass(frozen=True, slots=True)
class EDLSpatialKeyframe:
    timeline_time: MediaTime
    source_time: MediaTime
    crop_left: int
    crop_top: int
    crop_width: int
    crop_height: int
    scale: ExactRational = ExactRational(1)
    position_x: ExactRational = ExactRational(0)
    position_y: ExactRational = ExactRational(0)


@dataclass(frozen=True, slots=True)
class EDLSpatialAutomation:
    interpolation: EDLInterpolation
    keyframes: tuple[EDLSpatialKeyframe, ...]


class EDLAudioAutomationKind(StrEnum):
    GAIN = "gain"
    DUCK = "duck"
    MUTE = "mute"
    FADE = "fade"
    LOOP = "loop"


@dataclass(frozen=True, slots=True)
class EDLAudioKeyframe:
    timeline_time: MediaTime
    gain_millibels: int
    muted: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.gain_millibels, bool) or not isinstance(self.gain_millibels, int):
            raise TypeError("gain_millibels must be an int")


@dataclass(frozen=True, slots=True)
class EDLAudioAutomation:
    kind: EDLAudioAutomationKind
    interpolation: EDLInterpolation
    keyframes: tuple[EDLAudioKeyframe, ...] = ()
    loop_source_range: MediaTimeRange | None = None

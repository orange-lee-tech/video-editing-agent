from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd
from typing import Self


def _require_int(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int")


@dataclass(frozen=True, slots=True)
class MediaTime:
    """Exact rational media time independent of frame rate or binary float equality."""

    value: int
    scale: int

    def __post_init__(self) -> None:
        _require_int("value", self.value)
        _require_int("scale", self.scale)
        if self.scale <= 0:
            raise ValueError("scale must be > 0")

        divisor = gcd(abs(self.value), self.scale)
        object.__setattr__(self, "value", self.value // divisor)
        object.__setattr__(self, "scale", self.scale // divisor)

    @classmethod
    def from_milliseconds(cls, milliseconds: int) -> Self:
        _require_int("milliseconds", milliseconds)
        return cls(milliseconds, 1_000)

    def as_fraction(self) -> Fraction:
        return Fraction(self.value, self.scale)

    def to_milliseconds_exact(self) -> int:
        numerator = self.value * 1_000
        quotient, remainder = divmod(numerator, self.scale)
        if remainder != 0:
            raise ValueError("MediaTime cannot be represented as an exact integer millisecond")
        return quotient

    def __add__(self, other: MediaTime) -> MediaTime:
        if not isinstance(other, MediaTime):
            raise TypeError("MediaTime can only be added to MediaTime")
        return MediaTime(
            self.value * other.scale + other.value * self.scale,
            self.scale * other.scale,
        )

    def __sub__(self, other: MediaTime) -> MediaTime:
        if not isinstance(other, MediaTime):
            raise TypeError("MediaTime can only be subtracted from MediaTime")
        return MediaTime(
            self.value * other.scale - other.value * self.scale,
            self.scale * other.scale,
        )


@dataclass(frozen=True, slots=True)
class MediaTimeRange:
    """Half-open exact media range [start, end) with strictly positive duration."""

    start: MediaTime
    duration: MediaTime

    def __post_init__(self) -> None:
        if self.duration.value <= 0:
            raise ValueError("duration must be > 0")

    @property
    def end(self) -> MediaTime:
        return self.start + self.duration

    @classmethod
    def from_milliseconds(cls, start_ms: int, end_ms: int) -> Self:
        _require_int("start_ms", start_ms)
        _require_int("end_ms", end_ms)
        if end_ms <= start_ms:
            raise ValueError("end_ms must be greater than start_ms")
        return cls(
            start=MediaTime.from_milliseconds(start_ms),
            duration=MediaTime.from_milliseconds(end_ms - start_ms),
        )

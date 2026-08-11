from fractions import Fraction

import pytest

from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange


def test_media_time_normalizes_and_preserves_exact_value() -> None:
    value = MediaTime(500, 1_000)

    assert value == MediaTime(1, 2)
    assert value.as_fraction() == Fraction(1, 2)
    assert value.to_milliseconds_exact() == 500


def test_media_time_rejects_boolean_and_non_positive_scale() -> None:
    with pytest.raises(TypeError):
        MediaTime(True, 1)
    with pytest.raises(ValueError):
        MediaTime(1, 0)


def test_non_millisecond_time_refuses_lossy_compatibility_conversion() -> None:
    value = MediaTime(1, 24)

    with pytest.raises(ValueError, match="exact integer millisecond"):
        value.to_milliseconds_exact()


def test_media_time_range_uses_exact_half_open_end() -> None:
    value = MediaTimeRange.from_milliseconds(250, 1_250)

    assert value.start == MediaTime(1, 4)
    assert value.duration == MediaTime(1, 1)
    assert value.end == MediaTime(5, 4)


def test_media_time_range_requires_positive_duration() -> None:
    with pytest.raises(ValueError):
        MediaTimeRange(start=MediaTime(0, 1), duration=MediaTime(0, 1))

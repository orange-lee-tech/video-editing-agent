from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.shot.model import Shot


@dataclass(frozen=True, slots=True)
class FrameSamplingOptions:
    max_frames: int = 5

    def __post_init__(self) -> None:
        if isinstance(self.max_frames, bool) or not isinstance(self.max_frames, int):
            raise TypeError("max_frames must be an int")
        if self.max_frames < 1:
            raise ValueError("max_frames must be >= 1")


@dataclass(frozen=True, slots=True, init=False)
class FrameSampleSpec:
    shot_ref: EntityRevisionRef
    ordinal: int
    source_timestamp: MediaTime

    def __init__(
        self,
        shot_ref: EntityRevisionRef,
        ordinal: int,
        source_timestamp_ms: int | None = None,
        *,
        source_timestamp: MediaTime | None = None,
    ) -> None:
        if source_timestamp is not None:
            if source_timestamp_ms is not None:
                raise ValueError("provide source_timestamp or source_timestamp_ms, not both")
            resolved_timestamp = source_timestamp
        else:
            if source_timestamp_ms is None:
                raise ValueError("source_timestamp or source_timestamp_ms is required")
            resolved_timestamp = MediaTime.from_milliseconds(source_timestamp_ms)

        if isinstance(ordinal, bool) or not isinstance(ordinal, int):
            raise TypeError("ordinal must be an int")
        if ordinal < 0:
            raise ValueError("ordinal must be >= 0")
        if resolved_timestamp.as_fraction() < 0:
            raise ValueError("source_timestamp must be >= 0")

        object.__setattr__(self, "shot_ref", shot_ref)
        object.__setattr__(self, "ordinal", ordinal)
        object.__setattr__(self, "source_timestamp", resolved_timestamp)

    @property
    def source_timestamp_ms(self) -> int:
        return self.source_timestamp.to_milliseconds_exact()


@dataclass(frozen=True, slots=True)
class FrameSamplingPlan:
    shot_ref: EntityRevisionRef
    samples: tuple[FrameSampleSpec, ...]

    def __post_init__(self) -> None:
        if any(sample.shot_ref != self.shot_ref for sample in self.samples):
            raise ValueError("every frame sample must reference the plan Shot revision")
        if tuple(sample.ordinal for sample in self.samples) != tuple(range(len(self.samples))):
            raise ValueError("frame sample ordinals must be contiguous from zero")
        timestamps = tuple(sample.source_timestamp.as_fraction() for sample in self.samples)
        if timestamps != tuple(sorted(set(timestamps))):
            raise ValueError("frame sample timestamps must be unique and increasing")


def _exact_midpoint_timestamp(shot: Shot, index: int, sample_count: int) -> MediaTime:
    duration = shot.source_range.duration
    offset = MediaTime(
        duration.value * (2 * index + 1),
        duration.scale * 2 * sample_count,
    )
    return shot.source_range.start + offset


def plan_uniform_frame_samples(
    shot: Shot,
    options: FrameSamplingOptions | None = None,
) -> FrameSamplingPlan:
    """Choose deterministic midpoint-of-bin sample timestamps inside one Shot range."""
    resolved_options = options or FrameSamplingOptions()
    shot_ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)

    try:
        duration_ms = shot.duration_ms
        source_start_ms = shot.source_start_ms
    except ValueError:
        sample_count = resolved_options.max_frames
        timestamps = tuple(
            _exact_midpoint_timestamp(shot, index, sample_count) for index in range(sample_count)
        )
    else:
        sample_count = min(resolved_options.max_frames, duration_ms)
        timestamps = tuple(
            MediaTime.from_milliseconds(
                source_start_ms + ((2 * index + 1) * duration_ms) // (2 * sample_count)
            )
            for index in range(sample_count)
        )

    samples = tuple(
        FrameSampleSpec(
            shot_ref=shot_ref,
            ordinal=index,
            source_timestamp=timestamp,
        )
        for index, timestamp in enumerate(timestamps)
    )
    return FrameSamplingPlan(shot_ref=shot_ref, samples=samples)

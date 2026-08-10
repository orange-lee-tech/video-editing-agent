from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shot.model import Shot


@dataclass(frozen=True, slots=True)
class FrameSamplingOptions:
    max_frames: int = 5

    def __post_init__(self) -> None:
        if isinstance(self.max_frames, bool) or not isinstance(self.max_frames, int):
            raise TypeError("max_frames must be an int")
        if self.max_frames < 1:
            raise ValueError("max_frames must be >= 1")


@dataclass(frozen=True, slots=True)
class FrameSampleSpec:
    shot_ref: EntityRevisionRef
    ordinal: int
    source_timestamp_ms: int

    def __post_init__(self) -> None:
        if isinstance(self.ordinal, bool) or not isinstance(self.ordinal, int):
            raise TypeError("ordinal must be an int")
        if self.ordinal < 0:
            raise ValueError("ordinal must be >= 0")
        if isinstance(self.source_timestamp_ms, bool) or not isinstance(
            self.source_timestamp_ms, int
        ):
            raise TypeError("source_timestamp_ms must be an int")
        if self.source_timestamp_ms < 0:
            raise ValueError("source_timestamp_ms must be >= 0")


@dataclass(frozen=True, slots=True)
class FrameSamplingPlan:
    shot_ref: EntityRevisionRef
    samples: tuple[FrameSampleSpec, ...]

    def __post_init__(self) -> None:
        if any(sample.shot_ref != self.shot_ref for sample in self.samples):
            raise ValueError("every frame sample must reference the plan Shot revision")
        if tuple(sample.ordinal for sample in self.samples) != tuple(range(len(self.samples))):
            raise ValueError("frame sample ordinals must be contiguous from zero")
        timestamps = tuple(sample.source_timestamp_ms for sample in self.samples)
        if timestamps != tuple(sorted(set(timestamps))):
            raise ValueError("frame sample timestamps must be unique and increasing")


def plan_uniform_frame_samples(
    shot: Shot,
    options: FrameSamplingOptions | None = None,
) -> FrameSamplingPlan:
    """Choose deterministic midpoint-of-bin sample timestamps inside one Shot range."""
    resolved_options = options or FrameSamplingOptions()
    shot_ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
    sample_count = min(resolved_options.max_frames, shot.duration_ms)

    timestamps_ms = tuple(
        shot.source_start_ms
        + ((2 * index + 1) * shot.duration_ms) // (2 * sample_count)
        for index in range(sample_count)
    )
    samples = tuple(
        FrameSampleSpec(
            shot_ref=shot_ref,
            ordinal=index,
            source_timestamp_ms=timestamp_ms,
        )
        for index, timestamp_ms in enumerate(timestamps_ms)
    )
    return FrameSamplingPlan(shot_ref=shot_ref, samples=samples)

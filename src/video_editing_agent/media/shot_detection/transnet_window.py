from __future__ import annotations

from collections import deque
from collections.abc import Iterable, Iterator
from dataclasses import dataclass


TRANSNETV2_CONTEXT_FRAMES = 25
TRANSNETV2_OUTPUT_FRAMES = 50
TRANSNETV2_WINDOW_FRAMES = 100


@dataclass(frozen=True, slots=True)
class TransNetV2Window:
    """One padded model window plus the number of center predictions that are real video."""

    frames: tuple[bytes, ...]
    valid_output_frames: int

    def __post_init__(self) -> None:
        if len(self.frames) != TRANSNETV2_WINDOW_FRAMES:
            raise ValueError(f"TransNetV2 window must contain {TRANSNETV2_WINDOW_FRAMES} frames")
        if not 1 <= self.valid_output_frames <= TRANSNETV2_OUTPUT_FRAMES:
            raise ValueError(
                f"valid_output_frames must be between 1 and {TRANSNETV2_OUTPUT_FRAMES}"
            )

    @property
    def center_frames(self) -> tuple[bytes, ...]:
        start = TRANSNETV2_CONTEXT_FRAMES
        end = start + self.valid_output_frames
        return self.frames[start:end]


def _validate_frame(frame: bytes, *, expected_size: int | None) -> int:
    if not isinstance(frame, bytes):
        raise TypeError("TransNetV2 frame source must yield bytes")
    if not frame:
        raise ValueError("TransNetV2 frame must not be empty")
    if expected_size is not None and len(frame) != expected_size:
        raise ValueError(
            f"TransNetV2 frame size changed within one stream: expected {expected_size} bytes, "
            f"got {len(frame)}"
        )
    return len(frame)


def iter_transnetv2_windows(frames: Iterable[bytes]) -> Iterator[TransNetV2Window]:
    """Build streaming 100-frame TransNetV2 inference windows with 25-frame context.

    The first frame supplies the 25-frame left context. New inference windows advance by
    50 frames. At end-of-stream, the final frame supplies right-context padding. Only
    predictions corresponding to real source frames are marked valid.

    Resident frame memory stays bounded by one model window regardless of video duration.
    """
    source = iter(frames)
    try:
        first_frame = next(source)
    except StopIteration:
        return

    frame_size = _validate_frame(first_frame, expected_size=None)
    last_real_frame = first_frame
    window: deque[bytes] = deque([first_frame] * TRANSNETV2_CONTEXT_FRAMES)
    window.append(first_frame)

    actual_frames_seen = 1
    actual_frames_emitted = 0
    source_exhausted = False

    while True:
        while len(window) < TRANSNETV2_WINDOW_FRAMES and not source_exhausted:
            try:
                frame = next(source)
            except StopIteration:
                source_exhausted = True
                break

            _validate_frame(frame, expected_size=frame_size)
            window.append(frame)
            last_real_frame = frame
            actual_frames_seen += 1

        if source_exhausted and len(window) < TRANSNETV2_WINDOW_FRAMES:
            window.extend([last_real_frame] * (TRANSNETV2_WINDOW_FRAMES - len(window)))

        if len(window) < TRANSNETV2_WINDOW_FRAMES:
            continue

        remaining_real_frames = actual_frames_seen - actual_frames_emitted
        if remaining_real_frames <= 0:
            return

        valid_output_frames = min(TRANSNETV2_OUTPUT_FRAMES, remaining_real_frames)
        yield TransNetV2Window(
            frames=tuple(window),
            valid_output_frames=valid_output_frames,
        )
        actual_frames_emitted += valid_output_frames

        for _ in range(TRANSNETV2_OUTPUT_FRAMES):
            window.popleft()

        if source_exhausted and actual_frames_emitted >= actual_frames_seen:
            return

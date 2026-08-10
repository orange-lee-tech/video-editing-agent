import math

import pytest

from video_editing_agent.media.shot_detection.transnet_window import (
    TRANSNETV2_CONTEXT_FRAMES,
    TRANSNETV2_OUTPUT_FRAMES,
    TRANSNETV2_WINDOW_FRAMES,
    iter_transnetv2_windows,
)


def make_frames(count: int) -> list[bytes]:
    return [bytes([index]) for index in range(count)]


@pytest.mark.parametrize("frame_count", [1, 49, 50, 51, 75, 100, 125])
def test_streaming_windows_reconstruct_each_real_frame_exactly_once(frame_count: int) -> None:
    source_frames = make_frames(frame_count)
    windows = list(iter_transnetv2_windows(source_frames))

    reconstructed = [frame for window in windows for frame in window.center_frames]

    assert reconstructed == source_frames
    assert len(windows) == math.ceil(frame_count / TRANSNETV2_OUTPUT_FRAMES)
    assert all(len(window.frames) == TRANSNETV2_WINDOW_FRAMES for window in windows)
    assert sum(window.valid_output_frames for window in windows) == frame_count


def test_first_and_last_frame_supply_padding_context() -> None:
    source_frames = [b"first", b"last!"]
    windows = list(iter_transnetv2_windows(source_frames))

    assert len(windows) == 1
    window = windows[0]
    assert window.frames[:TRANSNETV2_CONTEXT_FRAMES] == (b"first",) * TRANSNETV2_CONTEXT_FRAMES
    assert window.center_frames == tuple(source_frames)
    assert window.frames[-1] == b"last!"


def test_empty_stream_produces_no_windows() -> None:
    assert list(iter_transnetv2_windows([])) == []


def test_window_builder_rejects_frame_size_changes() -> None:
    with pytest.raises(ValueError, match="frame size changed"):
        list(iter_transnetv2_windows([b"a", b"bb"]))


def test_window_builder_rejects_empty_frame() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        list(iter_transnetv2_windows([b""]))


def test_window_builder_rejects_non_bytes_frame() -> None:
    with pytest.raises(TypeError, match="must yield bytes"):
        list(iter_transnetv2_windows([b"a", bytearray(b"b")]))  # type: ignore[list-item]

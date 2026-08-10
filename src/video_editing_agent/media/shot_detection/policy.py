from __future__ import annotations

from collections.abc import Iterable


def _require_non_negative_int(name: str, value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value}")
    return value


def _normalize_optional_constraint(name: str, value: int | None) -> int | None:
    if value is None:
        return None
    normalized = _require_non_negative_int(name, value)
    return None if normalized == 0 else normalized


def normalize_split_points_ms(
    split_points_ms: Iterable[int],
    *,
    total_duration_ms: int,
) -> tuple[int, ...]:
    """Return sorted, unique split points strictly inside the source duration."""
    duration_ms = _require_non_negative_int("total_duration_ms", total_duration_ms)

    normalized: set[int] = set()
    for point_ms in split_points_ms:
        point = _require_non_negative_int("split_point_ms", point_ms)
        if 0 < point < duration_ms:
            normalized.add(point)

    return tuple(sorted(normalized))


def scene_end_times_to_split_points_ms(
    scene_end_times_ms: Iterable[int],
    *,
    minimum_gap_ms: int = 1,
) -> tuple[int, ...]:
    """Convert ordered scene end times into cut points, excluding the final scene end.

    A detector adapter is expected to convert model-specific output into integer
    milliseconds before calling this function. Non-increasing or near-duplicate scene
    ends are ignored. The final accepted scene end is treated as the media end and is
    therefore not returned as a cut point.
    """
    gap_ms = _require_non_negative_int("minimum_gap_ms", minimum_gap_ms)

    accepted_end_times: list[int] = []
    last_end_ms = 0

    for end_time_ms in scene_end_times_ms:
        end_ms = _require_non_negative_int("scene_end_time_ms", end_time_ms)
        if end_ms > last_end_ms + gap_ms:
            accepted_end_times.append(end_ms)
            last_end_ms = end_ms

    if len(accepted_end_times) <= 1:
        return ()

    return tuple(accepted_end_times[:-1])


def _merge_short_segments(
    cut_points_ms: tuple[int, ...],
    *,
    total_duration_ms: int,
    min_shot_duration_ms: int | None,
) -> tuple[int, ...]:
    if min_shot_duration_ms is None or not cut_points_ms:
        return cut_points_ms

    kept: list[int] = []
    segment_start_ms = 0

    for cut_ms in cut_points_ms:
        if cut_ms - segment_start_ms < min_shot_duration_ms:
            continue
        kept.append(cut_ms)
        segment_start_ms = cut_ms

    if kept and total_duration_ms - kept[-1] < min_shot_duration_ms:
        kept.pop()

    return tuple(kept)


def _partition_segment(
    *,
    segment_start_ms: int,
    segment_end_ms: int,
    min_shot_duration_ms: int | None,
    max_shot_duration_ms: int,
) -> tuple[int, ...]:
    segment_length_ms = segment_end_ms - segment_start_ms
    if segment_length_ms <= max_shot_duration_ms:
        return ()

    minimum_piece_count = (segment_length_ms + max_shot_duration_ms - 1) // max_shot_duration_ms

    if min_shot_duration_ms is not None:
        maximum_piece_count = segment_length_ms // min_shot_duration_ms
        if minimum_piece_count > maximum_piece_count:
            raise ValueError(
                "shot duration constraints cannot both be satisfied for segment "
                f"[{segment_start_ms}, {segment_end_ms}) ms: "
                f"min={min_shot_duration_ms} ms, max={max_shot_duration_ms} ms"
            )

    piece_count = minimum_piece_count
    base_piece_ms, remainder_ms = divmod(segment_length_ms, piece_count)

    inserted_cuts: list[int] = []
    cursor_ms = segment_start_ms

    for piece_index in range(piece_count - 1):
        piece_length_ms = base_piece_ms + (1 if piece_index < remainder_ms else 0)
        cursor_ms += piece_length_ms
        inserted_cuts.append(cursor_ms)

    return tuple(inserted_cuts)


def enforce_shot_duration_policy(
    split_points_ms: Iterable[int],
    *,
    total_duration_ms: int,
    min_shot_duration_ms: int | None = None,
    max_shot_duration_ms: int | None = None,
) -> tuple[int, ...]:
    """Apply deterministic minimum/maximum duration constraints to cut points.

    Short segments are merged by removing cut points. Long segments are partitioned
    as evenly as possible. When minimum and maximum constraints cannot both be
    satisfied for a segment, the function fails explicitly rather than emitting a
    boundary set that violates its own policy.

    A source shorter than ``min_shot_duration_ms`` remains a single unavoidable shot.
    """
    duration_ms = _require_non_negative_int("total_duration_ms", total_duration_ms)
    min_ms = _normalize_optional_constraint("min_shot_duration_ms", min_shot_duration_ms)
    max_ms = _normalize_optional_constraint("max_shot_duration_ms", max_shot_duration_ms)

    if min_ms is not None and max_ms is not None and min_ms > max_ms:
        raise ValueError(
            f"min_shot_duration_ms ({min_ms}) cannot exceed max_shot_duration_ms ({max_ms})"
        )

    normalized_cuts = normalize_split_points_ms(
        split_points_ms,
        total_duration_ms=duration_ms,
    )
    merged_cuts = _merge_short_segments(
        normalized_cuts,
        total_duration_ms=duration_ms,
        min_shot_duration_ms=min_ms,
    )

    if max_ms is None or duration_ms == 0:
        return merged_cuts

    boundaries = (0, *merged_cuts, duration_ms)
    all_cuts = set(merged_cuts)

    for segment_start_ms, segment_end_ms in zip(boundaries[:-1], boundaries[1:], strict=True):
        all_cuts.update(
            _partition_segment(
                segment_start_ms=segment_start_ms,
                segment_end_ms=segment_end_ms,
                min_shot_duration_ms=min_ms,
                max_shot_duration_ms=max_ms,
            )
        )

    return tuple(sorted(all_cuts))


def split_points_to_ranges_ms(
    split_points_ms: Iterable[int],
    *,
    total_duration_ms: int,
) -> tuple[tuple[int, int], ...]:
    """Convert cut points into half-open source ranges ``[start_ms, end_ms)``."""
    duration_ms = _require_non_negative_int("total_duration_ms", total_duration_ms)
    cuts = normalize_split_points_ms(split_points_ms, total_duration_ms=duration_ms)
    boundaries = (0, *cuts, duration_ms)

    return tuple(zip(boundaries[:-1], boundaries[1:], strict=True))

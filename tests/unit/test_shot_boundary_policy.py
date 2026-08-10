import pytest

from video_editing_agent.media.shot_detection.policy import (
    enforce_shot_duration_policy,
    normalize_split_points_ms,
    scene_end_times_to_split_points_ms,
    split_points_to_ranges_ms,
)


def test_normalize_split_points_sorts_deduplicates_and_drops_edges() -> None:
    assert normalize_split_points_ms(
        [5_000, 0, 2_000, 2_000, 10_000, 12_000],
        total_duration_ms=10_000,
    ) == (2_000, 5_000)


def test_scene_end_times_drop_final_media_end() -> None:
    assert scene_end_times_to_split_points_ms([1_000, 2_500, 4_000]) == (1_000, 2_500)


def test_scene_end_times_ignore_near_duplicate_or_non_increasing_values() -> None:
    assert scene_end_times_to_split_points_ms(
        [1_000, 1_001, 900, 2_000, 3_000],
        minimum_gap_ms=1,
    ) == (1_000, 2_000)


def test_minimum_duration_merges_short_interior_and_tail_segments() -> None:
    assert (
        enforce_shot_duration_policy(
            [500, 1_500],
            total_duration_ms=2_000,
            min_shot_duration_ms=1_000,
        )
        == ()
    )


def test_maximum_duration_splits_long_segment_evenly() -> None:
    cuts = enforce_shot_duration_policy(
        [],
        total_duration_ms=3_000,
        max_shot_duration_ms=1_000,
    )

    assert cuts == (1_000, 2_000)
    assert split_points_to_ranges_ms(cuts, total_duration_ms=3_000) == (
        (0, 1_000),
        (1_000, 2_000),
        (2_000, 3_000),
    )


def test_combined_policy_can_merge_then_split() -> None:
    assert enforce_shot_duration_policy(
        [500, 2_500],
        total_duration_ms=3_000,
        min_shot_duration_ms=1_000,
        max_shot_duration_ms=1_500,
    ) == (1_500,)


def test_impossible_minimum_and_maximum_partition_fails_explicitly() -> None:
    with pytest.raises(ValueError, match="cannot both be satisfied"):
        enforce_shot_duration_policy(
            [],
            total_duration_ms=1_100,
            min_shot_duration_ms=1_000,
            max_shot_duration_ms=1_000,
        )


def test_source_shorter_than_minimum_remains_single_unavoidable_shot() -> None:
    assert (
        enforce_shot_duration_policy(
            [],
            total_duration_ms=800,
            min_shot_duration_ms=1_000,
        )
        == ()
    )

    assert split_points_to_ranges_ms([], total_duration_ms=800) == ((0, 800),)


def test_minimum_cannot_exceed_maximum() -> None:
    with pytest.raises(ValueError, match="cannot exceed"):
        enforce_shot_duration_policy(
            [],
            total_duration_ms=5_000,
            min_shot_duration_ms=2_000,
            max_shot_duration_ms=1_000,
        )

from dataclasses import replace
from datetime import UTC, datetime

import pytest

from video_editing_agent.application.ports.audio_editorial import (
    AudioAutomationIntent,
    AudioAutomationKind,
    AudioTrackRole,
    SourceAudioPolicy,
)
from video_editing_agent.application.ports.music_selection import MusicIntent
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.music.model import BeatMap, BeatPoint
from video_editing_agent.music.audio_editorial import plan_basic_mix
from video_editing_agent.music.execution import compile_audio_execution
from video_editing_agent.music.selection.service import (
    WindowScoringPolicy,
    generate_music_windows,
    select_music,
)

REF = EntityRevisionRef("music", 1)


def _beatmap() -> BeatMap:
    envelope = tuple(BeatPoint(MediaTime(index, 2), 0.2 + index / 25, 0.9) for index in range(20))
    return BeatMap(
        EntityEnvelope(
            "beat", 1, "0.2", EntityStatus.VALID, datetime(2026, 8, 13, tzinfo=UTC), "test"
        ),
        REF,
        MediaTimeRange(MediaTime(0, 1), MediaTime(10, 1)),
        tuple(envelope[1::2]),
        120.0,
        "test",
        "v2",
        0.9,
        envelope,
    )


def test_track_role_is_not_an_edit_slot_identifier() -> None:
    intent = AudioAutomationIntent(
        AudioAutomationKind.GAIN, REF, (), -10, target_role=AudioTrackRole.BGM
    )
    assert intent.target_role is AudioTrackRole.BGM and not intent.target_slot_ids
    with pytest.raises(ValueError, match="mutually exclusive"):
        AudioAutomationIntent(
            AudioAutomationKind.GAIN, REF, ("slot",), -10, target_role=AudioTrackRole.BGM
        )


def test_feature_scores_are_inspectable_nonconstant_and_deterministic() -> None:
    args = (
        _beatmap(),
        MediaTime(3, 1),
        ("att",),
        MusicIntent("energetic", mood_tags=("high",)),
        WindowScoringPolicy(speech_ranges=(MediaTimeRange(MediaTime(0, 1), MediaTime(2, 1)),)),
    )
    first = generate_music_windows(*args[:3], intent=args[3], policy=args[4])
    second = generate_music_windows(*args[:3], intent=args[3], policy=args[4])
    assert first == second and len({item.score for item in first}) > 1
    assert all(item.feature_contributions and item.reasons for item in first)


def test_selection_globally_ranks_unordered_cross_asset_candidates() -> None:
    generated = generate_music_windows(_beatmap(), MediaTime(3, 1), ("att",))
    low_ref = EntityRevisionRef("music-low", 1)
    high_ref = EntityRevisionRef("music-high", 1)
    low = replace(generated[0], candidate_id="candidate-low", audio_asset_ref=low_ref, score=0.4)
    duplicate_low_asset = replace(
        generated[1], candidate_id="candidate-alternative", audio_asset_ref=low_ref, score=0.3
    )
    high = replace(generated[2], candidate_id="candidate-high", audio_asset_ref=high_ref, score=0.9)

    first = select_music((low, duplicate_low_asset, high))
    reversed_input = select_music((high, duplicate_low_asset, low))

    assert first == reversed_input
    assert first is not None
    assert first.selected_asset_ref == high_ref
    assert first.score == 0.9
    assert first.alternative_asset_refs == (low_ref,)
    assert first.reasons[0] == "highest deterministic feature score"


def test_selection_tie_breaking_is_order_independent() -> None:
    generated = generate_music_windows(_beatmap(), MediaTime(3, 1), ("att",))
    first = replace(generated[0], candidate_id="candidate-z", score=0.8)
    second = replace(generated[1], candidate_id="candidate-a", score=0.8)
    expected = min((first, second), key=lambda item: item.source_range.start.as_fraction())

    forward = select_music((first, second))
    reverse = select_music((second, first))
    assert forward == reverse
    assert forward is not None
    assert forward.source_segments[0].source_range == expected.source_range


def test_loop_and_duck_ramps_are_bounded() -> None:
    windows = generate_music_windows(_beatmap(), MediaTime(3, 1), ("att",))
    decision = select_music(windows, target_duration=MediaTime(6, 1))
    assert decision is not None and len(decision.source_segments) == 2
    speech = (
        MediaTimeRange(MediaTime(0, 1), MediaTime(2, 1)),
        MediaTimeRange(MediaTime(3, 2), MediaTime(2, 1)),
    )
    mix = plan_basic_mix(EntityRevisionRef("plan", 1), REF, MediaTime(5, 1), speech)
    ducks = [item for item in mix.automation_intents if item.kind is AudioAutomationKind.DUCK]
    assert len(ducks) == 1 and ducks[0].start == MediaTime(0, 1) and ducks[0].end.as_fraction() <= 4
    plan = compile_audio_execution(decision, mix)
    assert plan.source_segments == tuple(item.source_range for item in decision.source_segments)
    assert (
        "atrim=start="
        + decision.source_segments[0].source_range.start.to_decimal_seconds_string(
            fractional_digits=6
        )
        in plan.filter_complex
    )
    assert "[chosen]," not in plan.filter_complex


def test_loop_tail_exactly_covers_non_multiple_target_duration() -> None:
    generated = generate_music_windows(_beatmap(), MediaTime(3, 1), ("att",))
    selected = replace(
        generated[0],
        source_range=MediaTimeRange(
            generated[0].source_range.start,
            MediaTime(5, 4),
        ),
    )

    decision = select_music((selected,), target_duration=MediaTime(3, 1))

    assert decision is not None
    assert tuple(segment.order for segment in decision.source_segments) == (0, 1, 2)
    assert tuple(
        segment.source_range.duration.as_fraction() for segment in decision.source_segments
    ) == (
        MediaTime(5, 4).as_fraction(),
        MediaTime(5, 4).as_fraction(),
        MediaTime(1, 2).as_fraction(),
    )
    assert (
        sum(segment.source_range.duration.as_fraction() for segment in decision.source_segments)
        == MediaTime(3, 1).as_fraction()
    )
    assert decision.warnings == ()


def test_decision_mutation_changes_compiled_plan() -> None:
    windows = generate_music_windows(_beatmap(), MediaTime(3, 1), ("att",))
    selection = select_music(windows)
    assert selection is not None
    first = plan_basic_mix(
        EntityRevisionRef("plan", 1),
        REF,
        MediaTime(3, 1),
        (MediaTimeRange(MediaTime(1, 1), MediaTime(1, 1)),),
    )
    second = plan_basic_mix(
        EntityRevisionRef("plan", 1),
        REF,
        MediaTime(3, 1),
        (MediaTimeRange(MediaTime(2, 1), MediaTime(1, 2)),),
    )
    assert (
        compile_audio_execution(selection, first).filter_complex
        != compile_audio_execution(selection, second).filter_complex
    )


def test_duck_multiplier_is_relative_to_decision_base_gain() -> None:
    windows = generate_music_windows(_beatmap(), MediaTime(3, 1), ("att",))
    selection = select_music(windows)
    assert selection is not None
    mix = plan_basic_mix(
        EntityRevisionRef("plan", 1),
        REF,
        MediaTime(3, 1),
        (MediaTimeRange(MediaTime(1, 1), MediaTime(1, 1)),),
    )
    changed_base = replace(
        mix,
        automation_intents=tuple(
            replace(intent, gain_db=-16.0) if intent.kind is AudioAutomationKind.GAIN else intent
            for intent in mix.automation_intents
        ),
    )

    assert "volume='0.251188643'" in compile_audio_execution(selection, mix).filter_complex
    assert "volume='0.501187234'" in compile_audio_execution(selection, changed_base).filter_complex


def test_source_audio_policy_mutation_changes_canonical_execution() -> None:
    selection = select_music(generate_music_windows(_beatmap(), MediaTime(3, 1), ("att",)))
    assert selection is not None
    preserve = plan_basic_mix(
        EntityRevisionRef("plan", 1),
        REF,
        MediaTime(3, 1),
        (MediaTimeRange(MediaTime(1, 1), MediaTime(1, 1)),),
    )
    mute = replace(preserve, source_audio_policy=SourceAudioPolicy.MUTE)

    preserve_plan = compile_audio_execution(selection, preserve)
    mute_plan = compile_audio_execution(selection, mute)
    assert preserve_plan.source_audio_policy is SourceAudioPolicy.PRESERVE
    assert preserve_plan.consumes_source_audio
    assert "[0:a]" in preserve_plan.filter_complex
    assert mute_plan.source_audio_policy is SourceAudioPolicy.MUTE
    assert not mute_plan.consumes_source_audio
    assert "[0:a]" not in mute_plan.filter_complex
    assert preserve_plan.filter_complex != mute_plan.filter_complex


def test_no_source_audio_still_compiles_intentional_bgm_output() -> None:
    selection = select_music(generate_music_windows(_beatmap(), MediaTime(3, 1), ("att",)))
    assert selection is not None
    preserve = plan_basic_mix(
        EntityRevisionRef("plan", 1),
        REF,
        MediaTime(3, 1),
        (MediaTimeRange(MediaTime(1, 1), MediaTime(1, 1)),),
    )

    plan = compile_audio_execution(selection, preserve, source_audio_available=False)
    assert not plan.consumes_source_audio
    assert "[0:a]" not in plan.filter_complex
    assert "[bgm]anull[a]" in plan.filter_complex


def test_source_audio_duck_fails_closed_until_semantics_are_owned() -> None:
    selection = select_music(generate_music_windows(_beatmap(), MediaTime(3, 1), ("att",)))
    assert selection is not None
    mix = replace(
        plan_basic_mix(EntityRevisionRef("plan", 1), REF, MediaTime(3, 1), ()),
        source_audio_policy=SourceAudioPolicy.DUCK,
    )
    with pytest.raises(ValueError, match="source-audio DUCK execution is not implemented"):
        compile_audio_execution(selection, mix)

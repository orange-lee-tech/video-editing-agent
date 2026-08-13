from datetime import UTC, datetime

import pytest

from video_editing_agent.application.ports.audio_editorial import (
    AudioAutomationIntent,
    AudioAutomationKind,
    AudioTrackRole,
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

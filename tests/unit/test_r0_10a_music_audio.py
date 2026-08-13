from datetime import UTC, datetime

from video_editing_agent.domain.asset.rights import RightsAttestation, RightsEligibility
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.music.model import BeatMap, BeatPoint
from video_editing_agent.music.audio_editorial import plan_basic_mix
from video_editing_agent.music.selection.service import (
    generate_music_windows,
    local_rights_eligibility,
    select_music,
)

REF = EntityRevisionRef("music", 1)
NOW = datetime(2026, 8, 13, tzinfo=UTC)


def beatmap() -> BeatMap:
    return BeatMap(
        EntityEnvelope("beat", 1, "0.2", EntityStatus.VALID, NOW, "test"),
        REF,
        MediaTimeRange(MediaTime(0, 1), MediaTime(8, 1)),
        (BeatPoint(MediaTime(1, 2), 1.0, 0.8), BeatPoint(MediaTime(1, 1), 0.9, 0.8)),
        120.0,
        "test",
        "v1",
    )


def test_rights_fail_closed_and_attestation_is_not_certification() -> None:
    assert local_rights_eligibility(REF, None) is RightsEligibility.UNKNOWN
    attestation = RightsAttestation("att", REF, "user", NOW, "I own this local fixture")
    assert local_rights_eligibility(REF, attestation) is RightsEligibility.ELIGIBLE
    assert generate_music_windows(beatmap(), MediaTime(3, 1), ()) == ()


def test_windows_are_rational_grounded_and_deterministic() -> None:
    first = generate_music_windows(beatmap(), MediaTime(3, 1), ("att",))
    assert first == generate_music_windows(beatmap(), MediaTime(3, 1), ("att",))
    assert all(x.source_range.end.as_fraction() <= 8 for x in first)
    decision = select_music(first)
    assert (
        decision is not None and decision.source_segments[0].source_range == first[0].source_range
    )


def test_mix_envelope_is_bounded_and_speech_explicit() -> None:
    speech = (MediaTimeRange(MediaTime(1, 1), MediaTime(2, 1)),)
    mix = plan_basic_mix(EntityRevisionRef("plan", 1), REF, MediaTime(6, 1), speech)
    assert any(
        x.kind.value == "duck" and x.evidence_refs == ("speech_vad",)
        for x in mix.automation_intents
    )
    assert all(x.start is None or x.end.as_fraction() <= 6 for x in mix.automation_intents)

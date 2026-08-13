from __future__ import annotations

import hashlib
from dataclasses import dataclass
from fractions import Fraction

from video_editing_agent.application.ports.music_selection import (
    CandidateMusicWindow,
    MusicIntent,
    MusicSelectionDecision,
    MusicSourceSegment,
)
from video_editing_agent.domain.asset.rights import RightsAttestation, RightsEligibility
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.music.model import BeatMap


@dataclass(frozen=True, slots=True)
class WindowScoringPolicy:
    strategy_version: str = "r0.10b-features-v1"
    speech_ranges: tuple[MediaTimeRange, ...] = ()


def local_rights_eligibility(
    asset_ref: EntityRevisionRef, attestation: RightsAttestation | None
) -> RightsEligibility:
    return (
        RightsEligibility.ELIGIBLE
        if attestation is not None and attestation.asset_ref == asset_ref
        else RightsEligibility.UNKNOWN
    )


def _overlap(left: MediaTimeRange, right: MediaTimeRange) -> float:
    start = max(left.start.as_fraction(), right.start.as_fraction())
    end = min(left.end.as_fraction(), right.end.as_fraction())
    overlap = end - start
    return float(max(Fraction(0), overlap))


def generate_music_windows(
    beat_map: BeatMap,
    duration: MediaTime,
    rights_refs: tuple[str, ...],
    intent: MusicIntent | None = None,
    policy: WindowScoringPolicy | None = None,
) -> tuple[CandidateMusicWindow, ...]:
    if not rights_refs:
        return ()
    active = policy or WindowScoringPolicy()
    target_energy = 0.7 if intent is not None and "high" in intent.mood_tags else 0.5
    starts = (beat_map.analyzed_source_range.start, *(beat.source_time for beat in beat_map.beats))
    found = []
    for start in starts:
        if (start + duration).as_fraction() > beat_map.analyzed_source_range.end.as_fraction():
            continue
        source_range = MediaTimeRange(start, duration)
        energy = [
            point.energy
            for point in beat_map.energy_envelope
            if source_range.start.as_fraction()
            <= point.source_time.as_fraction()
            < source_range.end.as_fraction()
        ]
        mean_energy = sum(energy) / len(energy) if energy else 0.0
        energy_fit = max(0.0, 1.0 - abs(mean_energy - target_energy))
        aligned = (
            any(beat.source_time == start for beat in beat_map.beats)
            or start == beat_map.analyzed_source_range.start
        )
        boundary = 1.0 if aligned else 0.0
        speech_seconds = sum(_overlap(source_range, speech) for speech in active.speech_ranges)
        speech_fit = max(0.0, 1.0 - speech_seconds / float(duration.as_fraction()))
        completeness = 1.0
        rights = 1.0
        contributions = (
            ("boundary_alignment", boundary * 0.25),
            ("energy_fit", energy_fit * 0.25),
            ("duration_completeness", completeness * 0.2),
            ("speech_fit", speech_fit * 0.15),
            ("rights_confidence", rights * 0.15),
        )
        score = sum(value for _, value in contributions)
        confidence = min(1.0, beat_map.confidence * 0.8 + 0.2)
        identity = hashlib.sha256(
            f"{beat_map.envelope.id}:{start}:{duration}:{active.strategy_version}".encode()
        ).hexdigest()
        found.append(
            CandidateMusicWindow(
                f"cmw_{identity}",
                beat_map.audio_asset_ref,
                source_range,
                EntityRevisionRef(beat_map.envelope.id, beat_map.envelope.revision),
                rights_refs,
                active.strategy_version,
                score,
                confidence,
                contributions,
                ("feature-ranked grounded BeatMap window",),
            )
        )
    found.sort(
        key=lambda item: (-item.score, item.source_range.start.as_fraction(), item.candidate_id)
    )
    return tuple(found[:5])


def select_music(
    windows: tuple[CandidateMusicWindow, ...], *, target_duration: MediaTime | None = None
) -> MusicSelectionDecision | None:
    if not windows:
        return None
    selected = windows[0]
    segments: tuple[MusicSourceSegment, ...] = (MusicSourceSegment(0, selected.source_range),)
    warnings: tuple[str, ...] = ()
    if (
        target_duration is not None
        and target_duration.as_fraction() > selected.source_range.duration.as_fraction()
    ):
        repeats = int(target_duration.as_fraction() // selected.source_range.duration.as_fraction())
        if repeats < 2:
            warnings = ("structural loop refused: target does not require a full repeat",)
        else:
            segments = tuple(
                MusicSourceSegment(index, selected.source_range) for index in range(repeats)
            )
            if (
                sum(segment.source_range.duration.as_fraction() for segment in segments)
                < target_duration.as_fraction()
            ):
                warnings = ("loop plan does not fully cover target duration",)
    digest = hashlib.sha256(
        f"{selected.candidate_id}:{segments}:r0.10b-select-v1".encode()
    ).hexdigest()
    return MusicSelectionDecision(
        f"msd_{digest}",
        selected.audio_asset_ref,
        segments,
        selected.rights_evidence_refs,
        selected.score,
        selected.confidence,
        ("highest deterministic feature score", *selected.reasons),
        warnings,
        tuple(dict.fromkeys(item.audio_asset_ref for item in windows[1:])),
    )

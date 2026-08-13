from __future__ import annotations

import hashlib

from video_editing_agent.application.ports.music_selection import (
    CandidateMusicWindow,
    MusicSelectionDecision,
    MusicSourceSegment,
)
from video_editing_agent.domain.asset.rights import RightsAttestation, RightsEligibility
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.music.model import BeatMap


def local_rights_eligibility(
    asset_ref: EntityRevisionRef, attestation: RightsAttestation | None
) -> RightsEligibility:
    return (
        RightsEligibility.ELIGIBLE
        if attestation is not None and attestation.asset_ref == asset_ref
        else RightsEligibility.UNKNOWN
    )


def generate_music_windows(
    beat_map: BeatMap, duration: MediaTime, rights_refs: tuple[str, ...]
) -> tuple[CandidateMusicWindow, ...]:
    if not rights_refs:
        return ()
    starts = (beat_map.analyzed_source_range.start, *(beat.source_time for beat in beat_map.beats))
    found = []
    for start in starts:
        if (start + duration).as_fraction() > beat_map.analyzed_source_range.end.as_fraction():
            continue
        identity = hashlib.sha256(
            f"{beat_map.envelope.id}:{start}:{duration}:r0.10a-v1".encode()
        ).hexdigest()
        found.append(
            CandidateMusicWindow(
                f"cmw_{identity}",
                beat_map.audio_asset_ref,
                MediaTimeRange(start, duration),
                EntityRevisionRef(beat_map.envelope.id, beat_map.envelope.revision),
                rights_refs,
                "r0.10a-v1",
                0.8,
                0.8,
            )
        )
    return tuple(found[:5])


def select_music(windows: tuple[CandidateMusicWindow, ...]) -> MusicSelectionDecision | None:
    if not windows:
        return None
    selected = sorted(
        windows, key=lambda x: (-x.score, x.source_range.start.as_fraction(), x.candidate_id)
    )[0]
    digest = hashlib.sha256(f"{selected.candidate_id}:r0.10a-select-v1".encode()).hexdigest()
    return MusicSelectionDecision(
        f"msd_{digest}",
        selected.audio_asset_ref,
        (MusicSourceSegment(0, selected.source_range),),
        selected.rights_evidence_refs,
        selected.score,
        selected.confidence,
        ("highest deterministic rights-eligible grounded window",),
    )

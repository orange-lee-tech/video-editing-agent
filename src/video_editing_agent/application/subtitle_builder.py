from __future__ import annotations

from dataclasses import replace

from video_editing_agent.domain.edl.model import EDL, EDLTrack, EDLTrackFamily
from video_editing_agent.domain.edl.subtitle import EDLSubtitleCue, StructuredSubtitleCue
from video_editing_agent.domain.edl.validation import validate_edl


def compile_subtitle_cues(
    edl: EDL,
    cues: tuple[StructuredSubtitleCue, ...],
    *,
    track_id: str = "subtitle",
) -> EDL:
    """Attach approved cue intent to canonical EDL without rewriting or retiming it."""

    tracks = {track.track_id: track for track in edl.effective_tracks}
    existing = tracks.get(track_id)
    if existing is not None and existing.family is not EDLTrackFamily.SUBTITLE:
        raise ValueError("subtitle track_id is already owned by another track family")
    tracks[track_id] = EDLTrack(track_id, EDLTrackFamily.SUBTITLE)
    compiled = tuple(
        EDLSubtitleCue(
            cue.cue_id,
            track_id,
            cue.timeline_range,
            cue.text,
            cue.language,
            cue.speaker_ref,
            cue.emphasis,
            cue.layout,
        )
        for cue in cues
    )
    result = replace(edl, tracks=tuple(tracks.values()), subtitle_cues=compiled)
    validation = validate_edl(result)
    if not validation.is_valid:
        codes = ",".join(item.code.value for item in validation.diagnostics)
        raise ValueError(f"approved subtitle cues cannot compile into canonical EDL: {codes}")
    return result

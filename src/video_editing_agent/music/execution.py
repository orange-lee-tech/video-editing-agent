from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.application.ports.audio_editorial import (
    AudioAutomationKind,
    AudioMixDecision,
    AudioTrackRole,
)
from video_editing_agent.application.ports.music_selection import MusicSelectionDecision
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange


@dataclass(frozen=True, slots=True)
class AudioExecutionPlan:
    selected_asset_id: str
    source_segments: tuple[MediaTimeRange, ...]
    filter_complex: str
    output_duration_seconds: str


def _seconds(value: MediaTime) -> str:
    return value.to_decimal_seconds_string(fractional_digits=6)


def compile_audio_execution(
    selection: MusicSelectionDecision, mix: AudioMixDecision
) -> AudioExecutionPlan:
    segments = tuple(item.source_range for item in selection.source_segments)
    if not segments:
        raise ValueError("music selection has no source segments")
    if any(
        item.target_asset_ref != selection.selected_asset_ref for item in mix.automation_intents
    ):
        raise ValueError("mix automation targets a different music Asset revision")
    if any(item.target_role is not AudioTrackRole.BGM for item in mix.automation_intents):
        raise ValueError("diagnostic compiler accepts BGM role automation only")
    base_gain_intents = tuple(
        item
        for item in mix.automation_intents
        if item.kind is AudioAutomationKind.GAIN and item.gain_db is not None
    )
    if len(base_gain_intents) != 1:
        raise ValueError("diagnostic compiler requires exactly one explicit BGM base gain")
    base_gain_db = base_gain_intents[0].gain_db
    assert base_gain_db is not None
    segment_filters = [
        f"[1:a]atrim=start={_seconds(item.start)}:duration={_seconds(item.duration)},asetpts=PTS-STARTPTS[m{index}]"
        for index, item in enumerate(segments)
    ]
    concat_inputs = "".join(f"[m{index}]" for index in range(len(segments)))
    bgm_filters = []
    for intent in mix.automation_intents:
        if intent.start is None or intent.end is None:
            continue
        start, end = _seconds(intent.start), _seconds(intent.end)
        if intent.kind is AudioAutomationKind.GAIN and intent.gain_db is not None:
            bgm_filters.append(f"volume={10 ** (intent.gain_db / 20):.9f}")
        elif intent.kind is AudioAutomationKind.FADE_IN:
            bgm_filters.append(f"afade=t=in:st={start}:d={_seconds(intent.end - intent.start)}")
        elif intent.kind is AudioAutomationKind.FADE_OUT:
            bgm_filters.append(f"afade=t=out:st={start}:d={_seconds(intent.end - intent.start)}")
        elif intent.kind is AudioAutomationKind.DUCK and intent.gain_db is not None:
            multiplier = 10 ** ((intent.gain_db - base_gain_db) / 20)
            bgm_filters.append(f"volume='{multiplier:.9f}':enable='between(t,{start},{end})'")
    duration = sum(item.duration.as_fraction() for item in segments)
    duration_text = f"{float(duration):.6f}".rstrip("0").rstrip(".")
    graph = ";".join(
        (
            *segment_filters,
            f"{concat_inputs}concat=n={len(segments)}:v=0:a=1[chosen]",
            f"[chosen]{','.join(bgm_filters) if bgm_filters else 'anull'}[bgm]",
            f"[0:a]atrim=0:{duration_text},asetpts=PTS-STARTPTS[src]",
            "[src][bgm]amix=inputs=2:duration=first:normalize=0[a]",
        )
    )
    return AudioExecutionPlan(
        selection.selected_asset_ref.entity_id, segments, graph, duration_text
    )

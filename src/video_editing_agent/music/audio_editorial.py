from __future__ import annotations

import hashlib
import math
import wave
from dataclasses import dataclass

from video_editing_agent.application.ports.audio_editorial import (
    AudioAutomationIntent,
    AudioAutomationKind,
    AudioMixDecision,
    AudioTrackRole,
    SourceAudioPolicy,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange


def _clamp(value: MediaTime, duration: MediaTime) -> MediaTime:
    if value.as_fraction() < 0:
        return MediaTime(0, 1)
    return duration if value.as_fraction() > duration.as_fraction() else value


def plan_basic_mix(
    edit_plan_ref: EntityRevisionRef,
    bgm_ref: EntityRevisionRef,
    duration: MediaTime,
    speech_ranges: tuple[MediaTimeRange, ...],
) -> AudioMixDecision:
    intents = [
        AudioAutomationIntent(
            AudioAutomationKind.GAIN,
            bgm_ref,
            (),
            -10.0,
            reason="audible BGM base gain",
            start=MediaTime(0, 1),
            end=duration,
            target_role=AudioTrackRole.BGM,
        ),
        AudioAutomationIntent(
            AudioAutomationKind.FADE_IN,
            bgm_ref,
            (),
            -10.0,
            reason="linear fade from silence to base gain",
            start=MediaTime(0, 1),
            end=min_time(MediaTime(1, 2), duration),
            target_role=AudioTrackRole.BGM,
        ),
        AudioAutomationIntent(
            AudioAutomationKind.FADE_OUT,
            bgm_ref,
            (),
            -10.0,
            reason="linear fade from base gain to silence",
            start=_clamp(duration - MediaTime(1, 2), duration),
            end=duration,
            target_role=AudioTrackRole.BGM,
        ),
    ]
    merged = _merge_ranges(speech_ranges, duration)
    for item in merged:
        attack = _clamp(item.start - MediaTime(1, 4), duration)
        release = _clamp(item.end + MediaTime(1, 2), duration)
        intents.append(
            AudioAutomationIntent(
                AudioAutomationKind.DUCK,
                bgm_ref,
                (),
                -22.0,
                ("speech_vad",),
                "speech duck with 250ms attack and 500ms release",
                attack,
                release,
                AudioTrackRole.BGM,
            )
        )
    digest = hashlib.sha256(
        f"{edit_plan_ref}:{bgm_ref}:{duration}:{merged}:r0.10b".encode()
    ).hexdigest()
    return AudioMixDecision(
        f"amd_{digest}",
        edit_plan_ref,
        SourceAudioPolicy.PRESERVE if merged else SourceAudioPolicy.MUTE,
        tuple(intents),
        "diagnostic PCM peak/RMS only",
        0.9,
        (() if speech_ranges else ("speech evidence unavailable; no ducking applied",)),
    )


def min_time(left: MediaTime, right: MediaTime) -> MediaTime:
    return left if left.as_fraction() <= right.as_fraction() else right


def _merge_ranges(
    ranges: tuple[MediaTimeRange, ...], duration: MediaTime
) -> tuple[MediaTimeRange, ...]:
    clipped = sorted(
        (
            MediaTimeRange(
                _clamp(item.start, duration),
                _clamp(item.end, duration) - _clamp(item.start, duration),
            )
            for item in ranges
            if _clamp(item.end, duration).as_fraction() > _clamp(item.start, duration).as_fraction()
        ),
        key=lambda item: item.start.as_fraction(),
    )
    merged: list[MediaTimeRange] = []
    for item in clipped:
        if merged and item.start.as_fraction() <= merged[-1].end.as_fraction():
            end = max(item.end.as_fraction(), merged[-1].end.as_fraction())
            merged[-1] = MediaTimeRange(
                merged[-1].start, MediaTime(end.numerator, end.denominator) - merged[-1].start
            )
        else:
            merged.append(item)
    return tuple(merged)


@dataclass(frozen=True, slots=True)
class AudioQcResult:
    peak_dbfs: float | None
    rms_dbfs: float | None
    silent_fraction: float
    clipped_samples: int
    warnings: tuple[str, ...]


def inspect_pcm16_wav(path: str) -> AudioQcResult:
    with wave.open(path, "rb") as stream:
        if stream.getsampwidth() != 2:
            return AudioQcResult(None, None, 1.0, 0, ("QC unavailable for non-PCM16 input",))
        raw = stream.readframes(stream.getnframes())
    samples = [
        int.from_bytes(raw[index : index + 2], "little", signed=True)
        for index in range(0, len(raw), 2)
    ]
    if not samples:
        return AudioQcResult(None, None, 1.0, 0, ("empty audio",))
    peak = max(abs(item) for item in samples)
    rms = math.sqrt(sum(item * item for item in samples) / len(samples))
    silent = sum(abs(item) < 32 for item in samples) / len(samples)
    clipped = sum(abs(item) >= 32767 for item in samples)

    def db(value: float) -> float | None:
        return None if value == 0 else 20 * math.log10(value / 32768)

    warnings = tuple(
        message
        for condition, message in (
            (clipped > 0, "clipped PCM samples detected"),
            (silent > 0.95, "mostly silent audio"),
        )
        if condition
    )
    return AudioQcResult(db(peak), db(rms), silent, clipped, warnings)

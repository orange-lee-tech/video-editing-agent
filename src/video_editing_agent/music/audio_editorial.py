from __future__ import annotations

import hashlib

from video_editing_agent.application.ports.audio_editorial import (
    AudioAutomationIntent,
    AudioAutomationKind,
    AudioMixDecision,
    SourceAudioPolicy,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange


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
            ("bgm",),
            -10.0,
            reason="audible BGM base gain",
            start=MediaTime(0, 1),
            end=duration,
        ),
        AudioAutomationIntent(
            AudioAutomationKind.FADE_IN,
            bgm_ref,
            ("bgm",),
            -10.0,
            reason="bounded fade in",
            start=MediaTime(0, 1),
            end=MediaTime(1, 2),
        ),
        AudioAutomationIntent(
            AudioAutomationKind.FADE_OUT,
            bgm_ref,
            ("bgm",),
            -10.0,
            reason="bounded fade out",
            start=duration - MediaTime(1, 2),
            end=duration,
        ),
    ]
    intents.extend(
        AudioAutomationIntent(
            AudioAutomationKind.DUCK,
            bgm_ref,
            ("bgm",),
            -22.0,
            ("speech_vad",),
            "speech-aware duck",
            item.start,
            item.end,
        )
        for item in speech_ranges
    )
    digest = hashlib.sha256(
        f"{edit_plan_ref}:{bgm_ref}:{duration}:{speech_ranges}".encode()
    ).hexdigest()
    return AudioMixDecision(
        f"amd_{digest}",
        edit_plan_ref,
        SourceAudioPolicy.PRESERVE,
        tuple(intents),
        "diagnostic mix; no delivery loudness claim",
        0.85,
        (() if speech_ranges else ("speech evidence unavailable; no ducking applied",)),
    )

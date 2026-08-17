from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange


class SourceAudioPolicy(StrEnum):
    PRESERVE = "preserve"
    DUCK = "duck"
    MUTE = "mute"


class VoiceTreatment(StrEnum):
    PRESERVE = "preserve"
    CLEAN = "clean"
    ALLOW_REVOICE = "allow_revoice"
    DO_NOT_USE_ORIGINAL = "do_not_use_original"


@dataclass(frozen=True, slots=True)
class SourceAudioTreatment:
    """Audio intent grounded to one Resolver-owned selection/source range."""

    selection_id: str
    source_range: MediaTimeRange
    source_audio_policy: SourceAudioPolicy
    voice_treatment: VoiceTreatment = VoiceTreatment.PRESERVE
    required_speech: bool = False
    duck_gain_db: float | None = None
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.selection_id.strip():
            raise ValueError("selection_id must not be empty")
        if self.source_audio_policy is SourceAudioPolicy.DUCK:
            if self.duck_gain_db is None:
                raise ValueError("DUCK source treatment requires an explicit duck_gain_db")
        elif self.duck_gain_db is not None:
            raise ValueError("duck_gain_db is valid only for DUCK source treatment")
        if self.duck_gain_db is not None:
            if isinstance(self.duck_gain_db, bool) or not isinstance(
                self.duck_gain_db, (int, float)
            ):
                raise TypeError("duck_gain_db must be a number or None")
            if not math.isfinite(float(self.duck_gain_db)) or self.duck_gain_db > 0:
                raise ValueError("duck_gain_db must be finite and <= 0")


class AudioAutomationKind(StrEnum):
    GAIN = "gain"
    DUCK = "duck"
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    CROSSFADE = "crossfade"


class AudioTrackRole(StrEnum):
    SOURCE = "source"
    BGM = "bgm"
    VOICEOVER = "voiceover"
    SFX = "sfx"


@dataclass(frozen=True, slots=True)
class AudioAutomationIntent:
    kind: AudioAutomationKind
    target_asset_ref: EntityRevisionRef
    target_slot_ids: tuple[str, ...]
    gain_db: float | None = None
    evidence_refs: tuple[str, ...] = ()
    reason: str | None = None
    start: MediaTime | None = None
    end: MediaTime | None = None
    target_role: AudioTrackRole | None = None

    def __post_init__(self) -> None:
        if any(not value.strip() for value in self.target_slot_ids):
            raise ValueError("target_slot_ids must contain non-empty slot identifiers")
        if not self.target_slot_ids and self.target_role is None:
            raise ValueError("automation requires a track role or real EditSlot IDs")
        if self.target_slot_ids and self.target_role is not None:
            raise ValueError("track role and EditSlot targets are mutually exclusive")
        if self.gain_db is not None:
            if isinstance(self.gain_db, bool) or not isinstance(self.gain_db, (int, float)):
                raise TypeError("gain_db must be a number or None")
            if not math.isfinite(float(self.gain_db)):
                raise ValueError("gain_db must be finite")
        if (self.start is None) != (self.end is None):
            raise ValueError("automation start/end must both be present or absent")
        if self.start is not None and self.end is not None:
            if self.start.as_fraction() < 0 or self.end.as_fraction() <= self.start.as_fraction():
                raise ValueError("automation range must be positive and ordered")


@dataclass(frozen=True, slots=True)
class AudioEditorialRequest:
    edit_plan_ref: EntityRevisionRef
    music_selection_decision_id: str | None = None
    source_audio_asset_refs: tuple[EntityRevisionRef, ...] = ()
    voiceover_asset_refs: tuple[EntityRevisionRef, ...] = ()
    sound_effect_asset_refs: tuple[EntityRevisionRef, ...] = ()
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AudioMixDecision:
    decision_id: str
    edit_plan_ref: EntityRevisionRef
    source_audio_policy: SourceAudioPolicy
    automation_intents: tuple[AudioAutomationIntent, ...] = ()
    loudness_intent: str | None = None
    confidence: float = 1.0
    warnings: tuple[str, ...] = ()
    source_treatments: tuple[SourceAudioTreatment, ...] = ()

    def __post_init__(self) -> None:
        if not self.decision_id.strip():
            raise ValueError("decision_id must not be empty")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise TypeError("confidence must be a number")
        value = float(self.confidence)
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError("confidence must be finite and between 0 and 1")


class AudioEditorialService(Protocol):
    """Own audio-mix intent; EDLBuilder owns exact timeline automation."""

    def plan(self, request: AudioEditorialRequest) -> AudioMixDecision: ...

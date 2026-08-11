from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime


def _require_nonempty(name: str, value: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} must not be empty")


def _require_optional_nonempty(name: str, value: str | None) -> None:
    if value is not None:
        _require_nonempty(name, value)


@dataclass(frozen=True, slots=True)
class NarrativeSection:
    section_id: str
    narrative_role: str
    information_goal: str
    spoken_content: str | None = None
    visual_requirement: str | None = None
    target_duration: MediaTime | None = None
    on_screen_text_intent: str | None = None
    emotion: str | None = None
    pacing: str | None = None
    music_intent: str | None = None
    editing_intent: str | None = None
    importance: str | None = None
    protected_fact_ids: tuple[str, ...] = ()
    locked: bool = False

    def __post_init__(self) -> None:
        _require_nonempty("section_id", self.section_id)
        _require_nonempty("narrative_role", self.narrative_role)
        _require_nonempty("information_goal", self.information_goal)
        for name, value in (
            ("spoken_content", self.spoken_content),
            ("visual_requirement", self.visual_requirement),
            ("on_screen_text_intent", self.on_screen_text_intent),
            ("emotion", self.emotion),
            ("pacing", self.pacing),
            ("music_intent", self.music_intent),
            ("editing_intent", self.editing_intent),
            ("importance", self.importance),
        ):
            _require_optional_nonempty(name, value)
        if self.target_duration is not None and self.target_duration.value <= 0:
            raise ValueError("target_duration must be > 0")
        if any(not fact_id.strip() for fact_id in self.protected_fact_ids):
            raise ValueError("protected_fact_ids must not contain empty values")
        if len(set(self.protected_fact_ids)) != len(self.protected_fact_ids):
            raise ValueError("protected_fact_ids must not contain duplicates")


@dataclass(frozen=True, slots=True)
class ScriptPlan:
    envelope: EntityEnvelope
    brief_ref: EntityRevisionRef
    sections: tuple[NarrativeSection, ...] = ()

    def __post_init__(self) -> None:
        section_ids = tuple(section.section_id for section in self.sections)
        if len(set(section_ids)) != len(section_ids):
            raise ValueError("sections must have unique section_id values")

    @property
    def locked_section_ids(self) -> tuple[str, ...]:
        return tuple(section.section_id for section in self.sections if section.locked)

    @property
    def estimated_duration(self) -> MediaTime | None:
        if not self.sections or any(section.target_duration is None for section in self.sections):
            return None
        result = MediaTime(0, 1)
        for section in self.sections:
            assert section.target_duration is not None
            result = result + section.target_duration
        return result

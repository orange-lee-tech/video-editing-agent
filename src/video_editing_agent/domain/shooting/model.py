from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime


def _require_nonempty(name: str, value: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} must not be empty")


def _require_optional_nonempty(name: str, value: str | None) -> None:
    if value is not None:
        _require_nonempty(name, value)


def _require_time(name: str, value: MediaTime | None, *, allow_zero: bool = False) -> None:
    if value is None:
        return
    minimum = 0 if allow_zero else 1
    if value.value < minimum:
        operator = ">=" if allow_zero else ">"
        raise ValueError(f"{name} must be {operator} 0")


class CoveragePriority(StrEnum):
    REQUIRED = "required"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"
    BACKUP = "backup"


@dataclass(frozen=True, slots=True)
class ProductionLocation:
    """User-authorized production location identity; label/notes are descriptive only."""

    location_id: str
    label: str
    notes: str | None = None

    def __post_init__(self) -> None:
        _require_nonempty("location_id", self.location_id)
        _require_nonempty("label", self.label)
        _require_optional_nonempty("notes", self.notes)


@dataclass(frozen=True, slots=True)
class ProductionConstraints:
    camera_or_phone: str | None = None
    stabilizer: str | None = None
    lighting: str | None = None
    microphones: tuple[str, ...] = ()
    people_count: int | None = None
    locations: tuple[ProductionLocation, ...] = ()
    available_time_notes: str | None = None
    user_skill_level: str | None = None
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("camera_or_phone", self.camera_or_phone),
            ("stabilizer", self.stabilizer),
            ("lighting", self.lighting),
            ("available_time_notes", self.available_time_notes),
            ("user_skill_level", self.user_skill_level),
        ):
            _require_optional_nonempty(name, value)
        if self.people_count is not None:
            if isinstance(self.people_count, bool) or not isinstance(self.people_count, int):
                raise TypeError("people_count must be an int or None")
            if self.people_count < 0:
                raise ValueError("people_count must be >= 0")
        for name, values in (
            ("microphones", self.microphones),
            ("notes", self.notes),
        ):
            if any(not value.strip() for value in values):
                raise ValueError(f"{name} must not contain empty values")

        normalized_locations: list[ProductionLocation] = []
        for index, location in enumerate(self.locations):
            if isinstance(location, str):
                # R0.7B migration shim for pre-identity callers/persisted v1 payloads.
                normalized_locations.append(
                    ProductionLocation(
                        location_id=f"loc_legacy_{index + 1:03d}",
                        label=location,
                    )
                )
            elif isinstance(location, ProductionLocation):
                normalized_locations.append(location)
            else:
                raise TypeError("locations must contain ProductionLocation values")
        location_ids = tuple(location.location_id for location in normalized_locations)
        if len(set(location_ids)) != len(location_ids):
            raise ValueError("locations must have unique location_id values")
        object.__setattr__(self, "locations", tuple(normalized_locations))


@dataclass(frozen=True, slots=True)
class ShotRequirement:
    requirement_id: str
    script_section_ref: str
    purpose: str
    subject: str
    action: str | None = None
    location_ref: str | None = None
    environment_description: str | None = None
    framing: str | None = None
    camera_motion: str | None = None
    target_duration: MediaTime | None = None
    minimum_duration: MediaTime | None = None
    audio_dialogue_requirement: str | None = None
    continuity_hint: str | None = None
    visual_constraints: tuple[str, ...] = ()
    priority: CoveragePriority = CoveragePriority.RECOMMENDED
    backup_intent: str | None = None
    capture_instruction: str | None = None
    alternate_coverage: tuple[str, ...] = ()
    handle_before: MediaTime | None = None
    handle_after: MediaTime | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("requirement_id", self.requirement_id),
            ("script_section_ref", self.script_section_ref),
            ("purpose", self.purpose),
            ("subject", self.subject),
        ):
            _require_nonempty(name, value)
        for optional_name, optional_value in (
            ("action", self.action),
            ("location_ref", self.location_ref),
            ("environment_description", self.environment_description),
            ("framing", self.framing),
            ("camera_motion", self.camera_motion),
            ("audio_dialogue_requirement", self.audio_dialogue_requirement),
            ("continuity_hint", self.continuity_hint),
            ("backup_intent", self.backup_intent),
            ("capture_instruction", self.capture_instruction),
        ):
            _require_optional_nonempty(optional_name, optional_value)
        _require_time("target_duration", self.target_duration)
        _require_time("minimum_duration", self.minimum_duration)
        _require_time("handle_before", self.handle_before, allow_zero=True)
        _require_time("handle_after", self.handle_after, allow_zero=True)
        if (
            self.target_duration is not None
            and self.minimum_duration is not None
            and self.target_duration.as_fraction() < self.minimum_duration.as_fraction()
        ):
            raise ValueError("target_duration cannot be shorter than minimum_duration")
        for name, values in (
            ("visual_constraints", self.visual_constraints),
            ("alternate_coverage", self.alternate_coverage),
        ):
            if any(not value.strip() for value in values):
                raise ValueError(f"{name} must not contain empty values")


@dataclass(frozen=True, slots=True)
class ShootingPlan:
    envelope: EntityEnvelope
    script_plan_ref: EntityRevisionRef
    requirements: tuple[ShotRequirement, ...]
    constraints: ProductionConstraints = field(default_factory=ProductionConstraints)
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        requirement_ids = tuple(requirement.requirement_id for requirement in self.requirements)
        if len(set(requirement_ids)) != len(requirement_ids):
            raise ValueError("requirements must have unique requirement_id values")
        if any(not note.strip() for note in self.notes):
            raise ValueError("notes must not contain empty values")
        location_ids = {location.location_id for location in self.constraints.locations}
        for requirement in self.requirements:
            if requirement.location_ref is not None and requirement.location_ref not in location_ids:
                raise ValueError(
                    f"ShotRequirement {requirement.requirement_id!r} references unknown production "
                    f"location {requirement.location_ref!r}"
                )

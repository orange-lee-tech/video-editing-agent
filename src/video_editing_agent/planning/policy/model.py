from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


def _require_nonempty(name: str, value: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} must not be empty")


def _require_unique_ids(name: str, values: tuple[CreativePrior, ...]) -> None:
    ids = tuple(value.prior_id for value in values)
    if len(set(ids)) != len(ids):
        raise ValueError(f"{name} must have unique prior_id values")


class MarketingObjective(StrEnum):
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    CONVERSION = "conversion"
    MIXED = "mixed"


@dataclass(frozen=True, slots=True)
class PlatformProfile:
    profile_id: str
    version: str
    platform_family: str
    output_context: str
    aspect_ratio: tuple[int, int] | None = None
    technical_constraints: tuple[str, ...] = ()
    creative_guidance: tuple[str, ...] = ()
    evidence_notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("profile_id", self.profile_id),
            ("version", self.version),
            ("platform_family", self.platform_family),
            ("output_context", self.output_context),
        ):
            _require_nonempty(name, value)
        if self.aspect_ratio is not None:
            width, height = self.aspect_ratio
            if width <= 0 or height <= 0:
                raise ValueError("aspect_ratio values must be > 0")
        for name, values in (
            ("technical_constraints", self.technical_constraints),
            ("creative_guidance", self.creative_guidance),
            ("evidence_notes", self.evidence_notes),
        ):
            if any(not value.strip() for value in values):
                raise ValueError(f"{name} must not contain empty values")


@dataclass(frozen=True, slots=True)
class CreativePrior:
    prior_id: str
    guidance: str

    def __post_init__(self) -> None:
        _require_nonempty("prior_id", self.prior_id)
        _require_nonempty("guidance", self.guidance)


@dataclass(frozen=True, slots=True)
class CommercialSkill:
    skill_id: str
    version: str
    genre: str
    creative_priors: tuple[CreativePrior, ...]
    review_dimensions: tuple[str, ...]
    supported_objectives: tuple[MarketingObjective, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("skill_id", self.skill_id),
            ("version", self.version),
            ("genre", self.genre),
        ):
            _require_nonempty(name, value)
        if not self.creative_priors:
            raise ValueError("creative_priors must not be empty")
        if not self.review_dimensions:
            raise ValueError("review_dimensions must not be empty")
        _require_unique_ids("creative_priors", self.creative_priors)
        if any(not value.strip() for value in self.review_dimensions):
            raise ValueError("review_dimensions must not contain empty values")
        if len(set(self.supported_objectives)) != len(self.supported_objectives):
            raise ValueError("supported_objectives must not contain duplicates")


@dataclass(frozen=True, slots=True)
class CommercialPolicySelection:
    platform_profile: PlatformProfile
    skill: CommercialSkill
    marketing_objective: MarketingObjective | None = None

    def __post_init__(self) -> None:
        if (
            self.marketing_objective is not None
            and self.skill.supported_objectives
            and self.marketing_objective not in self.skill.supported_objectives
        ):
            raise ValueError(
                f"skill {self.skill.skill_id!r} does not support objective "
                f"{self.marketing_objective.value!r}"
            )

    def provider_guidance(self) -> tuple[str, ...]:
        objective_guidance = (
            ()
            if self.marketing_objective is None
            else (f"Marketing objective: {self.marketing_objective.value}.",)
        )
        return (
            *self.platform_profile.technical_constraints,
            *self.platform_profile.creative_guidance,
            *(prior.guidance for prior in self.skill.creative_priors),
            *objective_guidance,
        )

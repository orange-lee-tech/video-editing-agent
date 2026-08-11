from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from video_editing_agent.domain.common.entity import EntityRevisionRef


def _require_text(name: str, value: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} must not be empty")


class RightsEligibility(StrEnum):
    """Product gate assessment, not a legal certification."""

    ELIGIBLE = "eligible"
    WARNING = "warning"
    INELIGIBLE = "ineligible"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class RightsAttestation:
    """User assertion that required rights exist for an exact Asset revision."""

    attestation_id: str
    asset_ref: EntityRevisionRef
    asserted_by: str
    asserted_at: datetime
    statement: str

    def __post_init__(self) -> None:
        _require_text("attestation_id", self.attestation_id)
        _require_text("asserted_by", self.asserted_by)
        _require_text("statement", self.statement)


@dataclass(frozen=True, slots=True)
class LicenseSnapshot:
    """Evidence snapshot relied upon for a provider/library audio candidate."""

    snapshot_id: str
    provider: str
    provider_item_id: str
    captured_at: datetime
    eligibility: RightsEligibility
    license_identifier: str | None = None
    terms_ref: str | None = None
    attribution_text: str | None = None
    commercial_scope: str | None = None
    advertising_scope: str | None = None
    platform_scope: str | None = None
    territory: str | None = None
    expires_at: datetime | None = None
    evidence_artifact_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_text("snapshot_id", self.snapshot_id)
        _require_text("provider", self.provider)
        _require_text("provider_item_id", self.provider_item_id)
        if any(not value.strip() for value in self.evidence_artifact_refs):
            raise ValueError("evidence_artifact_refs must not contain blank values")


@dataclass(frozen=True, slots=True)
class ManualLicenseOverride:
    """Explicit user override when the system cannot independently verify a right."""

    override_id: str
    asset_ref: EntityRevisionRef
    asserted_by: str
    asserted_at: datetime
    reason: str

    def __post_init__(self) -> None:
        _require_text("override_id", self.override_id)
        _require_text("asserted_by", self.asserted_by)
        _require_text("reason", self.reason)

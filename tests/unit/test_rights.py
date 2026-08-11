from datetime import UTC, datetime

import pytest

from video_editing_agent.domain.asset.rights import (
    LicenseSnapshot,
    ManualLicenseOverride,
    RightsAttestation,
    RightsEligibility,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef

NOW = datetime(2026, 8, 11, 2, 0, tzinfo=UTC)
ASSET_REF = EntityRevisionRef("ast_rights", 1)


def test_rights_attestation_records_user_claim_without_certification() -> None:
    value = RightsAttestation(
        attestation_id="att_1",
        asset_ref=ASSET_REF,
        asserted_by="user",
        asserted_at=NOW,
        statement="I hold the required commercial usage rights.",
    )

    assert value.asset_ref == ASSET_REF


def test_license_snapshot_keeps_unknown_as_unknown() -> None:
    value = LicenseSnapshot(
        snapshot_id="lic_1",
        provider="example",
        provider_item_id="track_1",
        captured_at=NOW,
        eligibility=RightsEligibility.UNKNOWN,
    )

    assert value.eligibility is RightsEligibility.UNKNOWN
    assert value.terms_ref is None


def test_manual_override_requires_a_reason() -> None:
    with pytest.raises(ValueError, match="reason"):
        ManualLicenseOverride(
            override_id="ovr_1",
            asset_ref=ASSET_REF,
            asserted_by="user",
            asserted_at=NOW,
            reason=" ",
        )

from datetime import UTC, datetime

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.shot.model import Shot


def test_shot_duration_is_derived_from_boundaries() -> None:
    shot = Shot(
        envelope=EntityEnvelope(
            id="sht_test",
            revision=1,
            schema_version="0.1.1",
            status=EntityStatus.VALID,
            created_at=datetime.now(UTC),
            created_by="test",
        ),
        asset_ref=EntityRevisionRef("ast_test", 1),
        source_start_ms=1_000,
        source_end_ms=2_750,
        boundary_method="test",
    )

    assert shot.duration_ms == 1_750

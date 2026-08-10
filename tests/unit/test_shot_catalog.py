from datetime import UTC, datetime

import pytest

from video_editing_agent.application.ports.shot_detector import ShotBoundaryProposal
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.media.shot_detection.catalog import ShotCatalog


class SequentialIds:
    def __init__(self) -> None:
        self._index = 0

    def __call__(self) -> str:
        self._index += 1
        return f"sht_{self._index}"


def proposal(start: int, end: int, *, asset_id: str = "ast_1") -> ShotBoundaryProposal:
    return ShotBoundaryProposal(
        asset_ref=EntityRevisionRef(asset_id, 1),
        source_start_ms=start,
        source_end_ms=end,
        detection_method="transnetv2-pytorch:1.0.5",
    )


def test_catalog_commits_contiguous_proposals_with_neighbor_refs() -> None:
    now = datetime(2026, 8, 10, 7, 45, tzinfo=UTC)
    catalog = ShotCatalog(shot_id_factory=SequentialIds(), clock=lambda: now)

    shots = catalog.commit_boundaries(
        (proposal(0, 1_000), proposal(1_000, 2_000), proposal(2_000, 3_000))
    )

    assert [shot.envelope.id for shot in shots] == ["sht_1", "sht_2", "sht_3"]
    assert [shot.duration_ms for shot in shots] == [1_000, 1_000, 1_000]
    assert shots[0].previous_shot_ref is None
    assert shots[0].next_shot_ref == EntityRevisionRef("sht_2", 1)
    assert shots[1].previous_shot_ref == EntityRevisionRef("sht_1", 1)
    assert shots[1].next_shot_ref == EntityRevisionRef("sht_3", 1)
    assert shots[2].previous_shot_ref == EntityRevisionRef("sht_2", 1)
    assert shots[2].next_shot_ref is None
    assert all(shot.envelope.created_at == now for shot in shots)
    assert all(shot.boundary_method == "transnetv2-pytorch:1.0.5" for shot in shots)


def test_catalog_rejects_gap_or_overlap() -> None:
    catalog = ShotCatalog(shot_id_factory=SequentialIds())

    with pytest.raises(ValueError, match="contiguous"):
        catalog.commit_boundaries((proposal(0, 1_000), proposal(1_100, 2_000)))


def test_catalog_rejects_mixed_asset_revisions() -> None:
    catalog = ShotCatalog(shot_id_factory=SequentialIds())

    with pytest.raises(ValueError, match="same Asset"):
        catalog.commit_boundaries((proposal(0, 1_000), proposal(1_000, 2_000, asset_id="ast_2")))


def test_catalog_requires_first_boundary_at_zero() -> None:
    catalog = ShotCatalog(shot_id_factory=SequentialIds())

    with pytest.raises(ValueError, match="source time 0"):
        catalog.commit_boundaries((proposal(100, 1_000),))

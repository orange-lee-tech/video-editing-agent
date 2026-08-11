from __future__ import annotations

import uuid
from collections.abc import Callable, Iterable
from datetime import UTC, datetime

from video_editing_agent.application.ports.shot_detector import ShotBoundaryProposal
from video_editing_agent.application.ports.shot_repository import ShotPersistenceRepository
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.shot.model import Shot

SHOT_SCHEMA_VERSION = "0.1.1"


def _default_shot_id() -> str:
    return f"sht_{uuid.uuid4().hex}"


def _utc_now() -> datetime:
    return datetime.now(UTC)


class ShotCatalog:
    """Commit validated detector proposals into authoritative Shot identity."""

    def __init__(
        self,
        *,
        repository: ShotPersistenceRepository | None = None,
        shot_id_factory: Callable[[], str] = _default_shot_id,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._repository = repository
        self._shot_id_factory = shot_id_factory
        self._clock = clock

    def commit_boundaries(
        self,
        proposals: Iterable[ShotBoundaryProposal],
        *,
        created_by: str = "system",
    ) -> tuple[Shot, ...]:
        ordered = tuple(proposals)
        if not ordered:
            return ()

        asset_ref = ordered[0].asset_ref
        if any(proposal.asset_ref != asset_ref for proposal in ordered):
            raise ValueError(
                "all ShotBoundaryProposal values must reference the same Asset revision"
            )
        if ordered[0].source_range.start != MediaTime(0, 1):
            raise ValueError("the first shot boundary must start at source time 0")

        for previous, current in zip(ordered, ordered[1:], strict=False):
            if current.source_range.start != previous.source_range.end:
                raise ValueError("shot boundaries must be ordered, contiguous, and non-overlapping")

        shot_ids = tuple(self._shot_id_factory() for _ in ordered)
        if any(not shot_id.startswith("sht_") for shot_id in shot_ids):
            raise ValueError("shot_id_factory must return sht_* identifiers")
        if len(set(shot_ids)) != len(shot_ids):
            raise ValueError("shot_id_factory must return unique identifiers")

        created_at = self._clock()
        shots: list[Shot] = []
        for index, proposal in enumerate(ordered):
            previous_ref = EntityRevisionRef(shot_ids[index - 1], 1) if index > 0 else None
            next_ref = (
                EntityRevisionRef(shot_ids[index + 1], 1) if index + 1 < len(shot_ids) else None
            )
            shots.append(
                Shot(
                    envelope=EntityEnvelope(
                        id=shot_ids[index],
                        revision=1,
                        schema_version=SHOT_SCHEMA_VERSION,
                        status=EntityStatus.VALID,
                        created_at=created_at,
                        created_by=created_by,
                    ),
                    asset_ref=asset_ref,
                    source_range=proposal.source_range,
                    boundary_method=proposal.detection_method,
                    previous_shot_ref=previous_ref,
                    next_shot_ref=next_ref,
                )
            )

        committed = tuple(shots)
        if self._repository is not None:
            self._repository.save_many(committed)
        return committed

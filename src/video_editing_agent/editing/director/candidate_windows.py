from __future__ import annotations

import hashlib
from dataclasses import dataclass

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTimeRange
from video_editing_agent.domain.edit.model import EditSlot
from video_editing_agent.domain.edit.resolution import CandidateWindow
from video_editing_agent.domain.evidence.temporal import TemporalAnchor, TemporalEvidence
from video_editing_agent.domain.shot.model import Shot


@dataclass(frozen=True, slots=True)
class SlotCandidateWindow:
    slot_id: str
    window: CandidateWindow
    policy_version: str


def generate_candidate_windows(
    slot: EditSlot,
    shot: Shot,
    anchors: tuple[TemporalAnchor, ...],
    evidence: tuple[TemporalEvidence, ...],
) -> tuple[SlotCandidateWindow, ...]:
    shot_ref = EntityRevisionRef(shot.envelope.id, shot.envelope.revision)
    if any(x.shot_ref != shot_ref for x in anchors) or any(
        x.shot_ref != shot_ref for x in evidence
    ):
        raise ValueError("candidate evidence must belong to exact Shot")
    if slot.target_duration is None:
        return ()
    duration = slot.target_duration.maximum
    found = []
    for anchor in sorted(anchors, key=lambda x: (x.source_time.as_fraction(), x.anchor_id)):
        start = anchor.source_time
        if start.as_fraction() < shot.source_range.start.as_fraction():
            continue
        if (start + duration).as_fraction() > shot.source_range.end.as_fraction():
            start = shot.source_range.end - duration
        if start.as_fraction() < shot.source_range.start.as_fraction():
            continue
        source_range = MediaTimeRange(start, duration)
        refs = tuple(sorted(anchor.evidence_refs))
        digest = hashlib.sha256(
            f"{slot.slot_id}:{shot_ref}:{source_range}:{anchor.anchor_id}:r0.9a-v1".encode()
        ).hexdigest()
        found.append(
            SlotCandidateWindow(
                slot.slot_id,
                CandidateWindow(
                    f"cwin_{digest}",
                    shot_ref,
                    source_range,
                    anchor.confidence,
                    anchor.anchor_id,
                    None,
                    (),
                    refs,
                ),
                "r0.9a-v1",
            )
        )
    return tuple(found[:3])

from __future__ import annotations

import json
from datetime import UTC, datetime

from video_editing_agent.application.edl_builder import (
    DeterministicEDLBuilder,
    EDLBuildDiagnosticCode,
    EDLBuildRequest,
)
from video_editing_agent.domain.common.entity import (
    EntityEnvelope,
    EntityRevisionRef,
    EntityStatus,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.model import EditPlan, EditSlot
from video_editing_agent.domain.edit.resolution import (
    ResolutionDecision,
    ResolutionDecisionType,
    ResolvedSelection,
)
from video_editing_agent.domain.edl import decode_edl, encode_edl, validate_edl
from video_editing_agent.domain.shot.model import Shot

NOW = datetime(2026, 8, 16, tzinfo=UTC)


def _envelope(identity: str) -> EntityEnvelope:
    return EntityEnvelope(identity, 1, "0.2", EntityStatus.VALID, NOW, "r0.12-probe")


def main() -> int:
    plan = EditPlan(
        _envelope("edit-plan"),
        EntityRevisionRef("script", 1),
        EntityRevisionRef("shooting", 1),
        (EditSlot("opening", "open", 0), EditSlot("proof", "prove", 1)),
    )
    decisions = tuple(
        ResolutionDecision(
            f"resolution-{index}",
            EntityRevisionRef("edit-plan", 1),
            (slot_id,),
            ResolutionDecisionType.RESOLVED,
            (
                ResolvedSelection(
                    f"selection-{index}",
                    EntityRevisionRef(f"shot-{index}", 1),
                    source_range,
                    0,
                ),
            ),
        )
        for index, (slot_id, source_range) in enumerate(
            (
                ("opening", MediaTimeRange(MediaTime(1, 24), MediaTime(1, 2))),
                ("proof", MediaTimeRange(MediaTime(2, 1), MediaTime(3, 4))),
            )
        )
    )
    shots = tuple(
        Shot(
            _envelope(f"shot-{index}"),
            EntityRevisionRef(f"asset-{index}", 1),
            boundary_method="probe",
            source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(4, 1)),
        )
        for index in range(2)
    )
    builder = DeterministicEDLBuilder()
    request = EDLBuildRequest(_envelope("edl"), plan, decisions, shots)
    built = builder.build(request)
    reordered = builder.build(
        EDLBuildRequest(
            request.envelope,
            plan,
            tuple(reversed(decisions)),
            tuple(reversed(shots)),
        )
    )
    incomplete = builder.build(EDLBuildRequest(request.envelope, plan, decisions[:1], shots))
    assert built.edl is not None and reordered.edl is not None
    encoded = encode_edl(built.edl)
    ranges = tuple(item.timeline_range for item in built.edl.ordered_segments)
    gates = {
        "APPROVED_DECISIONS_ASSEMBLED": built.is_built,
        "EXACT_CONTIGUOUS_ALLOCATION": ranges
        == (
            MediaTimeRange(MediaTime(0, 1), MediaTime(1, 2)),
            MediaTimeRange(MediaTime(1, 2), MediaTime(3, 4)),
        ),
        "INPUT_ORDER_INDEPENDENT": encode_edl(reordered.edl) == encoded,
        "CANONICAL_VALIDATION": validate_edl(built.edl).is_valid,
        "DETERMINISTIC_ROUND_TRIP": encode_edl(decode_edl(encoded)) == encoded,
        "INCOMPLETE_INPUT_STRUCTURED": incomplete.edl is None
        and EDLBuildDiagnosticCode.MISSING_SLOT_COVERAGE
        in {item.code for item in incomplete.diagnostics},
    }
    report = {
        "classification": "ENGINEERING_FOUNDATION_ONLY",
        "gates": {name: "PASS" if passed else "FAIL" for name, passed in gates.items()},
        "timeline_ranges": [
            {
                "start": [item.start.value, item.start.scale],
                "duration": [item.duration.value, item.duration.scale],
            }
            for item in ranges
        ],
        "pass": all(gates.values()),
    }
    print(json.dumps(report, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

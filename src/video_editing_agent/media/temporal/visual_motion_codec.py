from __future__ import annotations

import json
import math
from typing import Any

from video_editing_agent.application.ports.visual_motion import (
    VisualMotionMeasurement,
    VisualMotionProposal,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange

SCHEMA_VERSION_V1 = "r0.8c-visual-motion-v1"
SCHEMA_VERSION = "r0.8e-visual-motion-v2"


def _time(value: MediaTime) -> dict[str, int]:
    return {"value": value.value, "scale": value.scale}


def encode_visual_motion(proposal: VisualMotionProposal) -> bytes:
    if proposal.analyzed_source_range is None:
        raise ValueError("v2 visual motion Artifact requires analyzed_source_range")
    measurements = []
    for item in proposal.measurements:
        values = {
            name: getattr(item, name)
            for name in item.__dataclass_fields__
            if name != "relative_range"
        }
        values["relative_range"] = {
            "start": _time(item.relative_range.start),
            "duration": _time(item.relative_range.duration),
        }
        measurements.append(values)
    root = {
        "schema_version": SCHEMA_VERSION,
        "proposal": {
            "shot_ref": {
                "entity_id": proposal.shot_ref.entity_id,
                "revision": proposal.shot_ref.revision,
            },
            "provider_id": proposal.provider_id,
            "provider_revision": proposal.provider_revision,
            "frames_per_second": proposal.frames_per_second,
            "width": proposal.width,
            "height": proposal.height,
            "measurements": measurements,
            "analyzed_source_range": {
                "start": _time(proposal.analyzed_source_range.start),
                "duration": _time(proposal.analyzed_source_range.duration),
            },
        },
    }
    return json.dumps(root, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def decode_visual_motion(content: bytes) -> VisualMotionProposal:
    root: dict[str, Any] = json.loads(content)
    schema = root.get("schema_version")
    if schema not in (SCHEMA_VERSION_V1, SCHEMA_VERSION):
        raise ValueError("unsupported visual motion artifact schema")
    value = root["proposal"]
    shot = value["shot_ref"]
    items = []
    for raw in value["measurements"]:
        interval = raw.pop("relative_range")
        item = VisualMotionMeasurement(
            relative_range=MediaTimeRange(
                MediaTime(**interval["start"]), MediaTime(**interval["duration"])
            ),
            **raw,
        )
        for field in item.__dataclass_fields__:
            number = getattr(item, field)
            if isinstance(number, float) and not math.isfinite(number):
                raise ValueError("visual motion artifact contains non-finite measurement")
        items.append(item)
    analyzed = value.get("analyzed_source_range")
    proposal = VisualMotionProposal(
        EntityRevisionRef(shot["entity_id"], shot["revision"]),
        value["provider_id"],
        value["provider_revision"],
        value["frames_per_second"],
        value["width"],
        value["height"],
        tuple(items),
        None
        if analyzed is None
        else MediaTimeRange(MediaTime(**analyzed["start"]), MediaTime(**analyzed["duration"])),
    )
    if not proposal.provider_id.strip() or not proposal.provider_revision.strip():
        raise ValueError("visual motion artifact provider identity is empty")
    return proposal

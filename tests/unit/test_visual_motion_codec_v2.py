from __future__ import annotations

import json
from dataclasses import replace

import pytest
from test_visual_motion_foundation import SHOT, _measurement

from video_editing_agent.application.ports.visual_motion import VisualMotionProposal
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.media.temporal.visual_motion_codec import (
    SCHEMA_VERSION,
    decode_visual_motion,
    encode_visual_motion,
)


def _proposal() -> VisualMotionProposal:
    return VisualMotionProposal(
        SHOT,
        "provider",
        "r1",
        30,
        320,
        180,
        (_measurement(),),
        MediaTimeRange(MediaTime(7, 2), MediaTime(1, 1)),
    )


def test_v2_round_trip_persists_exact_analyzed_source_range() -> None:
    encoded = encode_visual_motion(_proposal())
    assert json.loads(encoded)["schema_version"] == SCHEMA_VERSION
    assert decode_visual_motion(encoded) == _proposal()


def test_v1_remains_readable_and_unknown_schema_fails_closed() -> None:
    root = json.loads(encode_visual_motion(_proposal()))
    root["schema_version"] = "r0.8c-visual-motion-v1"
    del root["proposal"]["analyzed_source_range"]
    legacy = decode_visual_motion(json.dumps(root).encode())
    assert legacy.analyzed_source_range is None
    root["schema_version"] = "future-v99"
    with pytest.raises(ValueError, match="unsupported"):
        decode_visual_motion(json.dumps(root).encode())


def test_v2_write_requires_range_and_decode_rejects_non_finite() -> None:
    with pytest.raises(ValueError, match="requires analyzed"):
        encode_visual_motion(replace(_proposal(), analyzed_source_range=None))
    root = json.loads(encode_visual_motion(_proposal()))
    root["proposal"]["measurements"][0]["residual_p95"] = float("nan")
    with pytest.raises(ValueError, match="non-finite"):
        decode_visual_motion(json.dumps(root).encode())

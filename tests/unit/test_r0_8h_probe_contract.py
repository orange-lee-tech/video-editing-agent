from __future__ import annotations

import pathlib


def test_closure_probe_has_every_named_product_gate() -> None:
    source = (
        pathlib.Path(__file__).resolve().parents[2] / "tools" / "probes" / "r0_8h_closure_live.py"
    ).read_text(encoding="utf-8")
    for gate in (
        "REAL_FOOTAGE_SOURCE_TIME",
        "SPEECH_TIMESTAMP_USEFULNESS",
        "SPEECH_CUT_QUALITY",
        "PAN_FALSE_LOCAL_ACTION",
        "LOCAL_ACTION_RECALL",
        "LOW_MOTION_FALSE_POSITIVE",
        "NOISY_BLURRED_FAIL_SAFE",
        "TRACKING_REAL_FOOTAGE",
        "RETRIEVAL_REAL_PROJECT_SANITY",
        "R0_8_RESTART_PROVENANCE",
    ):
        assert f'"{gate}"' in source

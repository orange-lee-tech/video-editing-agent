from __future__ import annotations

import ast
import pathlib

PROBE = pathlib.Path(__file__).parents[2] / "tools" / "probes" / "r0_9_product_probe.py"
DENSE_PROBE = PROBE.with_name("r0_9_product_dense_live.py")


def test_product_probe_does_not_construct_retrieval_or_window_answers() -> None:
    tree = ast.parse(PROBE.read_text(encoding="utf-8"))
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "CandidateWindow" not in calls
    assert "ShotCandidate" not in calls


def test_product_probe_uses_real_pipeline_owners() -> None:
    source = PROBE.read_text(encoding="utf-8") + DENSE_PROBE.read_text(encoding="utf-8")
    for owner in (
        "LexicalShotIndex",
        "reciprocal_rank_fusion",
        "VisualMotionEvidenceService",
        "VisualMotionEventService",
        "generate_candidate_windows",
        "optimize_sequence",
    ):
        assert owner in source

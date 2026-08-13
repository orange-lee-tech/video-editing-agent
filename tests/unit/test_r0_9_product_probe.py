import importlib.util
import pathlib
import sys

_path = pathlib.Path(__file__).parents[2] / "tools" / "probes" / "r0_9_product_probe.py"
_spec = importlib.util.spec_from_file_location("r0_9_product_probe", _path)
assert _spec is not None and _spec.loader is not None
_probe = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _probe
_spec.loader.exec_module(_probe)
run_comparison = _probe.run_comparison


def test_product_comparison_has_same_recall_but_improves_action_rank() -> None:
    comparison = run_comparison()
    assert comparison.report["recall"] == {"lexical_only": 1.0, "hybrid": 1.0}
    assert comparison.report["rank_change"]["action_shot"] == {"lexical": 2, "hybrid": 1}
    assert comparison.report["pass"] is True


def test_product_comparison_is_deterministic_and_grounded() -> None:
    first = run_comparison()
    second = run_comparison()
    assert first.ranges == second.ranges
    assert first.report["variants"] == second.report["variants"]
    assert first.report["resolver"] == second.report["resolver"]
    assert first.report["gates"]["EXPLICIT_UNRESOLVED"] == "PASS"

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[2] / "tools/maintenance/foreman.py"
SPEC = importlib.util.spec_from_file_location("foreman_under_test", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
FOREMAN = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = FOREMAN
SPEC.loader.exec_module(FOREMAN)
BRIEF_PATH = FOREMAN.BRIEF_PATH
build_foreman_brief = FOREMAN.build_foreman_brief
write_foreman_brief = FOREMAN.write_foreman_brief

TEST_BRANCH = "work/test-wave"
TEST_WAVE = "docs/operations/TEST_WAVE.md"


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


def _control(
    *,
    phase: str = "R0.12",
    work_order: str = "CONTROL-PLANE-002",
    branch: str = TEST_BRANCH,
) -> str:
    return f"""# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-22
current_phase: {phase}
phase_state: TEST_ACTIVE
active_work_order: {work_order}
active_construction_branch: {branch}
accepted_code_baseline: {"0" * 40}
codex_release: OPEN_TEST_ONLY
writer: chatgpt
---
"""


def _work(*, phase: str = "R0.12", identity: str = "CONTROL-PLANE-002") -> str:
    return f"""# Current Work Order

**ID:** `{identity}`
**Status:** ACTIVE
**Phase:** {phase} — control-plane test

## Objective

Generate a concise deterministic brief. Keep the worker inside the released wave.
"""


def _execution(
    *,
    work_order: str = "CONTROL-PLANE-002",
    branch: str = TEST_BRANCH,
    wave: str = TEST_WAVE,
) -> str:
    return f"""# Codex Execution Entry

**Work Order:** `{work_order}`
**Release:** OPEN — TEST WAVE ONLY
**Construction branch:** `{branch}`
**Wave specification:** `{wave}`
"""


def _repo(
    tmp_path: Path,
    *,
    control: str | None = None,
    work: str | None = None,
    execution: str | None = None,
) -> Path:
    paths = {
        "docs/operations/CURRENT_CONTROL_STATE.md": control or _control(),
        "docs/operations/CURRENT_WORK_ORDER.md": work or _work(),
        "docs/operations/CODEX_EXECUTION_ENTRY.md": execution or _execution(),
        "docs/operations/CODEX_TOOLBOX.md": "TOOLBOX_TARGET_CONTENT_MUST_NOT_BE_PRELOADED\n",
        TEST_WAVE: "DURABLE_WAVE_BODY_MUST_NOT_BE_COPIED\n" * 100,
        ".gitignore": "/.private/\n",
    }
    for relative, content in paths.items():
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    _git(tmp_path, "init")
    _git(tmp_path, "checkout", "-b", TEST_BRANCH)
    _git(tmp_path, "config", "user.email", "test@example.invalid")
    _git(tmp_path, "config", "user.name", "Test")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "fixture")
    return tmp_path


def test_valid_release_generates_concise_deterministic_brief(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    first, first_errors = build_foreman_brief(root)
    second, second_errors = build_foreman_brief(root)

    assert first_errors == second_errors == ()
    assert first == second
    assert "- Work: `CONTROL-PLANE-002`" in first
    assert "- Release: `OPEN — TEST WAVE ONLY`" in first
    assert f"- Wave: `{TEST_WAVE}`" in first
    assert f"- Expected branch: `{TEST_BRANCH}`" in first
    assert f"- Local: `{TEST_BRANCH}`" in first
    assert "tree=`clean`" in first
    assert "DURABLE_WAVE_BODY_MUST_NOT_BE_COPIED" not in first
    assert "TOOLBOX_TARGET_CONTENT_MUST_NOT_BE_PRELOADED" not in first
    assert len(first.splitlines()) < 50


def test_selected_trigger_exposes_only_its_route_without_target_content(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    brief, errors = build_foreman_brief(root, "architecture")

    assert errors == ()
    assert "CODEX_TOOLBOX.md#architecturecontract-ambiguity" in brief
    assert "#testquality-failure" not in brief
    assert "#gitrepository-state-issue" not in brief
    assert "TOOLBOX_TARGET_CONTENT_MUST_NOT_BE_PRELOADED" not in brief


@pytest.mark.parametrize(
    ("control", "expected"),
    (
        ("# no metadata\n", "no opening metadata delimiter"),
        (
            _control().replace("phase_state: TEST_ACTIVE\n", ""),
            "phase_state",
        ),
    ),
)
def test_missing_or_malformed_control_metadata_fails_closed(
    tmp_path: Path, control: str, expected: str
) -> None:
    _, errors = build_foreman_brief(_repo(tmp_path, control=control))
    assert any(expected in error for error in errors)


def test_phase_and_work_order_mismatch_fail_closed(tmp_path: Path) -> None:
    _, errors = build_foreman_brief(
        _repo(tmp_path, control=_control(phase="R0.13", work_order="OTHER"))
    )
    assert any("phase mismatch" in error for error in errors)
    assert any("active work-order mismatch" in error for error in errors)
    assert any("Codex release work-order mismatch" in error for error in errors)


def test_dirty_tree_is_prominent_and_generated_brief_remains_ignored(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "dirty.txt").write_text("dirty", encoding="utf-8")
    output, errors = write_foreman_brief(root)

    assert errors == ()
    assert "tree=`DIRTY`" in output.read_text(encoding="utf-8")
    assert output == root / BRIEF_PATH
    assert _git(root, "check-ignore", BRIEF_PATH) == BRIEF_PATH
    assert BRIEF_PATH not in _git(root, "status", "--porcelain")


def test_missing_released_wave_fails_closed(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / TEST_WAVE).unlink()

    _, errors = build_foreman_brief(root)

    assert errors == (f"released wave specification is missing: {TEST_WAVE}",)


def test_local_branch_mismatch_fails_closed(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _git(root, "checkout", "-b", "work/wrong-wave")

    _, errors = build_foreman_brief(root)

    assert any("local branch mismatch" in error for error in errors)


def test_execution_work_order_mismatch_fails_closed(tmp_path: Path) -> None:
    root = _repo(tmp_path, execution=_execution(work_order="OTHER"))

    _, errors = build_foreman_brief(root)

    assert any("Codex release work-order mismatch" in error for error in errors)

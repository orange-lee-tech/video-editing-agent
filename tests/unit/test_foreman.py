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


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


def _control(*, phase: str = "R0.12", work_order: str = "CONTROL-PLANE-001") -> str:
    return f"""# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-14
current_phase: {phase}
phase_state: ACTIVATION_CONTROL_PLANE_HARDENING
active_work_order: {work_order}
accepted_code_baseline: {"0" * 40}
writer: codex
---
"""


def _work(*, phase: str = "R0.12", identity: str = "CONTROL-PLANE-001") -> str:
    return f"""# Current Work Order

**ID:** `{identity}`
**Status:** ACTIVE
**Phase:** {phase} — control-plane test

## Objective

Generate a concise deterministic brief.

## Read

1. `docs/operations/CURRENT_CONTROL_STATE.md`
2. `docs/operations/CODEX_EXECUTION_ENTRY.md`
3. `docs/task-specific.md`

## Allowed scope

- `tools/maintenance/foreman.py`
- focused tests

Do not touch product implementation.

## Authority boundary

It may not:

- invent product decisions;
- auto-commit/push.

## Stop gate

- brief generated;
- tests green.
"""


def _repo(tmp_path: Path, *, control: str | None = None, work: str | None = None) -> Path:
    paths = {
        "docs/operations/CURRENT_CONTROL_STATE.md": control or _control(),
        "docs/operations/CURRENT_WORK_ORDER.md": work or _work(),
        "docs/operations/CODEX_EXECUTION_ENTRY.md": "entry marker that may be referenced only\n",
        "docs/task-specific.md": "DURABLE_DOCUMENT_BODY_MUST_NOT_BE_COPIED\n" * 100,
        ".gitignore": "/.private/\n",
    }
    for relative, content in paths.items():
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.invalid")
    _git(tmp_path, "config", "user.name", "Test")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "fixture")
    return tmp_path


def test_valid_control_state_generates_concise_deterministic_brief(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    first, first_errors = build_foreman_brief(root)
    second, second_errors = build_foreman_brief(root)

    assert first_errors == second_errors == ()
    assert first == second
    assert "Active work order: `CONTROL-PLANE-001`" in first
    assert "Working tree: `clean`" in first
    assert "`docs/operations/CURRENT_CONTROL_STATE.md`" in first
    assert "`docs/operations/CURRENT_WORK_ORDER.md`" in first
    assert "`docs/task-specific.md`" in first
    assert "DURABLE_DOCUMENT_BODY_MUST_NOT_BE_COPIED" not in first
    assert len(first.splitlines()) < 100


@pytest.mark.parametrize(
    ("control", "expected"),
    (
        ("# no metadata\n", "no opening metadata delimiter"),
        (
            _control().replace("phase_state: ACTIVATION_CONTROL_PLANE_HARDENING\n", ""),
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


def test_dirty_tree_is_prominent_and_generated_brief_remains_ignored(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "dirty.txt").write_text("dirty", encoding="utf-8")
    output, errors = write_foreman_brief(root)

    assert errors == ()
    assert "Working tree: `DIRTY`" in output.read_text(encoding="utf-8")
    assert output == root / BRIEF_PATH
    assert _git(root, "check-ignore", BRIEF_PATH) == BRIEF_PATH
    assert BRIEF_PATH not in _git(root, "status", "--porcelain")


def test_missing_referenced_read_file_fails_closed(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "docs/task-specific.md").unlink()
    _, errors = build_foreman_brief(root)
    assert errors == ("work-order read reference is missing: docs/task-specific.md",)

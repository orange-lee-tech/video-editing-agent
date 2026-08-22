#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTROL_STATE = "docs/operations/CURRENT_CONTROL_STATE.md"


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _git_optional(*args: str) -> str:
    try:
        return _git(*args)
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def _control_metadata() -> dict[str, str]:
    try:
        text = (ROOT / CONTROL_STATE).read_text(encoding="utf-8")
    except OSError:
        return {}
    match = re.search(r"^---\s*$\n(.*?)^---\s*$", text, re.MULTILINE | re.DOTALL)
    if match is None:
        return {}
    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        if key and value:
            metadata[key] = value
    return metadata


def _build_snapshot() -> str:
    head = _git("rev-parse", "HEAD")
    origin_main = _git_optional("rev-parse", "origin/main")
    branch = _git_optional("branch", "--show-current") or "detached"
    upstream = _git_optional("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    status = _git_optional("status", "--porcelain")
    dirty = status not in {"", "unavailable"}
    generated = datetime.now(UTC).isoformat(timespec="seconds")
    state = _control_metadata()

    parts = [
        "# Repository Handoff Snapshot",
        "",
        "> Non-authoritative orientation only. Reobserve GitHub main/CI before acting.",
        "",
        f"- Generated UTC: `{generated}`",
        f"- Branch: `{branch}`",
        f"- Local HEAD: `{head}`",
        f"- Upstream: `{upstream}`",
        f"- Local `origin/main`: `{origin_main}`",
        f"- Working tree: `{'DIRTY' if dirty else 'clean'}`",
        f"- Phase: `{state.get('current_phase', 'unavailable')}`",
        f"- Phase state: `{state.get('phase_state', 'unavailable')}`",
        f"- Active work order: `{state.get('active_work_order', 'unavailable')}`",
        f"- Structural progress: `{state.get('structural_progress_percent', 'unavailable')}%`",
        f"- Stage-A gate: `{state.get('stage_a_completion_gate', 'unavailable')}`",
        f"- Codex release: `{state.get('codex_release', 'unavailable')}`",
        "",
        "## Canonical re-entry",
        "",
        "1. `AGENTS.md`",
        "2. `docs/DOCUMENT_REGISTRY.json`",
        "3. `docs/operations/CURRENT_CONTROL_STATE.md`",
        "4. `docs/roadmap/CURRENT_PHASE_STATUS.md`",
        "5. `docs/operations/CURRENT_WORK_ORDER.md`",
        "6. `docs/operations/CODEX_EXECUTION_ENTRY.md` only when Codex handoff is relevant.",
        "",
        "## Rule",
        "",
        "Do not treat this snapshot as live authority and do not preload archive/history. "
        "Use the canonical files above, then open only the active wave and task-relevant code/tests.",
        "",
    ]
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a compact local handoff pointer.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output path. Prefer an ignored path such as .private/handoff.md.",
    )
    args = parser.parse_args()

    snapshot = _build_snapshot()
    if args.output is None:
        print(snapshot)
        return 0

    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(snapshot, encoding="utf-8")
    print(f"Wrote handoff snapshot: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

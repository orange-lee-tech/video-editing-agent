#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


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
    except subprocess.CalledProcessError:
        return "unavailable"


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8").strip()


def _build_snapshot() -> str:
    head = _git("rev-parse", "HEAD")
    origin_main = _git_optional("rev-parse", "origin/main")
    branch = _git_optional("branch", "--show-current") or "detached"
    dirty = bool(_git_optional("status", "--porcelain").strip())
    generated = datetime.now(UTC).isoformat(timespec="seconds")

    parts = [
        "# Repository Handoff Snapshot",
        "",
        "> Non-authoritative orientation only. The receiving ChatGPT must reobserve GitHub/main.",
        "",
        f"- Generated UTC: `{generated}`",
        f"- Branch: `{branch}`",
        f"- Local HEAD: `{head}`",
        f"- Local `origin/main`: `{origin_main}`",
        f"- Working tree: `{'DIRTY' if dirty else 'clean'}`",
        "",
        "## Read first",
        "",
        "1. `docs/README.md`",
        "2. `docs/operations/CHATGPT_GITHUB_CODEX_COLLABORATION.md`",
        "3. `docs/roadmap/CURRENT_PHASE_STATUS.md`",
        "4. `docs/operations/CURRENT_WORK_ORDER.md`",
        "",
        "## Current phase source",
        "",
        _read("docs/roadmap/CURRENT_PHASE_STATUS.md"),
        "",
        "## Current work-order source",
        "",
        _read("docs/operations/CURRENT_WORK_ORDER.md"),
        "",
        "## Receiving-conversation rule",
        "",
        "Reobserve current GitHub `origin/main` and CI before activating work. "
        "If this snapshot conflicts with GitHub, GitHub/evidence wins.",
        "",
    ]
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a local non-authoritative handoff snapshot.")
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

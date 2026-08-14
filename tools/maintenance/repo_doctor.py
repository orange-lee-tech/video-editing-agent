#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = (
    "README.md",
    "docs/README.md",
    "docs/archive/README.md",
    "docs/product/PRODUCT_CONSTITUTION_V1.0.md",
    "docs/architecture/ARCHITECTURE_CONTRACT_V0.2.md",
    "docs/roadmap/ROADMAP_V2.md",
    "docs/roadmap/CURRENT_PHASE_STATUS.md",
    "docs/operations/CHATGPT_GITHUB_CODEX_COLLABORATION.md",
    "docs/operations/CODEX_EXECUTION_ENTRY.md",
    "docs/operations/CURRENT_WORK_ORDER.md",
)

REQUIRED_READMES = (
    ".github/README.md",
    "LICENSES/README.md",
    "docs/README.md",
    "docs/adr/README.md",
    "docs/architecture/README.md",
    "docs/archive/README.md",
    "docs/capabilities/README.md",
    "docs/logs/README.md",
    "docs/operations/README.md",
    "docs/product/README.md",
    "docs/roadmap/README.md",
    "docs/upstream/README.md",
    "docs/validation/README.md",
    "scripts/README.md",
    "src/README.md",
    "tests/README.md",
    "tools/README.md",
    "tools/maintenance/README.md",
    "tools/probes/README.md",
)

RETIRED_ACTIVE_PATHS = (
    "docs/architecture/ARCHITECTURE_CONTRACT_V0.1.md",
    "docs/architecture/ARCHITECTURE_CONTRACT_V0.1.1.md",
    "docs/architecture/ARCHITECTURE_CONTRACT_V0.1.2.md",
    "docs/decisions",
    "docs/upstream/UPSTREAM_COMPONENTS.md",
    "docs/upstream/UPSTREAM_POLICY.md",
    "docs/roadmap/R0.7A_MIGRATION_AUDIT.md",
)

REQUIRED_ARCHIVE_PATHS = (
    "docs/archive/architecture/ARCHITECTURE_CONTRACT_V0.1.md",
    "docs/archive/architecture/ARCHITECTURE_CONTRACT_V0.1.1.md",
    "docs/archive/architecture/ARCHITECTURE_CONTRACT_V0.1.2.md",
    "docs/archive/decisions/ADR-0001-sqlite-structured-persistence.md",
    "docs/archive/upstream/UPSTREAM_COMPONENTS.md",
    "docs/archive/upstream/UPSTREAM_POLICY.md",
    "docs/archive/roadmap/R0.7A_MIGRATION_AUDIT.md",
)

FORBIDDEN_TRACKED_PREFIXES = ("example/", ".tools/", ".private/")
FORBIDDEN_TRACKED_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".uv-cache",
}


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _git_lines(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _phase_token(text: str, field: str) -> str | None:
    match = re.search(rf"\*\*{re.escape(field)}:\*\*\s*(R\d+\.\d+[A-Z]?)", text)
    return match.group(1) if match else None


def _check_required_paths(errors: list[str]) -> None:
    for relative_path in (*REQUIRED_FILES, *REQUIRED_READMES, *REQUIRED_ARCHIVE_PATHS):
        if not (ROOT / relative_path).exists():
            errors.append(f"missing required path: {relative_path}")


def _check_retired_locations(errors: list[str]) -> None:
    for relative_path in RETIRED_ACTIVE_PATHS:
        if (ROOT / relative_path).exists():
            errors.append(f"retired path still present in active tree: {relative_path}")


def _check_live_state(errors: list[str]) -> None:
    status = _read("docs/roadmap/CURRENT_PHASE_STATUS.md")
    work_order = _read("docs/operations/CURRENT_WORK_ORDER.md")
    status_phase = _phase_token(status, "Current phase")
    work_phase = _phase_token(work_order, "Phase")

    if status_phase is None:
        errors.append("CURRENT_PHASE_STATUS.md has no parseable Current phase")
    if work_phase is None:
        errors.append("CURRENT_WORK_ORDER.md has no parseable Phase")
    if status_phase is not None and work_phase is not None and status_phase != work_phase:
        errors.append(
            "phase pointer mismatch: "
            f"CURRENT_PHASE_STATUS={status_phase}, CURRENT_WORK_ORDER={work_phase}"
        )

    collaboration_path = "docs/operations/CHATGPT_GITHUB_CODEX_COLLABORATION.md"
    if collaboration_path not in _read("docs/README.md"):
        errors.append("docs/README.md does not route new handoffs to the collaboration contract")


def _check_tracked_noise(errors: list[str]) -> None:
    for tracked in _git_lines("ls-files"):
        normalized = tracked.replace("\\", "/")
        parts = set(normalized.split("/"))
        if normalized.startswith(FORBIDDEN_TRACKED_PREFIXES):
            errors.append(f"local/private path is tracked: {normalized}")
        if parts & FORBIDDEN_TRACKED_PARTS:
            errors.append(f"cache path is tracked: {normalized}")
        if normalized.endswith((".pyc", ".pyo", ".log", ".tmp", ".bak")):
            errors.append(f"generated/noise file is tracked: {normalized}")


def main() -> int:
    errors: list[str] = []
    _check_required_paths(errors)
    _check_retired_locations(errors)
    _check_live_state(errors)
    _check_tracked_noise(errors)

    if errors:
        print("Repository doctor FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Repository doctor PASSED.")
    print("- navigation/required README paths present")
    print("- retired documents isolated under docs/archive")
    print("- current phase/work-order pointers agree")
    print("- no tracked private/cache/noise paths detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

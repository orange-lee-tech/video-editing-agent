#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = (
    "AGENTS.md",
    "README.md",
    "docs/README.md",
    "docs/DOCUMENT_REGISTRY.json",
    "docs/archive/README.md",
    "docs/product/PRODUCT_CONSTITUTION_V1.0.md",
    "docs/architecture/ARCHITECTURE_CONTRACT_V0.2.md",
    "docs/roadmap/ROADMAP_V2.md",
    "docs/roadmap/CURRENT_PHASE_STATUS.md",
    "docs/roadmap/STAGE_A_COMPLETION_GATE.md",
    "docs/operations/DOCUMENT_CONTROL_POLICY.md",
    "docs/operations/CHATGPT_GITHUB_CODEX_COLLABORATION.md",
    "docs/operations/CODEX_EXECUTION_ENTRY.md",
    "docs/operations/CURRENT_CONTROL_STATE.md",
    "docs/operations/CURRENT_WORK_ORDER.md",
    "tools/maintenance/document_registry.py",
    ".github/workflows/document-registry.yml",
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


class FrontmatterError(ValueError):
    pass


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


def _bold_field(text: str, field: str) -> str | None:
    match = re.search(rf"^\*\*{re.escape(field)}:\*\*\s*(.+?)\s*$", text, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip().strip("`")


def _frontmatter(text: str) -> dict[str, str]:
    match = re.search(r"^---\s*$\n(.*?)^---\s*$", text, re.MULTILINE | re.DOTALL)
    if not match:
        raise FrontmatterError("no parseable frontmatter block")
    values: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise FrontmatterError(f"invalid frontmatter line: {raw_line}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("`")
    return values


def _check_required_paths(errors: list[str]) -> None:
    for relative_path in (*REQUIRED_FILES, *REQUIRED_READMES, *REQUIRED_ARCHIVE_PATHS):
        if not (ROOT / relative_path).exists():
            errors.append(f"missing required path: {relative_path}")


def _check_retired_locations(errors: list[str]) -> None:
    for relative_path in RETIRED_ACTIVE_PATHS:
        if (ROOT / relative_path).exists():
            errors.append(f"retired path still present in active tree: {relative_path}")


def _control_progress(control: dict[str, str], errors: list[str]) -> int | None:
    raw_progress = control.get("structural_progress_percent")
    if raw_progress is None:
        errors.append("CURRENT_CONTROL_STATE.md missing structural_progress_percent")
        return None
    try:
        progress = int(raw_progress)
    except ValueError:
        errors.append("structural_progress_percent must be an integer")
        return None
    if not 0 <= progress <= 100:
        errors.append("structural_progress_percent must be between 0 and 100")
        return None
    return progress


def _check_stage_a_gate(control: dict[str, str], progress: int | None, errors: list[str]) -> None:
    stage_gate = control.get("stage_a_completion_gate")
    planning_gate = control.get("core_1_planning_product_gate")
    editing_gate = control.get("core_2_editing_product_gate")
    for field, value in (
        ("stage_a_completion_gate", stage_gate),
        ("core_1_planning_product_gate", planning_gate),
        ("core_2_editing_product_gate", editing_gate),
    ):
        if not value:
            errors.append(f"CURRENT_CONTROL_STATE.md missing {field}")

    if progress is None:
        return
    if progress == 100:
        required = {
            "stage_a_completion_gate": stage_gate,
            "core_1_planning_product_gate": planning_gate,
            "core_2_editing_product_gate": editing_gate,
        }
        not_pass = [field for field, value in required.items() if value != "PASS"]
        if not_pass:
            errors.append(
                "false Stage-A 100% claim: these gates are not PASS: " + ", ".join(not_pass)
            )
    elif stage_gate == "PASS":
        errors.append(
            "stage_a_completion_gate cannot be PASS while structural progress is below 100"
        )


def _check_live_state(errors: list[str]) -> None:
    status = _read("docs/roadmap/CURRENT_PHASE_STATUS.md")
    work_order = _read("docs/operations/CURRENT_WORK_ORDER.md")
    control_text = _read("docs/operations/CURRENT_CONTROL_STATE.md")

    status_phase = _phase_token(status, "Current phase")
    work_phase = _phase_token(work_order, "Phase")
    try:
        control = _frontmatter(control_text)
    except FrontmatterError as exc:
        errors.append(f"CURRENT_CONTROL_STATE.md {exc}")
        return
    control_phase = control.get("current_phase")

    if status_phase is None:
        errors.append("CURRENT_PHASE_STATUS.md has no parseable Current phase")
    if work_phase is None:
        errors.append("CURRENT_WORK_ORDER.md has no parseable Phase")
    if not control_phase:
        errors.append("CURRENT_CONTROL_STATE.md missing current_phase")

    observed_phases = {
        "CURRENT_PHASE_STATUS": status_phase,
        "CURRENT_WORK_ORDER": work_phase,
        "CURRENT_CONTROL_STATE": control_phase,
    }
    present_phases = {name: value for name, value in observed_phases.items() if value is not None}
    if len(set(present_phases.values())) > 1:
        errors.append(
            "phase pointer mismatch: "
            + ", ".join(f"{name}={value}" for name, value in present_phases.items())
        )

    work_id = _bold_field(work_order, "ID")
    work_status = _bold_field(work_order, "Status")
    active_work_order = control.get("active_work_order")
    if work_id is None:
        errors.append("CURRENT_WORK_ORDER.md has no parseable ID")
    if work_status is None:
        errors.append("CURRENT_WORK_ORDER.md has no parseable Status")
    if not active_work_order:
        errors.append("CURRENT_CONTROL_STATE.md missing active_work_order")

    if work_id and work_status and active_work_order:
        normalized_status = work_status.upper()
        if normalized_status == "ACTIVE" and active_work_order != work_id:
            errors.append(
                "active work-order mismatch: "
                f"CURRENT_CONTROL_STATE={active_work_order}, CURRENT_WORK_ORDER={work_id}"
            )
        if normalized_status.startswith("CLOSED") and active_work_order != "NONE":
            errors.append(
                "closed CURRENT_WORK_ORDER.md must not remain active in CURRENT_CONTROL_STATE.md"
            )
        if active_work_order != "NONE" and active_work_order not in status:
            errors.append("CURRENT_PHASE_STATUS.md does not mention active_work_order")

    accepted_baseline = control.get("accepted_code_baseline")
    if not accepted_baseline or not re.fullmatch(r"[0-9a-f]{40}", accepted_baseline):
        errors.append("CURRENT_CONTROL_STATE.md accepted_code_baseline must be a 40-char SHA")

    progress = _control_progress(control, errors)
    status_progress_raw = _bold_field(status, "Structural progress")
    if status_progress_raw is None:
        errors.append("CURRENT_PHASE_STATUS.md has no parseable Structural progress")
    else:
        match = re.fullmatch(r"(\d{1,3})%", status_progress_raw)
        if match is None:
            errors.append("CURRENT_PHASE_STATUS.md Structural progress must be an integer percent")
        elif progress is not None and int(match.group(1)) != progress:
            errors.append(
                "structural progress mismatch: "
                f"CURRENT_CONTROL_STATE={progress}, CURRENT_PHASE_STATUS={match.group(1)}"
            )

    _check_stage_a_gate(control, progress, errors)

    docs_readme = _read("docs/README.md")
    operations_readme = _read("docs/operations/README.md")
    required_routes = (
        "operations/CURRENT_CONTROL_STATE.md",
        "roadmap/CURRENT_PHASE_STATUS.md",
        "operations/CURRENT_WORK_ORDER.md",
        "roadmap/STAGE_A_COMPLETION_GATE.md",
    )
    for route in required_routes:
        if route not in docs_readme:
            errors.append(f"docs/README.md missing live route: {route}")

    for filename in (
        "CURRENT_CONTROL_STATE.md",
        "CURRENT_WORK_ORDER.md",
        "CURRENT_PHASE_STATUS.md",
    ):
        if filename not in operations_readme:
            errors.append(f"docs/operations/README.md missing live-state route: {filename}")

    collaboration_path = "operations/CHATGPT_GITHUB_CODEX_COLLABORATION.md"
    if collaboration_path not in docs_readme:
        errors.append("docs/README.md does not route new handoffs to the collaboration contract")


def _check_document_governance(errors: list[str]) -> None:
    try:
        registry = json.loads(_read("docs/DOCUMENT_REGISTRY.json"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"DOCUMENT_REGISTRY.json is not readable JSON: {exc}")
        return

    if registry.get("schema") != "video-editing-agent-document-registry/v1":
        errors.append("DOCUMENT_REGISTRY.json schema mismatch")

    canonical_entries = registry.get("canonical_entries")
    if not isinstance(canonical_entries, list):
        errors.append("DOCUMENT_REGISTRY.json canonical_entries must be a list")
        canonical_entries = []
    for entry in canonical_entries:
        if not isinstance(entry, dict):
            errors.append("DOCUMENT_REGISTRY.json has a non-object canonical entry")
            continue
        path = entry.get("path")
        if not isinstance(path, str) or not path:
            errors.append("DOCUMENT_REGISTRY.json canonical entry missing path")
        elif not (ROOT / path).exists():
            errors.append(f"DOCUMENT_REGISTRY.json points to missing path: {path}")

    excluded = registry.get("default_excluded")
    if not isinstance(excluded, list) or "docs/archive/**" not in excluded:
        errors.append("DOCUMENT_REGISTRY.json must default-exclude docs/archive/**")

    directory_map = registry.get("directory_map")
    archive_excluded = False
    if isinstance(directory_map, list):
        archive_excluded = any(
            isinstance(entry, dict)
            and entry.get("path") == "docs/archive/**"
            and entry.get("attention") == "EXCLUDED_DEFAULT"
            for entry in directory_map
        )
    if not archive_excluded:
        errors.append("DOCUMENT_REGISTRY.json must classify docs/archive/** as EXCLUDED_DEFAULT")

    agents = _read("AGENTS.md")
    for token in (
        "docs/DOCUMENT_REGISTRY.json",
        "docs/archive/**",
        "EXCLUDED_DEFAULT",
        "Compatible development",
        "Bounded self-repair",
    ):
        if token not in agents:
            errors.append(f"AGENTS.md missing required governance token: {token}")

    docs_readme = _read("docs/README.md")
    for token in ("DOCUMENT_REGISTRY.json", "DOCUMENT_CONTROL_POLICY.md", "archive/"):
        if token not in docs_readme:
            errors.append(f"docs/README.md missing document-governance route: {token}")


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
    _check_document_governance(errors)
    _check_tracked_noise(errors)

    if errors:
        print("Repository doctor FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Repository doctor PASSED.")
    print("- navigation/required README paths present")
    print("- document registry and attention policy present")
    print("- docs/archive remains default-excluded retired provenance")
    print("- phase/work-order/control-state pointers agree")
    print("- structural progress is synchronized across live state")
    print("- Stage-A 100% product-gate invariant preserved")
    print("- no tracked private/cache/noise paths detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

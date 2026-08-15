#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTROL_STATE = "docs/operations/CURRENT_CONTROL_STATE.md"
WORK_ORDER = "docs/operations/CURRENT_WORK_ORDER.md"
BRIEF_PATH = ".private/codex_brief.md"
CONTROL_SCHEMA = "video-editing-agent-control-state/v1"
TOOLBOX = "docs/operations/CODEX_TOOLBOX.md"

TRIGGER_ROUTES = {
    "architecture": (
        "architecture/contract ambiguity",
        f"{TOOLBOX}#architecturecontract-ambiguity",
        "Open the smallest relevant CAP/ADR/contract section named by the active task.",
    ),
    "location": (
        "code-location uncertainty",
        f"{TOOLBOX}#code-location-uncertainty",
        "Use targeted rg/rg --files before opening implementation files.",
    ),
    "quality": (
        "test/quality failure",
        f"{TOOLBOX}#testquality-failure",
        "Inspect the focused failure first, then use the canonical verification route.",
    ),
    "git": (
        "Git/repository-state issue",
        f"{TOOLBOX}#gitrepository-state-issue",
        "Stop writes and inspect status, branch, upstream, and diff before recovery.",
    ),
    "external": (
        "external/license/provider uncertainty",
        f"{TOOLBOX}#externallicenseprovider-uncertainty",
        "Fail closed and open only the relevant release/provider evidence.",
    ),
    "high-risk": (
        "destructive/high-risk operation",
        f"{TOOLBOX}#destructivehigh-risk-operation",
        "Stop and obtain the required ChatGPT/User authority before acting.",
    ),
}


@dataclass(frozen=True, slots=True)
class GitState:
    head: str
    branch: str
    clean: bool
    upstream: str
    ahead: int | None
    behind: int | None
    origin_main: str


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _git_optional(root: Path, *args: str) -> str:
    try:
        return _git(root, *args)
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def _git_state(root: Path, errors: list[str]) -> GitState:
    try:
        head = _git(root, "rev-parse", "HEAD")
        branch = _git(root, "branch", "--show-current") or "detached"
        clean = not bool(_git(root, "status", "--porcelain"))
    except (OSError, subprocess.CalledProcessError):
        errors.append("not a readable Git repository")
        return GitState(
            "unavailable", "unavailable", False, "unavailable", None, None, "unavailable"
        )
    upstream = _git_optional(
        root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"
    )
    ahead = behind = None
    if upstream != "unavailable":
        counts = _git_optional(root, "rev-list", "--left-right", "--count", f"HEAD...{upstream}")
        match = re.fullmatch(r"(\d+)\s+(\d+)", counts)
        if match:
            ahead, behind = int(match.group(1)), int(match.group(2))
    return GitState(
        head,
        branch,
        clean,
        upstream,
        ahead,
        behind,
        _git_optional(root, "rev-parse", "origin/main"),
    )


def _read(root: Path, relative_path: str, errors: list[str]) -> str:
    try:
        return (root / relative_path).read_text(encoding="utf-8")
    except OSError:
        errors.append(f"missing or unreadable control file: {relative_path}")
        return ""


def _front_matter(text: str, errors: list[str]) -> dict[str, str]:
    lines = text.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == "---")
    except StopIteration:
        errors.append("CURRENT_CONTROL_STATE has no opening metadata delimiter")
        return {}
    try:
        end = next(
            index
            for index, line in enumerate(lines[start + 1 :], start=start + 1)
            if line.strip() == "---"
        )
    except StopIteration:
        errors.append("CURRENT_CONTROL_STATE has no closing metadata delimiter")
        return {}
    metadata: dict[str, str] = {}
    for line in lines[start + 1 : end]:
        if not line.strip():
            continue
        if ":" not in line:
            errors.append(f"malformed control metadata line: {line.strip()}")
            continue
        key, value = (item.strip() for item in line.split(":", 1))
        if not key or not value or key in metadata:
            errors.append(f"malformed control metadata field: {key or '<empty>'}")
            continue
        metadata[key] = value
    required = (
        "schema",
        "current_phase",
        "phase_state",
        "active_work_order",
        "accepted_code_baseline",
    )
    for field in required:
        if field not in metadata:
            errors.append(f"missing control metadata field: {field}")
    if metadata.get("schema") not in {None, CONTROL_SCHEMA}:
        errors.append(f"unsupported control schema: {metadata['schema']}")
    if baseline := metadata.get("accepted_code_baseline"):
        if re.fullmatch(r"[0-9a-f]{40}", baseline) is None:
            errors.append("accepted_code_baseline must be a 40-character lowercase Git SHA")
    return metadata


def _work_metadata(text: str, errors: list[str]) -> dict[str, str]:
    metadata = {
        key.lower().replace(" ", "_"): value.strip().strip("`")
        for key, value in re.findall(r"^\*\*([^*]+):\*\*\s*(.+?)\s*$", text, re.MULTILINE)
    }
    for field in ("id", "status", "phase"):
        if not metadata.get(field):
            errors.append(f"missing work-order metadata field: {field}")
    return metadata


def _section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return "" if match is None else match.group(1).strip()


def _bullets(text: str) -> tuple[str, ...]:
    return tuple(match.strip() for match in re.findall(r"^-\s+(.+)$", text, re.MULTILINE))


def _validate_reads(root: Path, work_order: str, errors: list[str]) -> None:
    listed = re.findall(r"^\d+\.\s+`([^`]+)`", _section(work_order, "Read"), re.MULTILINE)
    for item in listed:
        normalized = item.replace("\\", "/")
        if not (root / normalized).exists():
            errors.append(f"work-order read reference is missing: {normalized}")


def _stop_conditions(work_order: str) -> tuple[str, ...]:
    section = _section(work_order, "Stop gate")
    conditions: list[str] = []
    for raw_line in section.splitlines():
        line = raw_line.removeprefix("-").strip()
        lowered = line.lower()
        if "do not " in lowered:
            conditions.append(line[lowered.index("do not ") :])
        elif lowered.startswith(("stop if ", "fail closed ", "blocked ")):
            conditions.append(line)
    return tuple(dict.fromkeys(conditions))


def build_foreman_brief(
    root: Path = ROOT, trigger: str | None = None
) -> tuple[str, tuple[str, ...]]:
    if trigger is not None and trigger not in TRIGGER_ROUTES:
        raise ValueError(f"unsupported foreman trigger: {trigger}")
    errors: list[str] = []
    state_text = _read(root, CONTROL_STATE, errors)
    work_text = _read(root, WORK_ORDER, errors)
    state = _front_matter(state_text, errors) if state_text else {}
    work = _work_metadata(work_text, errors) if work_text else {}
    if work_text:
        _validate_reads(root, work_text, errors)
    if not (root / TOOLBOX).is_file():
        errors.append(f"missing foreman toolbox: {TOOLBOX}")
    git = _git_state(root, errors)

    if state.get("active_work_order") and work.get("id"):
        if state["active_work_order"] != work["id"]:
            errors.append(
                "active work-order mismatch: "
                f"control={state['active_work_order']}, work_order={work['id']}"
            )
    phase_match = re.match(r"R\d+\.\d+[A-Z]?", work.get("phase", ""))
    work_phase = phase_match.group(0) if phase_match else ""
    if state.get("current_phase") and work_phase and state["current_phase"] != work_phase:
        errors.append(f"phase mismatch: control={state['current_phase']}, work_order={work_phase}")
    if work.get("status") and work["status"] != "ACTIVE":
        errors.append(f"work order is not ACTIVE: {work['status']}")

    objective_source = " ".join(_section(work_text, "Objective").split())
    objective_match = re.match(r"^(.+?[.!?])(?:\s|$)", objective_source)
    objective = (
        objective_match.group(1)
        if objective_match is not None
        else objective_source or "unavailable"
    )
    stops = _stop_conditions(work_text)
    sync = (
        "unavailable"
        if git.ahead is None or git.behind is None
        else f"ahead={git.ahead}, behind={git.behind}"
    )
    work_id = state.get("active_work_order", work.get("id", "unavailable"))
    lines = [
        "# Codex Foreman L0",
        "",
        "> Machine-generated routing only; open secondary context only when triggered.",
        "",
        "## Task",
        "",
        f"- Phase: `{state.get('current_phase', 'unavailable')}`",
        f"- Phase state: `{state.get('phase_state', 'unavailable')}`",
        f"- Active work order: `{work_id}`",
        f"- Objective: {objective}",
        "",
        "## Local Git",
        "",
        f"- HEAD: `{git.head}`",
        f"- Branch: `{git.branch}`",
        f"- Working tree: `{'clean' if git.clean else 'DIRTY'}`",
        f"- Upstream: `{git.upstream}` ({sync})",
        f"- Local origin/main ref: `{git.origin_main}`",
        "- Remote fetch/CI freshness: "
        "`not inferred; use explicit external observation when required`",
        "",
        "## Immediate action",
        "",
        f"Execute `{work_id}` only. Open a trigger route when secondary detail is needed.",
        "",
        "## Hard stops",
        "",
        *(f"- {item}" for item in (stops or ("none recorded",))),
        "",
        "## Blockers",
        "",
        *(f"- {item}" for item in (errors or ("none",))),
        "",
    ]
    if trigger is None:
        lines.extend(("## Trigger routes", ""))
        for name, (label, _, _) in TRIGGER_ROUTES.items():
            lines.append(f"- If {label}: rerun foreman with trigger `{name}`.")
        lines.append("")
    else:
        label, route, action = TRIGGER_ROUTES[trigger]
        lines.extend(
            (
                "## Trigger route",
                "",
                f"- Trigger: `{trigger}` — {label}",
                f"- Route: `{route}`",
                f"- Action: {action}",
                "- Do not preload unrelated toolbox sections.",
                "",
            )
        )
    return "\n".join(lines), tuple(errors)


def write_foreman_brief(
    root: Path = ROOT, trigger: str | None = None
) -> tuple[Path, tuple[str, ...]]:
    brief, errors = build_foreman_brief(root, trigger)
    output = root / BRIEF_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(brief, encoding="utf-8")
    return output, errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic Codex L0 or selected trigger route."
    )
    parser.add_argument("--trigger", choices=tuple(TRIGGER_ROUTES))
    args = parser.parse_args()
    output, errors = write_foreman_brief(ROOT, args.trigger)
    print(f"Wrote Codex foreman brief: {output}")
    if errors:
        print("Foreman BLOCKED:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Foreman PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

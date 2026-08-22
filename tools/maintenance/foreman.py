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
EXECUTION_ENTRY = "docs/operations/CODEX_EXECUTION_ENTRY.md"
BRIEF_PATH = ".private/codex_brief.md"
CONTROL_SCHEMA = "video-editing-agent-control-state/v1"
TOOLBOX = "docs/operations/CODEX_TOOLBOX.md"

TRIGGER_ROUTES = {
    "architecture": (
        "architecture/contract ambiguity",
        f"{TOOLBOX}#architecturecontract-ambiguity",
        "Open only the relevant CAP/ADR/contract section named by the active task.",
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


def _bold_metadata(text: str) -> dict[str, str]:
    return {
        key.strip().lower().replace(" ", "_"): value.strip().strip("`")
        for key, value in re.findall(r"^\*\*([^*]+):\*\*\s*(.+?)\s*$", text, re.MULTILINE)
    }


def _work_metadata(text: str, errors: list[str]) -> dict[str, str]:
    metadata = _bold_metadata(text)
    for field in ("id", "status", "phase"):
        if not metadata.get(field):
            errors.append(f"missing work-order metadata field: {field}")
    return metadata


def _execution_metadata(text: str, errors: list[str]) -> dict[str, str]:
    metadata = _bold_metadata(text)
    for field in ("work_order", "release", "construction_branch", "wave_specification"):
        if not metadata.get(field):
            errors.append(f"missing Codex execution metadata field: {field}")
    return metadata


def _section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return "" if match is None else match.group(1).strip()


def _validate_alignment(
    root: Path,
    state: dict[str, str],
    work: dict[str, str],
    execution: dict[str, str],
    git: GitState,
    errors: list[str],
) -> None:
    control_work = state.get("active_work_order")
    work_id = work.get("id")
    execution_work = execution.get("work_order")
    if control_work and work_id and control_work != work_id:
        errors.append(f"active work-order mismatch: control={control_work}, work_order={work_id}")
    if control_work and execution_work and control_work != execution_work:
        errors.append(
            f"Codex release work-order mismatch: control={control_work}, execution={execution_work}"
        )

    phase_match = re.match(r"R\d+\.\d+[A-Z]?", work.get("phase", ""))
    work_phase = phase_match.group(0) if phase_match else ""
    if state.get("current_phase") and work_phase and state["current_phase"] != work_phase:
        errors.append(f"phase mismatch: control={state['current_phase']}, work_order={work_phase}")
    if work.get("status") and work["status"] != "ACTIVE":
        errors.append(f"work order is not ACTIVE: {work['status']}")

    release = execution.get("release", "")
    if release and not release.startswith("OPEN"):
        errors.append(f"Codex release is not OPEN: {release}")

    control_release = state.get("codex_release")
    if control_release and not control_release.startswith("OPEN"):
        errors.append(f"control state does not expose an open Codex release: {control_release}")

    expected_branch = execution.get("construction_branch")
    control_branch = state.get("active_construction_branch")
    if expected_branch and control_branch and expected_branch != control_branch:
        errors.append(
            "construction-branch mismatch: "
            f"control={control_branch}, execution={expected_branch}"
        )
    if expected_branch and git.branch not in {expected_branch, "unavailable"}:
        errors.append(f"local branch mismatch: expected={expected_branch}, actual={git.branch}")

    wave_spec = execution.get("wave_specification")
    if wave_spec and not (root / wave_spec).is_file():
        errors.append(f"released wave specification is missing: {wave_spec}")
    if not (root / TOOLBOX).is_file():
        errors.append(f"missing foreman toolbox: {TOOLBOX}")


def build_foreman_brief(
    root: Path = ROOT, trigger: str | None = None
) -> tuple[str, tuple[str, ...]]:
    if trigger is not None and trigger not in TRIGGER_ROUTES:
        raise ValueError(f"unsupported foreman trigger: {trigger}")

    errors: list[str] = []
    state_text = _read(root, CONTROL_STATE, errors)
    work_text = _read(root, WORK_ORDER, errors)
    execution_text = _read(root, EXECUTION_ENTRY, errors)
    state = _front_matter(state_text, errors) if state_text else {}
    work = _work_metadata(work_text, errors) if work_text else {}
    execution = _execution_metadata(execution_text, errors) if execution_text else {}
    git = _git_state(root, errors)
    _validate_alignment(root, state, work, execution, git, errors)

    objective_source = " ".join(_section(work_text, "Objective").split())
    objective_match = re.match(r"^(.+?[.!?。])(?:\s|$)", objective_source)
    objective = objective_match.group(1) if objective_match else objective_source or "unavailable"
    sync = (
        "unavailable"
        if git.ahead is None or git.behind is None
        else f"ahead={git.ahead}, behind={git.behind}"
    )
    work_id = state.get("active_work_order", work.get("id", "unavailable"))
    release = execution.get("release", state.get("codex_release", "unavailable"))
    expected_branch = execution.get(
        "construction_branch", state.get("active_construction_branch", "unavailable")
    )
    wave_spec = execution.get("wave_specification", "unavailable")

    lines = [
        "# Codex Foreman L0",
        "",
        f"- Work: `{work_id}`",
        f"- Release: `{release}`",
        f"- Wave: `{wave_spec}`",
        f"- Objective: {objective}",
        f"- Expected branch: `{expected_branch}`",
        f"- Local: `{git.branch}` @ `{git.head}`; "
        f"tree=`{'clean' if git.clean else 'DIRTY'}`; upstream={sync}",
        "- Remote freshness: `not inferred; ChatGPT/GitHub must reobserve when required`",
        "",
        "## Action",
        "",
        f"Open `{wave_spec}` and execute only this released wave. Use targeted source/tests only.",
        "",
        "## Blockers",
        "",
        *(f"- {item}" for item in (errors or ("none",))),
        "",
    ]

    if trigger is None:
        lines.extend(
            (
                "## Escalation",
                "",
                "Rerun with `-Trigger architecture|location|quality|git|external|high-risk` only when needed.",
                "",
            )
        )
    else:
        label, route, action = TRIGGER_ROUTES[trigger]
        lines.extend(
            (
                "## Trigger",
                "",
                f"- `{trigger}` — {label}",
                f"- Route: `{route}`",
                f"- Action: {action}",
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
    parser = argparse.ArgumentParser(description="Generate a compact validated Codex L0 brief.")
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

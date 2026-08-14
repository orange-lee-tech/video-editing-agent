#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTROL_STATE = "docs/operations/CURRENT_CONTROL_STATE.md"
WORK_ORDER = "docs/operations/CURRENT_WORK_ORDER.md"
BRIEF_PATH = ".private/codex_brief.md"
CONTROL_SCHEMA = "video-editing-agent-control-state/v1"


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
            ahead, behind = (int(match.group(1)), int(match.group(2)))
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
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
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
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
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
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL
    )
    return "" if match is None else match.group(1).strip()


def _bullets(text: str) -> tuple[str, ...]:
    return tuple(match.strip() for match in re.findall(r"^-\s+(.+)$", text, re.MULTILINE))


def _required_reads(root: Path, work_order: str, errors: list[str]) -> tuple[str, ...]:
    listed = re.findall(r"^\d+\.\s+`([^`]+)`", _section(work_order, "Read"), re.MULTILINE)
    result: list[str] = [CONTROL_STATE, WORK_ORDER]
    for item in listed:
        normalized = item.replace("\\", "/")
        if normalized not in result:
            result.append(normalized)
        if not (root / normalized).is_file():
            errors.append(f"work-order read reference is missing: {normalized}")
    return tuple(result)


def _forbidden_scope(work_order: str) -> tuple[str, ...]:
    scoped = "\n".join((_section(work_order, "Allowed scope"), _section(work_order, "Stop gate")))
    result = re.findall(r"^(Do (?:\*\*)?not(?:\*\*)? .+)$", scoped, re.MULTILINE)
    return tuple(dict.fromkeys(item.replace("**", "").strip() for item in result))


def build_foreman_brief(root: Path = ROOT) -> tuple[str, tuple[str, ...]]:
    errors: list[str] = []
    state_text = _read(root, CONTROL_STATE, errors)
    work_text = _read(root, WORK_ORDER, errors)
    state = _front_matter(state_text, errors) if state_text else {}
    work = _work_metadata(work_text, errors) if work_text else {}
    reads = _required_reads(root, work_text, errors) if work_text else (CONTROL_STATE, WORK_ORDER)
    git = _git_state(root, errors)

    if state.get("active_work_order") and work.get("id"):
        if state["active_work_order"] != work["id"]:
            errors.append(
                "active work-order mismatch: "
                f"control={state['active_work_order']}, work_order={work['id']}"
            )
    work_phase_match = re.match(r"R\d+\.\d+[A-Z]?", work.get("phase", ""))
    work_phase = work_phase_match.group(0) if work_phase_match else ""
    if state.get("current_phase") and work_phase and state["current_phase"] != work_phase:
        errors.append(f"phase mismatch: control={state['current_phase']}, work_order={work_phase}")
    if work.get("status") and work["status"] != "ACTIVE":
        errors.append(f"work order is not ACTIVE: {work['status']}")

    objective = " ".join(_section(work_text, "Objective").split()) or "unavailable"
    allowed = _bullets(_section(work_text, "Allowed scope"))
    stop_gate = _bullets(_section(work_text, "Stop gate"))
    forbidden = _forbidden_scope(work_text)
    sync = (
        "unavailable"
        if git.ahead is None or git.behind is None
        else f"ahead={git.ahead}, behind={git.behind}"
    )
    blockers = errors or ["none"]
    lines = [
        "# Codex Foreman Brief",
        "",
        "> Deterministic routing summary only; repository authorities remain authoritative.",
        "",
        "## Control",
        "",
        f"- Phase: `{state.get('current_phase', 'unavailable')}`",
        f"- Phase state: `{state.get('phase_state', 'unavailable')}`",
        f"- Active work order: `{state.get('active_work_order', work.get('id', 'unavailable'))}`",
        "- Accepted implementation baseline: "
        f"`{state.get('accepted_code_baseline', 'unavailable')}`",
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
        "## Objective",
        "",
        objective,
        "",
        "## Allowed scope",
        "",
        *(f"- {item}" for item in (allowed or ("none recorded",))),
        "",
        "## Forbidden scope",
        "",
        *(f"- {item}" for item in (forbidden or ("none recorded",))),
        "",
        "## Required read set",
        "",
        *(f"- `{item}`" for item in reads),
        "",
        "## Validation / stop gate",
        "",
        *(f"- {item}" for item in (stop_gate or ("none recorded",))),
        "",
        "## Blockers",
        "",
        *(f"- {item}" for item in blockers),
        "",
    ]
    return "\n".join(lines), tuple(errors)


def write_foreman_brief(root: Path = ROOT) -> tuple[Path, tuple[str, ...]]:
    brief, errors = build_foreman_brief(root)
    output = root / BRIEF_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(brief, encoding="utf-8")
    return output, errors


def main() -> int:
    output, errors = write_foreman_brief(ROOT)
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

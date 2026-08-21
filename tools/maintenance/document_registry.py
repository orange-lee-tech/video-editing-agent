#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "docs" / "DOCUMENT_REGISTRY.json"
DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
DATE_KEYS = ("last updated", "updated", "effective date", "date", "日期", "更新日期")

CORE_PATHS = {
    "AGENTS.md",
    "docs/README.md",
    "docs/product/PRODUCT_CONSTITUTION_V1.0.md",
    "docs/architecture/ARCHITECTURE_CONTRACT_V0.2.md",
    "docs/operations/CURRENT_CONTROL_STATE.md",
    "docs/roadmap/CURRENT_PHASE_STATUS.md",
    "docs/operations/CURRENT_WORK_ORDER.md",
    "docs/roadmap/STAGE_A_COMPLETION_GATE.md",
}
LIVE_PATHS = {
    "docs/operations/CURRENT_CONTROL_STATE.md",
    "docs/roadmap/CURRENT_PHASE_STATUS.md",
    "docs/operations/CURRENT_WORK_ORDER.md",
}


def _run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def _tracked_files() -> list[str]:
    return sorted(line for line in _run_git("ls-files").splitlines() if line)


def _is_managed(path: str) -> bool:
    if path.startswith("docs/"):
        return Path(path).suffix.casefold() in {".md", ".json", ".yaml", ".yml"}
    if path in {"AGENTS.md", "README.md", "LICENSE_STATUS.md"}:
        return True
    if path == ".github/README.md" or path.startswith(".github/workflows/"):
        return Path(path).suffix.casefold() in {".md", ".yaml", ".yml"}
    if path in {"scripts/README.md", "src/README.md", "tests/README.md", "tools/README.md"}:
        return True
    if path.startswith("tools/") and path.endswith("/README.md"):
        return True
    return False


def _git_last_changed(managed: set[str]) -> dict[str, str]:
    dates: dict[str, str] = {}
    current_date: str | None = None
    output = _run_git("log", "--format=__DATE__%cs", "--name-only", "--no-renames")
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("__DATE__"):
            current_date = line.removeprefix("__DATE__")
            continue
        normalized = line.replace("\\", "/")
        if normalized in managed and normalized not in dates and current_date is not None:
            dates[normalized] = current_date
    return dates


def _declared_date(path: str) -> str | None:
    if path.startswith("docs/archive/"):
        return None
    file_path = ROOT / path
    if file_path.suffix.casefold() != ".md" or not file_path.exists():
        return None
    text = file_path.read_text(encoding="utf-8")
    for line in text.splitlines()[:80]:
        lowered = line.casefold()
        if any(key in lowered for key in DATE_KEYS):
            match = DATE_RE.search(line)
            if match:
                return match.group(1)
    return None


def _category(path: str) -> str:
    if path.startswith("docs/archive/"):
        return "archive"
    if path.startswith("docs/"):
        parts = path.split("/")
        return parts[1] if len(parts) > 2 else "docs-root"
    if path.startswith(".github/"):
        return "github"
    if path.startswith("scripts/"):
        return "scripts"
    if path.startswith("src/"):
        return "source-navigation"
    if path.startswith("tests/"):
        return "test-navigation"
    if path.startswith("tools/"):
        return "tool-navigation"
    return "repository-root"


def _lifecycle(path: str) -> str:
    if path.startswith("docs/archive/"):
        return "RETIRED"
    if path in LIVE_PATHS:
        return "LIVE"
    if path.startswith(("docs/validation/", "docs/logs/", "docs/research/")):
        return "EVIDENCE"
    return "ACTIVE"


def _attention(path: str) -> str:
    if path.startswith("docs/archive/"):
        return "EXCLUDED_DEFAULT"
    if path in CORE_PATHS:
        return "CORE"
    if path.startswith(("docs/validation/", "docs/logs/", "docs/research/")):
        return "EVIDENCE_ONLY"
    return "ON_DEMAND"


def _load_registry() -> dict[str, Any]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _validate_registry(registry: dict[str, Any], tracked: set[str]) -> list[str]:
    errors: list[str] = []
    if registry.get("schema") != "video-editing-agent-document-registry/v1":
        errors.append("DOCUMENT_REGISTRY.json has an unsupported schema")

    canonical_entries = registry.get("canonical_entries")
    if not isinstance(canonical_entries, list):
        errors.append("DOCUMENT_REGISTRY.json canonical_entries must be a list")
        canonical_entries = []

    for entry in canonical_entries:
        if not isinstance(entry, dict):
            errors.append("DOCUMENT_REGISTRY.json contains a non-object canonical entry")
            continue
        path = entry.get("path")
        if not isinstance(path, str) or not path:
            errors.append("DOCUMENT_REGISTRY.json canonical entry missing path")
            continue
        if path not in tracked:
            errors.append(f"canonical registry path is not tracked: {path}")
        if path.endswith(".md") and _declared_date(path) is None:
            errors.append(
                f"canonical active Markdown lacks a declared update/effective date: {path}"
            )

    excluded = registry.get("default_excluded")
    if not isinstance(excluded, list) or "docs/archive/**" not in excluded:
        errors.append("DOCUMENT_REGISTRY.json must exclude docs/archive/** by default")

    directory_map = registry.get("directory_map")
    archive_rule_ok = False
    if isinstance(directory_map, list):
        for entry in directory_map:
            if (
                isinstance(entry, dict)
                and entry.get("path") == "docs/archive/**"
                and entry.get("attention") == "EXCLUDED_DEFAULT"
            ):
                archive_rule_ok = True
                break
    if not archive_rule_ok:
        errors.append("DOCUMENT_REGISTRY.json must classify docs/archive/** as EXCLUDED_DEFAULT")

    return errors


def build_manifest() -> tuple[dict[str, Any], list[str]]:
    tracked = set(_tracked_files())
    managed = {path for path in tracked if _is_managed(path)}
    dates = _git_last_changed(managed)
    registry = _load_registry()
    errors = _validate_registry(registry, tracked)

    files: list[dict[str, Any]] = []
    for path in sorted(managed):
        declared = _declared_date(path)
        git_date = dates.get(path)
        effective = declared or git_date
        if effective is None:
            errors.append(f"managed document has no discoverable update date: {path}")
        files.append(
            {
                "path": path,
                "category": _category(path),
                "lifecycle": _lifecycle(path),
                "attention": _attention(path),
                "declared_updated": declared,
                "git_last_changed": git_date,
                "effective_updated": effective,
            }
        )

    manifest = {
        "schema": "video-editing-agent-document-manifest/v1",
        "registry": "docs/DOCUMENT_REGISTRY.json",
        "managed_file_count": len(files),
        "files": files,
    }
    return manifest, errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and validate the repository document registry manifest."
    )
    parser.add_argument(
        "--output", type=Path, help="Write the exhaustive JSON manifest to this path."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate registry invariants and exit non-zero on failure.",
    )
    args = parser.parse_args()

    manifest, errors = build_manifest()
    rendered = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=False) + "\n"

    if args.output is not None:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")

    if errors:
        print("Document registry FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Document registry PASSED: {manifest['managed_file_count']} managed files indexed.")
    if args.output is not None:
        print(f"Exhaustive manifest: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

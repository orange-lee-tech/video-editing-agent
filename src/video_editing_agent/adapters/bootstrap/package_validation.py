from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from video_editing_agent.adapters.bootstrap.runtime_manifest import (
    HashPolicy,
    InclusionPolicy,
    RuntimeManifest,
    load_runtime_manifest,
)

_FORBIDDEN_NAMES = {".git", ".private", ".tools", ".venv", "__pycache__"}
_FORBIDDEN_PREFIXES = (".uv-cache",)
_SECRET_ASSIGNMENT = re.compile(
    rb"(?i)(?:DEEPSEEK|GEMINI|OPENAI)_API_KEY\s*[=:]\s*['\"]?[A-Za-z0-9_-]{12,}"
)


@dataclass(frozen=True, slots=True)
class PackageInspection:
    staged_root: Path
    file_count: int
    total_bytes: int
    component_hashes: dict[str, str]


def inspect_staged_package(root: Path, manifest: RuntimeManifest) -> PackageInspection:
    staged = root.resolve()
    if not staged.is_dir():
        raise ValueError("staged package root does not exist")
    files = tuple(path for path in staged.rglob("*") if path.is_file())
    for path in staged.rglob("*"):
        relative = path.relative_to(staged)
        if any(
            part in _FORBIDDEN_NAMES or part.startswith(_FORBIDDEN_PREFIXES)
            for part in relative.parts
        ):
            raise ValueError(f"forbidden staged content: {relative.as_posix()}")
    hashes: dict[str, str] = {}
    for component in manifest.components:
        if component.inclusion is not InclusionPolicy.INCLUDE:
            continue
        assert component.relative_path is not None
        target = staged / Path(*component.relative_path.parts)
        if not target.exists():
            raise ValueError(f"required staged component is missing: {component.component_id}")
        if target.is_file():
            actual = _sha256(target)
            hashes[component.component_id] = actual
            if component.hash_policy is HashPolicy.EXACT and actual != component.sha256:
                raise ValueError(f"component hash mismatch: {component.component_id}")
        elif target.is_dir():
            hashes[component.component_id] = _tree_sha256(target)
    for path in files:
        if path.stat().st_size <= 2_000_000 and _SECRET_ASSIGNMENT.search(path.read_bytes()):
            raise ValueError(f"plaintext provider secret pattern found: {path.relative_to(staged)}")
    return PackageInspection(staged, len(files), sum(path.stat().st_size for path in files), hashes)


def write_build_evidence(
    destination: Path,
    inspection: PackageInspection,
    manifest: RuntimeManifest,
    *,
    source_sha: str,
) -> None:
    payload = {
        "schema": "video-editing-agent-package-evidence/v1",
        "source_git_sha": source_sha,
        "application_version": manifest.application_version,
        "staged_directory": inspection.staged_root.name,
        "file_count": inspection.file_count,
        "total_bytes": inspection.total_bytes,
        "component_hashes": dict(sorted(inspection.component_hashes.items())),
        "manifest_sha256": _sha256(
            inspection.staged_root / "_internal/resources/packaging/runtime-manifest.json"
        ),
    }
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix().encode()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(bytes.fromhex(_sha256(path)))
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--staged-root", type=Path)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--source-sha")
    args = parser.parse_args(argv)
    manifest = load_runtime_manifest(args.manifest)
    if args.staged_root is None:
        print(f"runtime manifest valid: {len(manifest.components)} components")
        return 0
    inspection = inspect_staged_package(args.staged_root, manifest)
    if args.evidence is not None:
        if not args.source_sha:
            raise ValueError("--source-sha is required with --evidence")
        write_build_evidence(args.evidence, inspection, manifest, source_sha=args.source_sha)
    print(f"staged package valid: {inspection.file_count} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

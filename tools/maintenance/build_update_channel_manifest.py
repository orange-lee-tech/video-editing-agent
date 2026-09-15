from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

from video_editing_agent.adapters.product.component_update import sha256_file
from video_editing_agent.adapters.product.update_ed25519 import public_key_from_seed
from video_editing_agent.adapters.product.update_signature import (
    UPDATE_MANIFEST_PUBLIC_KEY,
    signed_manifest_text,
)

_COMPONENTS_SCHEMA = "video-editing-agent/update-release-components/v1"
_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and sign the stable update-channel manifest")
    parser.add_argument("--version", required=True)
    parser.add_argument("--published-at", required=True)
    parser.add_argument("--installer", type=Path, required=True)
    parser.add_argument("--component-metadata", type=Path, required=True)
    parser.add_argument("--component-root", type=Path, required=True)
    parser.add_argument("--repository-slug", required=True)
    parser.add_argument("--release-notes-url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--seed-hex",
        default=os.environ.get("UPDATE_MANIFEST_SIGNING_KEY", ""),
        help="32-byte Ed25519 seed as hex; defaults to UPDATE_MANIFEST_SIGNING_KEY",
    )
    return parser


def build_signed_manifest(
    *,
    version: str,
    published_at: str,
    installer: Path,
    component_metadata: Path,
    component_root: Path,
    repository_slug: str,
    release_notes_url: str,
    seed: bytes,
) -> dict[str, object]:
    if _SEMVER.fullmatch(version) is None:
        raise ValueError("version must be semantic major.minor.patch")
    if len(seed) != 32:
        raise ValueError("update signing seed must be 32 bytes")
    if public_key_from_seed(seed) != UPDATE_MANIFEST_PUBLIC_KEY:
        raise ValueError("update signing seed does not match the embedded public key")
    if not installer.is_file():
        raise ValueError(f"installer is missing: {installer}")

    metadata = json.loads(component_metadata.read_text(encoding="utf-8"))
    if not isinstance(metadata, dict) or metadata.get("schema") != _COMPONENTS_SCHEMA:
        raise ValueError("unsupported update-release-components schema")
    if metadata.get("application_version") != version:
        raise ValueError("component metadata application_version does not match version")
    layout_version = metadata.get("layout_version")
    minimum_updater_version = metadata.get("minimum_updater_version")
    if isinstance(layout_version, bool) or not isinstance(layout_version, int) or layout_version < 1:
        raise ValueError("component metadata layout_version must be >= 1")
    if (
        isinstance(minimum_updater_version, bool)
        or not isinstance(minimum_updater_version, int)
        or minimum_updater_version < 1
    ):
        raise ValueError("component metadata minimum_updater_version must be >= 1")

    release_base = f"https://github.com/{repository_slug}/releases/download/v{version}"
    components: list[dict[str, object]] = []
    raw_components = metadata.get("components")
    if not isinstance(raw_components, list) or not raw_components:
        raise ValueError("component metadata has no components")
    for raw in raw_components:
        if not isinstance(raw, dict):
            raise ValueError("component metadata entry is not an object")
        component_id = raw.get("id")
        component_version = raw.get("version")
        filename = raw.get("filename")
        expected_sha = raw.get("sha256")
        expected_size = raw.get("size_bytes")
        if not all(
            isinstance(value, str) and value
            for value in (component_id, component_version, filename, expected_sha)
        ):
            raise ValueError("component metadata contains a blank identity field")
        if isinstance(expected_size, bool) or not isinstance(expected_size, int) or expected_size < 1:
            raise ValueError(f"component {component_id} has invalid size_bytes")
        archive = component_root / filename
        if not archive.is_file():
            raise ValueError(f"component archive is missing: {archive}")
        actual_sha = sha256_file(archive)
        actual_size = archive.stat().st_size
        if actual_sha != expected_sha.casefold():
            raise ValueError(f"component {component_id} SHA-256 does not match metadata")
        if actual_size != expected_size:
            raise ValueError(f"component {component_id} size does not match metadata")
        components.append(
            {
                "id": component_id,
                "version": component_version,
                "url": f"{release_base}/{filename}",
                "sha256": actual_sha,
                "size_bytes": actual_size,
            }
        )

    payload: dict[str, object] = {
        "version": version,
        "published_at": published_at,
        "release_notes_url": release_notes_url,
        "download_url": f"{release_base}/{installer.name}",
        "installer_sha256": sha256_file(installer),
        "mandatory": False,
        "layout_version": layout_version,
        "minimum_updater_version": minimum_updater_version,
        "components": components,
    }
    return json.loads(signed_manifest_text(payload, seed))


def main() -> int:
    args = _parser().parse_args()
    seed_hex = args.seed_hex.strip()
    if len(seed_hex) != 64:
        raise SystemExit("signing seed must be 32 bytes encoded as 64 hex characters")
    try:
        seed = bytes.fromhex(seed_hex)
    except ValueError as exc:
        raise SystemExit("signing seed must be hexadecimal") from exc
    document = build_signed_manifest(
        version=args.version,
        published_at=args.published_at,
        installer=args.installer,
        component_metadata=args.component_metadata,
        component_root=args.component_root,
        repository_slug=args.repository_slug,
        release_notes_url=args.release_notes_url,
        seed=seed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath

from video_editing_agent.adapters.bootstrap.runtime_manifest import load_runtime_manifest
from video_editing_agent.adapters.product.component_update import PATCH_SCHEMA, sha256_file
from video_editing_agent.adapters.product.update_state import (
    UPDATE_LAYOUT_VERSION,
    UPDATER_PROTOCOL_VERSION,
    InstalledComponentState,
    InstalledUpdateState,
    UpdateFileRecord,
    default_update_state_path,
    save_update_state,
)

APP_CORE = "app-core"
MEDIA_RUNTIME = "media-runtime"
TRANSNET_RUNTIME = "transnet-runtime"
_UPDATER_EXE = "VideoEditingAgent-updater.exe"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--runtime-manifest", type=Path, required=True)
    parser.add_argument("--application-version", required=True)
    return parser


def _component_for(relative: PurePosixPath) -> str | None:
    value = relative.as_posix()
    if value == _UPDATER_EXE:
        return None
    if value == "_internal/resources/packaging/update-state.json":
        return None
    if value.startswith("_internal/tools/"):
        return MEDIA_RUNTIME
    if value.startswith("_internal/runtimes/transnet/"):
        return TRANSNET_RUNTIME
    return APP_CORE


def _record(path: Path, relative: PurePosixPath) -> UpdateFileRecord:
    return UpdateFileRecord(relative, sha256_file(path), path.stat().st_size)


def build_components(
    *,
    staged_root: Path,
    output_dir: Path,
    runtime_manifest: Path,
    application_version: str,
) -> dict[str, object]:
    staged_root = staged_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = load_runtime_manifest(runtime_manifest)
    ffmpeg = manifest.component("ffmpeg")
    transnet = manifest.component("transnet-runtime")
    if ffmpeg is None or transnet is None:
        raise ValueError("runtime manifest must define ffmpeg and transnet-runtime")

    versions = {
        APP_CORE: application_version,
        MEDIA_RUNTIME: ffmpeg.version,
        TRANSNET_RUNTIME: transnet.version,
    }
    grouped: dict[str, list[tuple[Path, UpdateFileRecord]]] = defaultdict(list)
    for path in sorted(item for item in staged_root.rglob("*") if item.is_file()):
        relative = PurePosixPath(path.relative_to(staged_root).as_posix())
        component_id = _component_for(relative)
        if component_id is None:
            continue
        grouped[component_id].append((path, _record(path, relative)))

    missing = set(versions) - set(grouped)
    if missing:
        raise ValueError(f"staged update components are empty: {sorted(missing)}")

    state = InstalledUpdateState(
        application_version=application_version,
        layout_version=UPDATE_LAYOUT_VERSION,
        updater_version=UPDATER_PROTOCOL_VERSION,
        components=tuple(
            InstalledComponentState(
                component_id,
                versions[component_id],
                tuple(record for _path, record in grouped[component_id]),
            )
            for component_id in (APP_CORE, MEDIA_RUNTIME, TRANSNET_RUNTIME)
        ),
    )
    save_update_state(default_update_state_path(staged_root), state)

    release_components: list[dict[str, object]] = []
    for component in state.components:
        archive = output_dir / (
            f"VideoEditingAgent-Update-{component.component_id}-{application_version}.zip"
        )
        patch_payload = {
            "schema": PATCH_SCHEMA,
            "component_id": component.component_id,
            "version": component.version,
            "layout_version": UPDATE_LAYOUT_VERSION,
            "files": [
                {
                    "path": str(item.relative_path),
                    "sha256": item.sha256,
                    "size_bytes": item.size_bytes,
                }
                for item in component.files
            ],
        }
        with zipfile.ZipFile(
            archive,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as package:
            package.writestr(
                "patch.json",
                json.dumps(
                    patch_payload,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n",
            )
            by_relative = {
                str(record.relative_path): path
                for path, record in grouped[component.component_id]
            }
            for record in component.files:
                package.write(
                    by_relative[str(record.relative_path)],
                    f"payload/{record.relative_path.as_posix()}",
                )
        release_components.append(
            {
                "id": component.component_id,
                "version": component.version,
                "filename": archive.name,
                "sha256": sha256_file(archive),
                "size_bytes": archive.stat().st_size,
            }
        )

    release_metadata = {
        "schema": "video-editing-agent/update-release-components/v1",
        "application_version": application_version,
        "layout_version": UPDATE_LAYOUT_VERSION,
        "minimum_updater_version": UPDATER_PROTOCOL_VERSION,
        "components": release_components,
    }
    metadata_path = output_dir / "update-release-components.json"
    metadata_path.write_text(
        json.dumps(
            release_metadata,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return release_metadata


def main() -> int:
    args = _parser().parse_args()
    build_components(
        staged_root=args.staged_root,
        output_dir=args.output_dir,
        runtime_manifest=args.runtime_manifest,
        application_version=args.application_version,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

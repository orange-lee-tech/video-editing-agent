from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
from typing import Any

MEDIA_SUFFIXES = frozenset({".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"})
COVERAGE_VALUES = frozenset(
    {
        "camera_pan",
        "hand_object_interaction",
        "handheld_product_demo",
        "low_motion",
        "noisy_blurred",
        "talking_head",
    }
)


def _probe(path: pathlib.Path, ffprobe: pathlib.Path) -> dict[str, Any]:
    completed = subprocess.run(
        [
            str(ffprobe),
            "-v",
            "error",
            "-show_entries",
            "format=duration,size:stream=codec_type,codec_name,width,height,avg_frame_rate,"
            "sample_rate,channels",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    root = json.loads(completed.stdout)
    streams = []
    for stream in root["streams"]:
        streams.append({key: stream[key] for key in sorted(stream)})
    return {
        "duration_seconds": round(float(root["format"]["duration"]), 6),
        "size_bytes": int(root["format"]["size"]),
        "streams": streams,
    }


def build_manifest(
    media_root: pathlib.Path,
    ffprobe: pathlib.Path,
    existing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    prior = {item["sha256"]: item for item in (existing or {}).get("clips", [])}
    clips = []
    paths = sorted(
        (path for path in media_root.rglob("*") if path.suffix.lower() in MEDIA_SUFFIXES),
        key=lambda path: path.relative_to(media_root).as_posix(),
    )
    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        previous = prior.get(digest, {})
        coverage = previous.get("coverage", [])
        if not isinstance(coverage, list) or any(item not in COVERAGE_VALUES for item in coverage):
            raise ValueError(f"invalid coverage for anonymous clip {digest[:12]}")
        item = {
            "clip_id": previous.get("clip_id", f"clip_{digest[:12]}"),
            "sha256": digest,
            **_probe(path, ffprobe),
            "coverage": sorted(coverage),
        }
        clips.append(item)
    clips.sort(key=lambda item: item["clip_id"])
    return {"schema_version": "r0.8h-local-corpus-v1", "clips": clips}


def _encoded(manifest: dict[str, Any]) -> str:
    return json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate/check anonymized local media manifest")
    parser.add_argument("--media-root", type=pathlib.Path, required=True)
    parser.add_argument("--manifest", type=pathlib.Path, required=True)
    parser.add_argument("--ffprobe", type=pathlib.Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    existing = (
        json.loads(args.manifest.read_text(encoding="utf-8")) if args.manifest.exists() else None
    )
    generated = _encoded(build_manifest(args.media_root, args.ffprobe, existing))
    if args.check:
        if not args.manifest.exists() or args.manifest.read_text(encoding="utf-8") != generated:
            print("local media corpus manifest is stale", file=sys.stderr)
            return 1
        return 0
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(generated, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

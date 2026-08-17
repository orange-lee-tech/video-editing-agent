from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, cast

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.storage.project.workspace import ProjectWorkspace


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify persisted Planning and real-media Editing ProductFlow evidence."
    )
    parser.add_argument("--planning-result", type=Path, required=True)
    parser.add_argument("--editing-result", type=Path, required=True)
    parser.add_argument("--source-media", type=Path, required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--ffprobe", default="ffprobe")
    return parser


def _load_json(path: Path) -> dict[str, Any]:
    resolved = path.expanduser().resolve(strict=True)
    value = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {resolved}")
    return cast(dict[str, Any], value)


def _ref(value: object, name: str) -> EntityRevisionRef:
    if not isinstance(value, dict):
        raise RuntimeError(f"{name} must be an entity revision object")
    entity_id = value.get("entity_id")
    revision = value.get("revision")
    if not isinstance(entity_id, str) or not entity_id:
        raise RuntimeError(f"{name}.entity_id is invalid")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise RuntimeError(f"{name}.revision is invalid")
    return EntityRevisionRef(entity_id, revision)


def _require_completed(result: dict[str, Any], mode: str) -> None:
    if result.get("mode") != mode:
        raise RuntimeError(f"Expected mode={mode}, got {result.get('mode')!r}")
    if result.get("outcome") != "completed":
        raise RuntimeError(
            f"{mode} ProductFlow did not complete: "
            f"outcome={result.get('outcome')!r} diagnostic={result.get('diagnostic')!r}"
        )
    events = result.get("events")
    if not isinstance(events, list) or not events:
        raise RuntimeError(f"{mode} result has no progress events")
    final = events[-1]
    if not isinstance(final, dict) or final.get("stage") != "completed":
        raise RuntimeError(f"{mode} progress did not terminate at completed")


def _verify_planning(result: dict[str, Any]) -> None:
    _require_completed(result, "planning")
    project = Path(str(result["project"])).resolve(strict=True)
    workspace = ProjectWorkspace.open(project)

    brief_ref = _ref(result.get("brief_ref"), "planning.brief_ref")
    script_ref = _ref(result.get("script_plan_ref"), "planning.script_plan_ref")
    shooting_ref = _ref(result.get("shooting_plan_ref"), "planning.shooting_plan_ref")

    brief = workspace.briefs.load(brief_ref)
    script = workspace.scripts.load(script_ref)
    shooting = workspace.shooting_plans.load(shooting_ref)

    if brief.envelope.id != brief_ref.entity_id or brief.envelope.revision != brief_ref.revision:
        raise RuntimeError("Planning Brief exact revision did not reload")
    if script.brief_ref != brief_ref:
        raise RuntimeError("Persisted ScriptPlan lost exact Brief lineage")
    if shooting.script_plan_ref != script_ref:
        raise RuntimeError("Persisted ShootingPlan lost exact ScriptPlan lineage")

    print("Planning Engineering Probe: PASS")
    print(f"planning_brief_ref={brief_ref.entity_id}@{brief_ref.revision}")
    print(f"planning_script_ref={script_ref.entity_id}@{script_ref.revision}")
    print(f"planning_shooting_ref={shooting_ref.entity_id}@{shooting_ref.revision}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _ffprobe(path: Path, executable: str) -> dict[str, Any]:
    completed = subprocess.run(
        [
            executable,
            "-v",
            "error",
            "-show_entries",
            "format=format_name,duration:stream=codec_type,codec_name",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    value = json.loads(completed.stdout)
    if not isinstance(value, dict):
        raise RuntimeError("ffprobe did not return a JSON object")
    return cast(dict[str, Any], value)


def _verify_editing(
    result: dict[str, Any],
    source_media: Path,
    expected_source_sha256: str,
    ffprobe_executable: str,
) -> None:
    _require_completed(result, "editing")
    project = Path(str(result["project"])).resolve(strict=True)
    workspace = ProjectWorkspace.open(project)

    source = source_media.expanduser().resolve(strict=True)
    actual_source_sha = _sha256(source)
    if actual_source_sha.lower() != expected_source_sha256.strip().lower():
        raise RuntimeError("Original source media changed during Editing ProductFlow")

    brief_ref = _ref(result.get("brief_ref"), "editing.brief_ref")
    edit_plan_ref = _ref(result.get("edit_plan_ref"), "editing.edit_plan_ref")
    edl_ref = _ref(result.get("edl_ref"), "editing.edl_ref")

    brief = workspace.briefs.load(brief_ref)
    edit_plan = workspace.edit_plans.load(edit_plan_ref)
    edl = workspace.edls.load(edl_ref)

    if brief.envelope.id != brief_ref.entity_id or brief.envelope.revision != brief_ref.revision:
        raise RuntimeError("Editing Brief exact revision did not reload")
    if edit_plan.brief_ref != brief_ref:
        raise RuntimeError("Persisted EditPlan lost exact Brief lineage")
    reloaded_edl_ref = EntityRevisionRef(edl.envelope.id, edl.envelope.revision)
    if reloaded_edl_ref != edl_ref:
        raise RuntimeError("Persisted canonical EDL exact revision did not reload")
    if edl.edit_plan_ref != edit_plan_ref:
        raise RuntimeError("Persisted canonical EDL lost exact EditPlan lineage")
    if not edl.segments:
        raise RuntimeError("Persisted canonical EDL contains no segments")
    if any(
        segment.source_range.start.as_fraction() < 0
        or segment.source_range.duration.as_fraction() <= 0
        for segment in edl.segments
    ):
        raise RuntimeError("Persisted canonical EDL contains invalid grounded source ranges")

    output_raw = result.get("output")
    if not isinstance(output_raw, str) or not output_raw:
        raise RuntimeError("Editing result did not expose a final output path")
    output = Path(output_raw).resolve(strict=True)
    if output == source:
        raise RuntimeError("Editing output overwrote the original source")

    review = result.get("review")
    if not isinstance(review, dict) or review.get("disposition") != "pass":
        raise RuntimeError(f"Review did not PASS: {review!r}")

    media = _ffprobe(output, ffprobe_executable)
    format_info = media.get("format")
    streams = media.get("streams")
    if not isinstance(format_info, dict) or not isinstance(streams, list):
        raise RuntimeError("Rendered output has incomplete ffprobe metadata")
    format_name = str(format_info.get("format_name", ""))
    if "mp4" not in format_name and "mov" not in format_name:
        raise RuntimeError(f"Rendered output is not an MP4-family container: {format_name!r}")
    try:
        duration = float(format_info.get("duration", 0.0))
    except (TypeError, ValueError) as exc:
        raise RuntimeError("Rendered output duration is invalid") from exc
    if duration <= 0:
        raise RuntimeError("Rendered output duration must be positive")

    codec_types = {
        stream.get("codec_type")
        for stream in streams
        if isinstance(stream, dict) and isinstance(stream.get("codec_type"), str)
    }
    if "video" not in codec_types:
        raise RuntimeError("Rendered MP4 has no video stream")
    if "audio" not in codec_types:
        raise RuntimeError("Rendered MP4 has no audio stream despite audible-output intent")

    print("Editing Engineering Probe: PASS")
    print(f"editing_brief_ref={brief_ref.entity_id}@{brief_ref.revision}")
    print(f"editing_edit_plan_ref={edit_plan_ref.entity_id}@{edit_plan_ref.revision}")
    print(f"editing_edl_ref={edl_ref.entity_id}@{edl_ref.revision}")
    print(f"rendered_output={output}")
    print(f"rendered_duration_seconds={duration:.3f}")
    print("canonical_edl_second_process_exact_revision_reload=PASS")
    print("canonical_edl_lineage_reload=PASS")
    print("source_original_hash_preserved=PASS")
    print("real_ffmpeg_mp4_video_audio=PASS")
    print("review_pass=PASS")


def main() -> int:
    args = _parser().parse_args()
    planning = _load_json(args.planning_result)
    editing = _load_json(args.editing_result)
    _verify_planning(planning)
    _verify_editing(editing, args.source_media, args.source_sha256, args.ffprobe)
    print("Product Flow Engineering Probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

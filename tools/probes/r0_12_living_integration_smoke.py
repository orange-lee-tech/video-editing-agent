from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from video_editing_agent.application.edl_builder import (
    DeterministicEDLBuilder,
    EDLBuildRequest,
)
from video_editing_agent.application.ports.asset_media import ResolvedLocalAssetMedia
from video_editing_agent.application.ports.audio_editorial import (
    AudioMixDecision,
    SourceAudioPolicy,
)
from video_editing_agent.application.ports.renderer import OutputSpec, RenderRequest
from video_editing_agent.domain.common.entity import (
    EntityEnvelope,
    EntityRevisionRef,
    EntityStatus,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.model import EditPlan, EditSlot
from video_editing_agent.domain.edit.resolution import CandidateWindow
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.editing.resolver.optimizer import ResolverCandidate, optimize_sequence
from video_editing_agent.render.edl_ffmpeg import FFmpegEDLRenderer

NOW = datetime(2026, 8, 16, tzinfo=UTC)
OUTPUT = Path(".private/probes/r0_12_living_smoke")
FFMPEG = Path(".tools/ffmpeg-8.1/ffmpeg-8.1-full_build/bin/ffmpeg.exe")
FFPROBE = Path(".tools/ffmpeg-8.1/ffmpeg-8.1-full_build/bin/ffprobe.exe")


def _envelope(identity: str) -> EntityEnvelope:
    return EntityEnvelope(identity, 1, "0.2", EntityStatus.VALID, NOW, "r0.12-smoke")


def _run(
    arguments: list[str], *, binary: bool = False
) -> subprocess.CompletedProcess[bytes] | subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        check=True,
        capture_output=True,
        text=not binary,
        shell=False,
    )


def _fixture(path: Path, color: str, frequency: int) -> None:
    _run(
        [
            str(FFMPEG),
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c={color}:s=320x192:r=30:d=2",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency={frequency}:sample_rate=48000:duration=2",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            str(path),
        ]
    )


def _candidate(identity: str, shot: str, start: MediaTime, score: float) -> ResolverCandidate:
    return ResolverCandidate(
        CandidateWindow(
            identity,
            EntityRevisionRef(shot, 1),
            MediaTimeRange(start, MediaTime(1, 1)),
            score,
            evidence_refs=(f"synthetic-grounding:{identity}",),
        ),
        score,
        score,
        score,
    )


def _probe(path: Path) -> dict[str, object]:
    completed = _run(
        [
            str(FFPROBE),
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,width,height,r_frame_rate",
            "-of",
            "json",
            str(path),
        ]
    )
    assert isinstance(completed.stdout, str)
    return json.loads(completed.stdout)


def _pixel(path: Path, at: str) -> tuple[int, int, int]:
    completed = _run(
        [
            str(FFMPEG),
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            at,
            "-i",
            str(path),
            "-frames:v",
            "1",
            "-vf",
            "scale=1:1",
            "-pix_fmt",
            "rgb24",
            "-f",
            "rawvideo",
            "pipe:1",
        ],
        binary=True,
    )
    assert isinstance(completed.stdout, bytes) and len(completed.stdout) == 3
    return tuple(completed.stdout)


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    media_paths = (OUTPUT / "source-red.mp4", OUTPUT / "source-blue.mp4")
    _fixture(media_paths[0], "red", 440)
    _fixture(media_paths[1], "blue", 660)
    plan = EditPlan(
        _envelope("smoke-plan"),
        EntityRevisionRef("script", 1),
        EntityRevisionRef("shooting", 1),
        (EditSlot("opening", "opening", 0), EditSlot("proof", "proof", 1)),
    )
    winner_red = _candidate("candidate-red", "shot-red", MediaTime(1, 4), 0.95)
    loser_blue = _candidate("candidate-blue-low", "shot-blue", MediaTime(0, 1), 0.2)
    winner_blue = _candidate("candidate-blue", "shot-blue", MediaTime(1, 2), 0.9)
    loser_red = _candidate("candidate-red-low", "shot-red", MediaTime(1, 1), 0.1)
    candidates = {
        "opening": (loser_blue, winner_red),
        "proof": (loser_red, winner_blue),
    }
    plan_ref = EntityRevisionRef("smoke-plan", 1)
    decisions = optimize_sequence(plan, candidates, plan_ref=plan_ref)
    repeated = optimize_sequence(plan, candidates, plan_ref=plan_ref)
    selected_ranges = tuple(decision.selections[0].selected_source_range for decision in decisions)
    selected_ids = tuple(
        next(
            candidate.window.candidate_id
            for candidate in candidates[slot.slot_id]
            if candidate.window.shot_ref == decision.selections[0].shot_ref
            and candidate.window.source_range == decision.selections[0].selected_source_range
        )
        for slot, decision in zip(plan.slots, decisions, strict=True)
    )
    shots = (
        Shot(
            _envelope("shot-red"),
            EntityRevisionRef("asset-red", 1),
            boundary_method="synthetic-smoke",
            source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(2, 1)),
        ),
        Shot(
            _envelope("shot-blue"),
            EntityRevisionRef("asset-blue", 1),
            boundary_method="synthetic-smoke",
            source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(2, 1)),
        ),
    )
    built = DeterministicEDLBuilder().build(
        EDLBuildRequest(
            _envelope("smoke-edl"),
            plan,
            decisions,
            shots,
            audio_mix=AudioMixDecision("smoke-mix-preserve", plan_ref, SourceAudioPolicy.PRESERVE),
        )
    )
    assert built.edl is not None
    video_segments = tuple(item for item in built.edl.ordered_segments if item.track_id == "video")
    output_path = OUTPUT / "resolver_edl_renderer_smoke.mp4"
    media = (
        ResolvedLocalAssetMedia(EntityRevisionRef("asset-red", 1), media_paths[0]),
        ResolvedLocalAssetMedia(EntityRevisionRef("asset-blue", 1), media_paths[1]),
    )
    rendered = FFmpegEDLRenderer(str(FFMPEG), str(FFPROBE)).render(
        RenderRequest(built.edl, tuple(reversed(media)), OutputSpec(output_path, 320, 192, 30))
    )
    probe = _probe(output_path) if rendered.is_rendered else {}
    first_pixel = _pixel(output_path, "0.25") if rendered.is_rendered else (0, 0, 0)
    second_pixel = _pixel(output_path, "1.25") if rendered.is_rendered else (0, 0, 0)
    streams = probe.get("streams", [])
    assert isinstance(streams, list)
    video_stream = next((item for item in streams if item.get("codec_type") == "video"), {})
    expected_ranges = (winner_red.window.source_range, winner_blue.window.source_range)
    gates = {
        "ACTUAL_OPTIMIZER_EXECUTED": all(
            decision.reasons == ("highest deterministic feasible sequence utility",)
            for decision in decisions
        ),
        "OPTIMIZER_DETERMINISTIC": decisions == repeated,
        "GROUNDED_WINDOWS_SELECTED": selected_ids == ("candidate-red", "candidate-blue")
        and selected_ranges == expected_ranges,
        "SELECTIONS_SURVIVE_EDL": tuple(item.source_range for item in video_segments)
        == expected_ranges,
        "EDL_TIMELINE_EXACT": tuple(item.timeline_range.start for item in video_segments)
        == (MediaTime(0, 1), MediaTime(1, 1)),
        "RENDERED_AND_VERIFIED": rendered.is_rendered and output_path.is_file(),
        "FINAL_DURATION_AND_CANVAS": probe.get("format", {}).get("duration") == "2.000000"
        and video_stream.get("width") == 320
        and video_stream.get("height") == 192
        and video_stream.get("r_frame_rate") == "30/1",
        "AUDIO_POLICY_PRESERVED": any(item.get("codec_type") == "audio" for item in streams),
        "FINAL_VISUAL_ORDER": first_pixel[0] > first_pixel[2] and second_pixel[2] > second_pixel[0],
        "NO_INVENTED_SPATIAL_DECISION": all(
            item.spatial_automation is None for item in video_segments
        ),
    }
    report = {
        "classification": "ENGINEERING_FOUNDATION_ONLY",
        "gates": {name: "PASS" if passed else "FAIL" for name, passed in gates.items()},
        "selected_candidate_ids": selected_ids,
        "selected_source_ranges": [
            {
                "start": [item.start.value, item.start.scale],
                "duration": [item.duration.value, item.duration.scale],
            }
            for item in selected_ranges
        ],
        "edl_timeline_starts": [
            [item.timeline_range.start.value, item.timeline_range.start.scale]
            for item in video_segments
        ],
        "sampled_rgb": {"first": first_pixel, "second": second_pixel},
        "output": str(output_path),
        "ffprobe": probe,
        "spatial_evidence_limitation": (
            "No approved ReframeDecision exists naturally in this grounded Resolver smoke; "
            "R0.12 Renderer spatial execution remains covered by r0_12_edl_renderer_live.py."
        ),
        "pass": all(gates.values()),
    }
    (OUTPUT / "smoke_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(report, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
import subprocess
from dataclasses import replace
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
from video_editing_agent.application.ports.spatial_composer import (
    OutputCanvas,
    PixelCrop,
    ReframeDecision,
    SourceFrameGeometry,
    SpatialCropKeyframe,
    SpatialInterpolationMode,
    SpatialTransformKeyframe,
    SpatialTransformPlan,
)
from video_editing_agent.domain.common.entity import (
    EntityEnvelope,
    EntityRevisionRef,
    EntityStatus,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.model import EditPlan, EditSlot
from video_editing_agent.domain.edit.resolution import (
    ResolutionDecision,
    ResolutionDecisionType,
    ResolvedSelection,
)
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.render.edl_ffmpeg import FFmpegEDLRenderer

NOW = datetime(2026, 8, 16, tzinfo=UTC)
OUTPUT = Path(".private/probes/r0_12_renderer")
FFMPEG = Path(".tools/ffmpeg-8.1/ffmpeg-8.1-full_build/bin/ffmpeg.exe")
FFPROBE = Path(".tools/ffmpeg-8.1/ffmpeg-8.1-full_build/bin/ffprobe.exe")


def _envelope(identity: str) -> EntityEnvelope:
    return EntityEnvelope(identity, 1, "0.2", EntityStatus.VALID, NOW, "r0.12-probe")


def _run(arguments: list[str]) -> None:
    completed = subprocess.run(arguments, check=False, capture_output=True, text=True, shell=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr)


def _make_fixture(path: Path, color: str, frequency: int) -> None:
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
            f"color=c={color}:s=320x192:r=30:d=1",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency={frequency}:sample_rate=48000:duration=1",
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


def _spatial(selection_id: str, shot_ref: EntityRevisionRef, offset: int) -> ReframeDecision:
    plan = SpatialTransformPlan(
        selection_id,
        shot_ref,
        MediaTimeRange(MediaTime(0, 1), MediaTime(1, 1)),
        SourceFrameGeometry(320, 192),
        OutputCanvas(180, 320),
        (
            SpatialCropKeyframe(MediaTime(0, 1), PixelCrop(offset, 0, 108, 192)),
            SpatialCropKeyframe(MediaTime(1, 2), PixelCrop(offset + 20, 0, 108, 192)),
        ),
        SpatialInterpolationMode.LINEAR,
    )
    legacy = tuple(
        SpatialTransformKeyframe(
            item.source_time,
            (item.crop.left + item.crop.width / 2) / 320,
            (item.crop.top + item.crop.height / 2) / 192,
            320 / item.crop.width,
        )
        for item in plan.keyframes
    )
    return ReframeDecision(
        f"reframe-{selection_id}",
        selection_id,
        "track",
        legacy,
        1.0,
        transform_plan=plan,
    )


def _probe(path: Path) -> dict[str, object]:
    completed = subprocess.run(
        [
            str(FFPROBE),
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,width,height,r_frame_rate",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
        shell=False,
    )
    return json.loads(completed.stdout)


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    assets = (OUTPUT / "fixture-a.mp4", OUTPUT / "fixture-b.mp4")
    _make_fixture(assets[0], "red", 440)
    _make_fixture(assets[1], "blue", 660)
    plan = EditPlan(
        _envelope("edit-plan"),
        EntityRevisionRef("script", 1),
        EntityRevisionRef("shooting", 1),
        (EditSlot("first", "first", 0), EditSlot("second", "second", 1)),
    )
    selections = tuple(
        ResolvedSelection(
            f"selection-{index}",
            EntityRevisionRef(f"shot-{index}", 1),
            MediaTimeRange(MediaTime(0, 1), MediaTime(1, 1)),
            0,
        )
        for index in range(2)
    )
    decisions = tuple(
        ResolutionDecision(
            f"resolution-{index}",
            EntityRevisionRef("edit-plan", 1),
            (("first", "second")[index],),
            ResolutionDecisionType.RESOLVED,
            (selections[index],),
        )
        for index in range(2)
    )
    shots = tuple(
        Shot(
            _envelope(f"shot-{index}"),
            EntityRevisionRef(f"asset-{index}", 1),
            boundary_method="probe",
            source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(1, 1)),
        )
        for index in range(2)
    )
    base_request = EDLBuildRequest(
        _envelope("edl-render-probe"),
        plan,
        decisions,
        shots,
        tuple(
            _spatial(selection.selection_id, selection.shot_ref, index * 20)
            for index, selection in enumerate(selections)
        ),
    )
    plan_ref = EntityRevisionRef("edit-plan", 1)
    preserve = DeterministicEDLBuilder().build(
        replace(
            base_request,
            audio_mix=AudioMixDecision("mix-preserve", plan_ref, SourceAudioPolicy.PRESERVE),
        )
    )
    mute = DeterministicEDLBuilder().build(
        replace(
            base_request,
            envelope=_envelope("edl-render-probe-muted"),
            audio_mix=AudioMixDecision("mix-mute", plan_ref, SourceAudioPolicy.MUTE),
        )
    )
    assert preserve.edl is not None and mute.edl is not None
    media = tuple(
        ResolvedLocalAssetMedia(EntityRevisionRef(f"asset-{index}", 1), path)
        for index, path in enumerate(assets)
    )
    renderer = FFmpegEDLRenderer(str(FFMPEG), str(FFPROBE))
    preserve_path = OUTPUT / "preserve.mp4"
    mute_path = OUTPUT / "mute.mp4"
    preserve_result = renderer.render(
        RenderRequest(preserve.edl, media, OutputSpec(preserve_path, 180, 320, 30))
    )
    mute_result = renderer.render(
        RenderRequest(mute.edl, media, OutputSpec(mute_path, 180, 320, 30))
    )
    preserve_probe = _probe(preserve_path) if preserve_result.is_rendered else {}
    mute_probe = _probe(mute_path) if mute_result.is_rendered else {}

    def streams(value: dict[str, object]) -> list[dict[str, object]]:
        raw = value.get("streams", [])
        assert isinstance(raw, list)
        return raw

    preserved_streams = streams(preserve_probe)
    muted_streams = streams(mute_probe)
    video = next((item for item in preserved_streams if item.get("codec_type") == "video"), {})
    preserve_graph = (
        ""
        if preserve_result.artifact is None
        else preserve_result.artifact.ffmpeg_invocation.arguments[
            preserve_result.artifact.ffmpeg_invocation.arguments.index("-filter_complex") + 1
        ]
    )
    gates = {
        "PRESERVE_RENDERED": preserve_result.is_rendered and preserve_path.is_file(),
        "MUTE_RENDERED": mute_result.is_rendered and mute_path.is_file(),
        "TIMELINE_DURATION": preserve_probe.get("format", {}).get("duration") == "2.000000",
        "EXPECTED_CANVAS": video.get("width") == 180 and video.get("height") == 320,
        "EXPECTED_FRAME_RATE": video.get("r_frame_rate") == "30/1",
        "SPATIAL_EDL_EXECUTED": "crop=108:192:" in preserve_graph
        and "max(t-1/2\\,0)" in preserve_graph,
        "AUDIO_POLICY_OBSERVABLE": any(
            item.get("codec_type") == "audio" for item in preserved_streams
        )
        and not any(item.get("codec_type") == "audio" for item in muted_streams),
        "NO_SHELL_COMMAND": preserve_result.artifact is not None
        and Path(preserve_result.artifact.ffmpeg_invocation.tool_id).name.casefold() == "ffmpeg.exe"
        and isinstance(preserve_result.artifact.ffmpeg_invocation.arguments, tuple),
    }
    report = {
        "classification": "ENGINEERING_FOUNDATION_ONLY",
        "gates": {name: "PASS" if passed else "FAIL" for name, passed in gates.items()},
        "outputs": {"preserve": str(preserve_path), "mute": str(mute_path)},
        "preserve_probe": preserve_probe,
        "mute_probe": mute_probe,
        "pass": all(gates.values()),
    }
    print(json.dumps(report, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

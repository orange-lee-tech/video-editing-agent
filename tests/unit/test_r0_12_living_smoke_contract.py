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
from video_editing_agent.render.edl_ffmpeg import compile_ffmpeg_render

NOW = datetime(2026, 8, 16, tzinfo=UTC)


def _envelope(identity: str) -> EntityEnvelope:
    return EntityEnvelope(identity, 1, "0.2", EntityStatus.VALID, NOW, "test")


def _candidate(identity: str, shot: str, start: MediaTime, score: float) -> ResolverCandidate:
    return ResolverCandidate(
        CandidateWindow(
            identity,
            EntityRevisionRef(shot, 1),
            MediaTimeRange(start, MediaTime(1, 1)),
            score,
            evidence_refs=(f"evidence:{identity}",),
        ),
        score,
        score,
        score,
    )


def test_actual_optimizer_output_survives_builder_and_renderer_planning(tmp_path: Path) -> None:
    plan = EditPlan(
        _envelope("plan"),
        EntityRevisionRef("script", 1),
        EntityRevisionRef("shooting", 1),
        (EditSlot("first", "first", 0), EditSlot("second", "second", 1)),
    )
    winner_a = _candidate("winner-a", "shot-a", MediaTime(1, 4), 0.95)
    loser_a = _candidate("loser-a", "shot-b", MediaTime(0, 1), 0.2)
    winner_b = _candidate("winner-b", "shot-b", MediaTime(1, 2), 0.9)
    loser_b = _candidate("loser-b", "shot-a", MediaTime(1, 1), 0.1)
    decisions = optimize_sequence(
        plan,
        {"first": (loser_a, winner_a), "second": (loser_b, winner_b)},
        plan_ref=EntityRevisionRef("plan", 1),
    )
    expected = (winner_a.window.source_range, winner_b.window.source_range)
    assert tuple(item.selections[0].selected_source_range for item in decisions) == expected

    shots = tuple(
        Shot(
            _envelope(f"shot-{suffix}"),
            EntityRevisionRef(f"asset-{suffix}", 1),
            boundary_method="test",
            source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(2, 1)),
        )
        for suffix in ("a", "b")
    )
    built = DeterministicEDLBuilder().build(
        EDLBuildRequest(
            _envelope("edl"),
            plan,
            decisions,
            shots,
            audio_mix=AudioMixDecision(
                "mix", EntityRevisionRef("plan", 1), SourceAudioPolicy.PRESERVE
            ),
        )
    )
    assert built.edl is not None
    video = tuple(item for item in built.edl.ordered_segments if item.track_id == "video")
    assert tuple(item.source_range for item in video) == expected
    assert tuple(item.timeline_range.start for item in video) == (
        MediaTime(0, 1),
        MediaTime(1, 1),
    )

    media = []
    for suffix in ("a", "b"):
        path = tmp_path / f"{suffix}.mp4"
        path.touch()
        media.append(ResolvedLocalAssetMedia(EntityRevisionRef(f"asset-{suffix}", 1), path))
    compiled = compile_ffmpeg_render(
        RenderRequest(
            built.edl,
            tuple(reversed(media)),
            OutputSpec(tmp_path / "smoke.mp4", 320, 192, 30),
        )
    )

    assert compiled.plan is not None
    assert compiled.plan.expected_duration == MediaTime(2, 1)
    assert compiled.plan.expects_audio
    graph = compiled.plan.invocation.arguments[
        compiled.plan.invocation.arguments.index("-filter_complex") + 1
    ]
    assert "trim=start=0.250:duration=1.000" in graph
    assert "trim=start=0.500:duration=1.000" in graph

import json
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest

from video_editing_agent.application.ports.asset_media import ResolvedLocalAssetMedia
from video_editing_agent.application.ports.renderer import OutputSpec, RenderRequest
from video_editing_agent.application.subtitle_builder import compile_subtitle_cues
from video_editing_agent.domain.common.entity import (
    EntityEnvelope,
    EntityRevisionRef,
    EntityStatus,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edl import (
    EDL,
    EDLDiagnosticCode,
    EDLSegment,
    EDLSubtitleCue,
    EDLTrack,
    EDLTrackFamily,
    StructuredSubtitleCue,
    SubtitleEmphasisSpan,
    SubtitleEmphasisStyle,
    SubtitleLayoutRegion,
    decode_edl,
    encode_edl,
    validate_edl,
)
from video_editing_agent.render.edl_ffmpeg import build_ass_subtitles, compile_ffmpeg_render


def _edl() -> EDL:
    return EDL(
        EntityEnvelope(
            "subtitle-edl",
            1,
            "0.2",
            EntityStatus.VALID,
            datetime(2026, 8, 16, tzinfo=UTC),
            "test",
        ),
        EntityRevisionRef("plan", 1),
        (
            EDLSegment(
                "video",
                EntityRevisionRef("asset", 1),
                source_range=MediaTimeRange(MediaTime(1, 2), MediaTime(3, 1)),
                timeline_range=MediaTimeRange(MediaTime(0, 1), MediaTime(3, 1)),
            ),
        ),
        (EDLTrack("video", EDLTrackFamily.VIDEO),),
    )


def _cues() -> tuple[StructuredSubtitleCue, ...]:
    return (
        StructuredSubtitleCue(
            "english",
            MediaTimeRange(MediaTime(1, 4), MediaTime(1, 1)),
            "Use {safe}, C:\\clips\nnow 'quoted'",
            "en-US",
            "speaker-a",
            (SubtitleEmphasisSpan(4, 10, SubtitleEmphasisStyle.BOLD),),
            SubtitleLayoutRegion.LOWER_SAFE,
        ),
        StructuredSubtitleCue(
            "chinese",
            MediaTimeRange(MediaTime(3, 2), MediaTime(1, 1)),
            "中文也可以",
            "zh-CN",
            emphasis=(SubtitleEmphasisSpan(0, 2, SubtitleEmphasisStyle.HIGHLIGHT),),
            layout=SubtitleLayoutRegion.UPPER_SAFE,
        ),
    )


def test_builder_preserves_approved_text_exact_rational_time_and_intent() -> None:
    result = compile_subtitle_cues(_edl(), tuple(reversed(_cues())))

    assert {track.family for track in result.effective_tracks} == {
        EDLTrackFamily.VIDEO,
        EDLTrackFamily.SUBTITLE,
    }
    assert tuple(cue.cue_id for cue in result.ordered_subtitle_cues) == ("english", "chinese")
    english = result.ordered_subtitle_cues[0]
    assert english.text == _cues()[0].text
    assert english.timeline_range == _cues()[0].timeline_range
    assert english.speaker_ref == "speaker-a"


def test_subtitle_codec_round_trip_is_canonical_and_exact() -> None:
    original = compile_subtitle_cues(_edl(), tuple(reversed(_cues())))

    encoded = encode_edl(original)
    decoded = decode_edl(encoded)

    assert decoded == replace(
        original,
        segments=original.ordered_segments,
        tracks=original.effective_tracks,
        subtitle_cues=original.ordered_subtitle_cues,
    )
    assert encode_edl(decoded) == encoded
    payload = json.loads(encoded)
    assert payload["edl"]["subtitle_cues"][0]["timeline_range"]["start"] == {
        "scale": 4,
        "value": 1,
    }


def test_codec_reads_prior_v2_edl_without_subtitle_payload() -> None:
    canonical = json.loads(encode_edl(_edl()))
    canonical["schema_version"] = "r0.12-edl-v2"
    del canonical["edl"]["subtitle_cues"]

    decoded = decode_edl(json.dumps(canonical).encode())

    assert decoded.subtitle_cues == ()
    assert decoded.segments == _edl().ordered_segments


@pytest.mark.parametrize(
    ("cues", "code"),
    (
        (
            (
                EDLSubtitleCue(
                    "dup",
                    "subtitle",
                    MediaTimeRange(MediaTime(0, 1), MediaTime(1, 1)),
                    "a",
                    "en",
                ),
                EDLSubtitleCue(
                    "dup",
                    "subtitle",
                    MediaTimeRange(MediaTime(1, 1), MediaTime(1, 1)),
                    "b",
                    "en",
                ),
            ),
            EDLDiagnosticCode.DUPLICATE_SUBTITLE_CUE_ID,
        ),
        (
            (
                EDLSubtitleCue(
                    "range",
                    "subtitle",
                    MediaTimeRange(MediaTime(5, 1), MediaTime(1, 1)),
                    "late",
                    "en",
                ),
            ),
            EDLDiagnosticCode.SUBTITLE_RANGE_INVALID,
        ),
        (
            (
                EDLSubtitleCue(
                    "emphasis",
                    "subtitle",
                    MediaTimeRange(MediaTime(0, 1), MediaTime(1, 1)),
                    "short",
                    "en",
                    emphasis=(SubtitleEmphasisSpan(1, 9, SubtitleEmphasisStyle.BOLD),),
                ),
            ),
            EDLDiagnosticCode.SUBTITLE_EMPHASIS_INVALID,
        ),
        (
            (
                EDLSubtitleCue(
                    "one",
                    "subtitle",
                    MediaTimeRange(MediaTime(0, 1), MediaTime(2, 1)),
                    "one",
                    "en",
                ),
                EDLSubtitleCue(
                    "two",
                    "subtitle",
                    MediaTimeRange(MediaTime(1, 1), MediaTime(1, 1)),
                    "two",
                    "en",
                ),
            ),
            EDLDiagnosticCode.SUBTITLE_OVERLAP_UNSUPPORTED,
        ),
        (
            (
                EDLSubtitleCue(
                    "track",
                    "missing",
                    MediaTimeRange(MediaTime(0, 1), MediaTime(1, 1)),
                    "track",
                    "en",
                ),
            ),
            EDLDiagnosticCode.SUBTITLE_TRACK_INVALID,
        ),
        (
            (
                EDLSubtitleCue(
                    "language",
                    "subtitle",
                    MediaTimeRange(MediaTime(0, 1), MediaTime(1, 1)),
                    "language",
                    "not a language",
                ),
            ),
            EDLDiagnosticCode.SUBTITLE_LANGUAGE_INVALID,
        ),
        (
            (
                EDLSubtitleCue(
                    "layout",
                    "subtitle",
                    MediaTimeRange(MediaTime(0, 1), MediaTime(1, 1)),
                    "layout",
                    "en",
                    layout=cast(SubtitleLayoutRegion, "middle"),
                ),
            ),
            EDLDiagnosticCode.SUBTITLE_LAYOUT_INVALID,
        ),
        (
            (
                EDLSubtitleCue(
                    "",
                    "subtitle",
                    MediaTimeRange(MediaTime(0, 1), MediaTime(1, 1)),
                    "identity",
                    "en",
                ),
            ),
            EDLDiagnosticCode.SUBTITLE_IDENTITY_INVALID,
        ),
        (
            (
                EDLSubtitleCue(
                    "text",
                    "subtitle",
                    MediaTimeRange(MediaTime(0, 1), MediaTime(1, 1)),
                    " ",
                    "en",
                ),
            ),
            EDLDiagnosticCode.SUBTITLE_TEXT_INVALID,
        ),
    ),
)
def test_validator_diagnoses_invalid_subtitle_shape(
    cues: tuple[EDLSubtitleCue, ...], code: EDLDiagnosticCode
) -> None:
    edl = replace(
        _edl(),
        tracks=(*_edl().tracks, EDLTrack("subtitle", EDLTrackFamily.SUBTITLE)),
        subtitle_cues=cues,
    )

    assert code in {item.code for item in validate_edl(edl).diagnostics}


def test_ass_generation_escapes_text_and_preserves_owned_emphasis_and_layout() -> None:
    content = build_ass_subtitles(compile_subtitle_cues(_edl(), _cues()), 1080, 1920)

    assert "0:00:00.25,0:00:01.25" in content
    assert r"Use {\b1}\{safe\}{\b0}, C:\\clips\Nnow 'quoted'" in content
    assert r"{\an2}" in content and r"{\an8}{\c&H00FFFF&}中文" in content
    assert "speaker-a" not in content


def test_builder_rejects_track_family_collision() -> None:
    collided = replace(_edl(), tracks=(*_edl().tracks, EDLTrack("subtitle", EDLTrackFamily.BGM)))

    with pytest.raises(ValueError, match="another track family"):
        compile_subtitle_cues(collided, _cues())


def test_renderer_compiles_subtitle_artifact_without_fake_media_asset(tmp_path: Path) -> None:
    source = tmp_path / "source.mp4"
    source.touch()
    edl = compile_subtitle_cues(_edl(), _cues())
    request = RenderRequest(
        edl,
        (ResolvedLocalAssetMedia(EntityRevisionRef("asset", 1), source),),
        OutputSpec(tmp_path / "result with ' punctuation.mp4", 1080, 1920, 30),
    )

    result = compile_ffmpeg_render(request)

    assert result.plan is not None and not result.diagnostics
    assert (
        result.plan.subtitle_artifact_path == tmp_path / ".subtitle-edl.r1.1080x1920.subtitles.ass"
    )
    assert result.plan.subtitle_artifact_content == build_ass_subtitles(edl, 1080, 1920)
    graph = result.plan.invocation.arguments[
        result.plan.invocation.arguments.index("-filter_complex") + 1
    ]
    assert "subtitles=filename=" in graph and "[vbase]" in graph
    assert len(request.asset_media) == 1

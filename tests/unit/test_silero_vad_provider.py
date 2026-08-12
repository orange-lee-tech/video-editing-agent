from pathlib import Path

import pytest

from video_editing_agent.application.ports.voice_activity import (
    VoiceActivityRequest,
    VoiceActivityState,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.providers.speech.silero_vad import (
    SAMPLE_RATE,
    SILERO_MODEL_GIT_BLOB_SHA,
    SILERO_VAD_COMMIT,
    SILERO_VAD_VERSION,
    WINDOW_SAMPLES,
    PcmWindow,
    SileroVadConfig,
    SileroVadUnavailableError,
    SileroVadVoiceActivityPort,
    _ffmpeg_command,
)


class FakeEngine:
    runtime_version = "1.28.2"

    def __init__(self, probabilities: list[float]) -> None:
        self.probabilities = iter(probabilities)
        self.reset_calls = 0
        self.window_calls = 0

    def reset(self) -> None:
        self.reset_calls += 1

    def probability(self, samples: tuple[float, ...]) -> float:
        assert len(samples) == WINDOW_SAMPLES
        self.window_calls += 1
        return next(self.probabilities)


def _request(duration: MediaTime | None = None) -> VoiceActivityRequest:
    return VoiceActivityRequest(
        shot_ref=EntityRevisionRef("sht_silero", 1),
        local_media_path=Path("C:/media/example.mp4"),
        source_range=MediaTimeRange(
            start=MediaTime(101, 10),
            duration=duration or MediaTime(2048, SAMPLE_RATE),
        ),
    )


def _windows(count: int) -> tuple[PcmWindow, ...]:
    samples = (0.0,) * WINDOW_SAMPLES
    return tuple(PcmWindow(samples, WINDOW_SAMPLES) for _ in range(count))


def test_adapter_merges_window_probabilities_into_complete_partition() -> None:
    engine = FakeEngine([0.1, 0.8, 0.9, 0.2])
    config = SileroVadConfig(Path("silero_vad.onnx"))
    port = SileroVadVoiceActivityPort(
        config,
        engine_factory=lambda ignored: engine,
        window_source=lambda request, ignored: _windows(4),
    )

    proposal = port.analyze(_request())

    assert [span.state for span in proposal.spans] == [
        VoiceActivityState.SILENCE,
        VoiceActivityState.SPEECH,
        VoiceActivityState.SILENCE,
    ]
    expected_ranges = (
        MediaTimeRange(MediaTime(0, 1), MediaTime(4, 125)),
        MediaTimeRange(MediaTime(4, 125), MediaTime(8, 125)),
        MediaTimeRange(MediaTime(12, 125), MediaTime(4, 125)),
    )
    assert tuple(span.relative_range for span in proposal.spans) == expected_ranges
    assert proposal.spans[0].confidence == pytest.approx(0.9)
    assert proposal.spans[1].confidence == pytest.approx(0.85)
    assert proposal.spans[2].confidence == pytest.approx(0.8)
    assert engine.reset_calls == 1
    assert engine.window_calls == 4
    assert proposal.provider_id == "local:silero-vad-onnx"
    assert f"silero-vad@{SILERO_VAD_VERSION}" in proposal.provider_revision
    assert f"commit={SILERO_VAD_COMMIT}" in proposal.provider_revision
    assert f"model_blob={SILERO_MODEL_GIT_BLOB_SHA}" in proposal.provider_revision
    assert "onnxruntime@1.28.2" in proposal.provider_revision
    assert "threshold=0.500000" in proposal.provider_revision


def test_final_span_uses_authoritative_shot_duration_for_small_decode_rounding() -> None:
    engine = FakeEngine([0.9])
    authoritative = MediaTime(WINDOW_SAMPLES - 1, SAMPLE_RATE)
    port = SileroVadVoiceActivityPort(
        SileroVadConfig(Path("silero_vad.onnx")),
        engine_factory=lambda ignored: engine,
        window_source=lambda request, ignored: _windows(1),
    )

    proposal = port.analyze(_request(authoritative))

    assert len(proposal.spans) == 1
    assert proposal.spans[0].relative_range.duration == authoritative


def test_decode_duration_mismatch_larger_than_one_window_is_rejected() -> None:
    engine = FakeEngine([0.9])
    port = SileroVadVoiceActivityPort(
        SileroVadConfig(Path("silero_vad.onnx")),
        engine_factory=lambda ignored: engine,
        window_source=lambda request, ignored: _windows(1),
    )

    with pytest.raises(SileroVadUnavailableError, match="differs"):
        port.analyze(_request(MediaTime(2, 1)))


def test_ffmpeg_command_is_exact_shot_scoped_16khz_mono_pcm() -> None:
    config = SileroVadConfig(Path("silero_vad.onnx"), ffmpeg_executable="ffmpeg-custom")
    command = _ffmpeg_command(_request(), config)

    assert command[0] == "ffmpeg-custom"
    assert command[command.index("-ss") + 1] == "10.100"
    assert command[command.index("-t") + 1] == "0.128"
    assert command[command.index("-ac") + 1] == "1"
    assert command[command.index("-ar") + 1] == str(SAMPLE_RATE)
    assert command[command.index("-acodec") + 1] == "pcm_s16le"
    assert command[-1] == "pipe:1"


def test_config_rejects_nonprobability_threshold() -> None:
    with pytest.raises(ValueError, match="strictly between"):
        SileroVadConfig(Path("silero_vad.onnx"), threshold=1.0)

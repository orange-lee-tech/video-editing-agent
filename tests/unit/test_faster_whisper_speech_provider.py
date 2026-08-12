from pathlib import Path
from types import SimpleNamespace
from typing import Any

from video_editing_agent.application.ports.speech_recognition import SpeechRecognitionRequest
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.providers.speech.faster_whisper import (
    DEFAULT_MODEL_ID,
    DEFAULT_MODEL_REVISION,
    FASTER_WHISPER_RUNTIME_VERSION,
    FasterWhisperConfig,
    FasterWhisperSpeechRecognitionPort,
)


class FakeModel:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def transcribe(self, path: str, **kwargs: Any):
        self.calls.append((path, kwargs))
        words = [
            SimpleNamespace(start=10.3, end=10.7, word=" hello", probability=0.91),
            SimpleNamespace(start=10.8, end=11.4, word=" world", probability=0.82),
        ]
        segments = [
            SimpleNamespace(
                start=10.3,
                end=11.4,
                text=" hello world",
                words=words,
            )
        ]
        return iter(segments), SimpleNamespace(language="en")


def _request() -> SpeechRecognitionRequest:
    return SpeechRecognitionRequest(
        shot_ref=EntityRevisionRef("sht_fw", 2),
        local_media_path=Path("C:/media/example.mp4"),
        source_range=MediaTimeRange(MediaTime(101, 10), MediaTime(3, 1)),
    )


def test_default_config_is_pinned_cpu_local_only_prototype() -> None:
    config = FasterWhisperConfig()

    assert config.runtime_version == FASTER_WHISPER_RUNTIME_VERSION == "1.2.1"
    assert config.model_id == DEFAULT_MODEL_ID == "Systran/faster-whisper-base"
    assert config.model_revision == DEFAULT_MODEL_REVISION
    assert config.device == "cpu"
    assert config.compute_type == "int8"
    assert config.local_files_only is True


def test_adapter_converts_upstream_absolute_clip_times_to_shot_relative_proposal() -> None:
    fake_model = FakeModel()
    factory_calls: list[FasterWhisperConfig] = []

    def factory(config: FasterWhisperConfig) -> FakeModel:
        factory_calls.append(config)
        return fake_model

    adapter = FasterWhisperSpeechRecognitionPort(model_factory=factory)
    proposal = adapter.recognize(_request())

    assert factory_calls == [adapter.config]
    assert proposal.provider_id == "local:faster-whisper"
    assert "faster-whisper@1.2.1" in proposal.provider_revision
    assert DEFAULT_MODEL_REVISION in proposal.provider_revision
    assert proposal.text == "hello world"
    assert proposal.language == "en"
    assert proposal.segments[0].relative_range.start == MediaTime(1, 5)
    assert proposal.segments[0].relative_range.end == MediaTime(13, 10)
    assert proposal.segments[0].words[0].relative_range.start == MediaTime(1, 5)
    assert proposal.segments[0].words[1].relative_range.start == MediaTime(7, 10)
    assert proposal.segments[0].words[0].confidence == 0.91


def test_adapter_requests_exact_clip_with_word_timestamps_and_without_internal_vad() -> None:
    fake_model = FakeModel()
    adapter = FasterWhisperSpeechRecognitionPort(model_factory=lambda config: fake_model)

    adapter.recognize(_request())

    path, kwargs = fake_model.calls[0]
    assert path == str(_request().local_media_path)
    assert kwargs["clip_timestamps"] == [10.1, 13.1]
    assert kwargs["word_timestamps"] is True
    assert kwargs["vad_filter"] is False
    assert kwargs["condition_on_previous_text"] is False
    assert kwargs["temperature"] == 0.0
    assert kwargs["task"] == "transcribe"


def test_adapter_reuses_one_runtime_instance() -> None:
    fake_model = FakeModel()
    calls = 0

    def factory(config: FasterWhisperConfig) -> FakeModel:
        nonlocal calls
        del config
        calls += 1
        return fake_model

    adapter = FasterWhisperSpeechRecognitionPort(model_factory=factory)
    adapter.recognize(_request())
    adapter.recognize(_request())

    assert calls == 1
    assert len(fake_model.calls) == 2

from __future__ import annotations

import importlib
import importlib.metadata
from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from math import isfinite
from typing import Any

from video_editing_agent.application.ports.speech_recognition import (
    SpeechRecognitionCapabilityUnavailable,
    SpeechRecognitionPort,
    SpeechRecognitionProposal,
    SpeechRecognitionRequest,
    SpeechSegmentProposal,
    SpeechWordProposal,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange

FASTER_WHISPER_RUNTIME_VERSION = "1.2.1"
DEFAULT_MODEL_ID = "Systran/faster-whisper-base"
DEFAULT_MODEL_REVISION = "ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66"


class FasterWhisperUnavailableError(SpeechRecognitionCapabilityUnavailable):
    """The approved pinned Stage-A ASR runtime/model is unavailable."""


@dataclass(frozen=True, slots=True)
class FasterWhisperConfig:
    model_id: str = DEFAULT_MODEL_ID
    model_revision: str = DEFAULT_MODEL_REVISION
    runtime_version: str = FASTER_WHISPER_RUNTIME_VERSION
    device: str = "cpu"
    compute_type: str = "int8"
    cpu_threads: int = 0
    beam_size: int = 5
    language: str | None = None
    local_files_only: bool = True

    def __post_init__(self) -> None:
        for name, value in (
            ("model_id", self.model_id),
            ("model_revision", self.model_revision),
            ("runtime_version", self.runtime_version),
            ("device", self.device),
            ("compute_type", self.compute_type),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        if isinstance(self.cpu_threads, bool) or not isinstance(self.cpu_threads, int):
            raise TypeError("cpu_threads must be an int")
        if self.cpu_threads < 0:
            raise ValueError("cpu_threads must be >= 0")
        if isinstance(self.beam_size, bool) or not isinstance(self.beam_size, int):
            raise TypeError("beam_size must be an int")
        if self.beam_size < 1:
            raise ValueError("beam_size must be >= 1")
        if self.language is not None and not self.language.strip():
            raise ValueError("language must be non-empty or None")


ModelFactory = Callable[[FasterWhisperConfig], Any]


def _default_model_factory(config: FasterWhisperConfig) -> Any:
    try:
        installed_version = importlib.metadata.version("faster-whisper")
        module = importlib.import_module("faster_whisper")
    except (importlib.metadata.PackageNotFoundError, ModuleNotFoundError) as exc:
        raise FasterWhisperUnavailableError(
            "approved Stage-A speech recognition requires faster-whisper==1.2.1, but the "
            "speech-runtime capability is not installed"
        ) from exc

    if installed_version != config.runtime_version:
        raise FasterWhisperUnavailableError(
            "faster-whisper runtime version mismatch: "
            f"expected {config.runtime_version}, found {installed_version}"
        )

    model_type = getattr(module, "WhisperModel", None)
    if model_type is None:
        raise FasterWhisperUnavailableError("installed faster-whisper has no WhisperModel")

    try:
        return model_type(
            config.model_id,
            device=config.device,
            compute_type=config.compute_type,
            cpu_threads=config.cpu_threads,
            local_files_only=config.local_files_only,
            revision=config.model_revision,
        )
    except Exception as exc:
        if config.local_files_only:
            raise FasterWhisperUnavailableError(
                "pinned faster-whisper model is not available locally; "
                "implicit download is disabled"
            ) from exc
        raise


def _seconds_float(value: MediaTime) -> float:
    return float(value.to_decimal_seconds_string(fractional_digits=9))


def _time_from_provider_seconds(value: object) -> MediaTime:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("faster-whisper timestamp must be numeric")
    normalized = float(value)
    if not isfinite(normalized):
        raise ValueError("faster-whisper timestamp must be finite")
    fraction = Fraction(str(normalized))
    return MediaTime(fraction.numerator, fraction.denominator)


def _relative_range(start: object, end: object, source_start: MediaTime) -> MediaTimeRange:
    absolute_start = _time_from_provider_seconds(start)
    absolute_end = _time_from_provider_seconds(end)
    relative_start = absolute_start - source_start
    relative_end = absolute_end - source_start
    return MediaTimeRange(relative_start, relative_end - relative_start)


def _word_proposal(word: Any, source_start: MediaTime) -> SpeechWordProposal:
    probability = getattr(word, "probability", None)
    confidence = None if probability is None else float(probability)
    return SpeechWordProposal(
        text=str(word.word),
        relative_range=_relative_range(
            word.start,
            word.end,
            source_start,
        ),
        confidence=confidence,
    )


def _segment_proposal(segment: Any, source_start: MediaTime) -> SpeechSegmentProposal:
    raw_words = getattr(segment, "words", None)
    words: tuple[SpeechWordProposal, ...]
    if raw_words is None:
        words = ()
    else:
        words = tuple(_word_proposal(word, source_start) for word in raw_words)
    return SpeechSegmentProposal(
        text=str(segment.text),
        relative_range=_relative_range(
            segment.start,
            segment.end,
            source_start,
        ),
        words=words,
    )


class FasterWhisperSpeechRecognitionPort(SpeechRecognitionPort):
    """Pinned Stage-A speech-recognition capability adapter.

    Installation/model availability is explicit and source-time authority remains local.
    """

    def __init__(
        self,
        config: FasterWhisperConfig | None = None,
        *,
        model_factory: ModelFactory = _default_model_factory,
    ) -> None:
        self._config = config or FasterWhisperConfig()
        self._model_factory = model_factory
        self._model: Any | None = None

    @property
    def config(self) -> FasterWhisperConfig:
        return self._config

    def _model_instance(self) -> Any:
        if self._model is None:
            self._model = self._model_factory(self._config)
        return self._model

    def recognize(self, request: SpeechRecognitionRequest) -> SpeechRecognitionProposal:
        source_start = request.source_range.start
        clip_start = _seconds_float(source_start)
        clip_end = _seconds_float(request.source_range.end)
        model = self._model_instance()
        segments_iter, info = model.transcribe(
            str(request.local_media_path),
            language=self._config.language,
            task="transcribe",
            beam_size=self._config.beam_size,
            temperature=0.0,
            condition_on_previous_text=False,
            word_timestamps=True,
            vad_filter=False,
            clip_timestamps=[clip_start, clip_end],
        )
        raw_segments = list(segments_iter)
        segments = tuple(_segment_proposal(segment, source_start) for segment in raw_segments)
        text = "".join(str(segment.text) for segment in raw_segments).strip()
        detected_language = getattr(info, "language", None)
        language = None if detected_language is None else str(detected_language)

        return SpeechRecognitionProposal(
            provider_id="local:faster-whisper",
            provider_revision=(
                f"faster-whisper@{self._config.runtime_version};"
                f"{self._config.model_id}@{self._config.model_revision}"
            ),
            text=text,
            language=language,
            segments=segments,
        )

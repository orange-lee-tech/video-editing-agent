from __future__ import annotations

import importlib
import importlib.metadata
import pathlib
import struct
import subprocess
import tempfile
import typing
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from fractions import Fraction
from math import isfinite

from video_editing_agent.application.ports.voice_activity import (
    VoiceActivityPort,
    VoiceActivityProposal,
    VoiceActivityRequest,
    VoiceActivitySpanProposal,
    VoiceActivityState,
)
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange

SILERO_VAD_VERSION = "6.2.1"
SILERO_VAD_COMMIT = "7e30209a3e901f9842f81b225f3e93d8199902b1"
SILERO_MODEL_REPOSITORY_PATH = "src/silero_vad/data/silero_vad.onnx"
SILERO_MODEL_GIT_BLOB_SHA = "80c5592ef1f4c9ede3e357bbd02eb863358a6a9d"
SAMPLE_RATE = 16_000
WINDOW_SAMPLES = 512
_CONTEXT_SAMPLES = 64
_ADAPTER_REVISION = "r0.8b-v1"


class SileroVadUnavailableError(RuntimeError):
    """The pinned local Silero VAD runtime/model or decodable audio is unavailable."""


@dataclass(frozen=True, slots=True)
class SileroVadConfig:
    model_path: pathlib.Path
    threshold: float = 0.5
    ffmpeg_executable: str = "ffmpeg"

    def __post_init__(self) -> None:
        if not self.ffmpeg_executable.strip():
            raise ValueError("ffmpeg_executable must not be empty")
        if isinstance(self.threshold, bool) or not isinstance(self.threshold, (int, float)):
            raise TypeError("threshold must be a number")
        threshold = float(self.threshold)
        if not isfinite(threshold) or not 0.0 < threshold < 1.0:
            raise ValueError("threshold must be finite and strictly between 0 and 1")


@dataclass(frozen=True, slots=True)
class PcmWindow:
    samples: tuple[float, ...]
    valid_samples: int

    def __post_init__(self) -> None:
        if len(self.samples) != WINDOW_SAMPLES:
            raise ValueError(f"PcmWindow must contain exactly {WINDOW_SAMPLES} samples")
        if isinstance(self.valid_samples, bool) or not isinstance(self.valid_samples, int):
            raise TypeError("valid_samples must be an int")
        if not 1 <= self.valid_samples <= WINDOW_SAMPLES:
            raise ValueError(f"valid_samples must be between 1 and {WINDOW_SAMPLES}")


class SileroProbabilityEngine(typing.Protocol):
    @property
    def runtime_version(self) -> str: ...

    def reset(self) -> None: ...

    def probability(self, samples: tuple[float, ...]) -> float: ...


class OnnxSileroProbabilityEngine:
    """Small ONNX-only Silero runtime without the torch-based silero-vad package."""

    def __init__(self, model_path: pathlib.Path) -> None:
        resolved = model_path.expanduser().resolve()
        if not resolved.is_file():
            raise SileroVadUnavailableError(f"Silero VAD model not found: {resolved}")
        try:
            self._runtime_version = importlib.metadata.version("onnxruntime")
            self._np: typing.Any = importlib.import_module("numpy")
            ort: typing.Any = importlib.import_module("onnxruntime")
        except (importlib.metadata.PackageNotFoundError, ModuleNotFoundError) as exc:
            raise SileroVadUnavailableError(
                "Silero ONNX prototype requires local numpy and onnxruntime installations"
            ) from exc

        if self._runtime_version.split(".", 1)[0] != "1":
            raise SileroVadUnavailableError(
                f"unsupported onnxruntime major version: {self._runtime_version}"
            )

        options = ort.SessionOptions()
        options.inter_op_num_threads = 1
        options.intra_op_num_threads = 1
        available = tuple(ort.get_available_providers())
        if "CPUExecutionProvider" in available:
            self._session: typing.Any = ort.InferenceSession(
                str(resolved),
                providers=["CPUExecutionProvider"],
                sess_options=options,
            )
        else:
            self._session = ort.InferenceSession(str(resolved), sess_options=options)
        self.reset()

    @property
    def runtime_version(self) -> str:
        return self._runtime_version

    def reset(self) -> None:
        self._state = self._np.zeros((2, 1, 128), dtype=self._np.float32)
        self._context = self._np.zeros((1, _CONTEXT_SAMPLES), dtype=self._np.float32)

    def probability(self, samples: tuple[float, ...]) -> float:
        if len(samples) != WINDOW_SAMPLES:
            raise ValueError(f"Silero VAD requires exactly {WINDOW_SAMPLES} samples per window")
        audio = self._np.asarray(samples, dtype=self._np.float32).reshape(1, WINDOW_SAMPLES)
        model_input = self._np.concatenate((self._context, audio), axis=1)
        outputs = self._session.run(
            None,
            {
                "input": model_input,
                "state": self._state,
                "sr": self._np.asarray(SAMPLE_RATE, dtype=self._np.int64),
            },
        )
        probability, state = outputs
        self._state = state
        self._context = model_input[:, -_CONTEXT_SAMPLES:]
        value = float(probability.reshape(-1)[0])
        if not isfinite(value) or not 0.0 <= value <= 1.0:
            raise RuntimeError(f"Silero VAD returned invalid speech probability: {value!r}")
        return value


ProbabilityEngineFactory = Callable[[SileroVadConfig], SileroProbabilityEngine]
PcmWindowSource = Callable[[VoiceActivityRequest, SileroVadConfig], Iterable[PcmWindow]]


def _default_engine_factory(config: SileroVadConfig) -> SileroProbabilityEngine:
    return OnnxSileroProbabilityEngine(config.model_path)


def _ffmpeg_command(request: VoiceActivityRequest, config: SileroVadConfig) -> list[str]:
    start = request.source_range.start.to_decimal_seconds_string(fractional_digits=9)
    duration = request.source_range.duration.to_decimal_seconds_string(fractional_digits=9)
    return [
        config.ffmpeg_executable,
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-i",
        str(request.local_media_path),
        "-ss",
        start,
        "-t",
        duration,
        "-vn",
        "-ac",
        "1",
        "-ar",
        str(SAMPLE_RATE),
        "-acodec",
        "pcm_s16le",
        "-f",
        "s16le",
        "pipe:1",
    ]


def _read_up_to(stream: typing.BinaryIO, size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining > 0:
        chunk = stream.read(remaining)
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _read_process_stderr(stderr_file: typing.BinaryIO) -> str:
    stderr_file.flush()
    stderr_file.seek(0)
    return stderr_file.read().decode("utf-8", errors="replace")


def _decode_s16le(chunk: bytes) -> tuple[float, ...]:
    if len(chunk) % 2:
        raise RuntimeError("FFmpeg returned an incomplete 16-bit PCM sample")
    return tuple(sample[0] / 32768.0 for sample in struct.iter_unpack("<h", chunk))


def iter_ffmpeg_pcm_windows(
    request: VoiceActivityRequest,
    config: SileroVadConfig,
) -> Iterator[PcmWindow]:
    """Stream one exact Shot as 16 kHz mono PCM windows without whole-clip buffering."""

    bytes_per_window = WINDOW_SAMPLES * 2
    command = _ffmpeg_command(request, config)
    with tempfile.TemporaryFile() as stderr_file:
        try:
            process: subprocess.Popen[bytes] = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=stderr_file,
            )
        except FileNotFoundError as exc:
            raise SileroVadUnavailableError(
                f"FFmpeg executable not found: {config.ffmpeg_executable}"
            ) from exc

        if process.stdout is None:
            process.kill()
            process.wait()
            raise RuntimeError("FFmpeg stdout pipe was not created")
        stdout_stream = typing.cast(typing.BinaryIO, process.stdout)

        try:
            while True:
                chunk = _read_up_to(stdout_stream, bytes_per_window)
                if not chunk:
                    break
                decoded = _decode_s16le(chunk)
                valid_samples = len(decoded)
                if valid_samples > WINDOW_SAMPLES:
                    raise RuntimeError("FFmpeg PCM window exceeded the requested sample count")
                padded = decoded + (0.0,) * (WINDOW_SAMPLES - valid_samples)
                yield PcmWindow(padded, valid_samples)
                if valid_samples < WINDOW_SAMPLES:
                    break

            return_code = process.wait()
            if return_code != 0:
                stderr = _read_process_stderr(typing.cast(typing.BinaryIO, stderr_file))
                raise SileroVadUnavailableError(
                    f"FFmpeg audio decode failed for {request.local_media_path}:\n{stderr}"
                )
        finally:
            stdout_stream.close()
            if process.poll() is None:
                process.kill()
                process.wait()


@dataclass(slots=True)
class _MergedSpan:
    state: VoiceActivityState
    start_sample: int
    end_sample: int
    confidence_weighted_sum: float
    confidence_weight: int

    @property
    def confidence(self) -> float:
        return self.confidence_weighted_sum / self.confidence_weight


class SileroVadVoiceActivityPort(VoiceActivityPort):
    """Pinned local Silero ONNX prototype producing a complete Shot-relative partition."""

    def __init__(
        self,
        config: SileroVadConfig,
        *,
        engine_factory: ProbabilityEngineFactory = _default_engine_factory,
        window_source: PcmWindowSource = iter_ffmpeg_pcm_windows,
    ) -> None:
        self._config = config
        self._engine_factory = engine_factory
        self._window_source = window_source
        self._engine: SileroProbabilityEngine | None = None

    @property
    def config(self) -> SileroVadConfig:
        return self._config

    def _engine_instance(self) -> SileroProbabilityEngine:
        if self._engine is None:
            self._engine = self._engine_factory(self._config)
        return self._engine

    def analyze(self, request: VoiceActivityRequest) -> VoiceActivityProposal:
        engine = self._engine_instance()
        engine.reset()
        merged: list[_MergedSpan] = []
        sample_cursor = 0

        for window in self._window_source(request, self._config):
            speech_probability = engine.probability(window.samples)
            if speech_probability >= self._config.threshold:
                state = VoiceActivityState.SPEECH
                confidence = speech_probability
            else:
                state = VoiceActivityState.SILENCE
                confidence = 1.0 - speech_probability

            start_sample = sample_cursor
            end_sample = start_sample + window.valid_samples
            sample_cursor = end_sample
            weighted = confidence * window.valid_samples
            if merged and merged[-1].state is state:
                merged[-1].end_sample = end_sample
                merged[-1].confidence_weighted_sum += weighted
                merged[-1].confidence_weight += window.valid_samples
            else:
                merged.append(
                    _MergedSpan(
                        state=state,
                        start_sample=start_sample,
                        end_sample=end_sample,
                        confidence_weighted_sum=weighted,
                        confidence_weight=window.valid_samples,
                    )
                )

        if not merged:
            raise SileroVadUnavailableError("no decodable audio samples were produced for the Shot")

        decoded_duration = Fraction(sample_cursor, SAMPLE_RATE)
        authoritative_duration = request.source_range.duration.as_fraction()
        mismatch = abs(decoded_duration - authoritative_duration)
        if mismatch > Fraction(WINDOW_SAMPLES, SAMPLE_RATE):
            raise SileroVadUnavailableError(
                "decoded audio duration differs from the authoritative Shot by more than one "
                "Silero window"
            )

        proposals: list[VoiceActivitySpanProposal] = []
        for index, span in enumerate(merged):
            start = MediaTime(span.start_sample, SAMPLE_RATE)
            if index == len(merged) - 1:
                if start.as_fraction() >= authoritative_duration:
                    raise SileroVadUnavailableError(
                        "decoded audio created a VAD span outside the authoritative Shot"
                    )
                relative_range = MediaTimeRange(
                    start=start,
                    duration=request.source_range.duration - start,
                )
            else:
                end = MediaTime(span.end_sample, SAMPLE_RATE)
                if end.as_fraction() > authoritative_duration:
                    raise SileroVadUnavailableError(
                        "decoded audio created an intermediate VAD boundary outside the Shot"
                    )
                relative_range = MediaTimeRange(start=start, duration=end - start)
            proposals.append(
                VoiceActivitySpanProposal(
                    state=span.state,
                    relative_range=relative_range,
                    confidence=span.confidence,
                )
            )

        threshold = float(self._config.threshold)
        return VoiceActivityProposal(
            provider_id="local:silero-vad-onnx",
            provider_revision=(
                f"silero-vad@{SILERO_VAD_VERSION};commit={SILERO_VAD_COMMIT};"
                f"model_blob={SILERO_MODEL_GIT_BLOB_SHA};"
                f"onnxruntime@{engine.runtime_version};adapter={_ADAPTER_REVISION};"
                f"threshold={threshold:.6f}"
            ),
            spans=tuple(proposals),
        )

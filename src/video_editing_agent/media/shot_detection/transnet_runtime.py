from __future__ import annotations

import importlib
import pathlib
from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Protocol, cast

from video_editing_agent.media.shot_detection.transnet_window import TRANSNETV2_WINDOW_FRAMES

TRANSNETV2_FRAME_WIDTH = 48
TRANSNETV2_FRAME_HEIGHT = 27
TRANSNETV2_FRAME_CHANNELS = 3
TRANSNETV2_BYTES_PER_FRAME = (
    TRANSNETV2_FRAME_WIDTH * TRANSNETV2_FRAME_HEIGHT * TRANSNETV2_FRAME_CHANNELS
)
TRANSNETV2_WEIGHTS_FILENAME = "transnetv2-pytorch-weights.pth"


class TransNetV2RuntimeUnavailable(RuntimeError):
    """Raised when the optional TransNetV2 runtime is not installed or loadable."""


class _ArrayLike(Protocol):
    def reshape(self, shape: tuple[int, ...]) -> _ArrayLike: ...

    def tolist(self) -> list[float]: ...


class _NumpyModule(Protocol):
    uint8: object

    def frombuffer(self, buffer: bytes, dtype: object) -> _ArrayLike: ...


class _TensorLike(Protocol):
    def detach(self) -> _TensorLike: ...

    def cpu(self) -> _TensorLike: ...

    def numpy(self) -> _ArrayLike: ...


class _TorchModule(Protocol):
    def load(
        self,
        file: str,
        *,
        map_location: object,
        weights_only: bool,
    ) -> object: ...

    def no_grad(self) -> AbstractContextManager[None]: ...


class _TransNetV2Model(Protocol):
    device: object

    def eval(self) -> object: ...

    def load_state_dict(self, state_dict: object) -> object: ...

    def predict_raw(self, frames: object) -> tuple[_TensorLike, object]: ...


class _ModelFactory(Protocol):
    def __call__(self, *, device: str) -> _TransNetV2Model: ...


class _TransNetV2Module(Protocol):
    __file__: str | None
    TransNetV2: _ModelFactory


@dataclass(frozen=True, slots=True)
class TorchTransNetV2Config:
    """Explicit heavy-runtime controls kept outside the application ShotDetector port."""

    device: str = "cpu"
    weights_path: pathlib.Path | None = None

    def __post_init__(self) -> None:
        if self.device not in {"auto", "cpu", "cuda", "mps"}:
            raise ValueError("device must be one of: auto, cpu, cuda, mps")


def _import_optional_runtime_module(name: str) -> object:
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError as exc:
        raise TransNetV2RuntimeUnavailable(
            "TransNetV2 runtime is optional. Run with "
            "`uv run --with 'transnetv2-pytorch==1.0.5' ...` or install an equivalent "
            "reviewed runtime environment."
        ) from exc


def _resolve_weights_path(
    package: _TransNetV2Module,
    explicit_path: pathlib.Path | None,
) -> pathlib.Path:
    if explicit_path is not None:
        candidate = explicit_path.expanduser().resolve()
        if not candidate.is_file():
            raise FileNotFoundError(f"TransNetV2 weights file not found: {candidate}")
        return candidate

    if package.__file__ is not None:
        candidate = pathlib.Path(package.__file__).resolve().parent / TRANSNETV2_WEIGHTS_FILENAME
        if candidate.is_file():
            return candidate

    raise FileNotFoundError(
        "TransNetV2 weights could not be located automatically. Pass an explicit weights_path."
    )


def _validate_window_frames(frames: tuple[bytes, ...]) -> None:
    if len(frames) != TRANSNETV2_WINDOW_FRAMES:
        raise ValueError(
            f"TransNetV2 runtime requires exactly {TRANSNETV2_WINDOW_FRAMES} frames, "
            f"got {len(frames)}"
        )
    for index, frame in enumerate(frames):
        if not isinstance(frame, bytes):
            raise TypeError(f"frame[{index}] must be bytes")
        if len(frame) != TRANSNETV2_BYTES_PER_FRAME:
            raise ValueError(
                f"frame[{index}] must contain {TRANSNETV2_BYTES_PER_FRAME} RGB24 bytes, "
                f"got {len(frame)}"
            )


class TorchTransNetV2WindowPredictor:
    """Lazy adapter from local RGB24 windows to transnetv2-pytorch `predict_raw`."""

    def __init__(self, config: TorchTransNetV2Config | None = None) -> None:
        self._config = config or TorchTransNetV2Config()
        self._numpy: _NumpyModule | None = None
        self._torch: _TorchModule | None = None
        self._model: _TransNetV2Model | None = None

    def _load_runtime(self) -> tuple[_NumpyModule, _TorchModule, _TransNetV2Model]:
        if self._numpy is not None and self._torch is not None and self._model is not None:
            return self._numpy, self._torch, self._model

        numpy_module = cast(_NumpyModule, _import_optional_runtime_module("numpy"))
        torch_module = cast(_TorchModule, _import_optional_runtime_module("torch"))
        transnet_module = cast(
            _TransNetV2Module,
            _import_optional_runtime_module("transnetv2_pytorch"),
        )
        weights_path = _resolve_weights_path(transnet_module, self._config.weights_path)

        model = transnet_module.TransNetV2(device=self._config.device)
        state_dict = torch_module.load(
            str(weights_path),
            map_location=model.device,
            weights_only=True,
        )
        model.load_state_dict(state_dict)
        model.eval()

        self._numpy = numpy_module
        self._torch = torch_module
        self._model = model
        return numpy_module, torch_module, model

    def predict_single_frame_probabilities(
        self,
        frames: tuple[bytes, ...],
    ) -> tuple[float, ...]:
        _validate_window_frames(frames)
        numpy_module, torch_module, model = self._load_runtime()

        frame_buffer = b"".join(frames)
        input_array = numpy_module.frombuffer(frame_buffer, dtype=numpy_module.uint8).reshape(
            (
                1,
                TRANSNETV2_WINDOW_FRAMES,
                TRANSNETV2_FRAME_HEIGHT,
                TRANSNETV2_FRAME_WIDTH,
                TRANSNETV2_FRAME_CHANNELS,
            )
        )

        with torch_module.no_grad():
            single_frame_predictions, _ = model.predict_raw(input_array)

        values = single_frame_predictions.detach().cpu().numpy().reshape((-1,)).tolist()
        if len(values) != TRANSNETV2_WINDOW_FRAMES:
            raise RuntimeError(
                "transnetv2-pytorch returned an unexpected single-frame prediction shape: "
                f"expected {TRANSNETV2_WINDOW_FRAMES} values, got {len(values)}"
            )
        return tuple(float(value) for value in values)

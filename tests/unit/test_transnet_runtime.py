import importlib
from contextlib import nullcontext
from pathlib import Path

import pytest

from video_editing_agent.media.shot_detection.transnet_runtime import (
    TRANSNETV2_BYTES_PER_FRAME,
    TorchTransNetV2Config,
    TorchTransNetV2WindowPredictor,
)


class FakeArray:
    def __init__(self, values: list[float] | None = None) -> None:
        self.values = values or []
        self.shape: tuple[int, ...] | None = None

    def reshape(self, shape: tuple[int, ...]):
        self.shape = shape
        return self

    def copy(self):
        return self

    def tolist(self) -> list[object]:
        return list(self.values)


class FakeNumpy:
    uint8 = object()

    def __init__(self) -> None:
        self.last_buffer_size = 0

    def frombuffer(self, buffer: bytes, dtype: object) -> FakeArray:
        del dtype
        self.last_buffer_size = len(buffer)
        return FakeArray()


class FakeTensor:
    def __init__(self, values: list[float]) -> None:
        self._array = FakeArray(values)

    def detach(self):
        return self

    def cpu(self):
        return self

    def numpy(self) -> FakeArray:
        return self._array


class FakeInputTensor:
    def __init__(self, array: FakeArray) -> None:
        self.array = array


class FakeTorch:
    def __init__(self) -> None:
        self.loaded: tuple[str, object, bool] | None = None

    def load(self, file: str, *, map_location: object, weights_only: bool) -> object:
        self.loaded = (file, map_location, weights_only)
        return {"weight": "state"}

    def from_numpy(self, array: FakeArray) -> FakeInputTensor:
        return FakeInputTensor(array)

    def no_grad(self):
        return nullcontext()


class FakeModel:
    device = "cpu"

    def __init__(self) -> None:
        self.loaded_state: object | None = None
        self.was_evaluated = False
        self.last_input: object | None = None

    def eval(self) -> object:
        self.was_evaluated = True
        return self

    def load_state_dict(self, state_dict: object) -> object:
        self.loaded_state = state_dict
        return None

    def predict_raw(self, frames: object):
        self.last_input = frames
        values = [index / 100.0 for index in range(100)]
        return FakeTensor(values), object()


class FakePackage:
    def __init__(self, package_file: Path, model: FakeModel) -> None:
        self.__file__ = str(package_file)
        self._model = model

    def TransNetV2(self, *, device: str) -> FakeModel:
        assert device == "cpu"
        return self._model


def test_runtime_predictor_loads_lazily_and_returns_100_probabilities(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package_dir = tmp_path / "transnetv2_pytorch"
    package_dir.mkdir()
    package_file = package_dir / "__init__.py"
    package_file.touch()
    weights = package_dir / "transnetv2-pytorch-weights.pth"
    weights.write_bytes(b"weights")

    fake_numpy = FakeNumpy()
    fake_torch = FakeTorch()
    fake_model = FakeModel()
    fake_package = FakePackage(package_file, fake_model)

    modules = {
        "numpy": fake_numpy,
        "torch": fake_torch,
        "transnetv2_pytorch": fake_package,
    }
    original_import = importlib.import_module

    def fake_import(name: str):
        if name in modules:
            return modules[name]
        return original_import(name)

    monkeypatch.setattr(importlib, "import_module", fake_import)
    predictor = TorchTransNetV2WindowPredictor(TorchTransNetV2Config(device="cpu"))
    frames = (b"\x00" * TRANSNETV2_BYTES_PER_FRAME,) * 100

    predictions = predictor.predict_single_frame_probabilities(frames)

    assert len(predictions) == 100
    assert predictions[25] == 0.25
    assert fake_numpy.last_buffer_size == TRANSNETV2_BYTES_PER_FRAME * 100
    assert fake_torch.loaded == (str(weights), "cpu", True)
    assert fake_model.loaded_state == {"weight": "state"}
    assert fake_model.was_evaluated is True
    assert isinstance(fake_model.last_input, FakeInputTensor)
    assert fake_model.last_input.array.shape == (1, 100, 27, 48, 3)


def test_runtime_predictor_validates_window_before_optional_imports() -> None:
    predictor = TorchTransNetV2WindowPredictor()

    with pytest.raises(ValueError, match="exactly 100"):
        predictor.predict_single_frame_probabilities((b"x",) * 99)


def test_runtime_predictor_requires_rgb24_frame_geometry() -> None:
    predictor = TorchTransNetV2WindowPredictor()

    with pytest.raises(ValueError, match="3888 RGB24 bytes"):
        predictor.predict_single_frame_probabilities((b"x",) * 100)


def test_runtime_config_rejects_unknown_device() -> None:
    with pytest.raises(ValueError, match="auto, cpu, cuda, mps"):
        TorchTransNetV2Config(device="gpu")

# transnetv2-pytorch Runtime — R0.1-D1 Provenance Record

## Package reference

- Package: `transnetv2-pytorch`
- Reviewed version: `1.0.5`
- PyPI release date: 2025-06-01
- Package repository: `allenday/transnetv2_pytorch`
- License expression published by PyPI: MIT
- Requires Python: `>=3.10`
- Published runtime dependencies: `ffmpeg-python`, `numpy`, `pandas`, `pillow`, `torch>=1.9.0`, `tqdm`
- Low-level API used as the compatibility target: `TransNetV2.predict_raw`

The package documentation states that `predict_raw` returns single-frame and all-frame predictions.
It also documents CPU, CUDA and MPS device modes and warns that MPS can produce numerically
inconsistent scene counts. The local adapter therefore defaults to CPU; faster devices remain an
explicit runtime choice.

## Local destinations

- `src/video_editing_agent/media/shot_detection/transnet_runtime.py`
- `src/video_editing_agent/media/shot_detection/transnet_backend.py`
- `src/video_editing_agent/media/shot_detection/transnet_scenes.py`
- `scripts/probe_transnetv2_runtime.py`

Reuse classification:

**The local adapter and normalization code are independently implemented. No source code from
`transnetv2-pytorch` or `soCzech/TransNetV2` is copied.**

## Dependency boundary

R0.1-D1 deliberately does **not** add `transnetv2-pytorch`, Torch or NumPy to the project's base
`pyproject.toml` or `uv.lock`.

The package currently pulls a materially wider dependency set than the low-level model call actually
needs from this project. Before adopting it as a persistent optional dependency, the package, weights,
Torch device behavior and Windows compatibility are probed in an isolated uv invocation.

The probe command is:

```powershell
uv run --with "transnetv2-pytorch==1.0.5" python .\scripts\probe_transnetv2_runtime.py
```

This adds the reviewed package only for that invocation and does not modify project dependency
metadata.

## Runtime adapter contract

`TorchTransNetV2WindowPredictor` implements the already-frozen `TransNetV2WindowPredictor` seam.
Its authority is intentionally narrow:

`100 RGB24 frames -> one predict_raw call -> 100 single-frame probabilities`

It cannot decide overlap, padding, source duration, scene boundaries, shot duration policy, `Shot`
identity or final timeline placement.

The adapter:

- validates exactly 100 frames;
- validates `27 x 48 x 3` RGB24 geometry;
- imports NumPy, Torch and `transnetv2_pytorch` lazily;
- loads model state with `weights_only=True`;
- defaults to CPU for reproducibility;
- accepts `auto`, `cpu`, `cuda` or `mps` only as explicit backend/runtime configuration;
- locates an explicit weights path first and otherwise checks beside the installed package module;
- fails clearly when the optional runtime or weights are unavailable.

The first real Windows package probe established an additional implementation fact that was not
assumed from the high-level package documentation: version `1.0.5` asserts that `predict_raw` receives
a `torch.Tensor` with uint8 RGB geometry. The local adapter therefore builds a writable NumPy uint8
window and converts it with `torch.from_numpy` before calling `predict_raw`.

## Scene-boundary backend

`TransNetV2SceneBoundaryBackend` composes existing local pieces rather than bypassing them:

`Asset revision`
`-> VideoAssetResolver`
`-> streaming FFmpeg RGB24 frames`
`-> TransNetV2WindowPredictor`
`-> prediction stitcher`
`-> scene normalization`
`-> SceneDetectionResult`
`-> PolicyDrivenShotDetector`
`-> ShotBoundaryProposal[]`

The backend receives authoritative source duration from `VideoAssetResolver`; it does not infer Asset
identity or duration from a model package.

## Gap-free scene normalization

The original TransNetV2 convenience scene conversion represents above-threshold transition spans as
separators between stable scene intervals. This project ultimately needs contiguous source ranges for
EDL-safe media handling.

R0.1-D1 therefore converts every **internal** contiguous above-threshold transition run into one cut at
the run midpoint. Transition runs touching the start or end of the source do not create artificial
edge cuts. This is a deliberate local normalization policy, not copied upstream behavior.

The threshold and sampling rate remain backend configuration, not application-level `ShotDetectionOptions`.

## R0.1-D1 validation scope

Unit coverage includes:

- transition-run to millisecond boundary conversion;
- threshold/probability validation;
- backend composition with an injected frame source and predictor;
- zero-duration short-circuit behavior;
- exact model-window and RGB24 geometry checks;
- lazy optional-runtime loading using test doubles;
- package-local weights discovery behavior;
- model state loading and `predict_raw` output normalization.

The real Windows package probe is automated by `.github/workflows/transnet-runtime-probe.yml` and
runs when the runtime adapter, probe script or workflow itself changes. A real-video FFmpeg + model
probe follows only after that runtime gate passes.

# transnetv2-pytorch Runtime — R0.1-D Provenance Record

## Package reference

- Package: `transnetv2-pytorch`
- Reviewed version: `1.0.5`
- PyPI release date: 2025-06-01
- Package repository: `allenday/transnetv2_pytorch`
- License expression published by PyPI: MIT
- Requires Python: `>=3.10`
- Low-level API used as the compatibility target: `TransNetV2.predict_raw`

The local runtime and normalization code are independently implemented. No source code from
`transnetv2-pytorch` or `soCzech/TransNetV2` is copied.

## Dependency boundary

R0.1 deliberately does **not** add `transnetv2-pytorch`, Torch or NumPy to the project's base
installation. Heavy-runtime probes use an isolated uv invocation:

```powershell
uv run --with "transnetv2-pytorch==1.0.5" ...
```

This keeps the default project environment light while the optional runtime boundary is validated.

## Runtime adapter evidence

The Windows package probe established that version `1.0.5` requires `predict_raw` input to be a
`torch.Tensor` with uint8 RGB geometry. The local adapter therefore builds a writable NumPy uint8
window and converts it with `torch.from_numpy` before calling `predict_raw`.

At commit `1aeed11f80a6bae873847d7b2434488b45880074`, both the ordinary quality gate and the real
Windows runtime probe passed. This proved package installation, package-local weights discovery,
model state loading and real `predict_raw` execution on Python 3.12 / Windows Server 2025.

## Real-video full-chain evidence

R0.1-D2 is validated at commit `0c1c6098b973eca14b3a9b93cfa0c4c270c4e9ea`.

The Windows integration workflow installs a pinned FFmpeg 8.1 Windows build, verifies the archive
SHA-256, generates a four-second MP4 containing hard cuts at approximately 1, 2 and 3 seconds, then
executes the complete path:

`MP4 -> FFmpeg RGB24 stream -> 100/50 TransNetV2 windows -> real Torch model -> scene normalization`

Observed result:

```text
TransNetV2 video probe: PASS
duration_ms=4000
boundary_count=3
scene_end_times_ms=(960, 1960, 2960)
```

The detected boundaries are inside the authoritative source duration and closely match the known
synthetic hard-cut positions. The workflow publishes `ci/transnetv2-windows-video` and remains a
relevant-path integration gate.

## R0.1 closure

The Shot Detection selective-migration phase now has evidence for:

- pure duration/boundary policy;
- model-agnostic ShotDetector contract;
- streaming FFmpeg RGB24 decode;
- bounded-memory 100/50 TransNetV2 windowing;
- prediction stitching;
- gap-free scene normalization;
- real `transnetv2-pytorch==1.0.5` inference on Windows;
- real video file full-chain execution.

Shot Detection therefore exits R0.1 as a validated capability. Asset identity, Shot identity commit,
persistence and downstream understanding remain separate architectural phases.

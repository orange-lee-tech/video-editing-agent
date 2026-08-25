# Third-Party Windows Runtime Notices

This engineering artifact contains exact third-party payloads selected by
`resources/packaging/runtime-manifest.json`. Package metadata and license files distributed inside
each Python payload remain part of the notice chain and must not be removed.

The managed Python standard-library tree is taken from the same pinned CPython 3.12.13 runtime
used by PyInstaller and remains covered by the Python Software Foundation license distributed with
that runtime.

## FFmpeg / ffprobe

- BtbN FFmpeg-Builds tag `autobuild-2026-08-20-13-45`.
- Revision `n8.1.2-44-g7c533d0f86`, LGPL shared Windows x64 asset.
- Archive SHA-256 `d311c8c7b86e06b54588e442652f963bae165bd4d8393e73cc9ebb445b025547`.
- Runtime validation rejects `--enable-gpl` and `--enable-nonfree`.
- The distributor-provided `LICENSE.txt` is included alongside this notice.

Codec and patent review remains separate from FFmpeg copyright licensing.

## TransNetV2 CPU runtime

- `transnetv2-pytorch==1.0.5`, MIT; wheel SHA-256
  `9f8e72085526aaa95383d219b6750b1fa45b865fd10d840cafa12ef78ab3bf27`.
- Exact Windows CPU dependency resolution is recorded in
  `packaging/requirements-transnet-windows-cpu.lock`.
- The resolved baseline includes `torch==2.13.0+cpu` and package-owned weights.
- Installed wheel metadata and license files are retained in the runtime tree.

## Speech runtime and model

- `faster-whisper==1.2.1`, MIT; wheel SHA-256
  `79a66ad50688c0b794dd501dc340a736992a6342f7f95e5811be60b5224a26a7`.
- Exact native/transitive resolution is recorded in
  `packaging/requirements-speech-windows-cpu.lock`, including `ctranslate2==4.8.1`,
  `av==18.1.0`, and `onnxruntime==1.29.0`.
- PyAV itself is BSD-3-Clause. Its upstream Windows wheel normally bundles a broad FFmpeg DLL
  set, including GPL codec libraries. Those wheel-provided native DLLs are intentionally excluded.
  The retained PyAV 18.1.0 extension modules are instead staged with aliases to the exact
  LGPL-only FFmpeg 8.1 shared DLL payload identified above; preparation and packaged probes verify
  decode compatibility. PyAV's own license metadata remains in the runtime tree.
- Model: `Systran/faster-whisper-base`, revision
  `ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66`, model card license MIT.
- Model file SHA-256 identities:
  - `config.json`: `56a6d8110d311f19c8f0471e562832c7527f146b567275bfca59fcf7c184da9a`;
  - `model.bin`: `d01c3014881c9c6f3133c182f3d2887eb6ca1c789a7538c5c007196857a0a6a9`;
  - `tokenizer.json`: `fb7b63191e9bb045082c79fd742a3106a12c99513ab30df4a0d47fa6cb6fd0ab`;
  - `vocabulary.txt`: `34ce3fe1c5041027b3f8d42912270993f986dbc4bb34cf27f951e34a1e453913`.
- Product runtime uses CPU/int8 and `local_files_only=True`.

The hash-addressed package evidence records deterministic component file/tree hashes.

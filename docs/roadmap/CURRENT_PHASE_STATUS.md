# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 95%  
**Current phase:** R0.12 — Stage-A final closure / runtime payload / final Human Gate  
**Engineering state:** STAGE_A_WINDOWS_RUNTIME_PAYLOAD_CLOSURE_ACTIVE  
**Updated:** 2026-08-25

## Progress truth

Structural percentage measures real ordinary-user end-to-end usability, not module/test/UI count.

Hard 100% contract:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Current gates:

- Planning Product/Human Gate: PASS on the supported Stage-A surface.
- local reference video: supported.
- remote reference URL: deliberately deferred to 2.0; not a 1.0 blocker.
- Editing no-speech Human baseline: PASS with real final MP4, source audio and rights-safe BGM.
- Workspace/desktop UX: ACCEPTED / MERGED in PR #17.
- Windows onedir packaging foundation: ACCEPTED / MERGED in PR #19.
- exact Windows runtime payload closure: ACTIVE / RELEASED.
- speech-bearing original voice + trusted subtitles: final runtime + Human evidence OPEN.
- Stage-A completion gate: OPEN.

Therefore progress remains **95%**, not 100%.

## Accepted Packaging foundation

PR #19 squash merge:

`cb63713c0daa02b396fd4f5268d280af831d5f70`

Implementation head:

`cf3e4ff7f2a05b88dabef33867ef813f67956cfb`

Proven foundation capabilities:

```text
runtime BOM / manifest + schema
→ strict manifest validation
→ frozen/development/managed ResourceRuntimeLocator
→ existing Environment Doctor integration
→ pinned PyInstaller 6.16.0 Windows x64 onedir
→ static staged-package inspection
→ packaged Doctor
→ packaged GUI launcher
→ external temporary Project Workspace
→ plaintext-secret scan
→ SHA-addressed GitHub artifact + evidence
```

The Windows Packaging Candidate workflow completed successfully and uploaded an identifiable artifact tied to the implementation SHA. Main `cb63713...` subsequently passed CI and document-registry.

This proves the packaging architecture, not final runtime completeness. The artifact intentionally reported required media/speech payloads as missing rather than fabricating readiness.

## Active construction — runtime payload closure

Construction branch:

`work/r012-runtime-payload-closure`

The accepted foundation must now receive exact reproducible payloads without weakening its flexible locator/manifest architecture.

### FFmpeg / ffprobe

Use an exact **LGPL-only** Windows x64 build; GPL/nonfree developer `full_build` payloads are forbidden for the release candidate.

Current engineering candidate:

- upstream distribution: BtbN FFmpeg-Builds;
- release tag: `autobuild-2026-08-20-13-45`;
- FFmpeg revision family: `n8.1.2-44-g7c533d0f86`;
- asset: `ffmpeg-n8.1.2-44-g7c533d0f86-win64-lgpl-shared-8.1.zip`;
- archive SHA-256: `d311c8c7b86e06b54588e442652f963bae165bd4d8393e73cc9ebb445b025547`.

The implementation must verify the downloaded archive hash and runtime `-version` configuration, retain required license/NOTICE/provenance evidence, and make ffmpeg/ffprobe executable discovery come only from the manifest/locator in frozen mode.

### TransNetV2

Retain `transnetv2-pytorch==1.0.5` and package-owned weights.

Exact PyPI wheel identity:

`transnetv2_pytorch-1.0.5-py3-none-any.whl`

SHA-256:

`9f8e72085526aaa95383d219b6750b1fa45b865fd10d840cafa12ef78ab3bf27`

Close the CPU PyTorch/native transitive runtime deliberately; do not depend on an existing `.venv` or user Python.

### Speech

Retain the accepted Stage-A baseline:

- `faster-whisper==1.2.1`;
- wheel SHA-256 `79a66ad50688c0b794dd501dc340a736992a6342f7f95e5811be60b5224a26a7`;
- `Systran/faster-whisper-base` revision `ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66`;
- CPU / int8;
- local-files-only.

Close CTranslate2/PyAV and other native/transitive payload identities, required notices and model-file hashes. No CUDA hard requirement and no implicit model download.

## Runtime closure proof required

The next candidate should prove, from the packaged/managed runtime rather than the development environment:

- FFmpeg and ffprobe execute and Doctor reports READY;
- TransNet package + weights import/load and a bounded CPU prediction probe succeeds;
- faster-whisper native runtime + pinned model load locally and a bounded recognition probe succeeds;
- manifest/Doctor/package evidence records exact component identities and hashes;
- no developer tree, secret or repository-relative fallback is required;
- packaged launcher and external Workspace smoke remain green.

## Final closure after runtime payload acceptance

Then perform the final packaged Human Gate:

- ordinary launcher without repo/Python/uv;
- packaged Workspace/UX behavior;
- supported Planning path;
- Editing no-speech non-regression as needed;
- one clear single-speaker original-voice + trusted-subtitle run;
- protected Windows credential/profile round trip;
- exact artifact identity recorded.

Only then may structural progress become 100%.

## Active Work Order

`R0.12-STAGE-A-FINAL-CLOSURE-002`

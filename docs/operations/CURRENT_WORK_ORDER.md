# Current Work Order

**ID:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Status:** ACTIVE  
**Phase:** R0.12 — Stage-A final closure  
**Mode:** RUNTIME PAYLOAD CLOSURE → FINAL PRODUCT/HUMAN GATE  
**Accepted production-code baseline:** `cb63713c0daa02b396fd4f5268d280af831d5f70`  
**Updated:** 2026-08-25  
**Codex release:** OPEN — `work/r012-runtime-payload-closure` / Windows runtime payload closure

## Objective

Turn the accepted Windows packaging foundation into a truthful ordinary-user runtime by closing the exact FFmpeg/ffprobe, TransNetV2 and speech payloads, while preserving the existing manifest/locator/Doctor architecture and all Domain/editorial boundaries.

Planning remains PASS on supported 1.0. Ordinary no-speech Editing remains Human PASS. Remote reference URL remains deferred to 2.0. Workspace/UX and the Windows packaging foundation are accepted. The remaining engineering terrain before final Human Gate is runtime payload completeness and real packaged capability proof.

## Permanent construction principles

1. bounded self-repair inside the active runtime/package boundary;
2. flexible manifest/locator capability ownership — do not replace it with developer-path hard coding;
3. CPU ordinary-user baseline; no CUDA hard requirement;
4. user/project writable data remains outside the install tree;
5. no secrets in build/runtime payloads;
6. one exact reproducible identity for every redistributed binary/model/native component;
7. reuse existing Environment Doctor and application composition;
8. Codex makes maximal bounded progress per batch and does not stop for ordinary reversible details;
9. ChatGPT and Codex operate serially on engineering surfaces, not concurrently.

## Accepted waves

### Wave A — governance — ACCEPTED

### Wave B — reference compatibility — ACCEPTED / remote product support deferred to 2.0

### Wave C — Workspace + UX — ACCEPTED / PR #17

Merge: `4b2b4ed5f6e2347ae3b29381f39e79ad6930e393`.

### Wave D1 — Windows Packaging foundation — ACCEPTED / PR #19

Merge: `cb63713c0daa02b396fd4f5268d280af831d5f70`.

Accepted proof includes runtime manifest/schema, validator, ResourceRuntimeLocator, existing Doctor integration, PyInstaller 6.16.0 onedir, package inspection, packaged launcher/Doctor/external-Workspace smoke and SHA-addressed artifact workflow.

Foundation implementation head `cf3e4ff7f2a05b88dabef33867ef813f67956cfb` produced a successful Windows Packaging Candidate artifact. The artifact was intentionally structural: missing runtime payloads were reported honestly.

## Wave D2 — Windows runtime payload closure — ACTIVE / RELEASED

Construction branch:

`work/r012-runtime-payload-closure`

### 1. FFmpeg / ffprobe payload

Use this engineering candidate unless its own validation disproves suitability:

- distributor: BtbN FFmpeg-Builds;
- tag: `autobuild-2026-08-20-13-45`;
- revision: `n8.1.2-44-g7c533d0f86`;
- asset: `ffmpeg-n8.1.2-44-g7c533d0f86-win64-lgpl-shared-8.1.zip`;
- archive SHA-256: `d311c8c7b86e06b54588e442652f963bae165bd4d8393e73cc9ebb445b025547`.

Required:

- deterministic download/cache input with exact hash verification;
- inspect `ffmpeg -version` / `ffprobe -version` and record configuration;
- reject GPL/nonfree configuration;
- retain LGPL/license/build/provenance/NOTICE evidence required by ADR-001/ADR-008;
- package ffmpeg/ffprobe and required shared DLLs under explicit manifest ownership;
- frozen product resolution must not use PATH or repository `.tools` fallback.

### 2. TransNetV2 payload

Baseline:

- `transnetv2-pytorch==1.0.5`;
- wheel `transnetv2_pytorch-1.0.5-py3-none-any.whl`;
- wheel SHA-256 `9f8e72085526aaa95383d219b6750b1fa45b865fd10d840cafa12ef78ab3bf27`;
- CPU ordinary baseline;
- package-owned weights.

Required:

- close exact CPU PyTorch/native dependency versions and hashes;
- preserve relevant license/NOTICE/provenance;
- create a reproducible managed/bundled component tree, not a `.venv` copy;
- prove frozen app can import/load the runtime and weights;
- run a bounded deterministic CPU prediction/load probe.

### 3. Speech payload

Baseline:

- `faster-whisper==1.2.1`;
- wheel `faster_whisper-1.2.1-py3-none-any.whl`;
- wheel SHA-256 `79a66ad50688c0b794dd501dc340a736992a6342f7f95e5811be60b5224a26a7`;
- model `Systran/faster-whisper-base`;
- revision `ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66`;
- CPU/int8;
- local-files-only.

Required:

- close exact CTranslate2/PyAV/other native dependency versions, hashes and notices;
- capture exact model file identities/hashes and model license evidence;
- do not permit implicit model/network download at product runtime;
- prove frozen/managed runtime imports and the pinned model loads;
- run bounded local ASR on a deterministic short speech sample where practical.

PyAV's bundled FFmpeg libraries form their own transitive notice/license chain; do not treat the main ffmpeg executable notice as covering them automatically.

### 4. Integrated packaged proof

Rebuild an identifiable Windows x64 onedir candidate and prove:

- runtime manifest validator PASS;
- staged package inspection PASS;
- FFmpeg/ffprobe Doctor READY and executable probe PASS;
- TransNet runtime/weights READY and real load/predict probe PASS;
- speech runtime/model READY and real load/recognition probe PASS;
- packaged GUI launcher PASS;
- external temporary Project Workspace PASS;
- no repo/Python/uv/Git/developer PATH requirement;
- no plaintext secret or forbidden developer tree;
- exact source SHA, payload hashes, notices and evidence retained/uploaded.

A large artifact is acceptable if required by retained 1.0 capabilities. Do not silently defer required runtime merely to keep package size small.

## Hard boundaries

Do not start:

- installer / onefile / auto-updater / signing;
- Remote Reference URL 2.0;
- TTS or advanced separation;
- rich effects/NLE expansion;
- Domain/EDL/Renderer authority redesign;
- unrelated cleanup.

Do not claim Stage-A 100% from engineering probes alone.

## Wave E — final Product/Human Gate

After D2 is accepted, the Product Owner tests the exact packaged artifact for ordinary launcher/Workspace behavior and one clear single-speaker original-voice + trusted-subtitle path, together with retained supported Planning/Editing expectations and protected credential/profile behavior.

Only after those gates and exact-head CI pass may Stage-A become 100%.

## Current progress

**95%**.

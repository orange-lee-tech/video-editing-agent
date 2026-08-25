# Codex Execution Entry

**Last updated:** 2026-08-25  
**Purpose:** expose the currently authorized local construction release.

## Release state

**Work Order:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Release:** OPEN — WINDOWS RUNTIME PAYLOAD CLOSURE  
**Construction branch:** `work/r012-runtime-payload-closure`  
**Accepted Packaging foundation:** `cb63713c0daa02b396fd4f5268d280af831d5f70`  
**Foreman:** ChatGPT  
**Authority:** `docs/operations/CURRENT_WORK_ORDER.md`

The Packaging foundation is already merged. Do not recreate it. This batch must close the actual Windows runtime payloads and prove them through the accepted manifest/locator/Doctor/onedir architecture.

## Mandatory attention order

1. root `AGENTS.md`;
2. `docs/DOCUMENT_REGISTRY.json`;
3. `docs/operations/CURRENT_CONTROL_STATE.md`;
4. `docs/roadmap/CURRENT_PHASE_STATUS.md`;
5. `docs/operations/CURRENT_WORK_ORDER.md`;
6. accepted Packaging foundation code on main;
7. ADR-001 / ADR-008 and upstream ledger only as needed for concrete redistribution work;
8. task-relevant source/tests/scripts/workflows.

Default-exclude archives, private data, `.venv`, `.uv-cache*`, arbitrary `.tools`, old build/dist output and unrelated history.

## Starting rule

Reobserve `origin/main`, the local branch and working tree before editing. Preserve unknown local changes. No blind reset/stash/clean.

The intended branch starts from a main control baseline newer than `cb63713...`; pull/rebase only by safe fast-forward or create the branch from the current remote branch prepared by ChatGPT. Do not force-push rewritten shared history.

For repository PowerShell scripts use process-scoped execution policy bypass when needed, e.g.:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_windows.ps1
```

Do not change machine-wide ExecutionPolicy.

## Authorized objective

In one low-frequency implementation batch, make the retained local media and speech capabilities genuinely resolvable from a reproducible Windows product payload.

This is implementation + build + debug + self-repair, not validation-only work. Continue through ordinary reversible engineering decisions without asking the user/ChatGPT.

## Payload A — FFmpeg / ffprobe

Use the following exact engineering candidate unless runtime/configuration verification disproves suitability:

- BtbN release tag: `autobuild-2026-08-20-13-45`;
- revision family: `n8.1.2-44-g7c533d0f86`;
- Windows x64 asset: `ffmpeg-n8.1.2-44-g7c533d0f86-win64-lgpl-shared-8.1.zip`;
- archive SHA-256: `d311c8c7b86e06b54588e442652f963bae165bd4d8393e73cc9ebb445b025547`.

Required work:

- deterministic acquisition with hash verification;
- inspect `ffmpeg -version` / `ffprobe -version` and fail closed on GPL/nonfree configuration;
- preserve exact provenance, build/config evidence, LGPL/license/NOTICE material and source/build-reference obligations required by ADR-001/ADR-008;
- stage ffmpeg/ffprobe plus required shared DLLs under explicit runtime-manifest ownership;
- frozen locator must use this owned payload only, never PATH or repository `.tools`.

Do not copy the pre-existing developer `full_build`.

## Payload B — TransNetV2

Fixed baseline:

- `transnetv2-pytorch==1.0.5`;
- wheel: `transnetv2_pytorch-1.0.5-py3-none-any.whl`;
- wheel SHA-256: `9f8e72085526aaa95383d219b6750b1fa45b865fd10d840cafa12ef78ab3bf27`;
- CPU ordinary-user baseline;
- package-owned weights expected by existing adapter.

Required work:

- derive and pin an exact Windows CPU dependency set, including PyTorch/native dependencies and hashes;
- preserve licenses/notices/provenance;
- construct a product-owned bundled/managed tree rather than copying `.venv`;
- update manifest classifications/hash/notice state truthfully;
- prove the frozen app can activate/import the managed runtime;
- prove the package-owned weights load;
- run a bounded CPU model prediction/load probe using deterministic input.

If PyTorch makes the artifact large, continue. Size alone is not authority to defer a retained core runtime.

## Payload C — speech

Fixed baseline:

- `faster-whisper==1.2.1`;
- wheel SHA-256: `79a66ad50688c0b794dd501dc340a736992a6342f7f95e5811be60b5224a26a7`;
- model: `Systran/faster-whisper-base`;
- revision: `ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66`;
- CPU / int8;
- `local_files_only=True`.

Required work:

- pin exact Windows CPU native/transitive payloads such as CTranslate2 and PyAV from the real dependency resolution, with hashes and notices;
- treat PyAV's bundled FFmpeg libraries as their own notice/license chain;
- acquire the exact model revision during build/preparation, record exact model file hashes and license/provenance;
- construct a product-owned bundled/managed tree;
- no runtime implicit download;
- prove frozen activation/import + model load;
- run bounded local ASR on a deterministic short spoken sample where practical.

Do not substitute a different Whisper model to simplify packaging.

## Integrated proof

Build a new identifiable Windows x64 onedir candidate and continue until the available released terrain is exhausted.

Required automated evidence:

- full normal repo engineering gate;
- runtime-manifest validator;
- static staged package inspection;
- FFmpeg/ffprobe real execution + Doctor READY;
- TransNet real import/load/predict + Doctor READY;
- speech native runtime/model real load/recognition + truthful Doctor state;
- packaged launcher smoke;
- external temporary Project Workspace smoke;
- install tree remains separate from writable project/profile state;
- no plaintext provider secrets or forbidden developer trees;
- exact payload identities/hashes/notices in evidence;
- SHA-addressed GitHub Actions artifact if practical.

Use safe sentinel provider configuration only where a Doctor configuration-state test needs it. Real user API keys are not required for this local runtime closure and must never be printed or committed.

## Autonomy rule

Do not stop for:

- helper/file/test names;
- package directory layout details consistent with manifest ownership;
- exact dependency-resolution mechanics;
- PyInstaller hooks/spec adjustments;
- deterministic download/cache helper implementation;
- test fixtures;
- bounded native DLL/search-path repairs;
- ordinary CI/workflow implementation required for this task.

Self-repair failures inside the release boundary and rerun until stable.

## Stop / escalate only for a genuine boundary

Stop and report only if:

1. exact payload evidence reveals a redistribution/license conflict that cannot be resolved by choosing the already-authorized permissive/LGPL route;
2. progress requires a real user credential/account action;
3. a Product Constitution / retained 1.0 scope decision is required;
4. fixing the issue would change Domain/EDL/Renderer authority;
5. continuing requires installer/onefile/updater/signing, Remote Reference 2.0, TTS, advanced separation/effects or unrelated expansion.

A blocker in one payload does not justify stopping work on the other independent payloads.

## Handoff

Push the branch and report once, with:

- exact HEAD and changed files;
- exact FFmpeg archive/config/hash/notices;
- exact TransNet/PyTorch payload identities and real probe result;
- exact speech native/model payload identities and real ASR probe result;
- final onedir/evidence/artifact identity and size;
- full test/CI/smoke results;
- genuine blockers only;
- whether the exact artifact is ready for the final Product/Human Gate.

Do not claim Stage-A 100%; ChatGPT/Product Owner retain final acceptance authority.

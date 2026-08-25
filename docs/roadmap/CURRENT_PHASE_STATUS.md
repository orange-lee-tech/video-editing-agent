# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 95%  
**Current phase:** R0.12 — Stage-A final closure / Windows packaging / final Human Gate  
**Engineering state:** STAGE_A_WINDOWS_PACKAGING_ACTIVE  
**Updated:** 2026-08-25

## Progress truth

Structural percentage measures real ordinary-user end-to-end usability, not module/test/UI count.

Hard 100% contract:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Current gate state:

- Planning Product/Human Gate: PASS on the supported Stage-A surface.
- local reference video: retained supported Planning input.
- remote reference URL: deliberately hidden and deferred to 2.0 provider-neutral `ReferenceObservation`; not a 1.0 blocker.
- bounded Bilibili acquisition fallback: Engineering PASS, not ordinary 1.0 product capability.
- Editing no-speech ordinary Human baseline: PASS with real final MP4.
- source audio preservation + rights-safe BGM: HUMAN PASS on the accepted real run.
- no-speech subtitle behavior: PASS (`SKIPPED` / no fabricated captions).
- speech-bearing original voice + basic trusted subtitles: engineering seam present; approved/pinned runtime/model + real Human evidence still OPEN.
- Project Workspace / desktop UX consolidation: **ACCEPTED / MERGED** in PR #17.
- Windows distributable proof without Python/uv/repository execution: **ACTIVE / RELEASED**.
- Stage-A completion gate: OPEN.

Therefore structural progress remains **95%**, not 100%.

## Accepted production-code baseline

Workspace/UX accepted merge:

`4b2b4ed5f6e2347ae3b29381f39e79ad6930e393`

PR #17 exact implementation head:

`21b2d1c52fc1b1c8aef6a1d269861ace2f0f7b8c`

Exact-head CI / repository-governance / document-registry all passed before merge.

The final attempted local `maintain.ps1 verify` did not start because the Windows host blocks `.ps1` execution by policy. This is tracked as a shell-invocation constraint, not a quality-gate failure. Use process-scoped ExecutionPolicy bypass for future local script invocation; do not weaken machine-wide policy.

## What is now proven

Ordinary Editing already has real evidence for:

```text
real user footage
→ media understanding
→ rights-safe public BGM
→ EditPlan / grounded Resolver
→ canonical EDL
→ SOURCE_AUDIO preservation
→ capability-aware no-speech subtitle handling
→ Renderer / Review
→ final MP4
```

Workspace/UX now additionally establishes the shared Project Workspace, project-scoped writable state, default-output ownership, bounded form history, project-bound Planning context, configuration surfaces and task-state gating needed before packaging freezes runtime/resource behavior.

The remaining Workspace ordinary-user acceptance is deliberately consolidated into the final packaged-artifact Human Gate. This avoids duplicate acceptance of a development launcher while preserving the final Human requirement.

## Active construction — compatible Windows packaging

Construction branch:

`work/r012-windows-packaging`

Contract:

`docs/operations/WINDOWS_PACKAGING_FOUNDATION_CONTRACT.md`

Execution entry:

`docs/operations/CODEX_EXECUTION_ENTRY.md`

The active wave must turn the existing development environment assumptions into explicit product-owned runtime behavior:

- machine-readable runtime/component manifest;
- manifest validation and package-content allow/deny rules;
- thin frozen/development resource/runtime locator;
- reuse/refactor the existing Environment Doctor rather than creating a second diagnostic architecture;
- approved/pinned TransNet runtime + weights resolution;
- approved/pinned faster-whisper speech runtime/model release strategy;
- approved FFmpeg/ffprobe exact build strategy and notices;
- deterministic Windows x64 onedir build;
- static package inspection;
- packaged launcher + Doctor + external temporary Workspace smoke;
- artifact identity with source SHA, manifest snapshot and hashes where required.

The ordinary target must not need repository checkout, system Python, uv, Git or developer-only PATH setup.

Codex may continue through bounded implementation/repair inside this wave until it has an identifiable onedir artifact and packaged smoke evidence, or reaches a genuine external blocker. It should not stop for ordinary low-risk implementation choices that can be resolved from repository contracts and tests.

## Known local Packaging seed work

The user reported pre-existing untracked local items:

```text
resources/
src/video_editing_agent/adapters/bootstrap/
tests/unit/test_packaging_foundation.py
```

These are not accepted repository facts yet. The active Packaging implementation must inspect and preserve them, classify/reuse useful work, and must not discard them via reset/stash/clean. They should be committed only after review and alignment with the active Packaging contract.

## Remaining retained 1.0 closure terrain

### A. Basic speech/subtitle retained capability

The repository already pins the intended Stage-A baseline to `faster-whisper==1.2.1` and `Systran/faster-whisper-base` at an exact revision, CPU/int8, local-files-only. Packaging must turn that code-level pin into a deliberate distributable/managed component with Doctor evidence rather than relying on developer cache state.

### B. Runtime/legal closure

FFmpeg/ffprobe and any bundled model/native component must have exact distributable identity, provenance/license/NOTICE state and approved release location. Do not copy arbitrary developer `.tools` or cache trees.

### C. Final closure

After Packaging evidence is accepted:

- run retained ordinary Planning/local-reference evidence;
- rerun Editing no-speech baseline if packaging changes touch its path;
- run clear single-speaker original-voice + basic subtitle Human Gate;
- verify packaged launcher/diagnostics without repo/Python/uv;
- exercise the final packaged Workspace/UX Human Gate;
- verify required full quality/governance gates and exact-head CI;
- synchronize live control documents;
- set Stage-A 100% only if every machine/human completion invariant genuinely passes.

## Active Work Order

`R0.12-STAGE-A-FINAL-CLOSURE-002`

The current implementation wave is Windows Packaging and must obey root `AGENTS.md`, `docs/operations/WINDOWS_PACKAGING_FOUNDATION_CONTRACT.md` and the live execution entry.

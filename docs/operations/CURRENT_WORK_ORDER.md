# Current Work Order

**ID:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Status:** ACTIVE  
**Phase:** R0.12 — Stage-A final closure  
**Mode:** WINDOWS PACKAGING → FINAL PRODUCT/HUMAN GATE  
**Accepted production-code baseline:** `4b2b4ed5f6e2347ae3b29381f39e79ad6930e393`  
**Activated:** 2026-08-21  
**Updated:** 2026-08-25  
**Codex release:** OPEN — `work/r012-windows-packaging` / compatible Windows Packaging foundation and artifact proof

## Objective

Reach truthful Stage-A / 1.0 structural closure by converting the already-working repository/development environment into an ordinary-user Windows product without compromising the existing modular architecture.

Planning remains PASS on the supported 1.0 surface. Ordinary no-speech Editing remains Human PASS. Remote reference URL remains deferred to 2.0. Project Workspace + UX consolidation is accepted in PR #17. The active engineering wave is now Windows Packaging plus the retained speech/runtime closure required for the final Product/Human Gate.

## Permanent construction principles

1. **Bounded self-repair** — repair blockers discovered inside the active packaging/1.0 boundary without unrelated cleanup.
2. **Compatible development** — runtime/provider/model/renderer substitutions must remain possible behind existing seams.
3. **Flexible production line** — missing optional capabilities report truthful degraded states rather than silently changing semantics.
4. **Source protection** — user originals remain immutable.
5. **Thin packaging** — bootstrap/resource/runtime location stays outside Domain authority and does not become a second architecture.
6. **Workspace ownership** — user/project writable data stays outside the installation tree.
7. **Single runtime truth** — runtime manifest, locator, Doctor, package validator and build evidence should share one ownership model where practical.
8. **Low-frequency execution** — Codex should make maximal bounded progress per released batch; ordinary reversible implementation decisions do not require repeated user/ChatGPT interruption.

## 1.0 retained scope

Must remain real and supportable:

- Planning: user intent, confirmed facts/constraints, optional local reference → ScriptPlan + ShootingPlan;
- Editing: real user footage → grounded automatic editing → canonical EDL → Renderer/Review → final MP4;
- original/source audio;
- rights-safe BGM;
- basic trusted subtitles for ordinary clear speech using the approved pinned speech capability;
- coherent Project Workspace and desktop interaction;
- truthful capability diagnostics;
- Windows ordinary-user distributable proof without repository/Python/uv/Git requirements.

## Explicitly deferred beyond 1.0

- production synthetic voice/TTS;
- advanced speech/ambience separation;
- rich subtitle animation/effects systems;
- advanced audiovisual/NLE feature surface;
- generic remote-reference URL product support and provider-neutral `ReferenceObservation` implementation.

## Accepted Waves

### Wave A — repository attention/document governance — ACCEPTED

Existing attention firewall, document registry, governance checks and lifecycle rules remain authoritative.

### Wave B — Planning reference compatibility — ACCEPTED / PRODUCT DEFERRED

Local reference video remains supported; remote reference URL is deferred to 2.0. Product Owner reconfirmed this decision on 2026-08-25.

### Wave C — Project Workspace + UX consolidation — ACCEPTED / MERGED

PR #17 merge:

`4b2b4ed5f6e2347ae3b29381f39e79ad6930e393`

Exact implementation head:

`21b2d1c52fc1b1c8aef6a1d269861ace2f0f7b8c`

Exact-head CI, repository-governance and document-registry all passed before merge.

The final ordinary-user Workspace/UX Human Gate is consolidated into the packaged-artifact Human Gate rather than duplicated on the development launcher. It remains mandatory before Stage-A closure.

## Wave D — compatible Windows Packaging foundation — ACTIVE / RELEASED

Construction branch:

`work/r012-windows-packaging`

Primary contract:

`docs/operations/WINDOWS_PACKAGING_FOUNDATION_CONTRACT.md`

Readiness input:

`docs/operations/WINDOWS_DESKTOP_PACKAGING_READINESS.md`

### Required engineering result

Build an identifiable Windows x64 onedir candidate that launches and diagnoses its retained capabilities without relying on a repository checkout, system Python, uv, Git or developer-only PATH setup.

The implementation should progress through the complete available boundary, not stop after creating one class or one test.

Preferred construction sequence:

```text
inspect/preserve existing local Packaging seed work
→ reconcile runtime BOM
→ machine-readable runtime manifest
→ manifest validator
→ frozen/development resource + runtime locator
→ adapt existing Environment Doctor to locator/manifest truth
→ close TransNet runtime/weights location
→ close speech runtime/model location
→ define approved FFmpeg/ffprobe release source/build identity
→ deterministic Windows x64 onedir build
→ static package inspection
→ packaged launcher + Doctor + external temporary Workspace smoke
→ artifact/build manifest + source SHA/component identity
→ upload/retain identifiable candidate evidence
```

### Existing local seed work

The user reports these currently untracked local paths:

```text
resources/
src/video_editing_agent/adapters/bootstrap/
tests/unit/test_packaging_foundation.py
```

Codex must inspect them before editing, preserve useful work, and must not reset/stash/clean them away. They are not accepted facts until reviewed/tested/committed.

### Runtime facts already frozen enough to avoid re-research

- Python baseline: 3.12.
- Desktop shell requires Tcl/Tk.
- TransNet ordinary path uses `transnetv2-pytorch==1.0.5` family and reviewed package-owned weight resolution; final release artifact identity still needs closure.
- Speech baseline in code is `faster-whisper==1.2.1`, `Systran/faster-whisper-base`, exact model revision `ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66`, CPU/int8, local-files-only.
- Existing Environment Doctor already probes host, FFmpeg/ffprobe, TransNet, preview and provider configuration. Extend/reuse it rather than creating a second Doctor architecture.
- Existing repository-local `.tools` FFmpeg path is a development fallback only.

### Packaging hard prohibitions

Do not:

- copy `.venv`, `.private`, `.uv-cache*`, `.git` or arbitrary `.tools` trees into the package;
- bundle plaintext API credentials;
- make install directory the Project Workspace/profile root;
- hard-code one provider/model as Domain truth;
- silently redistribute an unreviewed FFmpeg binary/model/native payload;
- bypass ordinary application composition just to make an EXE launch;
- require CUDA for the accepted CPU baseline;
- claim Stage-A 100% because an executable exists.

### Codex autonomy inside this wave

Codex is authorized to perform bounded multi-file implementation, focused/full tests, build/debug/repair loops and Packaging automation until one of these stopping conditions occurs:

1. an identifiable onedir candidate + packaged smoke evidence is produced; or
2. a genuine external blocker requires Product Owner/ChatGPT input, such as unresolved redistribution/license approval, secret/account access, or a constitutional/product-scope decision; or
3. continuing would cross into installer/onefile/updater/signing work not yet required for the onedir proof.

Ordinary implementation choices—file names, helper placement, test structure, PyInstaller hook/spec details, manifest schema refinements consistent with the contract, locator plumbing, deterministic script composition—do **not** require user interruption.

## Wave E — final retained Product/Human Gate

After Wave D produces an identifiable candidate:

1. double-click/ordinary packaged launcher works without repo/Python/uv;
2. packaged Project Workspace behavior is understandable and writes outside install tree;
3. Planning supported surface remains usable;
4. Editing no-speech baseline remains non-regressed;
5. one clear single-speaker sample proves original speech + trusted basic subtitles through the approved pinned speech capability;
6. bundled/managed FFmpeg, TransNet and speech states are truthful in Doctor;
7. protected profile/credential behavior works on Windows;
8. full quality/governance/exact-head CI passes;
9. exact artifact identity is recorded.

Only then may control state set `core_2_editing_product_gate: PASS`, `stage_a_completion_gate: PASS`, and `structural_progress_percent: 100`.

## Current progress

**95%**.

The percentage deliberately stays at 95 until a real Windows distributable and final retained Human evidence exist. Engineering should nevertheless advance aggressively inside the released boundary rather than preserving the percentage through procedural delay.

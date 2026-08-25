# Codex Execution Entry

**Last updated:** 2026-08-25  
**Purpose:** expose the currently authorized local construction release.

## Release state

**Work Order:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Release:** OPEN — WINDOWS PACKAGING FOUNDATION + ONEDIR ARTIFACT PROOF  
**Construction branch:** `work/r012-windows-packaging`  
**Accepted Workspace baseline:** `4b2b4ed5f6e2347ae3b29381f39e79ad6930e393`  
**Foreman:** ChatGPT  
**Authority:** `docs/operations/CURRENT_WORK_ORDER.md`  
**Wave contract:** `docs/operations/WINDOWS_PACKAGING_FOUNDATION_CONTRACT.md`

Codex must not infer authority from stale PR comments, old branches, archived work orders or prior chat history. The live control files above govern.

## Mandatory attention order

1. root `AGENTS.md`;
2. `docs/DOCUMENT_REGISTRY.json`;
3. `docs/operations/CURRENT_CONTROL_STATE.md`;
4. `docs/roadmap/CURRENT_PHASE_STATUS.md`;
5. `docs/operations/CURRENT_WORK_ORDER.md`;
6. `docs/operations/WINDOWS_PACKAGING_FOUNDATION_CONTRACT.md`;
7. `docs/operations/WINDOWS_DESKTOP_PACKAGING_READINESS.md` only as needed;
8. task-relevant source/tests/scripts/workflows;
9. Product/Architecture/CAP/ADR/upstream ledger only when a concrete implementation or redistribution question requires them.

Default-exclude `docs/archive/**`, `.private/**`, `.uv-cache*/**`, `.venv/**`, `build/**`, `dist/**` and unrelated history.

## Accepted baseline

Workspace/UX PR #17 is accepted and merged at:

`4b2b4ed5f6e2347ae3b29381f39e79ad6930e393`

Its exact implementation head `21b2d1c52fc1b1c8aef6a1d269861ace2f0f7b8c` passed CI, repository-governance and document-registry.

The final local `.ps1` verify attempt was blocked before script start by Windows ExecutionPolicy. Treat this as a shell-invocation constraint, not a verify result. For repository PowerShell scripts use an explicit process-scoped invocation such as:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\maintain.ps1 verify -SkipSync
```

Do not change machine-wide execution policy merely to run project scripts.

## Local preservation rule

The user currently reports these untracked local Packaging seed paths:

```text
resources/
src/video_editing_agent/adapters/bootstrap/
tests/unit/test_packaging_foundation.py
```

Before any branch switch or edit:

- inspect them;
- preserve them exactly;
- determine whether they align with the current Packaging contract;
- reuse/repair useful work instead of recreating it;
- do **not** reset, stash, clean or overwrite unknown local work blindly.

They become accepted repository evidence only after review, tests and an intentional commit.

## Authorized objective

Produce the deepest truthful Windows Packaging implementation possible in one bounded execution batch, ideally through an identifiable Windows x64 onedir candidate and packaged smoke evidence.

This is not a validation-only assignment. Codex should implement, test, debug and self-repair continuously inside the released boundary.

### Required implementation terrain

1. **Runtime BOM / manifest**
   - establish one machine-readable source for product-owned bundled/managed/remote/development-only components;
   - include stable id, version/revision, capability, location policy, required/optional classification, provenance/license/NOTICE state and hashes where distributable bytes are owned;
   - reject machine-specific absolute release paths and development-only content.

2. **Manifest validation / static package policy**
   - reject missing required fields, duplicate ownership, forbidden developer paths and unreviewed payloads;
   - define required staged artifact content and forbidden content.

3. **Resource/runtime locator**
   - explicitly distinguish development and frozen/packaged mode;
   - resolve install resources, bundled runtimes, managed optional components, user profile paths and external Project Workspaces without leaking repo-relative assumptions into business logic;
   - keep locator/bootstrap outside Domain/editorial authority.

4. **Capability Doctor integration**
   - reuse/refactor the existing `EnvironmentDoctor` and existing probes rather than inventing a second diagnostic architecture;
   - make FFmpeg/ffprobe, TransNet, speech/model, credential/profile and workspace/install permission states truthful under packaged resolution;
   - missing optional/remote capability must degrade explicitly rather than fail mysteriously.

5. **TransNet closure**
   - preserve the reviewed `transnetv2-pytorch==1.0.5` family and package-owned weight expectation;
   - make the packaged runtime/weight location explicit and testable;
   - do not rely on developer cache/PATH coincidence.

6. **Speech closure**
   - preserve the existing frozen Stage-A baseline: `faster-whisper==1.2.1`, `Systran/faster-whisper-base`, revision `ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66`, CPU/int8, local-files-only;
   - implement a deliberate bundled or managed component path consistent with license evidence and Doctor state;
   - never enable implicit network model download as a hidden runtime requirement.

7. **FFmpeg/ffprobe release strategy**
   - do not copy arbitrary existing `.tools` binaries into release output;
   - establish exact approved release identity/build/config/provenance/hash/notices consistent with ADR-001 and ADR-008;
   - if exact redistributable binary approval remains externally unresolved, continue all other Packaging implementation and surface this as the narrow external blocker rather than stopping the whole batch early.

8. **Deterministic Windows x64 onedir build**
   - choose/pin a practical bundler version and checked-in build configuration;
   - use ordinary application composition/launcher;
   - include only manifest-approved runtime/resources;
   - exclude secrets and developer trees;
   - emit source git SHA and component/build identity.

9. **Packaging micro-automation**
   - prefer a small PowerShell entry surface composing deterministic helpers;
   - build → validate staged tree → run packaged launcher/Doctor/external temporary Workspace smoke → collect evidence;
   - invoke repository PowerShell scripts with process-scoped ExecutionPolicy bypass where required.

10. **Artifact evidence**
   - produce/retain an identifiable candidate artifact or staged directory plus build manifest, runtime manifest snapshot, validation/smoke result and hashes where applicable;
   - if GitHub Actions packaging workflow is practical, add it and upload the artifact/evidence together.

## Known runtime facts — do not waste the batch re-researching settled choices

- Python baseline: 3.12.
- Tkinter/Tcl/Tk is part of the desktop shell requirement.
- Existing Environment Doctor already has host, FFmpeg, TransNet, preview and provider probes.
- Speech baseline/model/revision is already pinned in repository code.
- Remote provider code may bundle; API keys must not.
- GStreamer/VLC/libmpv are not mandatory Packaging dependencies unless the ordinary path proves otherwise.
- Remote Reference URL remains deferred to 2.0 and is out of scope.

## Autonomy / low-frequency interaction rule

Within this released wave, Codex should decide ordinary reversible engineering details independently and keep going. Examples that do not require interruption:

- helper/module/file names;
- small schema refinements consistent with the contract;
- test placement;
- PyInstaller spec/hook mechanics;
- locator/bootstrap plumbing;
- PowerShell helper organization;
- bounded refactors required to remove developer-path assumptions;
- iterative fixes required by tests/build/package smoke.

Ask/stop only when progress requires a genuine external decision or credential, including:

- unresolved redistribution/license approval for a concrete binary/model;
- API/user-account secret action that cannot be tested with a safe sentinel;
- Product Constitution / retained 1.0 scope change;
- a change that would alter Domain/EDL/Renderer authority;
- installer/onefile/updater/signing expansion beyond the current onedir proof.

When one narrow external blocker exists, continue independent parallel Packaging work first and report the blocker at the end unless it prevents all further progress.

## Verification protocol

During iteration use focused tests. Before handoff run, as applicable:

- repo doctor;
- Ruff format/check;
- mypy `src`;
- full pytest;
- import-linter;
- `uv build`;
- `git diff --check`;
- launcher smoke;
- runtime-manifest validator;
- static staged-package validator;
- packaged `doctor`/launcher smoke;
- external temporary Project Workspace smoke;
- plaintext secret scan.

For `.ps1` execution under the current Windows host, use process-scoped `-ExecutionPolicy Bypass`; do not treat host policy refusal as an application test failure.

## Handoff / stopping condition

Do not stop after merely proving tests pass. Continue until one of these is true:

1. the released Packaging terrain has produced an identifiable onedir candidate and packaged smoke evidence; or
2. a real external blocker prevents further bounded progress; or
3. continuing would cross the explicit release boundary.

At handoff report:

- exact branch HEAD;
- changed/added files;
- what was reused from the pre-existing untracked Packaging seed;
- runtime manifest/component classifications;
- build/artifact identity and location;
- test/gate/smoke results;
- exact remaining blocker(s), if any;
- whether the same artifact is ready for the final Product/Human Gate.

Do not claim Stage-A 100%; ChatGPT/user retain final acceptance authority.

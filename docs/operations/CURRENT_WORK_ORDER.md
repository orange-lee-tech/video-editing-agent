# Current Work Order

**ID:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Status:** ACTIVE  
**Phase:** R0.12 — Stage-A final closure  
**Mode:** WORKSPACE/UX CONSOLIDATION → WINDOWS PACKAGING → FINAL HUMAN GATE  
**Accepted production-code baseline:** `756a30562dd512fba9868eeee43cf6422f60f642`  
**Current main preparation baseline:** `d26249f71d895efff54c1d7167f4b6bc457b98f1`  
**Activated:** 2026-08-21  
**Updated:** 2026-08-22  
**Codex release:** OPEN — `work/r012-workspace-ux-consolidation` / Workspace + UX consolidation only

## Objective

Reach a truthful Stage-A / 1.0 structural closure without feature creep, while leaving a stable compatible foundation for later commercial-scale development.

The ordinary Editing no-speech baseline has passed a real Human Gate. Planning remains PASS on the supported Stage-A surface. Remote reference URL observation is intentionally deferred to 2.0 and hidden from the ordinary 1.0 UI. The active construction prerequisite is now to consolidate Project Workspace ownership and desktop interaction before packaging freezes path/resource behavior.

## Permanent construction principles

1. **Bounded self-repair** — repair blockers discovered inside the active 1.0/packaging boundary; do not expand into unrelated cleanup.
2. **Compatible development** — solve current defects without locking future provider/model/runtime/renderer substitution.
3. **Flexible production line** — stages expose capability/input/output/diagnostic/fallback semantics; absence of work is not automatically failure.
4. **Source protection** — user originals remain immutable; generated/analyzed/separated media are derived assets.
5. **Thin packaging** — bootstrap/resource/runtime location stays outside Domain authority and does not become a second application architecture.
6. **Attention discipline** — root `AGENTS.md` controls default reading; `docs/archive/**` is excluded by default.
7. **Workspace ownership** — project-specific writable state belongs to the user-selected Project Workspace, not the installation directory or scattered developer paths.

## 1.0 retained scope

Must remain real and supportable:

- Planning: user intent, confirmed facts/constraints, optional local reference → inspectable ScriptPlan + usable ShootingPlan;
- Editing: user-selected real footage → automatic grounded editing → canonical EDL → Review/Renderer → final media;
- original/source audio on the ordinary path;
- rights-safe BGM;
- basic trusted subtitles for ordinary clear speech when the approved speech capability is available;
- deterministic Stage-A editing-expression floor already accepted by the completion contract;
- understandable progress/failure/degraded states;
- coherent Project Workspace ownership and ordinary desktop interaction;
- Windows ordinary-user distributable proof without requiring Python/uv/repository execution.

## Explicitly deferred beyond 1.0

- production synthetic-voice/TTS backend;
- advanced speech/ambience source-separation backend and advanced stem mixing;
- rich subtitle font/animation/speaker systems;
- advanced audiovisual effects and feature-rich NLE behavior;
- generic/unbounded website crawling;
- remote reference URL product support until provider-neutral `ReferenceObservation` exists;
- Bilibili/Douyin/Xiaohongshu remote-reference product UI.

Typed seams already introduced for deferred capabilities must remain; do not remove them merely because their backends are deferred.

## Wave A — repository attention/document governance — ACCEPTED

Accepted outcomes:

- root `AGENTS.md` attention firewall;
- compact `docs/DOCUMENT_REGISTRY.json` relative-path map;
- automatic exhaustive registry inventory;
- update-date/document lifecycle/archive rules;
- `docs/archive/**` default exclusion;
- refreshed live trio and durable R0.12 evidence;
- existing governance checks extended rather than replaced.

Archive decisions remain semantic/manual; automation must not move documents automatically.

## Wave B — bounded Planning reference compatibility — ACCEPTED / PRODUCT DEFERRED

Accepted merge: `756a30562dd512fba9868eeee43cf6422f60f642` (PR #13).

Engineering exploration proved a bounded Bilibili acquisition fallback can live behind the existing acquisition seam while preserving HTTPS/SSRF/DNS/IP/redirect/MIME/size/timeout/provenance rules.

Product decision:

- current Gemini/OpenAI visual adapters are image-frame oriented and do not provide a provider-neutral remote/video-native observation contract;
- forcing ordinary remote references through a heavy full-download → probe → shot-detect → frame-analysis path is not required for 1.0;
- ordinary Tkinter reference-URL input is hidden;
- local reference video remains supported;
- provider-neutral remote/video-native `ReferenceObservation` is deferred to 2.0.

Durable evidence:

`docs/validation/R0.12_REFERENCE_COMPATIBILITY_CLOSURE_2026-08-22.md`

Do not reopen remote reference URL work during Stage A without an explicit new product decision.

## Wave C — Project Workspace + UX consolidation — RELEASED

Construction branch:

`work/r012-workspace-ux-consolidation`

Specification:

`docs/operations/STAGE_A_WORKSPACE_UX_CONSOLIDATION.md`

Execution entry:

`docs/operations/CODEX_EXECUTION_ENTRY.md`

Required outcomes:

- one shared top-level `Project Workspace` context for Planning and Editing;
- Project Workspace owns project-specific cache/work/autosave/undo-redo/log/output state without duplicating canonical Domain authority;
- ordinary output gets a sensible project-local default while preserving explicit Save As;
- configuration import/export/save/delete is consolidated on the main window;
- form-level Clear / Undo / Redo exists with bounded history and safe task-state behavior;
- Planning/Editing sub-sections become vertically collapsible instead of consuming unnecessary horizontal width;
- temporary pixel-camera mark is retired in favor of the approved feather identity if the real asset can be recovered; do not invent an approximation;
- remote reference URL remains hidden;
- existing source/EDL/provider/secret invariants remain unchanged.

This wave is a Packaging prerequisite because it defines writable-data and resource expectations that must not be frozen incorrectly in the distributable.

Codex must stop after this wave's engineering/manual-smoke report. Packaging remains closed until ChatGPT/user accepts the Workspace/UX Human Gate.

## Wave D — compatible Windows packaging foundation — PREPARED / NOT RELEASED

This is an **effective packaging** requirement, not documentation-only preparation.

Readiness input:

`docs/operations/WINDOWS_DESKTOP_PACKAGING_READINESS.md`

Minimum engineering proof:

```text
Windows distributable (prefer onedir first)
→ thin bootstrap
→ resource/runtime locator
→ ordinary GUI launch
→ environment/capability diagnostics
```

Target environment must not require:

- a repository checkout;
- Python installation;
- uv;
- developer-only PATH setup.

Packaging must not:

- hard-code one provider/model as Domain truth;
- place user-writable project/profile data inside the install directory;
- silently bundle unreviewed binaries/models/licenses;
- bypass the ordinary application composition path;
- copy arbitrary `.private`, `.tools`, `.venv`, caches or developer-machine artifacts into release output.

Required compatibility seams:

- resource location separate from business logic;
- runtime capability resolution explicit and diagnosable;
- later TTS/separation/providers/models/renderers can be added without replacing bootstrap architecture;
- FFmpeg/TransNet/speech-runtime/model handling uses deliberate manifest/config ownership;
- existing projects remain readable or have explicit migration if persistence contracts change.

The repository-local `.tools` FFmpeg/ffprobe locator accepted in PR #13 is a development fallback only. Packaging must not treat `.tools` as the install/resource contract.

When later released, Codex may self-repair packaging blockers inside that boundary and re-run validation until stable. It must report non-blocking unrelated debt instead of expanding scope.

## Wave E — final retained Product/Human Gate

After Waves C/D are accepted:

1. Planning without remote URL remains usable; local-reference Planning path is non-regressed.
2. Editing no-speech baseline remains non-regressed.
3. A simple, clear single-speaker video proves original speech + basic trusted subtitle timing with the approved/pinned speech capability.
4. Project Workspace behavior is understandable and project-specific writable state stays outside the install directory.
5. The packaged ordinary Windows surface launches without Python/uv/repository execution and exposes truthful diagnostics.
6. Sources remain unchanged.
7. Full repository quality/governance gates pass.
8. Exact-head CI passes.

Only then may control state set:

- `core_1_planning_product_gate: PASS`;
- `core_2_editing_product_gate: PASS`;
- `stage_a_completion_gate: PASS`;
- `structural_progress_percent: 100`.

## Current progress

**95%**.

Do not trade architecture compatibility, ordinary usability, or truthful product behavior for an artificial 100% number.

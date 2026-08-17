# Current Work Order

**ID:** `R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Stage-A ordinary-user Product Gate closure  
**Mode:** PRODUCT SURFACE → PRODUCT PROBE → HUMAN GATE  
**Accepted production-code baseline:** `1e90e2dd3d235271ef48bb7a708a1899ce5b87a4`  
**Activated:** 2026-08-18  
**Codex release:** ACTIVE — SINGLE COMPLEX BATCH

## Previous Work Order result

`R0.12-PRODUCT-FLOW-ORCHESTRATION-001` — **PASS / CLOSED**.

Closure evidence:

`docs/validation/R0.12_PRODUCT_FLOW_ORCHESTRATION_CLOSURE.md`

Accepted Windows Engineering Probe:

`32046190310` — PASS.

Exact-head deterministic CI:

`32046499144` — PASS.

## Current audit truth

The ordinary-user surface audit is complete:

`docs/validation/R0.12_STAGE_A_PRODUCT_SURFACE_AUDIT.md`

Result: **IMPLEMENTATION REQUIRED**.

The accepted owner chains already work, but the ordinary product path still has concrete gaps:

1. Planning ProductFlow does not expose accepted authoritative-fact/reference inputs;
2. ProductFlow / ProjectWorkspace plumbing drops existing `ReferenceStyleGuidance` before Script/Shooting workflows;
3. the current ProductFlow launch requires hand-written JSON;
4. Editing exposes provider/model/TransNet weight-path/tool arguments that are runtime composition, not editorial meaning;
5. there is no ordinary Windows launcher/file chooser;
6. Planning output returns exact refs but not an immediately readable ScriptPlan/ShootingPlan presentation;
7. ProductFlow progress events are returned after completion rather than observable live;
8. folder selection convenience is absent;
9. Environment Doctor does not currently cover mandatory Shot-detection runtime readiness.

This is the final Stage-A implementation batch before real Product Probe/Human Gate evidence.

## Frozen architecture

The accepted product architecture does not change.

### Planning-only

```text
user goal / commercial facts / optional reference
→ Brief
→ optional reference-only analysis / ReferenceStyleGuidance
→ ScriptPlanningWorkflow
→ ShootingPlanningWorkflow
→ persisted ScriptPlan + ShootingPlan
```

### Editing-only

```text
user-selected local footage + editing intent
→ existing Editing ProductFlow
→ grounded Resolver
→ canonical EDL
→ Renderer
→ Review
→ final MP4
```

### Combined

Planning exact revisions may enrich the same Editing Core. Planning remains optional for Editing.

Canonical EDL remains sole exact timeline authority.

## Codex implementation batch

Codex is the single writer for this implementation surface until it commits/pushes and stops.

### A. Complete the Planning reference bridge

Reuse existing accepted owners:

- `DirectHttpsReferenceAcquirer`;
- `AssetIngestService`;
- `REFERENCE_ANALYSIS_ONLY` policy;
- exact Shot detection;
- provider-neutral visual understanding;
- `ReferenceStyleEvidenceService`;
- existing `ReferenceStyleGuidance`;
- existing Script/Shooting workflows.

Add a product-facing reference input DTO using user semantics rather than AssetRef/ShotRef/timestamps.

Supported Stage-A reference inputs:

- supported direct HTTPS video URL;
- user-selected local reference video.

The product composition must convert these to reference-only Assets/evidence and forward exact `ReferenceStyleGuidance` to **both** Script and Shooting workflows.

Reference media must remain Resolver-ineligible and must never become final-output footage.

Planning with no reference must remain valid and must not require visual/TransNet capabilities.

### B. Preserve authoritative facts / references through ProductFlow

The ordinary Planning surface must be able to create the already-accepted `AuthoritativeFact` and `BriefReference` semantics without users typing internal entity refs.

Commercial Review stays fail-closed.

### C. Add live ProductFlow progress observation

Reuse existing `ProductFlowEvent` stages.

Add a small optional observation callback/sink at the application boundary so adapters can surface events when emitted.

It is observation-only and must not gain decision authority.

Existing callers without a sink must remain valid.

### D. Product runtime defaults / diagnostics

Ordinary Editing users must not locate a TransNet `.pth` file or supply routine provider/tool plumbing.

- preserve current configurable Engineering CLI;
- add reviewed product defaults for normal launcher composition;
- auto-resolve the reviewed installed TransNetV2 runtime/weights where supported by the existing runtime adapter;
- use normal FFmpeg/ffprobe executable discovery;
- use a reviewed visual provider/model default based on explicit configured capability, without silent failure-time provider switching;
- CPU remains a valid compatibility baseline;
- produce understandable diagnostics when mandatory capability is unavailable.

Extend Environment Doctor minimally if needed for mandatory Shot-detection/runtime readiness. Doctor remains read-only and is not an installer.

### E. Minimum Windows product shell

First verify the actual Windows development/runtime environment can import/use stdlib Tkinter.

If Tkinter is available, use it for the Stage-A shell; do not add a heavy GUI framework.

If Tkinter is genuinely unavailable in the target environment, STOP and report that concrete blocker before selecting a new GUI dependency.

Add a plain launcher, conceptually:

```text
video-editing-agent launch
```

It should have two primary modes.

#### Planning

- choose/create project directory;
- title / objective / audience / platform / core message;
- optional authoritative facts;
- optional supported URL or local reference video;
- production constraints/resources;
- start Planning;
- display live ProductFlow progress;
- load and display the **exact returned** ScriptPlan and ShootingPlan revisions;
- show understandable semantic/provider failure.

#### Editing

- choose/create project directory;
- select media files and/or a folder;
- enter editing intent/Brief fields;
- choose output MP4 path;
- optional Combined enrichment from Planning state when an exact revision can be resolved safely without requiring the user to type IDs;
- start Editing;
- display live ProductFlow progress;
- show Review/correction state;
- show/reveal final MP4 path.

Keep widget/layout logic thin. Put request construction, deterministic folder expansion, presentation serialization, runtime resolution and controller behavior below the Tk widget layer so they are testable.

No timeline editor, no NLE canvas, no rich preview/editor surface is required.

### F. Product-facing result presentation

Planning must be readable without invoking lower-level entity `show` commands manually.

Load the exact result refs and present at least:

- ScriptPlan sections in narrative order;
- spoken content / visual requirement / timing intent where present;
- ShootingPlan requirements;
- capture instructions, framing/motion, required resources and notes.

Editing must surface:

- outcome;
- Review/correction route;
- final output path on PASS;
- understandable diagnostics on failure.

Adapter-level Markdown/text export is allowed if useful, but do not create a new Domain entity merely for presentation.

## Required deterministic tests

At minimum:

1. Planning reference input requires no internal AssetRef/ShotRef;
2. supported direct URL remains reference-analysis-only and Resolver-ineligible;
3. local reference remains reference-analysis-only;
4. ReferenceStyleGuidance reaches Script workflow;
5. same guidance reaches Shooting workflow;
6. Planning without reference remains valid without visual/TransNet capability;
7. authoritative facts/references survive exact Brief commit;
8. event sink observes the same ordered ProductFlow events without changing result;
9. folder expansion is deterministic and originals are untouched;
10. normal launcher composition does not require user-supplied TransNet weight path;
11. unavailable mandatory runtime yields understandable diagnostic;
12. launcher/controller builds Planning requests without hand-written JSON;
13. launcher/controller builds Editing requests from selected files/folder/output;
14. Planning presentation loads exact returned ScriptPlan/ShootingPlan revisions;
15. Editing presentation exposes final MP4 or Review correction state;
16. Planning-only / Editing-only / Combined remain valid;
17. existing architecture contracts remain green.

Run focused tests during implementation, then the full repository Quality Gate.

## Local Windows verification

Before coding the desktop layer, verify:

```text
python/uv runtime
Tkinter import + root create/destroy
FFmpeg/ffprobe
current proxy/network only if provider calls are actually needed
```

Do not spend API money merely to validate widget plumbing.

At the end, perform a bounded launcher smoke that does not require fake Product Gate claims.

## Exit from Codex batch

Codex must:

1. inspect current local state first;
2. fast-forward to current `origin/main` only if working tree is clean;
3. implement the complete bounded surface above;
4. run focused tests + full Quality Gate;
5. commit one coherent implementation batch;
6. push to `main`;
7. report exact commit SHA, files changed, test/gate results, Windows/Tk smoke result, known limitations and `git status`;
8. STOP.

Codex must not run or declare the final real Product Probes/Human Gates. ChatGPT controls those after independent remote review.

## Product Gate after Codex returns

If implementation is accepted and exact `main` is green:

1. run a real Planning Product Probe using an actual user target/reference/commercial goal through the ordinary launcher;
2. ask the user ordinary Human Gate questions about ScriptPlan/ShootingPlan usefulness and shootability;
3. run a real Editing Product Probe using user-selected real/private footage through the ordinary launcher;
4. ask the user ordinary Human Gate questions about the final MP4 and workflow usability;
5. classify and repair only evidence-backed defects.

## Structural progress

Remain at **90%** throughout this implementation batch.

Only after both Product Gates + Human Gates + overall Stage-A gate PASS may the control plane set 100%.

## STOP boundary

Do not:

- build a feature-rich NLE/timeline editor;
- reopen Preview backend benchmarking;
- redesign persistence, Resolver, EDL or Renderer without concrete evidence;
- make Planning mandatory for Editing;
- let reference footage enter the visual Resolver/final output;
- add stock/generated replacement visuals;
- add universal/authenticated/social-platform downloaders;
- loosen semantic/commercial Review;
- expose internal IDs/timestamps as ordinary-user inputs;
- implement silent provider switching;
- add a heavy GUI framework without a proven Tkinter blocker;
- claim Product/Human Gate PASS;
- bump structural progress.

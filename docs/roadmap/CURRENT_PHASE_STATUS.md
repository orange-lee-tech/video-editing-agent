# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 90%  
**Current phase:** R0.12 — EDL / Renderer / Review / runtime productization  
**Engineering state:** STAGE_A_PRODUCT_GATE_EXECUTION_ACTIVE  
**Updated:** 2026-08-18

## Progress meaning

The structural percentage measures real end-to-end product usability, not module count, test count, workflow count, probe count or UI polish.

The hard 100% contract remains:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Current Product Gate state:

- Planning Engineering mechanism: PASS; Product Probe / Human Gate: OPEN.
- Editing Engineering mechanism: PASS; Product Probe / Human Gate: OPEN.
- Stage-A completion gate: OPEN.

Therefore structural progress remains **90%**.

## Current accepted production-code baseline

`fadefcbb2418477e794a782f5e94b6865a80297a`

Exact-head deterministic CI:

`32117815321` — PASS (`ci/quality-gate-diagnostic = success`).

## Stage-A ordinary-user product surface — PASS / ACCEPTED

Implementation closure evidence:

`docs/validation/R0.12_STAGE_A_PRODUCT_SURFACE_IMPLEMENTATION_CLOSURE.md`

The accepted ordinary-user capabilities now include:

- stdlib Tkinter `video-editing-agent launch`;
- Simplified Chinese / English switching;
- Planning authoritative facts and optional URL/local reference video;
- `REFERENCE_ANALYSIS_ONLY` reference bridge and exact guidance into both Planning owners;
- live progress observation;
- reviewed FFmpeg/ffprobe and TransNet runtime discovery/diagnostics;
- deterministic file/folder selection;
- readable exact ScriptPlan/ShootingPlan presentation;
- Editing final MP4 / correction presentation;
- Editing-only default path;
- optional same-session/same-project Combined enrichment with exact Planning revisions and no user-entered internal IDs;
- fail-closed ordinary-user path validation;
- an API Settings surface organized around `思考指挥 / Reasoning & Direction` and `视觉理解 / Visual Understanding` rather than raw environment-variable names.

Current Settings semantics:

- software does not include or gift API keys;
- the current reasoning/direction provider is DeepSeek;
- the current visual-understanding providers are Gemini and OpenAI;
- the same key string may be entered in both capability slots;
- the visual slot explicitly warns that its selected API/model must support image input;
- APIs are described as understanding/reasoning/planning/editing-decision services, not video-generation services;
- Stage-A keys are session-local and are not persisted into project state, repository files or logs.

These are product-surface capabilities, not Product/Human Gate evidence.

## Active Work Order

`R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001` remains ACTIVE, with execution mode:

`PRODUCT PROBE → HUMAN GATE`

There is **no active Codex writer**.

The remaining Stage-A work is real environment readiness and real ordinary-user evidence, not more speculative backend construction.

## Planning Product Gate target

```text
real user intent / optional supported reference / commercial facts
→ ordinary Windows launcher
→ real Planning workflow
→ persisted exact ScriptPlan + ShootingPlan
→ readable launcher presentation
→ Human Gate
```

Planning may be probed first without reference. That path requires the current reasoning/direction API but does not require visual-understanding capability.

## Editing Product Gate target

```text
user-selected real local footage
+ editing intent / output destination
→ ordinary Windows launcher
→ actual ingest / shot detection / understanding / Director
→ grounded Resolver
→ canonical EDL / Renderer / Review
→ real final MP4
→ Human Gate
```

Editing requires the actual media runtime plus both configured product capabilities required by the current provider composition.

## Runtime readiness strategy

Use the actual Windows host and repository Doctor. Repair environment/configuration with PowerShell or the product Settings surface before considering source changes.

Do not spend Codex quota on:

- FFmpeg/GStreamer/TransNet installation;
- PATH repair;
- API-secret configuration;
- launcher operation;
- ordinary deterministic checks;
- documentation/governance maintenance.

Codex may be re-released only for a concrete implementation defect after ChatGPT classifies the failure.

## Human Gate

Human Gate stays ordinary and product-centered.

Planning:

- Is the script usable for the intended video?
- Is the shooting plan realistically shootable?
- Is anything obviously wrong or missing?

Editing:

- Is the final video usable as the Stage-A automatic result?
- Are there obvious wrong shots/cuts/audio/subtitle/content problems?
- Was the source-to-output workflow understandable?

Do not ask the user to invent professional scoring criteria.

## Frozen authority rules

- Planning remains independently usable;
- Editing remains independently activatable;
- Combined uses optional exact Planning revisions;
- canonical EDL remains sole exact timeline authority;
- source-time grounding remains Resolver-owned;
- Renderer has no editorial authority;
- Review has no edit/render mutation authority;
- reference-only media remains Resolver-ineligible;
- commercial final visuals come from user-supplied local footage;
- originals remain protected;
- no silent provider switching or fabricated fallback visual assets.

## Immediate corridor

1. synchronize the accepted baseline and current control plane to the Windows workspace;
2. configure user-owned API credentials in the product Settings surface as required;
3. run real Planning Product Probe through the launcher and complete its Human Gate;
4. run real Editing Product Probe through the launcher using real local footage and complete its Human Gate;
5. classify any failure before changing code;
6. set Stage-A to 100% only if both core gates and `STAGE_A_COMPLETION_GATE.md` genuinely PASS.

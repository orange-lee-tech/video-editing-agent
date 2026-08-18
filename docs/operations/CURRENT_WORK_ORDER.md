# Current Work Order

**ID:** `R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Stage-A ordinary-user Product Gate closure  
**Mode:** PRODUCT PROBE → HUMAN GATE  
**Accepted production-code baseline:** `0134d0c4a741eb2babed7275c0aaef42045f2dc4`  
**Activated:** 2026-08-18  
**Codex release:** CLOSED — NO ACTIVE CODEX WRITER

## Objective

Close Stage-A only through real ordinary-user evidence for the two frozen core product functions. Do not add more backend construction merely to increase confidence.

## Accepted implementation result

The bounded ordinary-user product-surface implementation is **PASS / ACCEPTED**.

Closure evidence:

`docs/validation/R0.12_STAGE_A_PRODUCT_SURFACE_IMPLEMENTATION_CLOSURE.md`

Accepted implementation commits:

- `c765d4095f5337e1dc30ba2ef11308cc425d904e` — Stage-A product launcher;
- `0134d0c4a741eb2babed7275c0aaef42045f2dc4` — safe Combined/path/diagnostic repair.

Exact-head CI for the accepted baseline:

`32111192942` — `ci/quality-gate-diagnostic = success`.

The implementation provides the thin stdlib Tkinter launcher, ordinary Planning/Editing inputs, reference-only analysis bridge, exact Planning presentation, live progress observation, reviewed runtime discovery/diagnostics, Editing final-path/Review presentation, and safe same-session/same-project Combined enrichment.

No implementation defect is currently known that justifies another Codex batch.

## Frozen architecture

### Planning-only

```text
real user goal / commercial facts / optional supported reference
→ Brief
→ optional reference-only analysis / ReferenceStyleGuidance
→ ScriptPlanningWorkflow
→ ShootingPlanningWorkflow
→ persisted exact ScriptPlan + ShootingPlan
→ ordinary-user presentation
```

### Editing-only

```text
user-selected local footage + editing intent + output MP4
→ existing Editing ProductFlow
→ grounded Resolver
→ canonical EDL
→ Renderer
→ Review
→ final MP4 / explicit correction route
```

### Combined

Exact ScriptPlan/ShootingPlan revisions from a successful Planning result in the same launcher session and same project may optionally enrich the same Editing Core. Editing-only remains independently valid.

Canonical EDL remains sole exact timeline authority.

## Current execution boundary

The remaining work is **environment readiness + real Product Probe + Human Gate**, not another implementation phase.

Prefer:

- user-run PowerShell for local install/configuration and deterministic checks;
- ChatGPT for GitHub observation, evidence review and governance;
- Codex only if a concrete code defect is proven and cannot be repaired safely through a small deterministic ChatGPT/GitHub change.

Do not spend Codex quota on package installation, PATH repair, secret configuration, ordinary runtime checks, launcher operation or documentation maintenance.

## Runtime readiness gate

Before the real probes, use the repository Environment Doctor on the actual Windows target and repair only capabilities required by the selected probe path.

Current known target capabilities include:

- Windows/Python host runtime;
- FFmpeg + ffprobe for reference-video analysis and Editing;
- reviewed TransNetV2 runtime/package-owned weights for reference-video analysis and Editing;
- DeepSeek credential for Planning / Director;
- one explicitly configured supported visual-understanding provider for reference-video analysis and Editing;
- approved private GStreamer Preview runtime only where Preview evidence is actually required.

Do not place secret values in GitHub, logs, screenshots or chat transcripts.

## Planning Product Gate

Run through the ordinary `video-editing-agent launch` Planning surface with a real user target.

Required evidence:

1. user chooses/creates a real project directory;
2. real title/objective/audience/platform/core message are supplied;
3. use real authoritative facts where relevant;
4. optional reference may be omitted for the first probe, or may use a supported direct HTTPS/local reference when runtime capability is ready;
5. Planning reaches a persisted exact ScriptPlan and ShootingPlan;
6. the launcher presents the exact returned revisions readably;
7. the user judges whether the script is useful and whether the shooting plan is realistically shootable.

Human Gate questions should remain ordinary:

- Is this script usable for the intended video?
- Is the shooting plan realistically shootable with your available resources?
- Is anything obviously wrong, missing or misleading?

Do not require the user to invent a professional scoring rubric.

Planning Product Gate may PASS only after both execution evidence and Human Gate are positive.

## Editing Product Gate

Run through the ordinary `video-editing-agent launch` Editing surface using user-selected real/private local footage.

Required evidence:

1. select real local source media or a real source folder;
2. supply real editing intent/Brief fields and an MP4 output destination;
3. Editing-only remains valid; Combined may optionally be tested after Planning using the same project/session;
4. actual ingest / shot detection / understanding / Director / grounded Resolver / canonical EDL / Renderer / Review chain runs;
5. a real final MP4 is produced only on Review PASS;
6. original user media remains untouched;
7. the user watches the final MP4 and judges usefulness and obvious defects.

Human Gate questions should remain ordinary:

- Is the final video usable as an automatic first cut/final Stage-A result?
- Are there obvious wrong shots, bad cuts, audio/subtitle problems or missing content?
- Did the workflow behave understandably from source selection to final MP4?

Editing Product Gate may PASS only after both execution evidence and Human Gate are positive.

## Failure classification

If a real probe fails, classify before changing code:

1. **environment/configuration** — repair locally with PowerShell/configuration;
2. **provider/network/input condition** — retry only with evidence and without weakening policy;
3. **product-surface usability defect** — small deterministic repair if clear;
4. **implementation/architecture defect** — only then consider a bounded Codex release;
5. **Human Gate quality failure** — preserve evidence and repair the actual quality cause rather than gaming the gate.

No failure authorizes silent provider switching, synthetic replacement visuals, fabricated timestamps, Review weakening or Resolver/EDL authority changes.

## Required invariants

- Planning-only remains independently usable;
- Editing-only remains independently activatable;
- Combined remains optional enrichment only;
- reference media stays `REFERENCE_ANALYSIS_ONLY` and Resolver-ineligible;
- commercial final visuals come from user-supplied local footage;
- source-time grounding remains Resolver-owned;
- canonical EDL remains sole exact timeline authority;
- Renderer executes only;
- Review classifies/routes only;
- originals remain protected;
- no ordinary-user internal IDs/timestamps are required;
- no stock/generated visual substitution;
- no silent provider switching.

## Structural progress

Remain at **90%** while either core Product/Human Gate is OPEN.

Set 100% only when:

1. Planning Product Gate + Human Gate = PASS;
2. Editing Product Gate + Human Gate = PASS with a real final MP4;
3. Planning-only / Editing-only / Combined invariants remain intact;
4. ordinary Windows usability is demonstrated;
5. accepted `main` is green;
6. exact environment/provider/machine limitations are recorded;
7. `docs/roadmap/STAGE_A_COMPLETION_GATE.md` is fully satisfied.

## STOP gate

Do not:

- reopen the accepted implementation batch without a concrete defect;
- spend Codex quota on environment or documentation work;
- build a feature-rich NLE/timeline editor;
- redesign persistence, Resolver, EDL, Renderer or Preview without evidence;
- make Planning mandatory for Editing;
- let reference footage enter Resolver/final output;
- add stock/generated replacement visuals;
- loosen semantic/commercial Review;
- expose internal IDs/timestamps as ordinary-user inputs;
- claim Product/Human Gate PASS from deterministic tests or CI alone;
- bump structural progress before both real gates pass.

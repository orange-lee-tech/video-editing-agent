# Current Work Order

**ID:** `R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Stage-A ordinary-user Product Gate closure  
**Mode:** PRODUCT PROBE → HUMAN GATE  
**Accepted production-code baseline:** `b6572602c0f7faaa22383dab9fffa361fb946e75`  
**Activated:** 2026-08-18  
**Codex release:** CLOSED — NO ACTIVE CODEX WRITER

## Objective

Close Stage A only through real ordinary-user evidence for the two frozen core product functions. Do not add more backend construction or product polish merely to increase confidence.

## Gate state

### Planning Product Gate

**PASS**.

Durable evidence:

`docs/validation/R0.12_STAGE_A_PLANNING_PRODUCT_GATE.md`

The real ordinary Windows launcher produced inspectable ScriptPlan and ShootingPlan revisions and the user explicitly judged both acceptable with no blocking issue in the accepted result.

Known follow-up UX/robustness work is preserved in:

`docs/roadmap/PRODUCT_UX_BACKLOG.md`.

Those items do not reopen Planning PASS.

### Editing Product Gate

**ENGINEERING PASS / PRODUCT PROBE OPEN / HUMAN GATE OPEN**.

This is now the active execution boundary.

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

The remaining gate work is the **real Editing Product Probe + Editing Human Gate**.

Prefer:

- user-run PowerShell for local Windows setup, source hashing and deterministic checks;
- ChatGPT for GitHub observation, evidence review and governance;
- Codex only if a concrete nontrivial implementation defect is proven and cannot be repaired safely through a small deterministic ChatGPT/GitHub change.

Do not spend Codex quota on package installation, PATH repair, secret configuration, ordinary launcher operation, documentation maintenance or cosmetic UX backlog items.

## Editing Product Gate

Run through the ordinary `video-editing-agent launch` Editing surface using user-selected real/private local footage.

Required evidence:

1. select real local source media or a real source folder;
2. record non-empty source hashes before the run;
3. supply real editing intent/Brief fields and an MP4 output destination;
4. use **Editing-only** for the first gate probe; do not require Planning artifacts;
5. actual ingest / shot detection / understanding / Director / grounded Resolver / canonical EDL / Renderer / Review chain runs;
6. a real final MP4 is produced only on Review PASS;
7. source hashes after the run match the before-run hashes;
8. the user watches the final MP4 and judges usefulness and obvious defects.

Human Gate questions remain ordinary:

- Is the final video usable as an automatic Stage-A result?
- Are there obvious wrong shots, bad cuts, audio/subtitle problems or missing content?
- Did the workflow behave understandably from source selection to final MP4?

Editing Product Gate may PASS only after both execution evidence and Human Gate are positive.

## Known product backlog that must not distract from this gate

`docs/roadmap/PRODUCT_UX_BACKLOG.md` contains ordinary-user requests for:

- output scrollbar/TXT export;
- UI-aligned localization;
- profile persistence and protected credential storage;
- placeholder guidance;
- bounded reference share-link handling;
- no-facts safe creative repair;
- opt-in public-material guidance / similar-example research;
- startup splash/progress polish.

Only repair one now if it directly blocks the Editing Product Probe.

## Failure classification

If the real Editing probe fails, classify before changing code:

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
- commercial final visuals come from user-selected local footage;
- source-time grounding remains Resolver-owned;
- canonical EDL remains sole exact timeline authority;
- Renderer executes only;
- Review classifies/routes only;
- originals remain protected;
- no ordinary-user internal IDs/timestamps are required;
- no silent stock/generated visual substitution;
- no silent provider switching.

## Structural progress

Remain at **90%** until Editing also PASSes.

Set 100% only when:

1. Planning Product/Human Gate = PASS;
2. Editing Product/Human Gate = PASS with a real final MP4;
3. Planning-only / Editing-only / Combined invariants remain intact;
4. ordinary Windows usability is demonstrated;
5. accepted `main` is green;
6. exact environment/provider/machine limitations are recorded;
7. `docs/roadmap/STAGE_A_COMPLETION_GATE.md` is fully satisfied.

# Current Work Order

**ID:** `R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Stage-A ordinary-user Product Gate closure  
**Mode:** PRODUCT PROBE → HUMAN GATE  
**Accepted production-code baseline:** `af5865df14b9f1cceaa9e6c1fe4dadf14cc60058`  
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

**ENGINEERING PASS / PRODUCT PROBE IN PROGRESS / HUMAN GATE OPEN**.

Real Editing-only probes have already crossed local input validation and media understanding far enough to expose two evidence-backed runtime defects: a malformed DeepSeek Director exact-duration proposal and a Gemini 429 retry-delay handling defect. Both now have bounded fail-closed repairs on the accepted baseline.

This remains the active execution boundary.

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

## Accepted Director robustness repair

An earlier real Editing-only probe reached `editing_decision` and failed with:

`DeepSeekPlanningResponseError: invalid minimum_duration`.

Accepted repair through `c61c7e5abc8b7b388e0e92ad9ae533d094a27707`:

- supplies a complete valid Director JSON example to DeepSeek;
- explicitly states exact duration `value` / `scale` and positivity/order constraints;
- preserves strict local `MediaTime` and EditSlot validation;
- never coerces invalid provider values into a valid-looking plan;
- allows exactly one bounded repair proposal after a locally invalid first proposal, carrying the specific local validation error back as repair feedback;
- still fails closed when the second proposal is invalid;
- provides precise diagnostics for malformed/non-integer/non-positive exact-time values;
- has regression coverage for one invalid-then-valid sequence and a two-invalid bounded failure.

## Accepted provider-aware visual retry repair

After synchronizing the Director repair and launching a fresh Windows process, the real Editing-only probe reached local-media `ingest_understanding` and received a genuine Gemini HTTP 429 response reporting:

`generate_content_free_tier_requests, limit: 20, model: gemini-3.6-flash; Please retry in 10.577272831s`.

The provider condition itself is legitimate, but audit found a runtime defect: the existing retry decorator waited only 0.3 seconds and then 0.6 seconds, ignoring the provider's explicit recovery delay and exhausting the three bounded attempts before the indicated window could recover.

Accepted repair through `af5865df14b9f1cceaa9e6c1fe4dadf14cc60058`:

- `VisualProviderTransientError` can carry an optional validated `retry_after_seconds` hint;
- the Gemini transport extracts Google `RetryInfo.retryDelay` and retains a bounded message fallback for `retry in <seconds>s`;
- the visual retry decorator waits for the greater of its local bounded backoff and the provider-required delay;
- total attempts remain capped at three;
- there is no silent provider/model switch, quota bypass or fake semantic output;
- persistent provider quota exhaustion still fails closed with the real error;
- regression coverage proves structured RetryInfo propagation, fallback parsing and provider-directed waiting.

Exact accepted head `af5865df14b9f1cceaa9e6c1fe4dadf14cc60058` is green in CI run `32145822611` (`ci/quality-gate-diagnostic = success`).

## Current execution boundary

The remaining gate work is the **real Editing Product Probe + Editing Human Gate**.

Prefer:

- user-run PowerShell for local Windows synchronization, source hashing and deterministic checks;
- ChatGPT for GitHub observation, evidence review and governance;
- Codex only if a concrete nontrivial implementation defect is proven and cannot be repaired safely through a small deterministic ChatGPT/GitHub change.

Do not spend Codex quota on package installation, PATH repair, secret configuration, ordinary launcher operation, documentation maintenance, bounded provider retry/proposal repairs or cosmetic UX backlog items.

## Editing Product Gate rerun

Run through the ordinary `video-editing-agent launch` Editing surface using user-selected real/private local footage.

Required evidence:

1. select real local source media through one unambiguous source-selection method — explicit files **or** a source folder, not both for the gate-closing run;
2. record non-empty SHA-256 source hashes before the run;
3. supply real editing intent/Brief fields and an MP4 output destination;
4. use **Editing-only** for this gate probe; keep Planning enrichment unchecked;
5. allow the application to honor short provider-directed retry waits instead of manually restarting while a recoverable 429 window is active;
6. actual ingest / shot detection / understanding / Director / grounded Resolver / canonical EDL / Renderer / Review chain runs;
7. a real final MP4 is produced only on Review PASS;
8. source hashes after the run match the before-run hashes;
9. the user watches the final MP4 and judges usefulness and obvious defects.

A persistent account/provider quota exhaustion after bounded retries is a provider condition and must fail explicitly; it does not authorize silent switching or fabricated output.

Human Gate questions remain ordinary:

- Is the final video usable as an automatic Stage-A result?
- Are there obvious wrong shots, bad cuts, audio/subtitle problems or missing content?
- Did the workflow behave understandably from source selection to final MP4?

Editing Product Gate may PASS only after both execution evidence and Human Gate are positive.

## Known product backlog that must not distract from this gate

`docs/roadmap/PRODUCT_UX_BACKLOG.md` contains ordinary-user requests for:

- output scrollbar/TXT export;
- real-data estimated completion time to the minute, recalculated at least every 30 seconds;
- UI-aligned localization;
- profile persistence and protected credential storage;
- placeholder guidance;
- bounded reference share-link handling;
- no-facts safe creative repair;
- opt-in public-material guidance / similar-example research;
- startup splash/progress polish.

Provider-directed waits should eventually be surfaced in the same progress/ETA experience so an ordinary user can see that the application is deliberately waiting to retry rather than frozen.

Only repair a backlog item now if it directly blocks the Editing Product Probe.

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

# Current Work Order

**Status:** ACTIVE  
**Phase:** R0.11 — Spatial Composition / Auto Reframe foundation  
**Updated:** 2026-08-14

## Entry state

R0.10 is closed. Its final closure evidence is stored in:

`docs/validation/R0.10_FINAL_CLOSURE.md`

Current implementation baseline before R0.11 code work:

`4782889f3746cf1024abfa0c45f3402cfec834a3` — `fix: canonicalize music candidate ordering`

The control-plane closure/activation commits that follow are documentation/governance only.

## Read before coding

1. `docs/operations/CODEX_EXECUTION_ENTRY.md`
2. `docs/roadmap/CURRENT_PHASE_STATUS.md`
3. this work order
4. `docs/capabilities/CAP-07_SPATIAL_COMPOSITION_AUTO_REFRAME.md`
5. `docs/adr/ADR-007_SPATIAL_COMPOSER_AUTO_REFRAME.md`
6. only the R0.8 tracking/TemporalEvidence and R0.9 ResolvedSelection/EditSlot code actually needed for this boundary
7. relevant architecture types needed to preserve the v0.2 ownership model

Do not broadly reread unrelated phases.

## Goal

Establish the first real R0.11 spatial authority and deterministic geometry foundation without prematurely choosing a new detector/tracker vendor.

The intended ownership chain is:

```text
EditSlot / CommercialSkill spatial intent
+
existing grounded spatial/temporal evidence
→ SpatialComposer
→ ReframeDecision / SpatialTransformPlan
→ later EDLBuilder
→ later Renderer execution
```

Renderer is not allowed to become a cinematographer.

## Coherent implementation boundary

1. **Audit before adding types.** Locate and reuse the existing R0.8 tracking/TemporalEvidence and R0.9 resolved-selection references. Do not build a second spatial-understanding stack.
2. Add the smallest provider-neutral application contracts needed for `ReframeIntent`, spatial evidence input/view, crop/path primitives and `ReframeDecision`/`SpatialTransformPlan`. Keep them application artifacts/value contracts; do not create a new top-level Domain Entity without an architecture decision.
3. Represent source frame geometry and target canvas/aspect ratio exactly enough that legality can be validated deterministically.
4. Implement deterministic crop-candidate generation for an initial CPU/local baseline. At minimum support a static/hold result centered or biased by grounded focus evidence while respecting target aspect ratio and source bounds.
5. Add deterministic validation proving every executable crop remains inside source geometry and satisfies the target aspect ratio within exact/rational or explicitly bounded numeric semantics.
6. Define impossible-fit behavior explicitly. If mandatory focus constraints cannot be satisfied inside the source frame, return fallback/unresolved/warnings rather than fabricating pixels or silently violating constraints.
7. Preserve Shot boundaries. No smoothing/path state may cross a hard source Shot cut.
8. Keep provider/model output observational. If a focus proposal seam is needed, it may identify/score focus targets but cannot directly become executable crop coordinates without deterministic validation/ownership.
9. If manual locks/keyframes already have an obvious architecture seam, represent their precedence contract; do not build UI in this batch.
10. Add focused engineering regressions for deterministic repeatability, source-bound legality, target-aspect legality, hard-cut reset, and impossible-fit refusal/fallback.
11. Add one bounded Engineering Probe using deterministic/synthetic geometry and existing evidence fixtures if appropriate. Synthetic evidence is valid for mechanism proof here; it is not R0.11 Product Probe evidence.
12. Keep the full repository Quality Gate green.

## Explicitly not in this batch

- no new YOLO/MediaPipe/SAM2 or other detector/tracker dependency merely to make the demo look smarter;
- no transitive model/runtime license commitment without the existing dependency-license gate;
- no full smooth tracking optimizer yet unless the foundation naturally reaches it without widening scope;
- no generative outpainting/uncrop;
- no Auto Reframe Product Probe claim from synthetic fixtures;
- no Renderer hidden crop logic;
- no R0.12 preview/proxy/cache implementation;
- no subtitle/graphics UI work.

## Stop conditions

Stop and report rather than invent semantics if:

- existing R0.8 tracking evidence cannot represent the spatial information required and a new authority would be necessary;
- a proposed dependency introduces unresolved code/model/runtime licensing constraints;
- current source geometry/time mapping is insufficient to preserve authoritative source time;
- an architecture conflict would require changing Product Constitution or Architecture Contract v0.2.

Otherwise complete the whole coherent boundary autonomously.

## Required report

After one coherent green batch, report:

- starting/ending HEAD;
- files/types introduced or reused;
- exact SpatialComposer ownership boundary;
- geometry/candidate semantics;
- focused Engineering Probe results;
- full Quality Gate result;
- any unresolved evidence/provider need for the next R0.11 batch.

Do not mark R0.11 closed and do not begin R0.12.

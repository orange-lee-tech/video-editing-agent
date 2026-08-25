# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 95%  
**Current phase:** R0.12 — Stage-A Human Gate repair + Windows release delivery  
**Engineering state:** STAGE_A_HUMAN_GATE_REPAIR_ACTIVE  
**Updated:** 2026-08-25

## Progress truth

Structural percentage measures real ordinary-user end-to-end usability, not module/test/UI count.

Hard 100% contract:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

The latest real Product/Human Gate on main `1015096fc4c5b2b9138e98cbe713fc4cc1770c07` supersedes earlier optimistic gate labels.

Current gates:

- Planning Product/Human Gate: **REOPENED** — bounded model repair still introduced unsupported fit/operability claims and the semantic reviewer correctly vetoed them.
- Editing Product/Human Gate: **REOPENED** — bounded Resolver -> Director recovery executed, but the revised EditPlan still requested multiple beats not grounded in the supplied real local footage.
- Editing no-speech historical Human baseline: remains PASS unless a later regression disproves it.
- local reference video: supported.
- remote reference URL: deliberately deferred to 2.0; not a 1.0 blocker.
- Project Workspace / desktop UX foundation: ACCEPTED / PR #17.
- Windows packaging/runtime foundation: ACCEPTED / PR #19 + PR #20.
- Windows ordinary release delivery: **OPEN** — final user delivery must be guided `Setup.exe`, not raw large ZIP extraction.
- clear-speech original voice + trusted subtitles: still OPEN because Editing has not yet reached the downstream speech/subtitle/render path in the current real-footage Human Gate.
- Stage-A completion gate: OPEN.

Therefore progress remains **95%**, not 100%.

## Current implementation truth

Accepted runtime/packaging engineering foundation:

`c2c959239cf8842388ac661777c19f20f64a6a90` (PR #20)

Current main and latest Human Gate candidate:

`1015096fc4c5b2b9138e98cbe713fc4cc1770c07` (PR #21)

PR #21 proved one important mechanism: when the first Resolver pass cannot ground an EditPlan, the product now performs one bounded Director replan on the same authoritative lineage and re-resolves. It no longer exposes a raw `slot_6` failure immediately. The real Human Gate showed that the mechanism runs, but also showed that Director grounding/recovery quality is still insufficient.

The current onedir artifact size (~769 MB compressed / ~1.88 GB extracted) is no longer treated as the intended normal distribution shape. It is engineering staging/evidence only.

## Active repair method

Human Gate repair now uses an evidence-first / patch-first loop:

```text
real failure
→ collect small Workspace/log evidence
→ inspect exact persisted Brief / shot analysis / EditPlan revisions
→ focused patch
→ targeted tests + normal CI
→ local developer run for the same scenario
→ repeat if needed
→ explicit release-candidate build only after repair stability
→ Setup.exe Human Gate
```

Do not use a full Windows artifact as the transport for every small repair.

## What remains before effective 100%

### A. Planning factual recovery

Preserve commercial-fact safety while making ordinary creative positioning usable. A second unsupported-claim veto must not lead to endless model retries; recovery must conservatively remove unsupported semantic properties and pass an independent re-review before commit.

### B. Editing grounding recovery

Inspect the persisted Workspace evidence from the failed real run before changing Director/Resolver behavior. The goal is not to force a render: adapt optional/adaptable editorial beats to what real local footage actually contains, while keeping genuinely essential missing coverage fail-closed and never substituting public/generated visuals.

### C. Clear-speech retained path

Once Editing reaches a grounded EDL, confirm final MP4, preserved original speech, trusted subtitle content/timing and acceptable BGM balance.

### D. Combined semantics

Confirm Planning enrichment remains optional and Combined works through the ordinary UI.

### E. Windows release delivery

Produce and Human-test a guided `Setup.exe` install/upgrade-or-repair/uninstall path. The installer should use established tooling rather than bespoke installer mechanics and should support application-owned componentized runtime delivery.

### F. Closure evidence

Record exact final release SHA/artifact identities, installer/runtime component identities and concise Human PASS/FAIL observations.

If all gates pass, Stage-A may move directly from 95% to 100%. Do not create artificial percentage increments for each repair.

## Active Work Order

`R0.12-STAGE-A-FINAL-CLOSURE-002`

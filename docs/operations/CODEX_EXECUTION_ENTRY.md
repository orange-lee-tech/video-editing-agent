# Codex Execution Entry

Purpose: expose whether Codex currently has an authorized construction release.

## Release state

**Work Order:** `R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001`  
**Release:** CLOSED — NO ACTIVE CODEX WRITER  
**Writer:** NONE

The Stage-A ordinary-user product-surface implementation is accepted at:

`0134d0c4a741eb2babed7275c0aaef42045f2dc4`

Closure evidence:

`docs/validation/R0.12_STAGE_A_PRODUCT_SURFACE_IMPLEMENTATION_CLOSURE.md`

Current Work Order execution mode:

`PRODUCT PROBE → HUMAN GATE`

## Current policy

Do not start Codex merely because the Work Order remains ACTIVE.

The remaining Stage-A work is expected to be handled primarily by:

- user-run PowerShell for local runtime installation/configuration/checks;
- ChatGPT for GitHub observation, evidence review and governance;
- the ordinary `video-editing-agent launch` product surface for real Product Probes;
- the user for Human Gate judgments.

Codex quota must not be spent on:

- FFmpeg/GStreamer/TransNet installation;
- PATH repair;
- API-key/secret configuration;
- running Environment Doctor;
- launcher operation;
- routine test execution;
- documentation/governance edits.

## Re-release trigger

Codex may be re-released only after a real probe or deterministic check produces a concrete code defect that:

1. is not an environment/configuration/provider/input problem;
2. is not safely repairable as a small deterministic ChatGPT/GitHub change;
3. requires local multi-file implementation/test iteration.

Any new release must be bounded to that evidence-backed defect. Do not replay or reopen the accepted product-surface batch.

## Frozen boundaries

Do not use a future Codex release to:

- redesign Planning/Editing architecture;
- make Planning mandatory for Editing;
- weaken Resolver grounding, canonical EDL or Review policy;
- let reference-only media enter final visual output;
- add stock/generated replacement visuals;
- add a timeline/NLE editor merely for Stage-A closure;
- expose internal entity IDs or source timestamps as ordinary-user inputs;
- silently switch providers after failure;
- claim Product/Human Gate PASS from tests alone.

## Recovery rule

If a concrete defect eventually warrants Codex, first reobserve current `main`, CI and local working-tree state. Preserve unknown local changes. Generate a fresh foreman brief only after the control plane explicitly grants a new release.

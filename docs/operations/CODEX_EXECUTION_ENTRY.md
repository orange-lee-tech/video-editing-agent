# Codex Execution Entry

**Last updated:** 2026-09-18  
**Purpose:** expose whether any Codex/local construction work is currently authorized.

## Current release/control state

**Active Work Order:** `NONE`  
**Construction branch:** `NONE`  
**Development stage:** `RELEASED`  
**Stable release:** `v1.0.0`  
**Stable product source:** `fc6391b846432586a41311a295251e8860cdf9fa`  
**Current main baseline:** `b201c685fa74b83e3559e16b50f63aea58eddd83`  
**Foreman:** ChatGPT  
**Authority:** `docs/operations/CURRENT_WORK_ORDER.md`

There is currently **no standing Codex construction assignment**.

Stage A is complete, R0.13 is closed, and stable `v1.0.0` has been released. Planning and Automatic Editing remain accepted product gates.

Current activity is post-release security/signing governance review, not product construction.

## Open review tracks

### PR #36 — governance / SignPath preparation

`governance: adopt Apache-2.0 for 有岐`

State: **Ready for human review / not merged**.

This PR is being reviewed by Liu Lei. No Codex work is required for the current documentation/licensing/signing-policy review. Small deterministic documentation/governance corrections should be handled directly through bounded GitHub edits.

### PR #35 — update trust-chain hardening

`security: harden component update trust chain`

State: **Draft / not merge-ready**.

This branch contains security hardening but still requires the final public code-signing route. The currently intended route is SignPath Foundation, subject to approval and later trusted-build integration.

Codex may become appropriate only if the SignPath integration requires non-trivial multi-file workflow/build iteration that cannot be safely handled as a bounded deterministic GitHub change.

## Codex activation rule

Do **not** infer authorization from this file, old chat history, an old branch name, or an old failed Human Gate.

Before any Codex/local construction run:

1. read `CURRENT_CONTROL_STATE.md`;
2. read `CURRENT_PHASE_STATUS.md`;
3. read `CURRENT_WORK_ORDER.md`;
4. verify that an explicit active work order exists;
5. verify the exact target branch and accepted baseline;
6. constrain the task to that authorized boundary.

If `CURRENT_WORK_ORDER.md` says `ID: NONE`, Codex must not start product implementation.

## When Codex is appropriate

Use Codex only when it materially reduces risk for work such as:

- complex local Windows/runtime iteration;
- multi-file build/signing integration with meaningful execution feedback;
- difficult reproducibility/debugging work that requires local shell/tooling;
- other explicitly authorized construction where direct bounded GitHub edits are not sufficient.

Do not spend Codex budget on:

- clerical documentation synchronization;
- one-file deterministic metadata edits;
- simple PR/reviewer/status maintenance;
- changes that are not covered by an active work order.

## Current protected invariants

Until a new work order explicitly changes them:

- do not reopen Planning or Automatic Editing without a demonstrated regression;
- do not modify stable `v1.0.0` release bytes;
- do not weaken update/signature/signer/rollback evidence;
- do not treat a provisional signing adapter as accepted production signing;
- do not start unrelated 2.0 product capability work.

## Next likely handoff point

The next plausible Codex handoff is **after SignPath Foundation approval**, if integrating its trusted-build GitHub signing flow into PR #35 proves complex enough to justify local/multi-file execution.

Until then, direct GitHub governance/review work remains preferred.

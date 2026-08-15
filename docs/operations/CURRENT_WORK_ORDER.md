# Current Work Order

**ID:** `R0.12-EDITPLAN-COMPAT-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — parallel workflow compatibility correction  
**Owner/writer:** ChatGPT architecture/control + User PowerShell execution  
**Codex release:** NO unless escalation trigger occurs

## Why this work exists

`ADR-009_TWO_CORE_WORKFLOWS_PARALLEL_ENTRY.md` formally establishes that Planning Workflow and Editing Workflow are parallel primary-capability entries and Combined Workflow is their composition. Current `EditPlan` still requires both `script_plan_ref` and `shooting_plan_ref`, which incorrectly makes Planning artifacts an activation prerequisite for Editing-only use.

Repository audit shows the coupling is localized. Resolver, CandidateWindow generation and EDLBuilder do not use Planning references as edit authority. There is currently no persisted EditPlan table/codec that requires a database migration.

## Goal

Evolve `EditPlan` compatibly so it can represent explicit Brief-rooted Editing intent without requiring ScriptPlan/ShootingPlan, while preserving exact Planning provenance in Combined mode and retaining legacy combined construction semantics where needed.

## Allowed production scope

Primary production file:

- `src/video_editing_agent/domain/edit/model.py`

Focused tests may be added/updated under `tests/unit/`. Existing R0.9/R0.12 probes/tests may be adjusted only when necessary to preserve compatibility or prove invariance.

Do not add an EditPlan persistence/database layer in this work order.

## Required target semantics

Preserve the existing first four constructor positions for compatibility:

```text
EditPlan(
    envelope,
    script_plan_ref,
    shooting_plan_ref,
    slots,
    brief_ref=...
)
```

Target field semantics:

```text
envelope
script_plan_ref: EntityRevisionRef | None
shooting_plan_ref: EntityRevisionRef | None
slots: tuple[EditSlot, ...]
brief_ref: EntityRevisionRef | None = None
```

The optional type does not mean intent-free Editing is legal. Required validity matrix:

```text
brief only                         PASS  # Editing-only
brief + script                     PASS  # Planning-enriched context
brief + script + shooting          PASS  # Combined
legacy: script + shooting          PASS  # backward-compatible combined shape
nothing                            FAIL
shooting without script            FAIL
script only without brief          FAIL
```

Existing slot identity/order validation remains unchanged.

No code in this work order may infer/fabricate a Brief revision from missing data or rewrite historical provenance.

## Downstream authority invariance

For otherwise identical `EditPlan.slots`, changing only Planning context/provenance must not change downstream authority.

Focused regression evidence must show at least:

1. Resolver behavior is identical for an Editing-only plan and a Combined plan when slots/candidates/plan identity are otherwise identical.
2. EDLBuilder canonical timeline behavior remains independent of ScriptPlan/ShootingPlan refs for otherwise identical edit decisions.

This work does not make Planning context meaningless; a future Director may legitimately use optional Planning context when creating EditSlots. The invariant here is that downstream owners must not secretly treat the presence of Planning refs as execution authority.

## Explicit non-goals / stop conditions

Do not materially redesign or duplicate:

- Resolver / optimizer;
- CandidateWindow generation;
- Retrieval ownership;
- EDLBuilder;
- Canonical EDL or exact rational `MediaTime`;
- Renderer / FFmpeg execution;
- Media Understanding;
- subtitle, spatial, music or audio semantics;
- ApplicationRuntime/workspace Editing orchestration.

If this migration appears to require such changes, STOP and return to architecture audit.

The real Application Editing entry point is a separate downstream work order after this one closes.

## Verification matrix

Focused checks must cover:

- valid Editing-only shape;
- valid Combined shape with exact Planning refs retained;
- valid legacy combined shape;
- invalid intent-free shape;
- invalid shooting-without-script shape;
- invalid script-only-without-Brief shape;
- existing duplicate/unordered slot validation;
- Resolver provenance invariance;
- EDLBuilder provenance invariance.

Then run repository gates:

```text
uv run ruff check .
uv run mypy src
uv run pytest
uv run lint-imports
uv build
git diff --check
```

Run the existing R0.12 living integration smoke if its normal invocation is available in the repository/tooling. No new real-media Product Probe is required for this narrow Domain compatibility migration.

## Execution policy

First attempt is ChatGPT-authored patch applied by User PowerShell. No administrator shell is required.

Escalate to Codex only if actual evidence shows unexpected multi-file/type/import/test complexity requiring iterative local debugging.

## Exit gate

PASS only when:

- Editing-only no longer needs fabricated ScriptPlan/ShootingPlan;
- Combined Planning provenance remains representable exactly;
- legacy combined construction remains intentionally compatible;
- invalid broken provenance fails closed;
- downstream Resolver/EDL authority remains unchanged;
- full repository quality gates pass;
- working tree is clean after the user commits/pushes the accepted patch.

# ADR-009 — Two Core Workflows, Parallel Entry, One Editing Kernel

**Status:** ACCEPTED  
**Date:** 2026-08-15  
**Decision owner:** Product Owner + ChatGPT architecture control  
**Detailed audit basis:** `docs/architecture/TWO_CORE_WORKFLOWS_PARALLELISM_AND_RISK_GOVERNANCE.md`

## Context

The Product Constitution defines exactly two primary capabilities: pre-production creation and post-production editing. Architecture Contract v0.2 Section 1 shows a valid full-lifecycle chain from `Brief` through `ScriptPlan` / `ShootingPlan` into Editing, but that diagram must not be interpreted as the only legal product entry path.

Current `EditPlan` code still requires exact `script_plan_ref` and `shooting_plan_ref`, which makes Planning artifacts behave as activation prerequisites for Editing. The code-level audit shows this coupling is upstream and localized: Resolver, CandidateWindow generation, EDLBuilder, Canonical EDL and Renderer do not require Planning references for their authority.

## Decision

The product has three legitimate workflow meanings:

```text
Planning Workflow
Brief -> ScriptPlan -> ShootingPlan

Editing Workflow
Brief/editorial intent + user local footage
-> Understanding -> Director/EditPlan -> Retrieval/Resolver
-> Spatial/Audio/Music -> EDLBuilder -> Canonical EDL -> Renderer -> Review

Combined Workflow
Planning Workflow outputs
-> optional high-value context
-> the same Editing Workflow / same Editing Core
```

The Architecture Contract v0.2 Section 1 chain is therefore interpreted as **Combined Workflow**, not as the unique legal entry path.

`Brief` is the shared intent root. Planning may enrich Editing, but Planning is not an activation license for Editing.

## Durable invariants

1. New Editing-only execution must retain explicit Brief/editorial-intent provenance; it may not run as intent-free "upload and guess" behavior.
2. `ScriptPlan` and `ShootingPlan` are optional high-value Editing context, not mandatory prerequisites.
3. Combined mode preserves exact Planning revision provenance when such artifacts exist.
4. Editing-only must not fabricate ScriptPlan/ShootingPlan merely to satisfy a schema.
5. Combined mode must reuse the same Editing Core. Do not duplicate Resolver, EDLBuilder, Canonical EDL, Renderer or downstream editorial authority.
6. Grounded evidence, provider neutrality, exact rational `MediaTime`, Resolver/EDLBuilder authority separation, Canonical EDL timeline authority, provenance, locks and fail-closed behavior remain unchanged.
7. Backend limitations must not rewrite Domain truth. If a backend cannot faithfully execute Canonical EDL semantics, execution fails closed.
8. Long-chain resilience uses single authority, propagated uncertainty, explicit fallback/unresolved states, living integration spines and affected-only recompute. Redundancy belongs in evidence/provider/verification layers, not duplicated Domain authority.

## Compatibility migration

The immediate implementation migration is intentionally narrow:

- evolve `EditPlan` so Editing-only can carry Brief provenance without ScriptPlan/ShootingPlan;
- preserve exact Planning provenance for Combined mode;
- preserve legacy in-memory/test/probe construction semantics where needed for compatibility;
- do not invent a persistence/database migration for EditPlan unless real persisted EditPlan data/schema exists;
- do not materially modify Resolver, CandidateWindow, EDLBuilder, Canonical EDL, Renderer or Media Understanding as part of this migration.

If implementation appears to require broad downstream redesign, stop and re-audit before continuing.

## Application consequence

A later bounded Application step will expose independent Planning and Editing entry points. Combined user journeys compose those entry points and pass Planning artifacts as optional Editing context. That step must not be faked with an empty wrapper or a second editing engine.

## Verification consequence

Final product closure requires real Planning-only, Editing-only and Combined workflow probes. Editing-only must use actual Understanding/evidence and the real Editing Core; hand-authored `ResolutionDecision`, EDL or fabricated Planning artifacts cannot substitute for automatic stages being claimed.

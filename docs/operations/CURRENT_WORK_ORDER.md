# Current Work Order

**ID:** `R0.12-EDITING-DIRECTOR-ENTRY-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — real Editing Application entry / Director foundation  
**Owner/writer:** ChatGPT architecture/control + Codex implementation + User PowerShell/live verification  
**Codex release:** YES — one bounded multi-file implementation session

## Why this work exists

`ADR-009_TWO_CORE_WORKFLOWS_PARALLEL_ENTRY.md` establishes Planning Workflow and Editing Workflow as parallel primary entries. `R0.12-EDITPLAN-COMPAT-001` removed the Domain-level requirement to fabricate ScriptPlan/ShootingPlan for Editing-only mode.

The remaining structural gap is now concrete:

- `ApplicationRuntime` exposes preproduction/media only;
- `ProjectWorkspace.runtime()` requires preproduction provider ports and has no independent Editing composition root;
- `editing/director/` contains retrieval/candidate-window helpers but no production Director service/workflow that creates `EditPlan` from Brief + persisted media evidence;
- R0.9 Product Probe manually constructed EditSlots/EditPlan before entering retrieval/resolution;
- no EditPlan repository/codec/table exists because no production producer previously justified one.

Architecture Contract v0.2 treats EditPlan as a top-level durable Domain Entity and requires durable stages to support pause/revision/resume semantics. Once production Director creates EditPlan, persistence is therefore justified rather than speculative.

## Goal

Create the smallest real production Editing entry that can take an exact persisted Brief plus already-ingested/analyzed eligible user footage, optionally enrich it with exact ScriptPlan/ShootingPlan context, obtain provider-neutral Director slot proposals, commit a revisioned persisted EditPlan, and prove that its generated slots enter the existing Retrieval/Resolver path without a second editing engine.

This is an Application/Director foundation, not the final R0.16 one-click workflow.

## Required architecture

### 1. Provider-neutral Director seam

Add a provider-neutral Application port for Director proposal generation. The provider returns proposal DTOs only; it must not construct Domain entities or receive final source-selection authority.

Minimum request context:

- exact `Brief`;
- current eligible editable local visual footage evidence derived from persisted Shot/ShotAnalysis records;
- optional exact `ScriptPlan`;
- optional exact `ShootingPlan`;
- optional bounded instruction/policy context where already supported by current architecture.

Minimum proposal shape maps only to currently implemented EditSlot intent fields:

- slot identity/order;
- narrative role/purpose;
- semantic query / desired-content intent;
- target duration bounds where available;
- pacing;
- continuity hint;
- reuse policy;
- importance.

Do **not** expand this work order into the full future EditSlot vocabulary merely because CAP-04 lists music/spatial/lock/protected-fact concepts.

Provider output must not contain committed Shot IDs, Asset IDs, source timestamps, CandidateWindows, ResolutionDecisions or EDL coordinates. Unknown/extra authority-bearing fields must fail closed.

### 2. Director owner/workflow

Add a production Director service/workflow that:

1. loads the exact Brief revision;
2. validates optional Planning lineage:
   - ScriptPlan, if present, must reference the exact Brief;
   - ShootingPlan, if present, requires ScriptPlan and must reference that exact ScriptPlan;
3. gathers current latest ShotAnalysis evidence only for Resolver-eligible local visual Assets;
4. fails closed when there is no eligible analyzed visual footage;
5. calls the Director proposal port;
6. converts validated proposal DTOs into ordered unique `EditSlot` values;
7. creates a new `EditPlan` with exact Brief/optional Planning provenance;
8. persists the new EditPlan revision before returning it.

Do not infer/fabricate Planning artifacts for Editing-only mode.

### 3. EditPlan persistence is now required

Introduce the first official EditPlan persistence surface now that a production producer exists.

Expected shape:

- SQLite schema version advances from v5 to v6;
- new immutable `edit_plans` table;
- exact entity revision identity;
- exact Brief foreign-key lineage when Brief provenance exists;
- optional exact ScriptPlan/ShootingPlan lineage with nullable FK pairs;
- payload codec and repository protocol/implementation;
- row identity/payload integrity checks;
- immutable revision conflict behavior consistent with existing repositories.

There are no historical persisted EditPlan rows to rewrite. Migration v5 -> v6 creates the new table and records the schema migration only. Do not invent legacy EditPlan data.

Legacy in-memory ScriptPlan+ShootingPlan EditPlan construction remains a Domain compatibility shape; new production Director output must always carry exact `brief_ref`.

### 4. Independent Editing composition root

Editing-only execution must not require dummy preproduction providers.

Prefer an additive independent Editing application surface/composition method (for example `EditingOperations` / `EditingApplicationRuntime` and `ProjectWorkspace.editing_runtime(...)`) rather than making callers provide fake Script/Shooting planning ports.

Preserve existing `ApplicationRuntime`, `ProjectWorkspace.runtime()` and current CLI planning behavior unless a small backward-compatible extension is clearly safer. Do not mass-rename `preproduction` in this work order.

### 5. Concrete DeepSeek Director adapter

Reuse the existing replaceable DeepSeek transport/config infrastructure where practical, but keep Director as a separate port/adapter responsibility.

The concrete adapter must:

- use structured JSON output;
- treat project content as untrusted data;
- preserve authoritative Brief facts/constraints;
- never invent source timestamps or commit footage selections;
- parse only the bounded proposal schema;
- fail closed on malformed/extra authority-bearing output;
- remain replaceable behind the provider-neutral Director port.

Do not make DeepSeek a Domain type or hard-wire Director semantics to one provider.

### 6. Engineering CLI entry

Add a bounded engineering adapter for generating/showing persisted EditPlans from an existing project workspace.

The command may require that footage has already been ingested, shot-detected and analyzed. It does **not** need to become the final ordinary-user one-click UI.

Editing-only generation must require only Brief + analyzed eligible footage + Director provider configuration. Optional ScriptPlan/ShootingPlan references may enrich Combined mode but may not be mandatory.

## Living integration requirement

Add deterministic offline integration evidence that does **not** hand-author an EditPlan:

`persisted Brief + persisted eligible Shot/ShotAnalysis evidence`
`→ Director proposal port`
`→ production Director workflow`
`→ persisted EditPlan`
`→ existing retrieval / CandidateWindow / Resolver path`

The generated EditPlan slots must feed the existing Editing Core. Do not duplicate or fork Resolver/optimizer logic.

A concrete DeepSeek live Engineering Probe should also be provided/updated when normal provider credentials are available. Offline CI must not depend on external API availability.

The existing R0.12 living Resolver → EDLBuilder → Renderer smoke remains a regression gate; this work order does not claim a new full Brief→MP4 Product Probe.

## Explicit non-goals / STOP conditions

Do not materially redesign or duplicate:

- Resolver / deterministic optimizer;
- CandidateWindow ownership;
- lexical/dense retrieval algorithms;
- Canonical EDL / EDLBuilder;
- Renderer / FFmpeg execution;
- subtitle semantics;
- SpatialComposer;
- music/audio editorial semantics;
- VisualUnderstanding provider ownership;
- Preview, Proxy/cache, Graphics/transitions, Review, packaging or GUI.

If implementation appears to require broad changes in those systems, STOP and report the unexpected dependency instead of expanding scope.

Do not reopen R0.9. R0.9 correctly closed the grounded retrieval/resolution kernel; this work order replaces the previously hand-authored upstream EditPlan with a production Application/Director producer.

## Compatibility requirements

- Existing positional legacy EditPlan construction continues to work.
- Existing `ApplicationRuntime` planning/media callers must remain source-compatible unless a strictly necessary change is documented and migrated.
- Existing SQLite v0-v5 projects must initialize/migrate deterministically to v6 without data loss.
- New production EditPlans always carry exact Brief provenance.
- Editing-only never requires ScriptPlan/ShootingPlan.
- Combined mode preserves exact Planning provenance.
- Reference-analysis-only and restricted visual Assets must not become Director/Resolver-eligible footage.

## Required tests

At minimum cover:

1. Director request exact-lineage validation.
2. Editing-only Brief + eligible analyses -> persisted EditPlan.
3. Combined Brief + exact Script/Shooting refs -> persisted EditPlan with exact provenance.
4. Shooting-without-Script and mismatched lineage fail closed.
5. No eligible analyzed footage fails closed.
6. Reference-analysis-only/restricted visual assets are excluded.
7. Provider proposal cannot inject source IDs/timestamps/unknown authority fields.
8. EditPlan v6 codec round-trip.
9. SQLite v5 -> v6 migration preserves existing records and creates empty EditPlan storage.
10. Immutable EditPlan revision conflict behavior.
11. Existing workspace planning/media behavior remains compatible.
12. Generated EditPlan slots enter the existing Retrieval/CandidateWindow/Resolver path.
13. Existing R0.9/R0.12 regression tests remain green.

## Full quality gate

Local acceptance must mirror CI:

```text
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest
uv run lint-imports
uv build
git diff --check
```

Then run the relevant Director/Editing-entry engineering probe(s) and the existing R0.12 living integration smoke when available.

## Execution routing

### ChatGPT / GitHub

- architecture and blast-radius audit — completed before activation;
- this bounded Work Order/control-state maintenance;
- independent commit/CI/code review after Codex reports completion;
- final acceptance/closure decision.

### Codex — RELEASED

One coherent implementation/test/debug session is justified because the required change crosses Domain persistence, Application ports/workflow, workspace composition, provider adapter, CLI and migration/integration tests.

Codex must work strictly inside this Work Order and stop on any listed STOP condition.

### User PowerShell

After Codex produces a candidate commit, User PowerShell is preferred for local Windows/provider/runtime probes and any simple deterministic verification that is not already covered by Codex.

## Exit gate

PASS only when:

- an Editing-only project can create a **provider-produced, validated, persisted** EditPlan from exact Brief + eligible persisted media understanding without ScriptPlan/ShootingPlan;
- Combined mode can provide optional exact Planning context without using it as an activation license;
- generated EditPlan slots demonstrably enter the existing Retrieval/Resolver kernel;
- new persistence is deterministic and migration-safe;
- existing planning/media/downstream editing authority remains intact;
- DeepSeek is only an adapter behind a neutral port;
- full quality gates pass locally and remote CI is green;
- ChatGPT independently re-observes and accepts the resulting GitHub baseline.

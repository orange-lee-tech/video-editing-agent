# Current Work Order

**ID:** `CONTROL-PLANE-002`  
**Status:** ACTIVE  
**Phase:** R0.12 — trigger-first Codex control plane  
**Owner/writer:** Codex

## Objective

Upgrade foreman v1 from a concise **summary generator** into a **progressive-disclosure router**. Reduce unnecessary model-visible context, not merely prompt length.

## Read

1. `tools/maintenance/foreman.py`
2. `docs/operations/CONTROL_PLANE_ARCHITECTURE.md`
3. `docs/operations/CODEX_EXECUTION_ENTRY.md`
4. `scripts/maintain.ps1`

## Required delta

- Default `.private/codex_brief.md` is L0 only: task/phase, one-sentence objective, actual Git state, immediate action, hard blocker/stop conditions, and trigger routes.
- Do **not** dump full allowed scope, full read set, full stop gate, or explanatory documents into L0 unless required for safe execution.
- Control state and work order may be machine-parsed without being model-read in full.
- Add deterministic trigger routes so Codex opens secondary information only when the condition occurs.
- Add a compact `CODEX_TOOLBOX.md` (or cleaner equivalent) indexing existing work tools and blocked/recovery strategies. It is a toolbox, not a default reading assignment.
- Prefer route references over copied content. A trigger should point to the smallest relevant file/section/command.
- Keep foreman deterministic and non-authoritative: no architecture invention, source edits, state rewrites, commit/push, or fake remote-CI claims.

## Minimum trigger classes

Cover at least: architecture/contract ambiguity, code-location uncertainty, test/quality failure, Git/repository-state issue, external/license/provider uncertainty, and destructive/high-risk operation.

## Verification

Prove with focused tests that:

- L0 omits secondary detail that is not immediately needed;
- a trigger exposes the correct route without preloading its target content;
- unrelated routes stay hidden;
- malformed/mismatched state still fails closed;
- dirty Git state remains prominent;
- full Quality Gate is green.

## Stop gate

Stop after foreman v2 + toolbox routing are green, committed/pushed, and the working tree is clean. Do not start R0.12 product features.

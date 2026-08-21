# Repository Agent Guide

**Last updated:** 2026-08-21

This file is the default entry contract for ChatGPT, Codex, and other repository-aware engineering agents.

## 1. Attention budget

Start from the smallest authoritative surface that can answer the current task. Do not recursively browse the repository by default.

Read in this order when relevant:

1. `docs/DOCUMENT_REGISTRY.json` — compact repository/document map and attention classes.
2. `docs/README.md` — documentation authority/navigation.
3. `docs/operations/CURRENT_CONTROL_STATE.md` — machine-readable live state.
4. `docs/roadmap/CURRENT_PHASE_STATUS.md` — human-readable live state.
5. `docs/operations/CURRENT_WORK_ORDER.md` — currently authorized construction boundary.
6. Only the relevant Product Constitution / Architecture Contract / CAP / ADR for the task.
7. Only then inspect implementation and tests inside the active boundary.

## 2. Default excluded surfaces

Do **not** read or recursively inspect these unless a concrete current task requires them:

- `docs/archive/**` — retired provenance only; never current authority.
- `.private/**`
- `.tools/**`
- `.uv-cache*/**`
- `.venv/**`
- `build/**`
- `dist/**`
- generated caches, probe outputs, downloaded models, and local runtime bundles.

`docs/archive/**` may be opened only for explicit historical/provenance, backward-compatibility, or legal investigation after active authority has been checked first.

## 3. Working-tree safety

- Preserve accepted dirty work.
- Never use blind `reset`, `clean`, `checkout`, or `stash` to make the tree look clean.
- Observe before changing.
- Do not reconstruct accepted local work from an older remote baseline.
- Do not commit or push unless the current work order/user instruction authorizes it.

## 4. Bounded self-repair

Within the active construction boundary, use:

`observe → change → verify → detect blocker → repair → re-verify`

Repair defects that materially block or weaken the current core product path, packaging proof, launcher/runtime usability, data safety, or required quality gates.

Do not expand self-repair into unrelated repository-wide cleanup or speculative refactoring. Record non-blocking side issues for later.

## 5. Compatible development

Prefer additive, replaceable, backward-compatible change over destructive replacement.

Protect these principles:

- Product/Domain authority must not depend on one vendor/provider/runtime.
- Ports/contracts remain stable seams; adapters/providers remain replaceable.
- Canonical artifacts own exact product decisions/timing where defined.
- User originals are immutable; generated/analyzed/separated media are derived assets.
- New capabilities should plug in through capability/configuration resolution rather than scattered hard-coded branches.
- Packaging/bootstrap/resource location must stay outside Domain authority.
- Writable user data must stay outside the install directory.
- When schemas/contracts evolve, preserve or explicitly migrate older persisted projects.

## 6. Flexible production-line rule

A stage should make its capability, inputs, outputs, diagnostics, provenance, fallback policy, and failure behavior explicit.

Use bounded adaptation:

- capability present → execute;
- capability absent + approved degradation exists → degrade explicitly;
- capability absent + degradation would fabricate/violate product truth → fail closed.

`SKIPPED`, `NO_SPEECH`, `CAPABILITY_UNAVAILABLE`, and real failure are different states. Do not collapse them.

Do not invent a generic workflow framework merely to satisfy this principle. Establish the smallest correct seam needed by current work.

## 7. Documentation lifecycle

Follow `docs/operations/DOCUMENT_CONTROL_POLICY.md`.

When active truth changes, refresh the canonical live files instead of creating duplicate scratch authorities. Every managed document must expose an update date either in-file or through the registry; active authority/control documents edited in a change must update their declared date.

Retired material goes to `docs/archive/<category>/` only when superseded and still useful for provenance. Validation evidence, incident/probe history, and research remain in their canonical directories instead of being archived merely because a phase ended.

## 8. Verification

Use the narrowest relevant checks during iteration, then the repository-required full gate before acceptance. GUI changes require launcher smoke. Product/Human Gate evidence cannot be replaced by unit tests, synthetic probes, or a successful package build.

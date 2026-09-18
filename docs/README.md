# Documentation Map

**Last updated:** 2026-09-18

This directory is the repository's documentation control plane. Do not infer current authority from file age, filename, or an old phase label alone.

## Start here

For ChatGPT/Codex/repository-aware agents, read root `../AGENTS.md` first. Then use `DOCUMENT_REGISTRY.json` to choose the smallest relevant documentation surface.

For a new engineering conversation or audit:

1. `DOCUMENT_REGISTRY.json` — compact relative-path map, attention classes and excluded-default surfaces;
2. `product/PRODUCT_CONSTITUTION_V1.0.md` — highest product authority;
3. `architecture/ARCHITECTURE_CONTRACT_V0.2.md` — active architecture baseline;
4. relevant `capabilities/CAP-*.md` and `adr/ADR-*.md` only when the current task touches them;
5. `operations/CURRENT_CONTROL_STATE.md` — machine-readable live control state;
6. `roadmap/CURRENT_PHASE_STATUS.md` — human-readable live phase/review state;
7. `operations/CURRENT_WORK_ORDER.md` — exact authorization boundary; it may explicitly say that no construction work order is active;
8. the one explicitly active operation/review document only when the live trio points to it;
9. `roadmap/STAGE_A_COMPLETION_GATE.md` when evaluating the already-achieved structural 100% contract;
10. implementation/tests only after the current boundary is understood.

`operations/CHATGPT_GITHUB_CODEX_COLLABORATION.md` and `operations/CODEX_EXECUTION_ENTRY.md` are read only when a ChatGPT/Codex handoff is actually relevant. The Codex entry must never be used to resurrect a closed construction wave.

## Current repository state

Stage A structural construction is **complete at 100%** and stable `v1.0.0` is published.

There is currently **no active product-construction work order**. Current activity is bounded post-release security/signing governance review:

- PR #35 — update trust-chain hardening; Draft / not merge-ready;
- PR #36 — Apache-2.0 and SignPath governance; Ready for human review / not merged.

The current intended public Windows signing route is SignPath Foundation, subject to Foundation approval and later trusted-build integration. Existing `v1.0.0` predates that signing route and must not be represented as SignPath-signed.

Always re-read the live trio for exact current SHA/state before acting.

## Default attention exclusion

`archive/` is retired provenance and **must not be read during ordinary current work**. Open it only for explicit historical/provenance, backward-compatibility or legal investigation after current authority has been checked.

The same attention-saving principle applies to local/runtime surfaces such as `.private/`, `.tools/`, `.uv-cache*`, `.venv/`, `build/` and `dist/`; see root `AGENTS.md`.

## Directory roles

- `product/` — constitutional product policy plus subordinate product-design guidance.
- `architecture/` — active Architecture Contract plus non-normative implementation/migration plans.
- `capabilities/` — capability specifications.
- `adr/` — current architecture decisions.
- `roadmap/` — durable roadmap, Stage-A completion contract, live phase state and non-authoritative backlog/history surfaces.
- `operations/` — dynamic execution/control, release/packaging maintenance and handoff references.
- `validation/` — durable Product/Engineering/Human Gate closure evidence.
- `logs/` — non-authoritative incidents, probes, collaboration records, chronicles and maintenance lessons.
- `research/` — survey/research evidence explaining why choices were made; not normative by itself.
- `upstream/` — active dependency/reference ledger and reuse/license policy.
- `archive/` — retired documents preserved only for provenance; `EXCLUDED_DEFAULT`.

## Live state vs history

Use this canonical live trio for **now**:

- `operations/CURRENT_CONTROL_STATE.md`
- `roadmap/CURRENT_PHASE_STATUS.md`
- `operations/CURRENT_WORK_ORDER.md`

The three files must stay synchronized. `tools/maintenance/repo_doctor.py` plus repository governance enforce machine-checkable invariants.

Use these for **why / what was proven**:

- `validation/`
- `logs/`
- `research/`

Use `archive/` only when historical provenance is genuinely needed.

## Document lifecycle and dates

`operations/DOCUMENT_CONTROL_POLICY.md` defines update-date, attention/lifecycle, placement/archive and registry rules.

The compact registry is tracked at `DOCUMENT_REGISTRY.json`. GitHub generates an exhaustive tracked-document manifest through `tools/maintenance/document_registry.py` / `.github/workflows/document-registry.yml`, so humans and agents do not need to recursively traverse the repository for routine navigation.

## Product/release references

Durable helpers do not become a second authority stack:

- `logs/PROJECT_CHRONICLE.md` — daily-indexed engineering chronicle;
- `roadmap/PRODUCT_RED_BLACK_BOARD.md` — historical diagnostic dashboard; not current blocker authority;
- `roadmap/PRODUCT_UX_BACKLOG.md` — non-authoritative post-release/future UX backlog;
- `product/DESKTOP_UI_DESIGN_SYSTEM_V0.1.md` — Windows desktop design guidance;
- `architecture/PROVIDER_NEUTRAL_PRODUCT_BINDING_PLAN.md` — provider-neutral binding migration plan;
- `operations/STAGE_A_WORKSPACE_UX_CONSOLIDATION.md` — released/closed Project Workspace + desktop UX implementation record;
- `operations/WINDOWS_DESKTOP_PACKAGING_READINESS.md` — released Windows packaging baseline and maintenance reference;
- `operations/WINDOWS_RUNTIME_DEPENDENCY_INVENTORY.md` — runtime/component packaging inventory;
- root `../CODE_SIGNING_POLICY.md` — public production-signing governance policy proposed by PR #36.

## Current controlled sequence

The live trio currently authorizes review/release-governance work only:

`PR #36 human review → protected merge if approved → real Windows VERSIONINFO package proof → SignPath Foundation application → SignPath integration into PR #35 → signed RC/migration verification → PR #35 human security review`

This is **not** a new product-construction phase. Planning and Automatic Editing remain accepted product gates.

Codex has no standing construction assignment. Use `operations/CODEX_EXECUTION_ENTRY.md` only if the live control state later authorizes a bounded Codex/local task.

## Stage-A 100% gate

`roadmap/STAGE_A_COMPLETION_GATE.md` remains the durable structural-completion contract.

Stage A reached 100% only after both real product outcomes and the ordinary Windows/deployment floor were proven. The gate remains useful as historical/structural evidence; it is no longer an open blocker list.

## Governance rule

Do not create another ad-hoc authority pack or phase-specific scratch document when an existing canonical location can carry the information. Prefer updating the correct live-state document, README, ledger, validation record or archive index.

Stable entry documents should route readers to canonical live state rather than duplicate rapidly changing phase snapshots.

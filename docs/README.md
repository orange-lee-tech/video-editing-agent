# Documentation Map

**Last updated:** 2026-08-22

This directory is the repository's documentation control plane. Do not infer current authority from file age or filename alone.

## Start here

For ChatGPT/Codex/repository-aware agents, read root `../AGENTS.md` first. Then use `DOCUMENT_REGISTRY.json` to choose the smallest relevant documentation surface.

For a new engineering conversation or audit:

1. `DOCUMENT_REGISTRY.json` — compact relative-path map, attention classes and excluded-default surfaces;
2. `product/PRODUCT_CONSTITUTION_V1.0.md` — highest product authority;
3. `architecture/ARCHITECTURE_CONTRACT_V0.2.md` — active architecture baseline;
4. relevant `capabilities/CAP-*.md` and `adr/ADR-*.md` only when the current task touches them;
5. `operations/CURRENT_CONTROL_STATE.md` — machine-readable live control state;
6. `roadmap/CURRENT_PHASE_STATUS.md` — human-readable live phase state;
7. `operations/CURRENT_WORK_ORDER.md` — exact live implementation/evidence boundary;
8. the one explicitly active wave specification when the Work Order points to it;
9. `roadmap/STAGE_A_COMPLETION_GATE.md` when evaluating progress or structural 100%;
10. implementation/tests only after the active boundary is understood.

`operations/CHATGPT_GITHUB_CODEX_COLLABORATION.md` and `operations/CODEX_EXECUTION_ENTRY.md` are read only when a ChatGPT/Codex handoff is actually relevant.

## Default attention exclusion

`archive/` is retired provenance and **must not be read during ordinary current work**. Open it only for explicit historical/provenance, backward-compatibility or legal investigation after current authority has been checked.

The same attention-saving principle applies to local/runtime surfaces such as `.private/`, `.tools/`, `.uv-cache*`, `.venv/`, `build/` and `dist/`; see root `AGENTS.md`.

## Directory roles

- `product/` — constitutional product policy plus subordinate product-design guidance.
- `architecture/` — active Architecture Contract plus non-normative implementation/migration plans.
- `capabilities/` — active capability specifications.
- `adr/` — current architecture decisions.
- `roadmap/` — Roadmap, Stage-A completion gate, live phase state and non-authoritative UX backlog.
- `operations/` — dynamic ChatGPT/GitHub/Codex/PowerShell execution control and operational release/packaging readiness.
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

## Product evolution references

Durable helpers do not become a second authority stack:

- `logs/PROJECT_CHRONICLE.md` — daily-indexed engineering chronicle;
- `roadmap/PRODUCT_RED_BLACK_BOARD.md` — live red/black dashboard;
- `roadmap/PRODUCT_UX_BACKLOG.md` — non-authoritative current/future UX backlog;
- `product/DESKTOP_UI_DESIGN_SYSTEM_V0.1.md` — Windows desktop design guidance;
- `architecture/PROVIDER_NEUTRAL_PRODUCT_BINDING_PLAN.md` — provider-neutral binding migration plan;
- `operations/STAGE_A_WORKSPACE_UX_CONSOLIDATION.md` — **active released** Project Workspace + desktop UX wave;
- `operations/WINDOWS_DESKTOP_PACKAGING_READINESS.md` — prepared next packaging/release-readiness plan;
- `operations/WINDOWS_RUNTIME_DEPENDENCY_INVENTORY.md` — runtime/component packaging inventory.

## Current Stage-A sequencing

Current Work Order sequencing is:

`Workspace/UX consolidation [ACTIVE] → Windows packaging [NOT RELEASED] → final retained Product/Human Gate`

Remote reference URL product support is deferred to 2.0. The ordinary Stage-A GUI keeps the unfinished URL field hidden and retains local reference video.

Current local construction branch:

`work/r012-workspace-ux-consolidation`

Codex release details:

`operations/CODEX_EXECUTION_ENTRY.md`

## Stage-A 100% gate

`roadmap/STAGE_A_COMPLETION_GATE.md` is the stable structural completion contract.

Structural progress may reach 100 only after both real product outcomes are proven and the ordinary Windows/deployment floor is satisfied. A green backend, synthetic probe, CLI-only path, hand-authored internal artifact or polished GUI cannot substitute for those outcomes.

## Governance rule

Do not create another ad-hoc authority pack or phase-specific scratch document when an existing canonical location can carry the information. Prefer updating the correct live-state document, README, ledger, validation record or archive index.

Stable entry documents should route readers to canonical live state rather than duplicate rapidly changing phase snapshots.

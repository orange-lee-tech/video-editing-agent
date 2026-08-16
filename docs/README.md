# Documentation Map

This directory is the repository's documentation control plane. Do not infer current authority from file age or filename alone.

## Read first

For a new engineering conversation or audit:

1. `product/PRODUCT_CONSTITUTION_V1.0.md` — highest product authority;
2. `architecture/ARCHITECTURE_CONTRACT_V0.2.md` — active architecture baseline;
3. relevant `capabilities/CAP-*.md` and `adr/ADR-*.md`;
4. `operations/CURRENT_CONTROL_STATE.md` — machine-readable live control state, accepted baseline, active Work Order pointer and Stage-A product gates;
5. `roadmap/CURRENT_PHASE_STATUS.md` — human-readable live phase state;
6. `operations/CURRENT_WORK_ORDER.md` — exact live implementation/evidence boundary;
7. `roadmap/STAGE_A_COMPLETION_GATE.md` when evaluating progress or any claim of structural 100%;
8. `operations/CHATGPT_GITHUB_CODEX_COLLABORATION.md` / `CODEX_EXECUTION_ENTRY.md` only when a ChatGPT/Codex handoff or Codex execution is actually relevant;
9. implementation/tests after the above boundary is understood.

A0 acceptance is recorded in `roadmap/A0_PLANNING_BASELINE_ACCEPTANCE.md`.

## Directory roles

- `product/` — constitutional product policy. Rarely changed; explicit user approval required for constitutional revision.
- `architecture/` — active Architecture Contract v0.2.
- `capabilities/` — active capability specifications CAP-01…CAP-10.
- `adr/` — **current ADR home**.
- `roadmap/` — Roadmap V2, Stage-A completion gate, live phase state and planning acceptance records.
- `operations/` — dynamic ChatGPT/GitHub/Codex/PowerShell execution control and live Work Order state. Operational, not product authority.
- `validation/` — durable phase/probe closure evidence.
- `logs/` — non-authoritative incident, probe, collaboration and repository-maintenance lessons worth retaining.
- `research/` — Survey/research evidence explaining why choices were made; not normative by itself.
- `upstream/` — active dependency/reference ledger and reuse/license policy.
- `archive/` — retired documents preserved only for provenance; never an active entry point.

## Live state vs history

Use this canonical live trio for **now**:

- `operations/CURRENT_CONTROL_STATE.md`
- `roadmap/CURRENT_PHASE_STATUS.md`
- `operations/CURRENT_WORK_ORDER.md`

The three files must stay synchronized. `tools/maintenance/repo_doctor.py` plus the `repository-governance` workflow enforce the machine-checkable invariants.

Use these for **why / what was proven**:

- `validation/`
- `logs/`
- `research/`

Use `archive/` only when historical provenance is genuinely needed.

## Stage-A 100% gate

`roadmap/STAGE_A_COMPLETION_GATE.md` is the stable structural completion contract.

Structural progress may reach 100 only after both real product outcomes are proven:

- Planning: ordinary user intent/reference/commercial input → persisted inspectable ScriptPlan + usable ShootingPlan.
- Editing: ordinary user-selected local footage → actual automatic pipeline → real final MP4.

A green backend, synthetic probe, CLI-only path, hand-authored internal artifact or polished GUI cannot substitute for those outcomes.

## Governance rule

Do not create another ad-hoc authority pack or phase-specific scratch document when an existing canonical location can carry the information. Prefer updating the correct live-state document, README, ledger, validation record or archive index.

Stable entry documents should route readers to canonical live state rather than duplicate rapidly changing phase snapshots.
# Documentation Map

This directory is the repository's documentation control plane. Do not infer current authority from file age or filename alone.

## Read first

For a new engineering conversation or audit:

1. `product/PRODUCT_CONSTITUTION_V1.0.md` — highest product authority;
2. `architecture/ARCHITECTURE_CONTRACT_V0.2.md` — active architecture baseline;
3. relevant `capabilities/CAP-*.md` and `adr/ADR-*.md`;
4. `roadmap/CURRENT_PHASE_STATUS.md` — live phase state;
5. `operations/CURRENT_WORK_ORDER.md` — live implementation boundary, if any;
6. implementation/tests only after the above boundary is understood.

A0 acceptance is recorded in `roadmap/A0_PLANNING_BASELINE_ACCEPTANCE.md`.

## Directory roles

- `product/` — constitutional product policy. Rarely changed; explicit user approval required for constitutional revision.
- `architecture/` — active architecture contract plus historical v0.1.x baselines.
- `capabilities/` — active capability specifications CAP-01…CAP-10.
- `adr/` — **current ADR home**.
- `decisions/` — legacy ADR archive only; do not add new decisions there.
- `roadmap/` — active Roadmap V2, live phase state and major planning acceptance/audit records.
- `operations/` — dynamic ChatGPT/Codex execution entry and current work order. Operational, not product authority.
- `validation/` — durable phase/probe closure evidence.
- `logs/` — non-authoritative incident/probe memory that is expensive to rediscover.
- `research/` — Survey/research evidence explaining why choices were made; not normative by itself.
- `upstream/` — dependency/reference ledger and reuse/license policy.

## Live state vs history

Use these for **now**:

- `roadmap/CURRENT_PHASE_STATUS.md`
- `operations/CURRENT_WORK_ORDER.md`

Use these for **why / what was proven**:

- `validation/`
- `logs/`
- `research/`

Historical documents are intentionally retained for provenance. A historical file is not garbage merely because it is no longer authoritative.

## Governance rule

Do not create another ad-hoc authority pack or phase-specific scratch document when an existing canonical location can carry the information. Prefer updating the correct README, live-state document, ledger or validation record.

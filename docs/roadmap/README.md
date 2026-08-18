# Roadmap

## Active map

`ROADMAP_V2.md` is the active construction map. It was explicitly activated/frozen by `A0_PLANNING_BASELINE_ACCEPTANCE.md` on 2026-08-11.

The original `CANDIDATE ROADMAP` wording at the top of the drafted file is a pre-A0 drafting label. A0 supersedes that label for activation status.

Do not infer the current phase from dated prose in this README. Use the live-state files below.

## Development stage

The project is currently in **Stage A — Structural Construction**. `DEVELOPMENT_STAGE_MODEL.md` defines the meaning of the 0–100% construction scale.

`STAGE_A_COMPLETION_GATE.md` is the hard 100% contract.

Stage-A 100% does **not** mean commercial polish is perfect. It does mean both core product functions are genuinely usable through the real product path by an ordinary Windows user:

1. Planning: real intent/reference/commercial input → persisted inspectable ScriptPlan + usable ShootingPlan.
2. Editing: selected local footage → actual automatic pipeline → real final MP4.

Synthetic probes, CLI-only operation, hand-authored EditPlan/EDL, or a polished GUI cannot substitute for those outcomes.

## Live state

Canonical current state is the synchronized trio:

- `../operations/CURRENT_CONTROL_STATE.md` — machine-readable control state, structural progress and Product Gates;
- `CURRENT_PHASE_STATUS.md` — current phase and remaining terrain;
- `../operations/CURRENT_WORK_ORDER.md` — exact authorized execution boundary.

`tools/maintenance/repo_doctor.py` and the `repository-governance` workflow enforce machine-checkable consistency among those pointers.

Do not duplicate current phase/commit/progress snapshots in this README; that creates stale parallel truth.

## Product red/black dashboard

`PRODUCT_RED_BLACK_BOARD.md` is a continuously maintained **non-authoritative dashboard**:

- 红榜 only records strengths/capabilities backed by implementation + CI/Probe/Human evidence;
- 黑榜 records unresolved product problems, major attack goals and commercial/reliability risks;
- issues move only with evidence, and the board cannot override the live-state trio or Stage-A gate.

Use it for a fast product-health scan, not as a substitute for the Roadmap or Work Order.

## Durable downstream integration constraints

The following are **structural integration requirements**, not optional Stage-B polish:

1. Final one-click Editing execution must use actual VisualUnderstanding-derived evidence to drive Retrieval/Resolver. Human-entered or human-confirmed coverage text may be advisory, but it may not replace automatic material understanding in the claimed automatic chain.
2. The one-click input contract must be explicit. If visual-only user input promises automatic BGM, the full workflow must contain at least one concrete rights-aware music discovery/acquisition path; a Port-only seam is insufficient for that product claim.
3. Stage A must provide a bounded minimum editing-expression floor for ordinary short-form output without creating a monolithic Effects Engine: deterministic cuts plus a minimal transition vocabulary, existing spatial automation, structured subtitle emphasis, basic deterministic title/CTA/price-card graphics, and basic audio fade/duck execution.
4. The final Reference/B爆款 → Script Product Probe should reuse downstream evidence available by then — including speech/temporal, music/rhythm and subtitle/transition/execution evidence — to demonstrate that post-production understanding improves Script/ShootingPlan guidance rather than remaining a one-way pipeline.
5. Planning-only, Editing-only and Combined remain parallel legitimate product meanings; Combined must not become the only usable path.
6. Ordinary-user product operation must not require repository-file editing or manual Domain/EDL construction.

These constraints belong to Roadmap V2 / the Stage-A completion gate. Do not create a parallel roadmap or a second governance system.

## Historical planning records

- `A0_PLANNING_BASELINE_ACCEPTANCE.md` — planning-set activation/freeze decision; still canonical because it defines authority.
- `../archive/roadmap/R0.7A_MIGRATION_AUDIT.md` — completed migration planning/audit provenance.
- `../logs/PROJECT_CHRONICLE.md` — simplified-Chinese narrative history; useful for why/how, not current authority.

Do not create a new roadmap merely because completed phases have advanced. Revise/replace Roadmap V2 only when the planned construction sequence, capability decomposition or exit criteria materially change.

# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE

**Current phase:** R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer

**Active boundary:** R0.9 READY_FOR_HUMAN_ACCEPTANCE

**Date:** 2026-08-13

## Closed

- R0.7A — Architecture v0.2 Migration Foundation.
- R0.7B — Pre-production Planning + Commercial Skill Foundation.
- R0.8 — Media Evidence Foundation.

## Accepted R0.9 engineering baselines

- R0.9A `ef6efa1f047201c96caeb2c56d7c895af00549a1` — grounded EditSlot → hybrid retrieval → CandidateWindow.
- R0.9B `fb2584d2c707fab3885179ad6f28e713362f2d68` — canonical edit contracts + grounded Resolver + deterministic sequence optimizer.

R0.9B converged duplicate EditPlan/EditSlot/CandidateWindow ownership onto the existing Domain contracts, introduced rational DurationConstraint semantics, preserved R0.9A regression behavior, and passed its Resolver/optimizer probe and repository Quality Gate.

## Ready for human acceptance — R0.9 phase closure

No new R0.9 feature module is planned before the Product Probe.

The real-footage comparison has passed its technical acceptance gates:

`lexical-only` vs `hybrid retrieval` vs `hybrid + grounded Resolver`.

The probe exposes candidate recall, trim/source windows, final sequence decisions and three
human-inspectable previews under the local gitignored
`example/probe-output/r0_9_product/` directory. Technical gates passed; sequence/cut
preference remains a Human Gate and has not been self-approved by Codex.

R0.9 is now `READY_FOR_HUMAN_ACCEPTANCE`. After human acceptance, close R0.9 and activate
R0.10 without adding another engineering subphase.

Do not begin R0.10 implementation before R0.9 closure.

## Operational control

Codex reads `CODEX_EXECUTION_ENTRY.md`, this file, then `CURRENT_WORK_ORDER.md`.

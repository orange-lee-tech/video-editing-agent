# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.8 — Media Evidence Foundation  
**Active boundary:** R0.8H — Real-Footage Product Probe + Phase Closure  
**Date:** 2026-08-13

## Completed engineering baselines

- R0.7A — Architecture v0.2 Migration Foundation: CLOSED.
- R0.7B — Pre-production Planning + Commercial Skill Foundation: CLOSED.
- R0.8 Speech: CPU ASR, timestamps, VAD/silence, transcript persistence, phrase/time mapping.
- R0.8 Visual temporal evidence: camera/global motion, compensated residual motion, event regions, coarse/fine anchors, seeded tracking.
- R0.8 Retrieval representation: multilingual local embedding prototype, explicit provenance, rebuildable dense Artifacts, selective refresh/invalidation and deterministic project-local exact vector scan.

R0.8G accepted implementation baseline:

`ae67be32c3f8726399fecfc20173a7effa06ef34` — `fix: harden dense retrieval provenance`

Post-review authority defects are closed: ShotAnalysis revision is separate from representation-source revision; speech transcript provenance no longer corrupts candidate analysis revision; selective representation maintenance is explicit; provider model identity is configured and validated; v1 ambiguous dense provenance is rejected rather than silently reinterpreted. Windows Engineering Probe reports 10/10 gates PASS and repository CI is green.

## Active — R0.8H Closure Sprint

No new R0.8 feature module is planned.

The remaining Roadmap V2 requirement is the phase-level Product Probe on private real footage. It must cover, collectively:

- talking head;
- handheld product demo;
- camera pan;
- hand/product interaction;
- low motion;
- noisy/blurred footage.

The probe must evaluate the usefulness of grounded temporal evidence on real footage, including anchor recall/false positives and speech-cut quality, and must confirm the existing retrieval representation remains usable on the probe project.

Synthetic fixtures may support diagnostics but cannot satisfy this closure gate.

## Closure rule

Treat R0.8H as one closure sprint, not a chain of new subphases.

If the real-footage probe exposes a bounded defect in an already-owned R0.8 mechanism, repair it, rerun the affected deterministic tests and the same Product Probe, and continue toward closure in the same work order when practical.

If all R0.8H acceptance gates pass:

1. write `docs/validation/R0.8_FINAL_CLOSURE.md` with anonymized evidence/metrics only;
2. mark R0.8 CLOSED;
3. set the roadmap active phase to R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer;
4. stop before R0.9 implementation so the next work order starts from a verified phase boundary.

Do not commit private media, absolute local media paths, private transcripts or other sensitive source content.

## Operational control

Codex reads, in order:

1. `docs/operations/CODEX_EXECUTION_ENTRY.md`
2. this file
3. `docs/operations/CURRENT_WORK_ORDER.md`

`CURRENT_WORK_ORDER.md` is the single active implementation/probe boundary.

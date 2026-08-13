# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE

**Current phase:** R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer

**Active boundary:** R0.9 Product Probe evidence hardening + Phase Closure

**Date:** 2026-08-13

## Closed

- R0.7A — Architecture v0.2 Migration Foundation.
- R0.7B — Pre-production Planning + Commercial Skill Foundation.
- R0.8 — Media Evidence Foundation.

## Accepted R0.9 engineering baselines

- R0.9A `ef6efa1f047201c96caeb2c56d7c895af00549a1` — grounded EditSlot → hybrid retrieval → CandidateWindow.
- R0.9B `fb2584d2c707fab3885179ad6f28e713362f2d68` — canonical edit contracts + grounded Resolver + deterministic sequence optimizer.

R0.9A/B implementation remains accepted and CI-green.

## Product Probe evidence hardening

Candidate closure probe `1d889ad1879f52e02966e6a441169db8ef0a6ddd` is **not yet valid for Human Gate**.

The probe renders real local footage, but its comparison function pre-constructs `ShotCandidate`, `CandidateWindow` and source ranges in probe code. Therefore the previews do not yet prove the required end-to-end chain from the real local corpus through the actual R0.9 retrieval/window machinery into Resolver.

This is a probe-validity defect, not a reason to add R0.9C/R0.9D or reopen accepted R0.9A/B mechanisms.

The same Product Probe must be rerun with candidate identities/ranks produced by the actual lexical+dense retrieval path and source windows produced from actual R0.8 evidence/anchors through the canonical CandidateWindow generator. Fixed EditPlan intent and separate human-known scoring expectations are allowed; preselected candidate IDs or answer source ranges are not.

After the repaired technical Product Probe passes, restore `READY_FOR_HUMAN_ACCEPTANCE` and expose the three real-pipeline previews for human candidate/trim/sequence judgment. Human acceptance then closes R0.9 and activates R0.10.

Do not begin R0.10 before R0.9 closure.

## Operational control

Codex reads `CODEX_EXECUTION_ENTRY.md`, this file, then `CURRENT_WORK_ORDER.md`.

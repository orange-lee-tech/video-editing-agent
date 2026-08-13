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

R0.9A/B implementation remains accepted and CI-green.

## Product Probe evidence hardening

Candidate closure probe `1d889ad1879f52e02966e6a441169db8ef0a6ddd` was not valid for
Human Gate because it preconstructed decision inputs. The hardened replacement now passes
the required real-pipeline technical gates.

That probe-validity defect was repaired without adding R0.9C/R0.9D or reopening accepted
R0.9A/B mechanisms.

The replacement executes the actual lexical and multilingual-E5 dense indexes over the
managed local corpus, derives persisted OpenCV motion evidence and anchors, generates windows
through the canonical CandidateWindow generator, and passes those windows to the grounded
Resolver/optimizer. Its three previews remain local and gitignored.

R0.9 is `READY_FOR_HUMAN_ACCEPTANCE`. Human acceptance then closes R0.9 and activates R0.10.

Do not begin R0.10 before R0.9 closure.

## Operational control

Codex reads `CODEX_EXECUTION_ENTRY.md`, this file, then `CURRENT_WORK_ORDER.md`.

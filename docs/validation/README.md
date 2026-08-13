# Validation Archive

This directory stores durable phase/probe evidence: readiness records, engineering probes, product probes and final closure records.

## How to read it

- Prefer a phase's `*_FINAL_CLOSURE.md` when one exists.
- Intermediate readiness/audit/probe files remain historical evidence and should not be mistaken for current state.
- Current live phase/status belongs in `../roadmap/CURRENT_PHASE_STATUS.md`, not here.

Closed modern phases include R0.7A, R0.7B, R0.8 and R0.9 with their corresponding final evidence.

R0.10 is **not closed** as of the 2026-08-13 governance pause. R0.10A/R0.10B are accepted engineering baselines, but the real-music Product Probe/Human Gate has not been completed; therefore no R0.10 final-closure document should exist yet.

Never commit private footage, local absolute paths or generated media merely to make validation self-contained. Record hashes/IDs/metrics and keep private media local.

# Validation Archive

This directory stores durable phase/probe evidence: readiness records, engineering probes, product probes and final closure records.

## How to read it

- Prefer a phase's `*_FINAL_CLOSURE.md` when one exists.
- Intermediate readiness/audit/probe files remain historical evidence and should not be mistaken for current state.
- Current live phase/status belongs in `../roadmap/CURRENT_PHASE_STATUS.md`, not here.

Closed modern phases include R0.7A, R0.7B, R0.8, R0.9 and R0.10 with their corresponding final evidence.

R0.10 closed on 2026-08-14 after the real-music Product Probe and explicit Human Gate acceptance. See `R0.10_FINAL_CLOSURE.md` for the durable engineering/Product Probe/Human Gate record.

Never commit private footage, local absolute paths or generated media merely to make validation self-contained. Record hashes/IDs/metrics and keep private media local.

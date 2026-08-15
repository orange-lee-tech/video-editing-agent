# Validation Archive

This directory stores durable phase/probe evidence: readiness records, engineering probes, product probes and final closure records.

## How to read it

- Prefer a phase's `*_FINAL_CLOSURE.md` when one exists.
- Intermediate readiness/audit/probe files remain historical evidence and should not be mistaken for current state.
- Current live phase/status belongs in `../roadmap/CURRENT_PHASE_STATUS.md`, not here.
- Cross-phase probe anchors are summarized in `../logs/PROBE_LEDGER.md`.
- Engineering Probe and Product Probe are different evidence classes: synthetic/local fixtures may prove deterministic machinery, but they do not prove real-user usefulness.

Closed modern phases include R0.7A, R0.7B, R0.8, R0.9, R0.10 and R0.11.

R0.11 closed as `PASS_WITH_MINOR_DEFECT`; its accepted movement baseline is retained while the occlusion/recovery micro-jump remains a known non-blocking limitation.

R0.12 is **ACTIVE**, not closed. Its accepted engineering foundations currently include canonical EDL v0.2, deterministic EDLBuilder and the EDL-driven FFmpeg Renderer. Their Engineering Probes accumulate evidence toward R0.12 closure; they are not themselves a final phase Product Probe/Human Gate.

Never commit private footage, local absolute paths or generated media merely to make validation self-contained. Record hashes/IDs/metrics and keep private media local.

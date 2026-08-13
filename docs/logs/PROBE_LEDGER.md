# Probe Ledger

Non-authoritative durable probe history. See `docs/logs/README.md`.

## Probe rule

A paid Product Probe requires a question that deterministic/local evidence cannot answer and must discriminate materially different hypotheses. Record the question, required evidence and cost before execution. Engineering Probes may use controlled/synthetic fixtures when testing mechanism rather than product usefulness.

## Durable probe anchors

### R0.7A private real-footage Product Probe — CLOSED

- Date: 2026-08-11
- Evidence: `docs/validation/R0.7A_FINAL_CLOSURE.md`
- Result: PASS WITH QUALITY GUARD
- Real phone footage produced the correct three-shot structure; retained cut deltas were approximately 91 ms and 142 ms early.
- Durable conclusion: exact-time Asset → Shot works on real footage; boundary timing error remains an explicit quality guard.

### R0.7B Product Probe cluster — CLOSED

- Runs: #14 `31599408682`, #15 `31608957718`, #16 `31610613082`
- Final accepted baseline: `48ecafcf45a299ced4d9abafd5501e2b9031f4a3`
- Evidence: `docs/validation/R0.7B_FINAL_CLOSURE.md`
- Runs #14/#15 isolated commercial-authority inconsistencies rather than mere prompt wording defects.
- Run #16 passed Product Ad + Natural Vlog automated gates; Human Gate accepted usefulness, shooting executability, factual fidelity and expected coverage.

### R0.8 Media Evidence Foundation — CLOSED

- Final closure: `6257586310e266ef271ea67f8eda1cc5434e6df1`.
- Evidence: `docs/validation/R0.8_FINAL_CLOSURE.md`.
- Speech/VAD, camera-compensated motion, event reduction/refinement, seeded tracking, multilingual E5 retrieval and managed local corpus evidence all reached accepted engineering/product gates.
- Final Product Probe gates: 10/10 PASS; Quality Gate: 437 tests.
- Durable conclusion: real footage can yield useful grounded candidate-time evidence on a CPU-practical path; this phase did not claim a finished edit.

### R0.9 Grounded Director / Resolver Product Probe — CLOSED

- Accepted engineering baselines: R0.9A `ef6efa1f047201c96caeb2c56d7c895af00549a1`; R0.9B `fb2584d2c707fab3885179ad6f28e713362f2d68`.
- Repaired real-pipeline Product Probe: `a8574d170aeb366a655b6d32486b481eb081321f`.
- Evidence: `docs/validation/R0.9_FINAL_CLOSURE.md`.
- Real pipeline: managed corpus → lexical index → E5 dense index → RRF → OpenCV motion/evidence → canonical CandidateWindow generator → Resolver/optimizer → exact diagnostic previews.
- Human Gate accepted visual selections and cut points; Resolver-vs-hybrid subjective preference was explicitly inconclusive rather than fabricated.
- Durable conclusion: grounded exact source-selection plans can be produced without LLM timestamp hallucination.

### R0.10A/B Music / Audio Engineering Baselines — ACCEPTED, PHASE OPEN

- R0.10A: `7d4dcc0afb26556f9a161b73ca408946f6f417d7` — local rights-aware audio, BeatMap, grounded music window and audible mix foundation.
- R0.10B candidate: `d893d4c6fb67f1218416a302c7c6775c22bde088` — signal-derived BeatMap confidence, feature-ranked windows, bounded loop plan and structured duck/fade intent.
- R0.10B bridge repair: `81afb604b96486587a308f6f4c69d89f1450f46e` — canonical MusicSelectionDecision/AudioMixDecision compiled to diagnostic FFmpeg execution; QC measured post-mix decoded PCM.
- Repaired R0.10B gates: 15/15 PASS; Quality Gate: 454 tests; CI success.
- Durable conclusion: the local engineering path is rights-aware, inspectable and audibly executable, but R0.10 has **not** passed its real-music Product Probe/Human Gate and is not closed.

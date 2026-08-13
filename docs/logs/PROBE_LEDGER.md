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
- Product Ad 23 s vs 30 s target remains a non-blocking quality note.

### R0.8B Windows Speech / VAD Engineering Probe — ACCEPTED BASELINE

- Date: 2026-08-13
- Evidence: `docs/validation/R0.8B_WINDOWS_SPEECH_VAD_ENGINEERING_PROBE.md`
- Windows 11 x64 / Python 3.12.13 / CPU-only.
- Faster-Whisper 1.2.1 + pinned base model: English/Chinese timed transcription and offline local-files-only execution passed.
- Silero VAD 6.2.1 ONNX + ONNX Runtime 1.28.0: silence/speech/no-audio semantics passed.
- Durable conclusion: local CPU ASR/VAD providers are viable; exact product-quality speech accuracy remains a real-footage concern.

### R0.8C Visual Motion Engineering Probe — ADEQUATE

- Initial implementation: `27cc9addc25454d47da122bcd47d11046befeb4b`
- Hardened baseline: `9b6bbf53220abc42be31f0c5ac12c3aa618cc8b3`
- Runtime: OpenCV headless 4.13.0.92 candidate, CPU, exact Shot `[1s,4s)`.
- Static: ~0 global / ~0 residual.
- Pan-only: ~2 px global with ~0.007 px residual p95.
- Local-only / pan+local: ~2.998 px residual p95 retained.
- Negative control: pure camera pan did not become local residual/action evidence.
- Hardening added streaming frame-pair processing, fail-closed probe output and Artifact reopen integrity.

### R0.8D Visual Event Reduction Engineering Probe — ADEQUATE

- Baseline: `8718191a5b637e01c626b888970934f73db45b22`
- Dense pairwise motion remains in Artifact; durable raw evidence reduced to one measurement-set row per analyzed set.
- Deterministic camera/residual event regions plus coarse onset/peak/settle anchors passed static, pan-only, local-only, pan+local, separated-burst and unavailable-gap gates.
- Artifact identity rehydration, durable lifecycle, atomic evidence+anchor persistence and restart passed.
- Durable conclusion: temporal evidence density now scales with accepted regions/anchors rather than frame pairs.

### R0.8E Fine Temporal Refinement Engineering Probe — ADEQUATE WITH OWNER FIX

- Implementation: `edc21522dd39c79125a487c6be4c82680c3ec553`
- CI: run `31666387172` success.
- New motion Artifact write schema: `r0.8e-visual-motion-v2`, with exact `analyzed_source_range`; v1 remains readable.
- Controlled 10 FPS coarse → 30 FPS bounded refinement:
  - onset error: 66.7 ms → 33.3 ms;
  - peak error: 83.3 ms → 16.7 ms;
  - settle error: 66.7 ms → 33.3 ms;
  - refined anchors stayed within one refined frame of ground truth.
- Non-zero Shot offset, restart equality, V1 compatibility, pan-only negative control and unavailable-gap behavior passed.
- Code review then found the provider-range equality guard unreachable after `return`; commit `220f6c3d912319cf5e66f2ddf989bdff0d41302d` repaired the owner boundary and CI run `31666637333` succeeded.
- Durable conclusion: exact bounded high-rate refinement is viable; natural footage, VFR and threshold calibration remain for later real-footage evidence.

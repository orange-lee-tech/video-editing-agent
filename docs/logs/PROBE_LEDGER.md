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

### R0.10 Music Selection + BeatMap + Audio Editorial — CLOSED

- Final implementation baseline before governance closure: `4782889f3746cf1024abfa0c45f3402cfec834a3`.
- Evidence: `docs/validation/R0.10_FINAL_CLOSURE.md`.
- Real-music Product Probe gates: 9/9 PASS; Human Gate chose Track B, selected moment and structured mix with no blocking audible defect.
- Canonical execution distinguishes source-audio MUTE/PRESERVE and keeps uncertain semantics fail-closed.
- Durable conclusion: a rights-aware, auditable music-selection/mix path is real and executable; broader BeatMap quality and provider acquisition remain downstream work.

### R0.11 Spatial Composition / Auto Reframe — CLOSED

- Accepted implementation baseline: `d06592560dbeb764666592effa00f7d5537715ef` — interpolation-aware spatial QC.
- Result: `PASS_WITH_MINOR_DEFECT`.
- Movement baseline accepted as natural/stable; occlusion recovery retains a visible micro-jump as a known non-blocking limitation.
- Durable conclusion: spatial ownership and executable transform plans are structurally accepted; do not endlessly retune this during Stage A unless broader real-corpus evidence shows a systematic failure.

### R0.12 EDL v0.2 foundation — ACCEPTED ENGINEERING BASELINE

- `ff343833deb9296c1df0b6fc944735388d5c8296` — typed tracks, deterministic composition and structured validation.
- Engineering Probe: 5 named gates PASS.
- Durable conclusion: EDL owns deterministic typed track/timeline structure.

### R0.12 EDL automation / serialization — ACCEPTED ENGINEERING BASELINE

- `4b2522ae1a6838517baf4c5bcf36d30026f86912` — exact rational spatial/audio automation and deterministic v0.2 codec.
- Reported Engineering Probe: 5/5 PASS; focused tests 21 PASS; full gate 505 tests.
- Durable conclusion: executable automation and persisted EDL round-trip no longer depend on binary-float timeline authority.

### R0.12 deterministic EDLBuilder — ACCEPTED ENGINEERING BASELINE

- `b6c5684a9b07d79f20a10d28886cd087eaeecf10` — grounded decisions → authoritative Shot/Asset mapping → exact EDL assembly.
- Reported Engineering Probe: 6/6 PASS; focused verification 26 tests; full gate 513 tests.
- Durable conclusion: already-approved Resolver/Spatial/Audio decisions can converge into one canonical executable EDL without Renderer guesswork.

### R0.12 EDL-driven FFmpeg Renderer — ACCEPTED ENGINEERING BASELINE

- `83fc2999297023f828fa77719cd357fe82eab5de` — `feat: add deterministic EDL-driven renderer`.
- Remote `ci/quality-gate-diagnostic`: success.
- Live Engineering Probe: 8/8 PASS; it invokes `DeterministicEDLBuilder` → `FFmpegEDLRenderer` → real MP4 → ffprobe rather than bypassing the Renderer.
- Verified output characteristics: 2.000 s, 180×320, 30 FPS; PRESERVE output has audio while MUTE output has no audio.
- Focused tests: 22 PASS; reported full Quality Gate: 522 tests plus Ruff/mypy/import contracts/build/diff check.
- Durable conclusion: canonical EDL is physically executable into a locally verifiable MP4 while missing/unsupported semantics remain fail-closed.

### R0.12 living Resolver → Renderer integration smoke — ACCEPTED ENGINEERING BASELINE

- `9f06386f9f311fe241f250f4679fa6b2042699b0` — `test: add living Resolver to Renderer smoke`.
- Remote `ci/quality-gate-diagnostic`: success.
- Actual `optimize_sequence()` output selects `candidate-red` at source start `1/4` for 1 s and `candidate-blue` at source start `1/2` for 1 s; those exact ranges survive EDLBuilder unchanged.
- Final ignored/private MP4: 2.000 s, 320×192, 30 FPS, source audio present under PRESERVE.
- Final-frame pixel sampling at 0.25 s and 1.25 s proves red → blue visual order after real Renderer execution; this closes the previous ordered-final-image evidence gap without inventing a spatial decision.
- Named Engineering Probe gates: 10/10 PASS; reported full Quality Gate: 523 tests plus Ruff/mypy/import contracts/build/diff check.
- Temporary `tmp-renderer-nav-sync*` branches were removed and independently confirmed absent.
- Classification remains `ENGINEERING_FOUNDATION_ONLY`; it is not a substitute for R0.16 VisualUnderstanding-driven one-click Product Probe evidence.
- Durable conclusion: a cheap living cross-phase execution spine now catches Resolver/EDLBuilder/Renderer contract drift before final integration.

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
- Durable conclusion: real planning Product Probes accepted useful, executable and commercially faithful Script/ShootingPlan behavior.

### R0.8 Media Evidence Foundation — CLOSED

- Final closure: `6257586310e266ef271ea67f8eda1cc5434e6df1`.
- Evidence: `docs/validation/R0.8_FINAL_CLOSURE.md`.
- Speech/VAD, motion, temporal evidence, tracking and dense retrieval reached accepted engineering/product gates.
- Final Product Probe gates: 10/10 PASS; Quality Gate: 437 tests.

### R0.9 Grounded Director / Resolver Product Probe — CLOSED

- Accepted engineering baselines: `ef6efa1f047201c96caeb2c56d7c895af00549a1`, `fb2584d2c707fab3885179ad6f28e713362f2d68`.
- Repaired real-pipeline Product Probe: `a8574d170aeb366a655b6d32486b481eb081321f`.
- Evidence: `docs/validation/R0.9_FINAL_CLOSURE.md`.
- Durable conclusion: grounded exact source-selection plans can be produced without LLM timestamp hallucination.

### R0.10 Music Selection + BeatMap + Audio Editorial — CLOSED

- Final implementation baseline before governance closure: `4782889f3746cf1024abfa0c45f3402cfec834a3`.
- Evidence: `docs/validation/R0.10_FINAL_CLOSURE.md`.
- Real-music Product Probe gates: 9/9 PASS; Human Gate accepted the chosen track/moment/mix.

### R0.11 Spatial Composition / Auto Reframe — CLOSED

- Accepted implementation baseline: `d06592560dbeb764666592effa00f7d5537715ef`.
- Result: `PASS_WITH_MINOR_DEFECT`.
- Movement accepted as natural/stable; occlusion recovery micro-jump remains a non-blocking Stage-B refinement item.

### R0.12 EDL v0.2 foundation — ACCEPTED ENGINEERING BASELINE

- `ff343833deb9296c1df0b6fc944735388d5c8296` — typed tracks, deterministic composition and structured validation.
- Engineering Probe: 5 named gates PASS.

### R0.12 EDL automation / serialization — ACCEPTED ENGINEERING BASELINE

- `4b2522ae1a6838517baf4c5bcf36d30026f86912` — exact rational spatial/audio automation and deterministic codec.
- Reported Engineering Probe: 5/5 PASS; focused tests 21 PASS; full gate 505 tests.

### R0.12 deterministic EDLBuilder — ACCEPTED ENGINEERING BASELINE

- `b6c5684a9b07d79f20a10d28886cd087eaeecf10` — grounded decisions → authoritative Shot/Asset mapping → exact EDL assembly.
- Reported Engineering Probe: 6/6 PASS; focused verification 26 tests; full gate 513 tests.

### R0.12 EDL-driven FFmpeg Renderer — ACCEPTED ENGINEERING BASELINE

- `83fc2999297023f828fa77719cd357fe82eab5de` — canonical-EDL-driven FFmpeg Renderer.
- Remote `ci/quality-gate-diagnostic`: success.
- Live Engineering Probe: 8/8 PASS; real MP4/ffprobe evidence; focused tests 22 PASS; full Quality Gate reported 522 tests.

### R0.12 living Resolver → Renderer integration smoke — ACCEPTED ENGINEERING BASELINE

- `9f06386f9f311fe241f250f4679fa6b2042699b0` — actual optimizer output → EDLBuilder → Renderer → final MP4/pixel verification.
- Named Engineering Probe gates: 10/10 PASS; reported full Quality Gate: 523 tests.
- Classification remains `ENGINEERING_FOUNDATION_ONLY`, not a substitute for the R0.16 one-click Product Probe.

### R0.12 structured subtitle execution — CLOSED / ACCEPTED ENGINEERING BASELINE

- Initial candidate: `12e4049c53a9597fba2a6654701d779d496b9433` — `feat: add structured subtitle execution`.
- Final accepted closure: `827b84941e1726bab374f2ffea9a746f49f6e570` — `fix: fail closed unsupported subtitle execution`.
- Independent GitHub review confirms the closure commit is one bounded commit from the previous governance baseline and changes only the expected four files.
- Remote `ci/quality-gate-diagnostic`: success.
- Structured cues remain canonical EDL subtitle payloads with exact rational time, schema-v3 deterministic round-trip/v2 backward read, language/speaker/emphasis/layout intent and no fake media Asset.
- Non-centisecond cue boundaries now fail closed before FFmpeg invocation; Renderer no longer silently rounds/retimes them.
- Stage-A ASS execution now rejects multiple SUBTITLE tracks and nonzero subtitle layers before invocation rather than flattening canonical layer semantics.
- Live Engineering Probe now places the actual ASS artifact beneath `filter, path's punctuation`, proving comma + apostrophe handling in the real libass filter path on the tested Windows setup.
- Reported closure verification: focused tests 39 PASS; subtitle live probe 8/8 PASS; living integration smoke 10/10 PASS; Ruff PASS; mypy PASS; full pytest 541 PASS; import-linter 3 contracts kept; `uv build` PASS; `git diff --check` PASS.
- Evidence remains Engineering Probe only; it does not claim universal semantic CJK glyph correctness or font-packaging completeness.
- Durable conclusion: the bounded Stage-A subtitle execution boundary is structurally closed without expanding into a typography/layer engine.

### R0.12 Reference URL acquisition + owner-seam probes — CLOSED

- Date: 2026-08-17.
- Accepted production baseline: `d15abf9258c0a080e37d666cd1112358723e823a`.
- Evidence: `docs/validation/R0.12_REFERENCE_URL_ACQUISITION_CLOSURE.md`.
- Real acquisition probe: direct public HTTPS sample → 1,128,375 bytes → SHA-256 preserved → real ffprobe H.264 960x540 → persisted `reference_acquired + reference_analysis_only` Asset → Resolver ineligible; PASS.
- Focused owner-seam probe: same real acquisition/ingest class reached the existing `ReferenceStyleEvidenceService`, created a content-addressed reference-style artifact and nine Planning guidance entries; PASS.
- The owner-seam probe used an explicitly labeled `SYNTHETIC_SEAM_FIXTURE` only for Shot + VisualSemantics and made no claim of real Gemini/OpenAI visual-model execution.
- Durable conclusion: supported Reference URLs can become governed project-local analysis-only media and reach existing reference guidance without becoming editable visual footage or Resolver authority.

### R0.12 ProductFlow orchestration Engineering Probe — CLOSED

- Date: 2026-08-17.
- Accepted production baseline: `1e90e2dd3d235271ef48bb7a708a1899ce5b87a4`.
- Evidence: `docs/validation/R0.12_PRODUCT_FLOW_ORCHESTRATION_CLOSURE.md`.
- Final Windows Engineering run: `32046190310` — PASS.
- Exact-head deterministic CI: `32046499144` — PASS.
- Planning path: ordinary request → live DeepSeek planning/review → persisted exact Brief/ScriptPlan/ShootingPlan refs — PASS.
- Editing path: real generated media with audio → ingest/understanding → live Director → grounded Resolver → canonical persisted EDL → actual FFmpeg MP4 → Review — PASS.
- Second-process verifier reopened the exact canonical EDL revision and lineage — PASS.
- Source-original SHA-256 preservation — PASS; rendered MP4 contained video + audio; Review disposition PASS.
- Earlier probe attempts correctly exposed two fixture/harness issues and one provider-contract weakness: a commercial-claim semantic veto, contradictory production-resource declarations, and insufficiently explicit Director scalar schema instructions. Review/parser boundaries were not loosened; the fixture was corrected and the Director prompt was minimally strengthened while strict parsing remained fail-closed.
- Durable conclusion: the accepted ProductFlow owner chains work end-to-end under bounded Windows Engineering evidence. This does **not** close the ordinary-user Product/Human Gates; those remain OPEN at Stage-A 90%.

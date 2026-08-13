# Probe Ledger

Non-authoritative probe history. See `docs/logs/README.md`.

## Probe execution rule

Before a paid Product Probe, write down:

1. the exact question;
2. at least two candidate root causes the run can discriminate;
3. the evidence fields needed to discriminate them;
4. why deterministic tests / existing CI cannot answer the question;
5. expected API and human-review cost class.

If a red result would merely reveal another wording example without separating root causes, do not run it.

## Durable anchors

### R0.7A private real-footage Product Probe — CLOSED

- Date: 2026-08-11
- Evidence: `docs/validation/R0.7A_FINAL_CLOSURE.md`
- Result: PASS WITH QUALITY GUARD
- Observed: correct three-shot structure; cut-point deltas approximately 91 ms and 142 ms early versus the retained source-clip cumulative reference.
- Durable information gain: real local footage traversed the exact-time Asset → Shot chain; boundary precision is now a first-class regression concern.

### R0.7B Product Probe run #14 — 31599408682

- Date: 2026-08-12
- Baseline: `371520938753f19af5dc2e7724a6dad91f58c2d9`
- Workflow: `R0.7B Product Probe Evidence`
- Result: `automated-gate-vetoed`
- Natural Vlog: `ready_for_human_acceptance`
- Product Ad Script semantic review: accepted
- Product Ad Shooting semantic review: accepted
- Product Ad automated Product Review: veto
- Final unsupported excerpt: `适合日常携带`
- Additional observed semantic risk: Product Ad ShootingPlan explicitly planned placing the bottle into a backpack side pocket, which visually demonstrates a fit outcome despite fit not being an authoritative fact.

#### Information gained

This run discriminated a stronger root cause than a missing prompt example: separate Script, Shooting, and Product-review LLM calls can interpret materially equivalent authority rules differently. It also exposed a Product Ad fixture tension: `core_message` requests convenient commute carrying while authoritative facts only establish 500 mL capacity and a screw-on lid.

#### Decision after run #14

Freeze paid Product Probe execution until:

- the commercial authority model is unified;
- the Product Ad fixture no longer requires an unauthorized factual conclusion;
- offline regressions cover the same semantic defect across spoken, on-screen, visual, and shooting-instruction surfaces;
- the next paid run can distinguish structural semantic-gate failure from product-quality failure.

No run #15 is authorized merely to test another prompt wording.

### R0.7B Product Probe run #15 — 31608957718

- Date: 2026-08-12
- Baseline: `186813be1b4d950266fbebe5edbeb9b82a5f0774`
- Result: `automated-gate-vetoed`
- Natural Vlog: `ready_for_human_acceptance`
- Product Ad: Script semantic veto only
- Veto excerpt: `拧紧就好`
- Reviewer classification: unsupported operability/ease-of-use implication from a screw-on-lid fact.

#### Information gained

The shared commercial-authority refactor was materially working: the earlier fit/commute contradiction disappeared and Natural Vlog stayed green. The remaining failure isolated a narrower invariant: a structural/mechanical fact must be rendered as a neutral observable mechanism/action/state, without evaluative or sufficiency semantics such as ease, convenience, simplicity, `just do X`, or `X is enough`.

#### Decision after run #15

Do not weaken the reviewer. Tighten the shared authority contract and fixture toward neutral observable mechanics, cover it with deterministic regressions, require free CI green, then allow one more Product Probe.

### R0.7B Product Probe run #16 — 31610613082 — CLOSED

- Date: 2026-08-12
- Baseline: `48ecafcf45a299ced4d9abafd5501e2b9031f4a3`
- Workflow: `R0.7B Product Probe Evidence`
- Result: `reviewable-evidence-generated`
- Workflow conclusion: success
- Product Ad: `ready_for_human_acceptance`
- Natural Vlog: `ready_for_human_acceptance`
- Script semantic review: accepted for both cases
- Shooting semantic review: accepted for both cases
- Automated Product Review: accepted for both cases
- All required/recommended coverage present: true for both cases
- Structured location references authorized: true for both cases
- Material provider invoked: false for both cases
- Product Ad duration: target 30 s, estimated 23 s, delta -7 s
- Natural Vlog duration: target 45 s, estimated 45 s, delta 0 s
- Human evaluation status: accepted
- Formal closure: `docs/validation/R0.7B_FINAL_CLOSURE.md`

#### Information gained

The unified Authority + neutral-observation rule carried both distinct R0.7B policies through real provider generation, semantic review, shooting planning, and final automated Product Review without the previous unsupported fit/ease claims.

The Product Ad 23/30-second duration result is retained as a non-blocking product-quality note. The Roadmap does not define exact duration equality as the R0.7B Product Probe exit criterion, so it is not converted into an engineering failure or another paid probe trigger.

#### Decision after run #16

Human Gate accepted usefulness, shooting executability, factual fidelity, and expected coverage. R0.7B is formally closed. No further R0.7B prompt tuning or paid probe is justified absent a new observed product defect.

### R0.8B Windows Speech / VAD Engineering Probe — 2026-08-13

- Baseline: `1b3406ccec0cc852918ff10d6d7dea9f830e5990`
- Environment: Windows 11 x64, CPython 3.12.13, Intel i5-6300U, ~19.9 GiB RAM
- Evidence: `docs/validation/R0.8B_WINDOWS_SPEECH_VAD_ENGINEERING_PROBE.md`
- Repository mutation during probe: none; `.tools/` only
- Local Quality Gate: all required checks passed
- Paid Product Probe: not run

#### Faster-Whisper

- Runtime: `faster-whisper 1.2.1`
- Model: `Systran/faster-whisper-base`
- Model revision: `ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66`
- CPU/int8: successful
- Word/segment timestamps: present
- Offline `local_files_only=True`: successful
- English SAPI sanity: successful, RTF 1.209
- Chinese SAPI sanity: successful, RTF 0.735
- Classification: `BASE ADEQUATE`
- Decision: approved as the R0.8 Windows CPU ASR Engineering baseline; natural-human-speech accuracy remains a later product-quality concern.

#### Silero VAD

- Upstream/model: Silero VAD 6.2.1 pinned ONNX
- ONNX Runtime 1.28.0: installed, loaded, inferred successfully
- Silence fixture: complete silence partition, RTF 0.127
- Speech fixture: silence → speech → silence, RTF 0.110
- No-audio: unavailable/error, not fabricated silence
- Atomic persistence and nondeterminism invariants: deterministic tests passed
- ONNX Runtime 1.29.0 Python comparison: deferred because a compatible Python package was not installable through the tested acquisition path at probe time
- Decision: ONNX Runtime 1.28.0 + pinned Silero ONNX path approved as the R0.8 Windows CPU VAD Engineering baseline; 1.29 comparison is non-blocking deferred maintenance.

#### Information gained

The existing ASR/VAD provider architecture is not merely unit-test scaffolding: both concrete local inference paths run on the target Windows CPU environment with the expected timing/probability outputs and without a high-end GPU.

The remaining Speech risk is now integration/product quality rather than provider viability. A reusable live provider → owner → SQLite reopen regression should be created before phrase/time mapping relies on persisted Speech/VAD evidence.

#### Decision after R0.8B Engineering Probe

- Preserve the current provider/domain authority boundaries.
- Do not switch model/runtime merely because a newer version exists.
- Build one reusable full-chain Speech/VAD integration probe next.
- If that gate is green, continue to deterministic phrase/time mapping.
- Do not start R0.9 Director/Resolver authority during this work.

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

### R0.7B Product Probe run #16 — 31610613082

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
- Human evaluation status: pending

#### Information gained

The unified Authority + neutral-observation rule can now carry both distinct R0.7B policies through real provider generation, semantic review, shooting planning, and final automated Product Review without the previous unsupported fit/ease claims. The remaining question is no longer an automated semantic-gate question; it is the explicit Human Gate over usefulness, shooting executability, factual fidelity, and expected coverage.

The Product Ad 23/30-second duration result is retained as a human product-quality note. The Roadmap does not define exact duration equality as the R0.7B Product Probe exit criterion, so this is not silently converted into an engineering failure or another paid probe trigger.

#### Decision after run #16

- No more paid Product Probe is justified before Human Gate feedback.
- Do not tune prompts merely to remove the 7-second duration delta.
- If Human Gate accepts both plans as practical, write formal R0.7B closure evidence and synchronize authoritative/current-state docs.
- If Human Gate rejects a material product property, classify that product-quality defect first and fix the shared mechanism rather than the observed sentence.

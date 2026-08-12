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

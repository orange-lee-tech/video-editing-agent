# Incident Ledger

Non-authoritative durable debugging history. See `docs/logs/README.md`.

## R0.7B commercial semantic-authority cluster — CLOSED

**Period:** 2026-08-11 to 2026-08-12

### Mechanism

Generation, Script review, Shooting review and Product review initially interpreted commercial authority independently. Mechanical facts such as a screw-on lid or 500 mL capacity could drift into unsupported convenience, fit, sufficiency or ease claims. Free-text production-location identity and reviewer projection drift created adjacent symptoms.

### Durable invariant

`objective`, `audience` and `core_message` may define narrative context/positioning but do not establish concrete product property, performance, fit, adequacy, operability, reliability or outcome facts. Concrete assertions and successful demonstrations require explicit authoritative support.

When authority establishes only a visible mechanism/action/state, generation and review surfaces may describe that neutral observation only. Ease, convenience, simplicity, sufficiency and resulting benefit require separate authority.

### Systemic fix

- shared Commercial Authority projection across generation/review;
- structured ProductionLocation identity;
- veto-only reviewer semantics;
- bounded repair that removes unsupported semantic properties rather than paraphrasing them;
- deterministic regressions across spoken, on-screen, visual and shooting-instruction surfaces.

### Closure evidence

Product Probe run `31610613082` on baseline `48ecafcf45a299ced4d9abafd5501e2b9031f4a3` passed automated gates for Product Ad and Natural Vlog. Human Gate subsequently accepted usefulness, shooting executability, factual fidelity and expected coverage. Formal closure: `docs/validation/R0.7B_FINAL_CLOSURE.md`.

Do not reopen this cluster for isolated wording unless new evidence demonstrates a shared invariant failure.

## R0.8E analyzed-source-range owner guard — CLOSED

**Date:** 2026-08-13

### Symptom

R0.8E introduced `analyzed_source_range` provenance and tests/Windows probe passed, but code review found the owner check that provider-reported range equals the requested analysis range placed after `return result`, making the validation unreachable.

### Mechanism / subsystem

Owner-boundary validation existed textually but not in the executable control flow. A faulty provider could therefore report a mismatched analysis window and still reach Artifact/evidence persistence.

### Shared invariant

Provider-reported exact analysis identity/range must be validated by the owner **before** any durable Artifact or evidence commit. A guard after persistence/return is not a guard.

### Fix / verification

Commit `220f6c3d912319cf5e66f2ddf989bdff0d41302d` moves the range-equality check before measurement validation/persistence and adds an explicit provider-range-mismatch regression. GitHub Actions run `31666637333` completed successfully.

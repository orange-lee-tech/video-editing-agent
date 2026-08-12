# Incident Ledger

Non-authoritative debugging history. See `docs/logs/README.md`.

## R0.7B pre-production stabilization cluster — 2026-08-11 to 2026-08-12

### Shared root-cause assessment

The recent sequence was not one bug repeatedly surviving. It was a mixture of provider/infrastructure failures and a deeper commercial-semantic authority problem. Infrastructure failures were valid to fix at their own layer; unsupported-claim failures increasingly exposed that authority semantics were being interpreted independently by natural-language generation/reviewer passes instead of being represented by one shared semantic contract.

| Symptom | Mechanism / subsystem | Classification | Durable conclusion |
|---|---|---|---|
| reviewer `finish_reason=length` | thinking review output-capacity exhaustion | NECESSARY_INFRASTRUCTURE_FIX | bounded capacity recovery is valid; do not treat capacity as semantic failure |
| 16k → bounded 32k recovery | reviewer execution envelope | NECESSARY_INFRASTRUCTURE_FIX | keep bounded; no unbounded retry loop |
| reviewer empty final JSON | provider transient completion failure | NECESSARY_INFRASTRUCTURE_FIX | one bounded transient retry is valid |
| reviewer capacity/transient diagnostics | probe/provider observability | OBSERVABILITY_FIX | preserve safe token/finish diagnostics without reasoning content |
| Script reviewer lost section fields such as `target_duration` | hand-built reviewer projection drift | SYSTEMIC_FIX | adjacent reviewer projections must be audited together when one loses execution-relevant shape |
| Shooting reviewer needed complete committed Script shape | reviewer projection drift | SYSTEMIC_FIX | review surfaces must inspect the same committed meaning used downstream |
| Chinese-only Product Probe criterion | fixture constrained language without product need | TEST_FIXTURE_FIX | Product Probe should measure product usefulness, not arbitrary fixture language |
| free-text production location ambiguity | authority identity mixed with descriptive prose | SYSTEMIC_FIX | structured `ProductionLocation` identity is the durable authority; prose is descriptive |
| structural fact → ease/convenience claim | semantic inference from mechanism to adequacy | SYSTEMIC_FIX | structural/mechanical authority now explicitly permits only neutral observable mechanism/action/state unless separate facts support evaluative meaning |
| `500 mL` → enough-for-use-case / easy-fit claim | semantic inference from property to adequacy/fit | SYSTEMIC_FIX | concrete fit/adequacy requires explicit support, not marketing framing |
| bounded repair paraphrased the same unsupported property | generate → veto → regenerate retained semantic defect | SYSTEMIC_ORCHESTRATION_FIX | reviewer diagnostics are non-authoritative and repair must remove the semantic property, not synonymize it |
| generation temperature reduced to 0.2 | generation variance | RELIABILITY_CONFIG_FIX | lower variance can improve reproducibility but cannot make an invalid authority model correct |
| Product Ad Script/Shooting accepted while Product Review vetoed `适合日常携带` | independent LLM passes interpreted the same authority differently | SYSTEMIC_FIX | one shared Commercial Authority projection/rule now feeds generation and review surfaces |
| ShootingPlan accepted `placing bottle into backpack side pocket` | visual demonstration implicitly asserts fit outcome | SYSTEMIC_FIX | planned successful demonstrations are treated as concrete claims requiring authority/conditional treatment |
| Product Ad Script reviewer vetoed `拧紧就好` after shared-authority refactor | neutral mechanism description still carried sufficiency/ease semantics | SYSTEMIC_FIX | neutral-observation invariant must cover spoken copy, on-screen text, information goals, visuals, demonstrations, and shooting instructions |

### Resolved shared invariant

`objective`, `audience`, and `core_message` may define narrative context and positioning intent. They do not establish concrete product property/performance/fit/adequacy/operability/material/reliability/outcome facts. Concrete product assertions or successful demonstrations require explicit authoritative support; unsupported desired claims remain unresolved rather than becoming facts through generation or review.

When authority establishes only a visible mechanism, action, or state, model-visible planning surfaces must describe only that neutral observable mechanism/action/state. Ease, convenience, simplicity, sufficiency, or resulting benefit require separate authoritative support.

### Affected surfaces audited together

- Brief commercial semantics;
- Script generation context;
- Script semantic review;
- Shooting generation context;
- Shooting semantic review;
- Product Probe full-plan evaluation;
- repair instructions;
- fixture design and offline regressions.

### Closure evidence for this incident cluster

Product Probe run #16 (`31610613082`) on baseline `48ecafcf45a299ced4d9abafd5501e2b9031f4a3` reached `ready_for_human_acceptance` for both Product Ad and Natural Vlog. Both Script semantic reviews, both Shooting semantic reviews, and both automated Product Reviews accepted. This closes the automated semantic-authority incident cluster; R0.7B itself still awaits the separate Human Gate.

Do not reopen this incident cluster for isolated wording unless new evidence demonstrates a shared invariant failure.

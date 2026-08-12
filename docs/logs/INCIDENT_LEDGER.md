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
| structural fact → ease/convenience claim | semantic inference from mechanism to adequacy | SYMPTOM_PATCH + UNRESOLVED_SYSTEMIC | examples are useful regressions, but prompt examples are not the long-term authority model |
| `500 mL` → enough-for-use-case / easy-fit claim | semantic inference from property to adequacy/fit | SYMPTOM_PATCH + UNRESOLVED_SYSTEMIC | concrete fit/adequacy requires explicit support, not marketing framing |
| bounded repair paraphrased the same unsupported property | generate → veto → regenerate retained semantic defect | SYSTEMIC_ORCHESTRATION_FIX | reviewer diagnostics are non-authoritative and repair must remove the semantic property, not synonymize it |
| generation temperature reduced to 0.2 | generation variance | RELIABILITY_CONFIG_FIX | lower variance can improve reproducibility but cannot make an invalid authority model correct |
| Product Ad Script/Shooting accepted while Product Review vetoed `适合日常携带` | independent LLM passes interpreted the same authority differently | UNRESOLVED_SYSTEMIC | shared wording in prompts is insufficient; authority execution must be unified |
| ShootingPlan accepted `placing bottle into backpack side pocket` | visual demonstration implicitly asserts fit outcome | UNRESOLVED_SYSTEMIC | a planned successful demonstration can itself be a concrete claim and needs authority/conditional treatment |

### Shared invariant for the next fix

`objective`, `audience`, and `core_message` may define narrative context and positioning intent. They do not establish concrete product property/performance/fit/adequacy/operability/material/reliability/outcome facts. Concrete product assertions or successful demonstrations require explicit authoritative support; unsupported desired claims remain unresolved rather than becoming facts through generation or review.

### Affected surfaces to audit together

- Brief commercial semantics;
- Script generation context;
- Script semantic review;
- Shooting generation context;
- Shooting semantic review;
- Product Probe full-plan evaluation;
- repair instructions;
- fixture design and offline regressions.

Do not fix the next unsupported expression by adding a vocabulary blacklist.

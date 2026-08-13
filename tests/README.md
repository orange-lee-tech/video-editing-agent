# Tests

Repository tests are organized by evidence level:

- `unit/` — deterministic local mechanism/invariant tests;
- `integration/` — cross-component/storage/provider-boundary behavior;
- `contracts/` — architecture/schema/ownership contracts;
- `fixtures/` — small redistributable deterministic fixtures and fixture metadata.

Private user media does not belong in committed fixtures. Real Product Probe media may remain local while committed tests verify the reusable mechanism around it.

Passing tests prove defined invariants and regressions; they do **not** by themselves prove editing quality. Human/Product Probe evidence belongs in `docs/validation/` and the probe ledger when material.

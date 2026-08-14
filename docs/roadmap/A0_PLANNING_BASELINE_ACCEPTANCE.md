# A0 Planning Baseline Acceptance Record

**Status:** PASSED / FROZEN  
**Accepted:** 2026-08-11  
**Decision:** Explicit user approval to freeze the current post-Survey V2 planning baseline and enter R0.7A.

## Accepted planning set

The following planning set is accepted as the active engineering baseline:

- `docs/product/PRODUCT_CONSTITUTION_V1.0.md` — unchanged highest product authority;
- `docs/architecture/ARCHITECTURE_CONTRACT_V0.2.md` — accepted as the active Architecture Contract;
- `docs/capabilities/CAP-01...CAP-10` — accepted capability boundaries/specification set;
- `docs/adr/` — accepted current architecture decisions, preserving each ADR's own accepted/provisional status;
- `docs/upstream/UPSTREAM_COMPONENTS_V2.md` and `UPSTREAM_POLICY_V2.md` — active upstream governance;
- `docs/roadmap/ROADMAP_V2.md` — activated roadmap;
- `docs/research/SURVEY_V2_FINAL_CLOSURE.md` — research-stage closure evidence.

The words `CANDIDATE` or `prepared after Survey V2` inside documents created before this acceptance remain historical drafting labels. This record supersedes those labels **for baseline activation status only**. It does not turn benchmark-dependent implementation candidates into approved dependencies.

## Precedence

From this acceptance forward:

```text
Product Constitution v1.0
        ↓
Architecture Contract v0.2
        ↓
Capability Specifications
        ↓
ADRs
        ↓
Implementation / Provider behavior
```

The retired v0.1 / v0.1.1 / v0.1.2 Architecture Contracts are preserved under `docs/archive/architecture/`. They are not current authority where they conflict with v0.2 or the Product Constitution.

This explicitly neutralizes legacy product behavior such as:

- autonomous remote/public visual fallback;
- `remote_allowed` / `remote_only` / `generated_allowed` visual-source semantics;
- `remote_search_queries` as a visual coverage mechanism;
- treating a local reference video as Resolver-eligible footage without an explicit editable-usage action.

## Product Constitution interpretation accepted for v0.2

For current engineering, a user-supplied reference video defaults to:

```text
usage_role = reference_analysis_only
```

It is not Resolver-eligible merely because it is a local file. If the user also wants the file to appear in the output, an explicit editable-footage usage declaration/reclassification with rights attestation is required.

This is accepted as a compatible interpretation of Product Constitution v1.0. A future Constitution revision is required only if product intent itself changes.

## Phase at acceptance

A0 completed the planning gate and entered:

> **R0.7A — Architecture v0.2 Migration Foundation**

The completed migration audit is preserved at:

`docs/archive/roadmap/R0.7A_MIGRATION_AUDIT.md`

Current construction state must be read from `CURRENT_PHASE_STATUS.md`, not from this historical acceptance record.

## Freeze discipline

The planning baseline is frozen against casual drift.

Future changes require the appropriate mechanism:

- product intent/policy → constitutional amendment;
- durable architecture ownership/invariants → Architecture Contract revision + ADR;
- capability behavior → Capability Spec revision;
- concrete implementation choice → ADR/benchmark/upstream gate;
- construction order → Roadmap revision.

No upstream SDK, convenience API, model behavior or old repository document may silently override this baseline.

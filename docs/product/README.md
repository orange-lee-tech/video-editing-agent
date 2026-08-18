# Product Authority

`PRODUCT_CONSTITUTION_V1.0.md` is the highest product-level authority in this repository.

## Change rule

A constitutional change requires an explicit user-approved product-policy revision. Implementation convenience, provider behavior, a new upstream library or a passing probe cannot silently amend it.

The 2026-08-13 repository governance review found **no product-policy conflict requiring a Constitution revision**. Recent R0.9/R0.10 lessons are already covered by existing rules for proposal-vs-authority, EDL/Renderer ownership, rights/provenance, and Engineering-Probe-vs-Product-Probe evidence.

Implementation/architecture details should be changed in lower-level contracts/specs/ADRs unless the actual product intent changes.

## Subordinate product guidance

The following files live in `docs/product/` because they describe ordinary-user product contracts or presentation, but they are **not constitutional peers**:

- `STAGE_A_PRODUCT_IO_CONTRACT.md` — ordinary Stage-A input/output contract;
- `REFERENCE_URL_ACQUISITION_CONTRACT.md` — bounded reference URL behavior;
- `STAGE_A_PUBLIC_MUSIC_ACQUISITION_CONTRACT.md` — public music acquisition boundary;
- `DESKTOP_UI_DESIGN_SYSTEM_V0.1.md` — Windows desktop shell/layout/design guidance.

If any subordinate guidance conflicts with `PRODUCT_CONSTITUTION_V1.0.md`, the Constitution wins and the lower-level file must be corrected.

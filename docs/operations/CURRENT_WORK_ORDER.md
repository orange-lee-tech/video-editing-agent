# Current Work Order

**Status:** WAITING_HUMAN  
**Phase:** R0.10 — Human Gate / closure  
**Updated:** 2026-08-14

## Current evidence

Current accepted implementation baseline:

`4782889f3746cf1024abfa0c45f3402cfec834a3` — `fix: canonicalize music candidate ordering`

Remote review confirmed:

- core `select_music()` owns deterministic global candidate ordering;
- ordering is score descending, then source start, then candidate ID;
- caller tuple ordering no longer affects the selection decision;
- `alternative_asset_refs` excludes the winner and is deterministic/deduplicated;
- Product Probe deliberately reverses cross-track candidate input and still selects the global top score;
- focused R0.10 tests passed (`15 passed`);
- full pytest passed (`461 passed`);
- remote `ci/quality-gate-diagnostic` is green;
- real-music Product Probe is `9/9 PASS`.

## Human Gate evidence set

Use the existing local previews under:

`example/probe-output/r0_10_product/`

Three ordinary comparisons are required:

1. Music candidate: `candidate_a.mp4` vs `candidate_b.mp4`.
2. Music moment: `moment_ordinary.mp4` vs `moment_selected.mp4`.
3. Mix: `mix_basic.mp4` vs `mix_structured.mp4`.

Known Product Probe facts:

- Track A score `0.9460`, range `6.05–12.05s`;
- Track B score `0.9553`, range `29.65–35.65s`;
- system winner Track B;
- ordinary moment `30.45–36.45s`;
- selected moment `29.65–35.65s`;
- source audio policy `MUTE`;
- Track B BeatMap confidence `0.0633` is low and must remain visible when judging usefulness.

## Required human response

Return only ordinary editorial judgments plus any obvious defect note:

- Music candidate: Track A / Track B / tie;
- Music moment: ordinary / selected / tie;
- Mix: basic / structured / tie;
- optional defect note: e.g. BGM too loud/quiet, pumping, unnatural fade, rhythm feels wrong, or another clearly audible problem.

The Human Gate is not a request to validate numeric scores. Prefer what sounds/feels better for the short-form result.

## After Human Gate

- If accepted or preference/ties show no blocking quality defect, ChatGPT records R0.10 closure and advances the control plane to R0.11.
- If a concrete audible defect is identified, repair only that defect inside R0.10, rerun the affected evidence, and return to Human Gate.

## Hard boundaries

- no further speculative R0.10 engineering before human evidence;
- no hidden compensation for Track B confidence;
- no scoring redesign without a Human Gate defect that justifies it;
- no R0.11 work before R0.10 closes;
- no proxy/cache implementation in this phase. Proxy/cache remains planned for R0.12 productization.

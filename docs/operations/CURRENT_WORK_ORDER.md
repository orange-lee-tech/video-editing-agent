# Current Work Order

**Status:** ACTIVE  
**Phase:** R0.10 — global music-selection ordering repair → Product Probe rerun → Human Gate / closure  
**Updated:** 2026-08-14

## Current evidence

Current observed implementation baseline:

`5d63268a39baf5a994a5fca41d2be43f768f9df0` — `test: add real music product probe`

Remote review confirmed:

- real-music Product Probe executed two materially different rights-attested local tracks;
- all six previews consumed canonical decisions and passed rendered-output QC;
- Product Probe 9/9 PASS and full remote CI green;
- Track B won the probe with score `0.9553` over Track A `0.9460`;
- Product Probe harness explicitly sorts cross-track top windows by global score before calling `select_music()`.

## Bounded defect found during review

`MusicSelectionService` owns rights-aware music choice. Current core helper `select_music()` selects `windows[0]` and records the reason `highest deterministic feature score`, but it does not itself sort or validate the input tuple.

Per-track `generate_music_windows()` sorts windows inside one BeatMap, but cross-track aggregation is not guaranteed to preserve global score order. The Product Probe harness manually sorts globally, so it can hide a caller-order dependency in core selection semantics.

This is a small decision-authority defect, not a reason to reopen R0.10 scoring or redesign the Product Probe.

## Coherent implementation boundary

1. Make core music selection deterministic and order-independent for candidate tuples: the highest score must win regardless of caller ordering.
2. Define deterministic tie-breaking consistent with existing window-ranking semantics and stable identity; do not introduce model randomness or new scoring weights.
3. Ensure `alternative_asset_refs` derives from the same canonical global ordering and remains deterministic/deduplicated.
4. Add regression(s) with deliberately unordered candidates from different audio Assets proving the higher-scored candidate wins and the decision reason remains truthful.
5. Remove redundant Product Probe pre-sorting if that improves evidence quality, or at minimum add a probe assertion that core selection itself wins under reversed/unsorted candidate input. The Product Probe must not be the only layer enforcing ordering.
6. Keep all R0.10A/R0.10B/source-audio-policy regressions and full Quality Gate green.
7. Rerun the same real-music Product Probe using the existing local tracks and previews/QC path. Do not alter rights attestations or substitute media.
8. If technically green, stop at `READY_FOR_HUMAN_ACCEPTANCE` and report the same three human comparisons. Do not close R0.10 yourself.

## Human Gate after repair

Present only ordinary judgments:

- Music candidate: Track A / Track B / tie;
- Music moment: ordinary / selected / tie;
- Mix: basic / structured / tie;
- optional obvious defect notes (voice clarity, pumping, fade naturalness, BGM too loud/quiet, other audible problem).

Track B BeatMap confidence `0.0633` must remain visible to the reviewer; do not silently compensate for it by changing scores during this bounded repair.

## Hard boundaries

- no scoring redesign or new heavyweight audio model;
- no new music/downloading/rights claims;
- no synthetic Product Probe evidence;
- no R0.11 work;
- no proxy/cache implementation in this work order; large-media caching remains a later architecture/productization concern.

## Codex entry

1. Sync clean `main` to current `origin/main`.
2. Read `docs/operations/CODEX_EXECUTION_ENTRY.md`.
3. Read `docs/roadmap/CURRENT_PHASE_STATUS.md` and this work order.
4. Inspect only music selection service/port, R0.10 tests and the Product Probe harness.
5. Execute the complete bounded repair and rerun the existing Product Probe if local inputs remain available.
6. Commit/push one coherent green batch and report starting/ending HEAD, changed files, gates, Product Probe result and final classification.

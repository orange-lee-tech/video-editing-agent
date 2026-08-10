# Upstream Reuse Policy — Legacy v0.1 Snapshot

**Status:** HISTORICAL — superseded by `UPSTREAM_POLICY_V2.md` for current upstream decisions.

This file preserves the bootstrap-era policy context. Product Constitution v1.0 and Policy V2 now take precedence.

## FireRed-OpenStoryline

Role: primary architectural and selectively reusable implementation source.

License: Apache-2.0 at the time of architectural review.

Historical policy:

- Do not fork its architecture wholesale.
- Code may enter this repository only after an explicit migration review.
- Record exact upstream repository/path/revision/license.
- Preserve required notices.
- Adapt imported implementation to local Architecture Contracts.

## MoneyPrinterTurbo

Role: provider/operational-engineering reference.

License: MIT at the time of architectural review.

**Current constitutional correction:** its remote visual-stock acquisition behavior is not a permitted product path. Only compatible provider/caching/retry/provenance ideas and audio/non-visual patterns may inform current design.

## CutClaw

Role: engineering reference only.

Do not copy source code. Independently reimplement useful ideas. The project does not depend on CutClaw receiving a future license.

## BeatSync Engine

Role: BeatMap/music-analysis reference.

Do not make it a core dependency by default. Review licensing separately before reuse.

## Historical global rule

No upstream source enters `src/` without explicit provenance.

The current V2 policy extends this rule to code, models/checkpoints, datasets, transitive/native libraries, provider/API commercial terms, codecs/patents and runtime redistribution.

See `UPSTREAM_POLICY_V2.md` and `UPSTREAM_COMPONENTS_V2.md`.

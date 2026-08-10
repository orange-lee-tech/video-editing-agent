# Upstream Reuse Policy

## FireRed-OpenStoryline

Role: primary architectural and selectively reusable implementation source.

License: Apache-2.0 at the time of architectural review.

Policy:

- Do not fork its architecture wholesale.
- Code may enter this repository only after an explicit migration review.
- Record the exact upstream repository, path, revision and license.
- Preserve required notices.
- Document whether code is copied, adapted, or independently reimplemented.
- Adapt all imported implementation to this repository's Architecture Contracts.

## MoneyPrinterTurbo

Role: material-provider and operational-engineering reference.

License: MIT at the time of architectural review.

Policy:

No source migration during Repository Bootstrap v0.1.
Any later reuse must be tracked per module with provenance and required notices.

## CutClaw

Role: engineering reference only.

Policy:

Do not copy source code.
Independently reimplement relevant ideas.
The project does not depend on CutClaw gaining a future license.

## BeatSync Engine

Role: BeatMap/music-analysis reference.

Policy:

Do not make it a core dependency by default.
Review licensing separately before any source reuse.

## Global rule

No upstream source code enters `src/` without an explicit provenance record.

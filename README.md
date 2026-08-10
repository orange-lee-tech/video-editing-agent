# video-editing-agent

A **script-driven, local-first personal video editing agent**.

The project is designed around a structured creative pipeline rather than a generic text-to-video generator:

`Brief -> ScriptPlan -> ShootingPlan -> Asset / Shot -> BeatMap -> EditPlan -> ResolutionDecision -> EDL -> Render -> ReviewReport`

The intended workflow is:

1. describe the video goal and provide references;
2. generate a structured script and shooting plan;
3. shoot or import original footage;
4. understand and index the available material;
5. select music and analyze its musical structure;
6. create an editorial plan;
7. resolve editorial requirements to concrete source footage;
8. build a deterministic EDL;
9. render and review;
10. revise through structured or natural-language editing instructions.

## Architecture first

The repository is governed by three reviewed Architecture Contracts under `docs/architecture/`.
External models, APIs, media engines and upstream projects contribute capabilities and implementation
ideas; they do not define the system's domain model.

Important ownership boundaries include:

- `ShotDetector` proposes boundaries; `ShotCatalog` owns final `Shot` identity;
- `UnderstandingService` describes footage; it does not change shot boundaries;
- `BeatMap` describes music facts; it does not decide cuts;
- `Director` creates `EditPlan`; it does not freeze source timestamps;
- `ShotResolver` chooses concrete footage; it does not rewrite director intent;
- `EDLBuilder` is the final timeline authority producer;
- `Renderer` executes EDL and has no creative authority.

## Current status

Current engineering baseline:

- Repository Bootstrap v0.1 complete;
- Python 3.12 + uv project layout;
- strict Ruff / mypy / pytest / Import Linter gates;
- GitHub Actions quality gate on `main`;
- FireRed-informed R0.1 Shot Detection capability complete;
- streaming FFmpeg RGB24 decode with bounded-memory TransNetV2 100/50 windows;
- lazy optional `transnetv2-pytorch==1.0.5` Torch runtime adapter;
- real Windows runtime and real-video probes passed;
- R0.2 Asset / Shot Identity complete;
- real ffprobe Asset ingest is validated with canonical SHA-256 identity data;
- real four-second Asset-to-Shots pipeline commits four contiguous Shot identities at `(0,960)`, `(960,1960)`, `(1960,2960)`, `(2960,4000)` ms;
- R0.3 footage understanding is the current phase;
- no AI provider integration, renderer, or end-user application is claimed complete yet.

See `docs/validation/R0.2_ASSET_SHOT_IDENTITY.md` for the R0.2 full-chain evidence and the boundary-semantics bug caught by the integration gate.

## Upstream engineering map

- **FireRed-OpenStoryline** — primary pipeline/media/render implementation reference;
- **soCzech/TransNetV2** — model inference-contract reference;
- **transnetv2-pytorch** — validated optional runtime compatibility target;
- **MoneyPrinterTurbo** — material-provider and operational-engineering reference;
- **CutClaw** — architecture/algorithm reference only; source code is not copied;
- **BeatSync Engine** — BeatMap/music-analysis reference.

See `docs/upstream/` for provenance and reuse policy.

## Development policy

Development proceeds directly on `main` with automated quality gates. A coherent change batch is
committed atomically, CI must return green, and only then does the next batch begin.

Do not bypass Architecture Contracts merely to accommodate a library or SDK. If implementation
evidence requires an architectural change, record an ADR under `docs/decisions/` first.

## License status

A repository-wide open-source license has not yet been selected. See `LICENSE_STATUS.md` and
`docs/upstream/UPSTREAM_POLICY.md`.

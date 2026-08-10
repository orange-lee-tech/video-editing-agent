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
- `UnderstandingService` owns derived `ShotAnalysis` revisions; providers only return proposals;
- `ShotIndex` is rebuildable retrieval infrastructure; it does not establish Resolver eligibility;
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
- real ffprobe Asset ingest and Asset-to-Shots identity chain validated;
- R0.3 provider-neutral footage-understanding foundation validated;
- deterministic Shot frame sampling and real PNG extraction validated on Windows;
- SHA-256 content-addressed local ArtifactStore implemented;
- provider-neutral VisualUnderstandingPort returns proposals only;
- UnderstandingService owns ShotAnalysis revisions and has a real-frame ownership probe;
- R0.4 local structured persistence complete with SQLite schema v1;
- exact revisioned Asset / Shot / ShotAnalysis records survive separate Python processes;
- AssetIngestService, ShotCatalog and UnderstandingService remain semantic owners while repositories
  persist their committed records;
- binary frame artifacts remain outside SQLite in the content-addressed ArtifactStore;
- R0.5 provider-neutral Shot Retrieval foundation complete;
- deterministic local lexical retrieval supports Latin and CJK matching, retrieval prefilters and exact
  analysis revision tracking;
- ShotIndex can be discarded and rebuilt from R0.4 persisted Shot + latest ShotAnalysis facts;
- R0.6 first concrete visual-provider integration complete;
- Gemini `gemini-3.5-flash-lite` is validated as the default cost-efficient visual-understanding adapter;
- a real Windows owner-chain probe sent three extracted PNG frames to Gemini and persisted
  `ShotAnalysis@1` with non-empty searchable semantics;
- the OpenAI Responses visual adapter remains available as an optional provider;
- no speech analysis, Director, Resolver, renderer, or end-user application is claimed complete yet.

See `docs/validation/` for full-chain evidence and integration bugs caught by automated probes.

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

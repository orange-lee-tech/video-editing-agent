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

The repository is governed by three reviewed Architecture Contracts:

- `docs/architecture/ARCHITECTURE_CONTRACT_V0.1.md` — domain model;
- `docs/architecture/ARCHITECTURE_CONTRACT_V0.1.1.md` — object relations and schema matrix;
- `docs/architecture/ARCHITECTURE_CONTRACT_V0.1.2.md` — module ownership and interface matrix.

Core rule:

> External models, APIs, media engines and upstream projects contribute capabilities and implementation ideas; they do not define the system's domain model.

Important ownership boundaries include:

- `ShotDetector` proposes boundaries; it does not create final `Shot` identity;
- `UnderstandingService` describes footage; it does not change shot boundaries;
- `BeatMap` describes music facts; it does not decide cuts;
- `Director` creates `EditPlan`; it does not freeze source timestamps;
- `ShotResolver` chooses concrete footage; it does not rewrite director intent;
- `EDLBuilder` is the final timeline authority producer;
- `Renderer` executes EDL and has no creative authority;
- review reports findings instead of silently mutating history.

## Current status

Current engineering baseline:

- Repository Bootstrap v0.1 complete;
- Python 3.12 + uv project layout;
- strict Ruff / mypy / pytest / Import Linter quality gates;
- architecture dependency rules encoded in `pyproject.toml`;
- GitHub Actions quality gate on `main`;
- FireRed-informed R0.1-A pure shot-boundary policy implemented independently;
- R0.1-B `ShotDetector` capability contract defined;
- no TransNetV2, Torch, FFmpeg runtime integration, AI provider integration, renderer, or end-user application has been claimed complete yet.

## Upstream engineering map

The project currently uses upstream work selectively:

- **FireRed-OpenStoryline** — primary pipeline/media/render implementation reference; selective reuse or independent reimplementation only after review;
- **MoneyPrinterTurbo** — material-provider and operational-engineering reference;
- **CutClaw** — architecture/algorithm reference only; source code is not copied;
- **BeatSync Engine** — BeatMap/music-analysis reference.

See `docs/upstream/` for provenance and reuse policy.

## Development policy

Development currently proceeds directly on `main` with automated quality gates.

Do not bypass Architecture Contracts merely to accommodate a library or SDK. If implementation evidence requires an architectural change, record an ADR under `docs/decisions/` first.

## License status

A repository-wide open-source license has not yet been selected. See `LICENSE_STATUS.md` and `docs/upstream/UPSTREAM_POLICY.md`.

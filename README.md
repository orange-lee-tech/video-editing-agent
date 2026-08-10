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
- GitHub Actions quality gate configured for `main`;
- FireRed-informed R0.1-A pure shot-boundary policy independently implemented;
- R0.1-B model-agnostic `ShotDetector` capability contract defined;
- R0.1-C1 policy-driven detector core separates model/media backends from boundary policy;
- R0.1-C2 streaming FFmpeg RGB24 frame source avoids whole-video raw-frame buffering;
- R0.1-C3 reproduces the published TransNetV2 100-frame / 50-output overlap contract as bounded-memory streaming windows and stitches only valid center predictions;
- R0.1-D1 adds a lazy optional `transnetv2-pytorch` predictor adapter, gap-free scene normalization and a composed scene-boundary backend without adding the heavy runtime to the base dependency lock;
- a one-command Windows verification gate is available at `scripts/verify.ps1`;
- a real package/weights runtime probe and real-video integration probe remain required before the TransNetV2 runtime is considered validated;
- no AI provider integration, renderer, or end-user application has been claimed complete yet.

## Upstream engineering map

The project currently uses upstream work selectively:

- **FireRed-OpenStoryline** — primary pipeline/media/render implementation reference; selective reuse or independent reimplementation only after review;
- **soCzech/TransNetV2** — authoritative model inference-contract reference;
- **transnetv2-pytorch** — optional runtime compatibility target under an explicit heavy-dependency boundary;
- **MoneyPrinterTurbo** — material-provider and operational-engineering reference;
- **CutClaw** — architecture/algorithm reference only; source code is not copied;
- **BeatSync Engine** — BeatMap/music-analysis reference.

See `docs/upstream/` for provenance and reuse policy.

## Development policy

Development currently proceeds directly on `main` with automated quality gates.

Do not bypass Architecture Contracts merely to accommodate a library or SDK. If implementation evidence requires an architectural change, record an ADR under `docs/decisions/` first.

## License status

A repository-wide open-source license has not yet been selected. See `LICENSE_STATUS.md` and `docs/upstream/UPSTREAM_POLICY.md`.

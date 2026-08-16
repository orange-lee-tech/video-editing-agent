# video-editing-agent

A **local-first, evidence-grounded AI Director + AI Video Editor** for user-supplied footage.

Initial product focus: Windows desktop, commercial short-form video, ecommerce/product advertising and Vlog, primarily under 60 seconds.

## Two core product functions

The project is not considered structurally complete until both of these are genuinely usable by an ordinary Windows user.

### 1. Planning

`reference/high-performing/commercial intent`
`→ Brief`
`→ persisted inspectable ScriptPlan`
`→ executable ShootingPlan`

The user should be able to obtain a practical shooting script/plan without editing repository files or constructing internal Domain objects.

### 2. Editing

`user-selected local footage + editing intent`
`→ media understanding/evidence`
`→ Director/EditPlan`
`→ Retrieval/Resolver`
`→ music/spatial/audio/subtitle/graphics/minimal transitions`
`→ canonical EDL`
`→ Renderer/Review`
`→ final MP4`

The automatic product path must not depend on a human hand-authoring EditPlan, ResolutionDecision or EDL.

Planning-only, Editing-only and Combined are all legitimate product paths. Combined uses Planning artifacts as optional exact-revision enrichment; Planning is not an activation license for Editing.

## Product boundary

This is **not** a generic text-to-video or autonomous stock-footage generator. Missing visual coverage is surfaced to the user instead of silently replaced with downloaded/generated imagery.

Final visual media comes from user-supplied local footage under the active Product Constitution. Provider/LLM output may propose/reason, but it does not own source timestamps, Domain authority or final timeline placement.

## Current state — do not duplicate stale snapshots here

The project is in **Stage A — Structural Construction**.

Current phase, exact Work Order, accepted code baseline, structural progress and Stage-A Product Gates are live in:

- [`docs/operations/CURRENT_CONTROL_STATE.md`](docs/operations/CURRENT_CONTROL_STATE.md)
- [`docs/roadmap/CURRENT_PHASE_STATUS.md`](docs/roadmap/CURRENT_PHASE_STATUS.md)
- [`docs/operations/CURRENT_WORK_ORDER.md`](docs/operations/CURRENT_WORK_ORDER.md)

The hard structural 100% contract is:

- [`docs/roadmap/STAGE_A_COMPLETION_GATE.md`](docs/roadmap/STAGE_A_COMPLETION_GATE.md)

Do not infer current progress from old commit notes, dated README prose, chat history or phase-specific source-pack snapshots.

Repository governance machine-checks the live-state pointers and rejects a false Stage-A 100% claim when either core Product Gate is not PASS.

## Durable product pipeline

```text
Brief
→ ScriptPlan
→ ShootingPlan
→ user-supplied footage
→ Asset / Shot understanding
→ speech + temporal evidence
→ Music / BeatMap
→ Director / EditPlan
→ Retrieval / Resolver
→ Spatial + Audio decisions
→ EDLBuilder
→ EDL
→ Renderer
→ Review / repair
→ final MP4
```

The parallel-entry architecture means Editing-only may begin from Brief/editorial intent + local footage without fabricated ScriptPlan/ShootingPlan.

## Authority and navigation

Start with [`docs/README.md`](docs/README.md).

Normative order:

1. [`docs/product/PRODUCT_CONSTITUTION_V1.0.md`](docs/product/PRODUCT_CONSTITUTION_V1.0.md) — highest product authority;
2. [`docs/architecture/ARCHITECTURE_CONTRACT_V0.2.md`](docs/architecture/ARCHITECTURE_CONTRACT_V0.2.md) — active architecture baseline;
3. [`docs/capabilities/`](docs/capabilities/) — active capability specifications;
4. [`docs/adr/`](docs/adr/) — active architecture decisions;
5. [`docs/roadmap/ROADMAP_V2.md`](docs/roadmap/ROADMAP_V2.md) — active construction map;
6. live control state / Work Order;
7. implementation/tests/provider behavior.

Retired documents live under [`docs/archive/`](docs/archive/) and are provenance only.

## Product rules that do not drift

- Commercial visual source material comes from user-supplied local files.
- Missing footage becomes unresolved/reshoot guidance, not autonomous stock/generated fallback.
- LLM/provider output is proposal/evidence, not Domain or timeline authority.
- Exact media time uses canonical rational `MediaTime` / `MediaTimeRange`.
- Resolver cannot invent source timestamps outside grounded evidence.
- BeatMap describes music; it does not own video cuts.
- EDL is the sole executable timeline authority.
- Renderer executes validated EDL; it does not create, repair or reposition editorial decisions.
- Engineering Probe and Product Probe evidence are different: synthetic fixtures may prove machinery, not real editing usefulness.
- Rights/provenance remain explicit; unknown rights are never silently promoted to verified rights.
- Stage-A UI may be visually plain, but must be practical, understandable, controllable and extensible.
- Normal user operation must not require repository-file editing or manual Domain/EDL construction.

## Repository map

- `.github/` — CI and reproducible probe/maintenance workflows.
- `docs/` — product/architecture/roadmap/ADR/validation/log/operations control plane.
- `docs/archive/` — retired documentation preserved for provenance only.
- `LICENSES/` — third-party license-text staging/retention policy, not the project license.
- `scripts/` — repository/developer helper scripts and historical standalone probes.
- `src/` — production Python package.
- `tests/` — unit/integration/contract tests and redistributable fixtures.
- `tools/` — developer/evidence/maintenance tooling; phase probes live under `tools/probes/`.

Local/private media, toolchains and probe outputs are intentionally gitignored and do not belong in GitHub.

## Development and verification

Python requirement: **3.12+**.

Typical setup:

```powershell
uv sync --frozen
```

Repository quality gate:

```powershell
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest
uv run lint-imports
uv build
git diff --check
```

Repository/control-plane health:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/maintain.ps1 doctor
```

At a new conversation, reobserve `origin/main` and use the live control-state/Work-Order path; do not reconstruct current work from chat memory alone.

## Upstream strategy

Strategic references currently include:

- FireRed-OpenStoryline — pipeline/media/render engineering reference;
- MoneyPrinterTurbo — provider/asset-supply operational ideas, never automatic visual-stock fallback;
- CutClaw — editing architecture/algorithm reference only; source is not copied;
- BeatSync Engine — beat/music synchronization reference;
- TransNetV2 — shot-detection inference reference.

Active upstream governance:

- [`docs/upstream/UPSTREAM_COMPONENTS_V2.md`](docs/upstream/UPSTREAM_COMPONENTS_V2.md)
- [`docs/upstream/UPSTREAM_POLICY_V2.md`](docs/upstream/UPSTREAM_POLICY_V2.md)

## License status

A repository-wide open-source license has not yet been selected. All rights are reserved by default until an explicit project license is adopted.

See [`LICENSE_STATUS.md`](LICENSE_STATUS.md) and [`LICENSES/README.md`](LICENSES/README.md).
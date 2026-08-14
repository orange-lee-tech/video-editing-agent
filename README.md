# video-editing-agent

A **local-first, evidence-grounded AI Director + AI Video Editor** for user-supplied footage.

Initial product focus: Windows desktop, commercial short-form video, ecommerce/product advertising and Vlog, primarily under 60 seconds.

The durable product pipeline is:

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

This is **not** a generic text-to-video or autonomous stock-footage generator. Missing visual coverage is surfaced to the user instead of silently replaced with downloaded/generated imagery.

## Current repository state

The repository is **HANDOFF_READY** as of 2026-08-14 and is intended to continue construction in the next ChatGPT conversation.

Completed/accepted milestones:

- R0.1–R0.6 — media/domain foundations, persistence, retrieval and provider seams;
- R0.7A — Architecture v0.2 migration foundation;
- R0.7B — Brief → ScriptPlan → ShootingPlan + commercial-authority baseline;
- R0.8 — real-footage speech, motion, temporal evidence, tracking and dense retrieval foundation;
- R0.9 — grounded Director → retrieval → CandidateWindow → Resolver/optimizer source-selection plan;
- R0.10A — local rights-aware music/BeatMap/audible-mix foundation;
- R0.10B — feature-ranked music windows, structured audio mix intent, decision→execution bridge and post-mix QC.

R0.10 is **not closed**. The next planned boundary is its real-music Product Probe → Human Gate → closure. R0.11+ has not started.

Live state is always recorded in:

- [`docs/roadmap/CURRENT_PHASE_STATUS.md`](docs/roadmap/CURRENT_PHASE_STATUS.md)
- [`docs/operations/CURRENT_WORK_ORDER.md`](docs/operations/CURRENT_WORK_ORDER.md)

New ChatGPT conversations should also read [`docs/operations/CHATGPT_GITHUB_CODEX_COLLABORATION.md`](docs/operations/CHATGPT_GITHUB_CODEX_COLLABORATION.md).

## Authority and navigation

Start with [`docs/README.md`](docs/README.md).

Normative order:

1. [`docs/product/PRODUCT_CONSTITUTION_V1.0.md`](docs/product/PRODUCT_CONSTITUTION_V1.0.md) — highest product authority;
2. [`docs/architecture/ARCHITECTURE_CONTRACT_V0.2.md`](docs/architecture/ARCHITECTURE_CONTRACT_V0.2.md) — active architecture baseline, accepted by A0;
3. [`docs/capabilities/`](docs/capabilities/) — active capability specifications;
4. [`docs/adr/`](docs/adr/) — active architecture decisions;
5. [`docs/roadmap/ROADMAP_V2.md`](docs/roadmap/ROADMAP_V2.md) — active construction map;
6. implementation/tests/provider behavior.

The explicit planning-baseline acceptance record is [`docs/roadmap/A0_PLANNING_BASELINE_ACCEPTANCE.md`](docs/roadmap/A0_PLANNING_BASELINE_ACCEPTANCE.md).

Retired documents are centralized under [`docs/archive/`](docs/archive/). They are provenance only and never override the active authority chain.

## Product rules that do not drift

- Commercial visual source material comes from user-supplied local files.
- Missing footage becomes unresolved/reshoot guidance, not autonomous stock/generated fallback.
- LLM/provider output is proposal/evidence, not Domain or timeline authority.
- Exact media time uses canonical rational `MediaTime` / `MediaTimeRange`.
- Resolver cannot invent source timestamps outside grounded evidence.
- BeatMap describes music; it does not own video cuts.
- EDL is the sole executable timeline authority.
- Renderer/execution code performs decisions; it does not create hidden editorial decisions.
- Engineering Probe and Product Probe evidence are different: synthetic fixtures may prove machinery, not real editing usefulness.
- Rights/provenance remain explicit; unknown rights are never silently promoted to verified rights.

## Repository map

- `.github/` — CI and reproducible probe/maintenance workflows.
- `docs/` — active product/architecture/roadmap/ADR/validation/log/operations documentation.
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

At a new conversation, reobserve `origin/main` before activating the handoff-ready work order. Do not reconstruct active work from chat memory alone.

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

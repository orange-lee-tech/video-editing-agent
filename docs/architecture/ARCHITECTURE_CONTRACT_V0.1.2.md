# Architecture Contract v0.1.2 — Module Ownership & Interface Matrix

Status: Pre-repository architecture baseline, materialized by Repository Bootstrap v0.1.

## Ownership rule

Ownership means semantic creation and revision authority, not storage location.

Storage may persist an object but does not own its business meaning.

## Layers

- Domain — entities, value objects, invariants and deterministic validation.
- Application — use cases, workflow orchestration, stale propagation and ports.
- Capabilities — planning, media analysis, music analysis, editing, review and render logic.
- Infrastructure — storage, external models/APIs, FFmpeg and indexes.
- Adapters — CLI/API/Desktop/MCP entry points.

Domain must not know OpenAI, Gemini, Claude, Pexels, FFmpeg, MoviePy, MCP, HTTP, SQLite or filesystem paths.

## Ownership matrix

- BriefService owns Brief.
- ScriptPlanner owns ScriptPlan.
- ShootingPlanner owns ShootingPlan and ShotRequirement.
- AssetIngestService owns Asset creation.
- ShotDetector proposes boundaries; ShotCatalog commits Shot identity.
- UnderstandingService owns ShotAnalysis revisions but cannot change Shot identity.
- BeatAnalysisService owns BeatMap.
- Director owns EditPlan/EditSlot.
- ShotResolver owns ResolutionDecision.
- EDLBuilder is the only EDL producer and timeline authority producer.
- Renderer owns RenderArtifact but cannot change EDL.
- ReviewService owns ReviewReport.
- AssetCatalogService owns AssetCatalogSnapshot.
- Repositories persist but do not make semantic decisions.

## Agent proposal pattern

All generative AI follows:

`Agent -> Proposal DTO -> Schema Validation -> Deterministic Validation -> Domain Owner Commit`

Agents own no Domain Entity and never write the domain database directly.

## Key interfaces

### MaterialProvider
`search(MaterialQuery) -> RemoteMaterialCandidate[]`
`fetch(RemoteMaterialCandidate) -> MediaSource`

Providers do not create Asset entities.

### ShotDetector
`detect(asset_ref) -> ShotBoundaryProposal[]`

It answers only where shot boundaries are.

### UnderstandingService
`analyze(shot_ref, profile) -> ShotAnalysis`

It describes what exists in the shot and never changes shot boundaries.

### BeatAnalysisService
`analyze(audio_asset_ref) -> BeatMap`

It outputs music facts, never cut decisions.

### Director
Creative context -> EditPlan.
It may define purpose, pacing and desired visuals but not exact source timestamps.

### ShotResolver
EditSlot + catalog/index/context -> ResolutionDecision.
It may choose a Shot/source window but may not alter Director intent.

### EDLBuilder
EditPlan + ResolutionDecision + optional BeatMap/voice/subtitle artifacts -> EDL.
It owns final source mapping and timeline placement.

### Renderer
`render(edl_ref, output_spec) -> RenderArtifact`

Renderer executes; it does not creatively repair invalid EDL.

### ReviewService
Reviews candidates, EDL or rendered output and returns ReviewReport.
It evaluates but does not mutate the target.

## Dependency direction

`Adapters -> Application -> Domain`

Infrastructure implements ports defined inward of itself.

Forbidden examples:

- Domain -> LLM
- Domain -> FFmpeg
- Director -> Pexels
- Renderer -> ShotResolver
- BeatAnalysis -> EditPlan
- Provider -> EDL
- UI -> database

## Incremental recomputation

Only affected downstream modules recompute.

Examples:

- subtitle wording change does not re-detect or re-understand footage;
- BGM replacement recomputes BeatMap and beat-sensitive downstream planning, not footage analysis;
- new material analyzes only new assets and may rerun unresolved/weak slots.

## Upstream map

FireRed:
- pipeline/node concepts -> application/workflow
- shot detection -> media/shot_detection
- clip understanding -> media/understanding, rewritten
- BGM selection -> music/selection
- beat analysis -> music/beat_analysis
- timeline planning -> editing/edl, rewritten
- rendering -> render/backends, selectively reusable

MoneyPrinterTurbo:
- provider operations -> providers/material
- task orchestration architecture -> not inherited

CutClaw:
- design ideas map to Director, ShotResolver and ReviewService
- source code is not copied

BeatSync Engine:
- music analysis ideas map to music/beat_analysis
- no final timeline ownership

## Repository bootstrap rule

The first repository remains a single local Python application with strict internal module boundaries.
It deliberately does not introduce microservices, Kubernetes, multi-tenancy, distributed storage, plugin marketplaces or a custom timeline DSL.

## Final invariants

1. Only the domain owner creates a new semantic revision.
2. Storage has no domain decision authority.
3. Pipeline has no creative authority.
4. Agents own no domain entities.
5. Providers do not produce formal Assets.
6. ShotDetector decides boundaries only.
7. Understanding does not change Shot identity.
8. BeatAnalysis does not produce editing decisions.
9. Director does not freeze source timestamps.
10. Resolver does not rewrite Director intent.
11. EDLBuilder is the only timeline authority producer.
12. Renderer does not modify EDL.
13. Review does not mutate its target.
14. External inputs are validated before Domain commit.
15. AI outputs are proposals until validated and committed.
16. Remote media must pass through Asset Ingest.
17. Every edited media segment traces back to an Asset.
18. EDL decisions trace back to EditPlan/ResolutionDecision.
19. Recompute only affected downstream work.
20. External SDK convenience never justifies reversing the dependency direction.

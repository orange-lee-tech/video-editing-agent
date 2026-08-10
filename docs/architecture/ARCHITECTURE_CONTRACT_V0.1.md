# Architecture Contract v0.1 — Domain Model

Status: Repository Bootstrap baseline.

## Core workflow

`Brief -> ScriptPlan -> ShootingPlan -> Footage -> Asset Understanding -> Music -> BeatMap -> EditPlan -> EDL -> Render -> ReviewReport`

Core durable domain objects:

- Brief
- ScriptPlan
- ShootingPlan
- Asset
- Shot
- BeatMap
- EditPlan
- EDL
- ReviewReport

## Domain principles

- Domain objects are more stable than any LLM, provider, framework, renderer, or open-source project.
- Agent, MCP, FFmpeg, MoviePy, Pexels, FireRed, MoneyPrinterTurbo, CutClaw and BeatSync Engine are not domain objects.
- Cross-object references target exact revisions.
- Asset identity is immutable with respect to source bytes.
- Asset and Shot are distinct: one source Asset may contain many Shots.
- BeatMap describes music facts; it does not own edit decisions.
- EditPlan describes editorial intent; EDL is the deterministic execution authority.
- Renderer executes EDL and has no creative authority.
- Review reports findings and never silently mutates its target.

## Core semantic boundaries

- Brief: what video should be made.
- ScriptPlan: how the story should be told.
- ShootingPlan: what footage should be captured.
- Asset: a real media source.
- Shot: a usable temporal interval inside an Asset.
- BeatMap: objective/derived music structure.
- EditPlan: director-level edit intent.
- EDL: exact executable source and timeline decisions.
- ReviewReport: quality assessment of a specific revision.

## Dependency topology

`Brief -> ScriptPlan -> ShootingPlan`

`Asset -> Shot`

`Audio Asset -> BeatMap`

`ScriptPlan + ShootingPlan + Asset/Shot + optional BeatMap -> EditPlan -> EDL -> Render -> ReviewReport`

Shot does not derive from ShootingPlan. A resolver connects requirements and real footage during editing.

## Global invariants

1. Natural-language Agent text is never the machine protocol.
2. Domain identities are IDs, not filesystem paths.
3. Renderer has no creative authority.
4. BeatMap has no editing authority.
5. Shot has no narrative authority.
6. ScriptPlan does not bind concrete source media.
7. ShootingPlan does not bind final selected footage.
8. EditPlan does not own exact source timestamps.
9. EDL contains execution decisions, not creative reasoning.
10. Review never silently edits history.

## Upstream engineering map

### FireRed-OpenStoryline
Use as primary pipeline and selective implementation reference.
Keep node/pipeline ideas, shot-detection experience, BGM ideas and rendering experience.
Rewrite its BaseNode coupling, footage-first product causality, understanding pipeline, media search abstraction, timeline contract and persistence ownership.

### MoneyPrinterTurbo
Use as material-provider and operational-engineering reference.
Retain provider operational lessons such as API-key rotation, caching, provenance, retries and encoder fallback.
Do not inherit its large procedural task orchestrator.

### CutClaw
Engineering reference only.
Independently reimplement hierarchical media understanding and Plan -> Resolve -> Review ideas.
Do not copy code.

### BeatSync Engine
BeatMap algorithm reference only.
Music analysis signals do not own final timeline decisions.

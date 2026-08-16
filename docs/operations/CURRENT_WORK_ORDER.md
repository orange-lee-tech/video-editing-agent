# Current Work Order

**ID:** `R0.12-STAGE-A-PRODUCT-IO-CONTRACT-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Stage-A Product I/O contract before remaining productization  
**Mode:** PRODUCT + ARCHITECTURE CONTRACT; code-light  
**Accepted production-code baseline:** `500c8563e3686a5aaef055ffb5301553aa999fd9`  
**Activated:** 2026-08-16  
**Codex release:** NO

## Why this work exists

The Preview backend family decision is closed by `ADR-010_GSTREAMER_PRIMARY_PREVIEW_BACKEND.md`.

The project must now return from player benchmarking to the real Stage-A product problem:

> What can an ordinary Windows user put into the product, what durable artifacts/results come out, and which owned boundary is responsible for every conversion between those two sides?

The two product cores remain:

1. high-performing/reference/commercial intent → ScriptPlan + ShootingPlan;
2. user-selected footage + editing intent → automatic editing chain → final MP4.

The existing backend foundations are substantial, but Stage-A 100% is still blocked because ordinary-user product entry/exit semantics are not yet frozen end to end.

## Previous Work Order result

`R0.12-PREVIEW-BACKEND-BENCHMARK-001` — **PASS / CLOSED**.

Accepted outcome:

- GStreamer selected as primary Stage-A Preview backend in ADR-010;
- libVLC retained as a validated alternative adapter family, not default dual-bundled fallback;
- libmpv hard-gate excluded for Stage A because an auditable LGPL Windows D3D11 distribution path would require disproportionate custom build/dependency/license maintenance;
- PreviewBackend remains playback-only; EDL remains sole exact timeline authority;
- no production Preview implementation was smuggled into the benchmark.

## Objective

Freeze one canonical Stage-A Product I/O Contract covering Planning-only, Editing-only and Combined without choosing the desktop/frontend framework.

The contract must make the normal product path possible without:

- editing repository files;
- constructing Domain entities by hand;
- hand-authoring EditPlan, ResolutionDecision or EDL;
- fabricating ScriptPlan/ShootingPlan for Editing-only;
- treating Planning output as an Editing activation license.

## Required contract surface

### 1. Project/session entry

Define ordinary-user semantics for:

- create project;
- open existing project;
- project-owned working/runtime data vs user-owned original media;
- recover/retry without overwriting user originals.

### 2. Planning input

Define product-facing input semantics for:

- goal/commercial intent;
- reference/high-performing target;
- supported local reference media;
- supported Reference URL as an acquisition request, not direct Domain media authority;
- commercial/product constraints.

Planning output must remain:

`Brief → persisted inspectable ScriptPlan → usable ShootingPlan`

### 3. Editing input

Define product-facing input semantics for:

- one or more local footage files/folders;
- lightweight Brief/editorial intent;
- optional exact-revision Planning artifacts when present;
- output destination;
- audio/voice intent needed by downstream ownership.

Editing-only must remain independently activatable.

### 4. Combined

Combined means Planning artifacts enrich the same Editing Core after the user supplies footage. It must not fork a second editing architecture.

### 5. Reference acquisition boundary

Freeze the semantic route:

`supported URL → acquisition adapter → controlled local reference file → REFERENCE_ANALYSIS_ONLY → existing analysis/planning`

Unsupported/login/DRM/auth-required acquisition must fail closed with understandable guidance.

This Work Order defines the contract only; provider/platform implementation remains later bounded work.

### 6. Music acquisition boundary

Freeze that public/provider music search is insufficient by itself. A usable provider path must be:

`search/discovery → rights-aware selection → acquisition → controlled local governed Asset → existing Music/BeatMap/audio chain`

The contract must preserve provenance/rights metadata and cannot silently convert unknown-rights URLs into output-eligible music.

### 7. Output/result contract

Define stable user-visible results for:

- Planning: ScriptPlan + ShootingPlan;
- Editing: final MP4 plus durable project artifacts needed for resume/diagnostics;
- Combined: both sets where applicable;
- progress/failure/retry state;
- output location discoverability.

Internal caches/provider DTOs are not promoted into user-facing Domain authority merely because a UI needs to display progress.

## Frozen downstream product gaps

This contract must explicitly prepare, but not prematurely implement, the next bounded work:

1. **P0 mixed source-audio semantics** at source-selection/source-range granularity;
2. speech protection / VoiceTreatment policy;
3. final audible-lane QC for non-silent intent;
4. Reference URL acquisition;
5. rights-aware public music provider + acquisition;
6. optional Planning reference-style evidence backflow;
7. remaining bounded R0.12 productization and ordinary-user integration.

## Authority constraints

- `Brief` remains the common intent root.
- ScriptPlan owns narrative planning, not source timestamps.
- ShootingPlan owns capture requirements, not final source selection.
- Director owns EditPlan editorial intent, not exact source/time/EDL coordinates.
- Resolver grounds source windows.
- EDL is sole exact executable timeline authority.
- Renderer executes EDL and does not repair it.
- Preview is playback-only.
- reference media defaults to analysis-only.
- commercial output visual material remains user-supplied local media.
- public remote visual replacement footage remains forbidden by the Product Constitution.
- original user media is never overwritten.

## Tool routing

### ChatGPT + GitHub

Primary for this contract:

- inspect existing product/application/domain/port boundaries;
- freeze product-visible input/output semantics;
- identify exact implementation gaps without redesigning accepted owners;
- write/synchronize the canonical contract and governance state.

### User

No Human Gate is expected for ordinary engineering naming/plumbing. Ask only if a genuine product-policy choice appears that cannot be derived from the two core goals and existing Constitution.

### Codex

**NOT RELEASED for the contract itself.**

The first expected post-contract Codex-worthy batch is mixed source-audio + speech protection + audible QC because it crosses Domain/Application/EDL/Renderer tests and benefits from a bounded multi-file edit/test/repair loop.

## Exit gate

PASS only when:

- one canonical Product I/O Contract is durable in the repository;
- all three workflow entries map to existing owned application/domain boundaries without fabricated artifacts;
- input ownership and output ownership are explicit;
- Reference URL and public-music remote inputs terminate in controlled local governed assets before entering existing analysis/editing chains;
- mixed-audio/voice/audible-QC ownership is located precisely enough to issue the next implementation Work Order;
- desktop/frontend framework remains deliberately undecided;
- structural progress remains 90% unless actual ordinary-user structural closure changes.

## Immediate next action

1. audit existing project/application entry and durable output boundaries against this Work Order;
2. write the canonical Stage-A Product I/O Contract;
3. identify exact mixed source-audio + speech-protection + audible-QC implementation surface;
4. close this contract Work Order;
5. issue one bounded Codex implementation Work Order for that audio/QC batch.

# Current Work Order

**ID:** `R0.12-EDLBUILDER-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — deterministic EDL assembly  
**Owner/writer:** Codex

## Objective

Create the deterministic EDLBuilder boundary that turns already-approved edit/resolution/spatial/audio decisions into the canonical EDL v0.2 without redoing their creative policy or letting Renderer invent timeline decisions.

## Read

1. `src/video_editing_agent/domain/edit/resolution.py`
2. `src/video_editing_agent/domain/shot/model.py`
3. `src/video_editing_agent/domain/edl/`
4. `docs/capabilities/CAP-08_EDL_RENDER_PREVIEW_SUBTITLE.md`

Use foreman trigger `location` to locate exact existing R0.10/R0.11 execution-decision types only when needed. Use `architecture` only for a genuine ownership ambiguity.

## Required delta

- Add an application-level `EDLBuilder` or equivalent deterministic assembly service; do not move creative policy into the EDL domain model.
- Consume ordered `EditPlan`/slot intent plus `ResolutionDecision`/`ResolvedSelection` outputs and a deterministic Shot lookup sufficient to obtain authoritative `asset_ref` and validate selected source ranges.
- Allocate exact timeline placement from approved ordered selections. With no typed playback-rate mapping yet, preserve source duration exactly rather than stretching material implicitly.
- Fail closed with structured diagnostics on unresolved/missing/ambiguous slot coverage, duplicate/conflicting coverage, missing Shot/Asset mapping, illegal selected ranges or other locally provable build blockers.
- Preserve deterministic ordering independent of incidental input collection order.
- Attach/translate already-approved spatial/audio execution data into the EDL automation surface only where the existing R0.10/R0.11 contracts make the mapping deterministic. Never rescore, reframe, remix or guess absent decisions.
- Produce an EDL that passes canonical validation and deterministic codec round-trip.
- Add focused deterministic tests plus one Engineering Probe showing approved grounded decisions assemble into a stable executable EDL and invalid/incomplete inputs fail with structured findings.

## Hard boundaries

- EDLBuilder owns exact timeline assembly, not source selection quality.
- Resolver owns grounded source choices; SpatialComposer owns framing decisions; AudioEditorial owns audio policy.
- EDL remains the sole exact executable timeline authority after assembly.
- Renderer executes the built EDL later and must not repair/reposition it.
- No LLM/provider-generated timing or shell fragments.
- No new third-party dependency unless a concrete blocker triggers the external route.
- Do not implement Renderer, Subtitle, Graphics, Preview, Proxy/cache or UI in this batch.

## Verification

Run focused EDLBuilder tests and Engineering Probe, then the repository full Quality Gate. Preserve import contracts and `git diff --check`.

## Stop gate

Stop after deterministic decision-to-EDL assembly is green, committed/pushed, and the working tree is clean. Do not continue into Renderer or other R0.12 deliverables.

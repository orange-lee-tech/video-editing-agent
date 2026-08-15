# Current Work Order

**ID:** `R0.12-EDL-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — EDL v0.2 foundation  
**Owner/writer:** Codex

## Objective

Upgrade the canonical EDL from the current thin segment model into the deterministic typed foundation required by R0.12, without letting Renderer or any model invent timeline decisions.

## Read

1. `src/video_editing_agent/domain/edl/model.py`
2. `docs/capabilities/CAP-08_EDL_RENDER_PREVIEW_SUBTITLE.md`

Use foreman trigger `location` if existing EDL consumers/persistence/tests are not obvious. Use trigger `architecture` only if ownership semantics are genuinely ambiguous.

## Required delta

- Preserve canonical rational `MediaTime` / `MediaTimeRange` semantics and existing source/timeline authority.
- Replace free-form track semantics with a typed deterministic multi-track foundation covering the CAP-08 track families needed now, while preserving compatibility for existing persisted/constructed EDLs where practical.
- Make track ordering/composition semantics deterministic and explicit rather than dependent on incidental tuple/string order.
- Add a deterministic EDL validation surface with structured diagnostics for the invariants that can be proven locally at this layer, including unique identities, legal ranges/mappings, track validity and illegal same-track overlap.
- Keep existing spatial/audio decision references compatible; do not duplicate SpatialComposer or AudioEditorial authority inside EDL.
- Preserve backward compatibility deliberately. If existing persistence/serialization or consumers require a migration/read adapter, implement the smallest safe compatibility path rather than silently breaking old revisions.
- Add focused tests and one small deterministic Engineering Probe/fixture demonstrating a known multi-track EDL validates and a deliberately invalid timeline fails with structured findings.

## Hard boundaries

- EDL is the sole exact executable timeline authority.
- Renderer executes EDL; it does not repair or reposition it.
- No LLM/provider shell fragments or timeline authority.
- No new third-party dependency unless a real blocker triggers the external/dependency route.
- Do not implement FFmpeg Renderer productization, subtitles, graphics, preview backend, proxy/cache or UI in this batch.
- Do not speculatively redesign unrelated R0.7–R0.11 domain entities.

## Verification

Run focused EDL tests/probe, then the repository full Quality Gate. Preserve import contracts and `git diff --check`.

## Stop gate

Stop after the typed EDL v0.2 foundation + deterministic validator are green, committed/pushed, and the working tree is clean. Do not continue into Renderer or other R0.12 deliverables.
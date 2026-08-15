# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** ACTIVE — `R0.12-EDL-001`  
**Updated:** 2026-08-15

## Closed

- R0.7A — Architecture v0.2 Migration Foundation.
- R0.7B — Pre-production Planning + Commercial Skill Foundation.
- R0.8 — Media Evidence Foundation.
- R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer.
- R0.10 — Music Selection + BeatMap + Audio Editorial.
- R0.11 — Spatial Composition / Auto Reframe (`PASS_WITH_MINOR_DEFECT`).

## Control-plane activation complete

Accepted control-plane baseline:

`1012f239aa95899e914ba6091c3b825dfc6302fe` — `feat: route Codex context by trigger`.

Verified:

- remote `ci/quality-gate-diagnostic` success;
- foreman v2 default output is L0-only;
- six deterministic trigger classes are available;
- selected triggers expose only the selected route;
- `CODEX_TOOLBOX.md` is a compact route index, not default model context;
- malformed/mismatched state still fails closed;
- dirty Git state remains visible;
- reported local Quality Gate: 494 tests plus Ruff, mypy, import contracts, build and diff check green.

The control-plane work is complete enough for real product use. Further refinements should be driven by observed construction friction, not by abstract prompt minimization.

## Active R0.12 frontier

Start with EDL v0.2 because CAP-08 keeps EDL as the sole exact executable timeline authority beneath approved decisions and above deterministic execution.

Current implementation already has rational `source_range` / `timeline_range` in `EDLSegment`, but the model remains thin and does not yet provide the typed multi-track and deterministic validation foundation required for Renderer/Subtitle/Preview/Proxy productization.

Active work order: `R0.12-EDL-001`.

Do not begin Renderer, Subtitle, Preview or Proxy feature construction in the same batch.
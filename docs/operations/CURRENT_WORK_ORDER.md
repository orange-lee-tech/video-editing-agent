# Current Work Order

**ID:** `R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Stage-A ordinary-user Product Gate closure  
**Mode:** LOCAL UX CANDIDATE FINALIZATION → EDITING INTEGRATION REPAIR → PRODUCT/HUMAN GATE  
**Accepted production-code baseline:** `af5865df14b9f1cceaa9e6c1fe4dadf14cc60058`  
**Activated:** 2026-08-18  
**Corrected after integration audit:** 2026-08-19  
**Codex release:** CLOSED — execution quota exhausted; preserve existing local candidate

## Objective

Close Stage A only through real ordinary-user evidence for the two frozen core product functions.

Planning Product/Human Gate is already **PASS**.

Editing has validated subsystems and a working ordinary orchestration skeleton, but a 2026-08-19 static audit found that the ordinary ProductFlow still omits part of the editing-expression floor explicitly required by the frozen Stage-A completion/product-I/O contracts. Therefore the next gate-closing real Editing run is **blocked until one bounded integration repair is accepted**.

This correction keeps structural progress at 90%, does not reopen accepted subsystem closures, and does not authorize a product-core redesign.

## Frozen architecture

The following remain unchanged:

- Planning-only: `Brief → ScriptPlan → ShootingPlan`;
- Editing-only: `Brief/editorial intent + user local footage → Editing Core`;
- Combined: exact Planning revisions optionally enrich the same Editing Core;
- reference-only media remains Resolver-ineligible;
- final commercial visuals come from user-selected local footage;
- source-time grounding remains Resolver-owned;
- Music/Audio/Spatial/Subtitle/Graphics/transition owners produce approved decisions/artifacts upstream of EDL assembly;
- EDLBuilder assembles but does not invent editorial decisions;
- canonical EDL remains the sole exact timeline authority;
- Renderer executes only;
- Review classifies/routes only;
- originals remain protected;
- no silent provider switching or fabricated replacement media.

## Gate state

### Planning Product Gate

**PASS**.

Durable evidence:

`docs/validation/R0.12_STAGE_A_PLANNING_PRODUCT_GATE.md`

The ordinary Windows launcher completed a real Planning run and produced persisted ScriptPlan/ShootingPlan revisions. The user judged both acceptable with no blocking issue.

### Editing Product Gate

**INTEGRATION GAP OPEN / PRODUCT PROBE NOT GATE-READY / HUMAN GATE OPEN**.

Real Windows probes already crossed input validation, local-media understanding and Director boundaries and exposed/fixed:

1. Gemini model/API-contract migration defects;
2. exact `MediaTime` provider-presentation misuse;
3. missing bounded visual transient retry wiring;
4. malformed DeepSeek Director exact-duration proposals;
5. provider-aware Gemini retry-delay handling.

Accepted remote production-code baseline:

`af5865df14b9f1cceaa9e6c1fe4dadf14cc60058`

Exact-head CI:

`32145822611` — `ci/quality-gate-diagnostic = success`.

The latest real Editing attempt then reached `ingest_understanding` and hit a genuine Gemini HTTP 429 after legitimate requests. That provider condition remains explicit and never authorizes silent fallback.

## 2026-08-19 integration audit correction — hard gate

The provider quota pause was used not only for UI work but also for a wider static audit of the actual ordinary Editing composition.

Two already-accepted contracts are unambiguous:

### Stage-A completion gate

The gate-closing route includes:

```text
understanding / Director / grounded Resolver
→ music/rhythm + spatial/audio + subtitle/graphics/minimal transitions
→ canonical EDL
→ Renderer / Review
→ final MP4
```

### Stage-A Product I/O contract

The canonical Editing-only chain includes:

```text
Director
→ Retrieval / Resolver
→ Music / Audio / Spatial / Subtitle / Graphics decisions
→ EDLBuilder
→ canonical EDL
→ Renderer
→ Review/repair
```

### Current ordinary ProductFlow evidence

At the audited remote `main`:

- `EditingProductCapabilities` exposes media probe, shot detector/options, visual understanding, Director, Renderer and rendered-media QC;
- `prepare_media()` performs local ingest, Shot detection and visual understanding;
- `generate_edit_plan()` uses the Director;
- `resolve_edit_plan()` uses the grounded Resolver;
- `build_edl()` calls `DeterministicEDLBuilder` with ResolutionDecision plus `build_conservative_source_audio_mix(...)`;
- it does **not** supply the already-supported `spatial_decisions` or `music_selection` seams to `EDLBuildRequest`;
- the ordinary ProductFlow does not yet wire the required structured Subtitle/Graphics/minimal-transition expression floor.

The EDL layer already proves that these concerns belong upstream of Renderer: `EDLBuildRequest` accepts approved spatial/music/audio decisions, EDL owns subtitle cues/track families, and Renderer consumes canonical EDL.

### Decision

**Do not run or accept a Stage-A gate-closing Editing Product Probe on the abbreviated route.**

A successfully rendered plain-cut/source-audio MP4 would prove useful machinery, but it would not satisfy the already-frozen Stage-A Product Gate.

Durable incident record:

`docs/logs/INCIDENT_LEDGER.md` — `R0.12 Stage-A ordinary Editing integration gap — OPEN`.

## Work boundary A — finalize the preserved local UX candidate

The previously authorized UX stabilization wave has already been implemented locally in the user's Windows working tree. Codex quota expired before final smoke/commit/push.

Local candidate includes the product-adapter/UI/test work for:

- responsive Tk background execution;
- scroll/export;
- UI-aligned localization;
- ETA/status;
- multi-select Media Files only in ordinary Editing UI;
- first-run placeholders;
- form/API profiles with Windows-protected secrets;
- bounded share-text URL extraction;
- no-facts planning repair regressions;
- provider/quota UX;
- real startup Splash.

Observed full local gate **before the final Splash micro-edits**:

- Ruff / mypy / import-linter / build / repo-doctor: PASS;
- pytest: `713 passed`;
- launcher/Tk smoke: PASS;
- manual UI smoke: PASS for all listed features except the original invisible Splash.

Splash was then repaired to perform a real Tk repaint and given a dependency-free Canvas pixel mark. The user confirmed the startup icon is visible.

### Required completion steps

1. **Do not pull/reset/stash over the current uncommitted Windows work.**
2. Rerun the full local Quality Gate after the final Splash edits.
3. Commit the current local product-adapter/UI/test candidate on its existing local base.
4. Fetch `origin/main` and rebase that local code commit onto the latest docs-only remote main.
5. Rerun required checks at rebased HEAD.
6. Push.
7. ChatGPT reobserves exact commit/diff/CI and accepts or rejects it.
8. Only after acceptance update `accepted_code_baseline`.

No further Codex execution is authorized for this candidate; the previous work must be preserved, not recreated.

## Work boundary B — one bounded Stage-A Editing integration repair

After boundary A is accepted, implement **one coherent integration wave** before the next real Editing gate.

### B1. Reuse R0.10 Music / Audio Editorial ownership

Integrate the already-owned MusicSelection / BeatMap / Audio Editorial chain into the ordinary Editing route rather than hardcoding BGM or audio behavior in ProductFlow/Renderer.

Requirements:

- rights/provenance boundary remains enforced;
- current local/user-rights-attested music remains a legitimate safe baseline where public acquisition is unavailable;
- approved `MusicSelectionDecision` / `AudioMixDecision` feed EDL assembly;
- source-audio treatment remains explicit and grounded to selected ranges;
- Renderer does not independently choose music/mix.

### B2. Reuse R0.11 Spatial / Auto Reframe ownership

For resolved selections, integrate the existing SpatialComposer/ReframeDecision path before EDL assembly.

Requirements:

- spatial evidence provider observes only;
- SpatialComposer owns executable transform decision;
- approved ReframeDecision maps into EDL spatial automation;
- Renderer merely executes the canonical transform;
- manual/user locks remain higher authority where represented.

### B3. Structured Subtitle integration

Use the existing subtitle semantic/builder path and canonical EDL subtitle cues rather than rendering raw ASR text directly.

Requirements:

- subtitle timing/content is structured before Renderer;
- EDL owns exact cue placement;
- existing FFmpeg/ASS execution remains deterministic;
- no Renderer-side editorial subtitle rewriting.

### B4. Minimum Graphics and transition floor

The Stage-A completion gate explicitly requires basic deterministic title/CTA/price-card graphics and a minimal transition vocabulary.

The current EDL already defines a `GRAPHICS` track family but the audited Renderer supports VIDEO/SOURCE_AUDIO/BGM/SUBTITLE only, and the current EDL model has no explicit transition semantics.

Therefore this sub-boundary must first define **small typed semantics** sufficient for Stage A, then execute them deterministically.

Allowed direction:

- a bounded title/CTA/price-card graphics decision/artifact seam;
- a very small deterministic transition vocabulary such as CUT plus only the minimum approved non-cut transition(s) supported by the canonical model/executor;
- explicit EDL representation and validation;
- Renderer backend compilation only after semantics exist.

Forbidden direction:

- monolithic Effects Engine;
- freeform FFmpeg filter strings as Domain truth;
- LLM-generated backend syntax as authority;
- broad motion-graphics/NLE feature creep.

### B5. Integration proof

Tests must prove **decision → canonical EDL → execution** alignment, not merely existence of independent subsystem objects.

Minimum expectations:

- change the approved Music/Audio decision and observe corresponding EDL/execution change;
- change the approved ReframeDecision and observe corresponding EDL/execution change;
- subtitle cues exist canonically and render through the EDL path;
- graphics/transition typed decisions alter canonical EDL/execution deterministically;
- no output path bypasses EDL;
- existing Resolver/source protection/regressions remain green;
- full Quality Gate passes.

If a required Stage-A expression cannot be represented without a larger redesign, stop and bring the exact gap to the user rather than silently weakening the gate.

## Work boundary C — real Editing Product/Human Gate

Only after A+B are accepted and provider quota/runtime are usable:

1. synchronize accepted `main` to Windows;
2. launch the ordinary product surface;
3. select real footage through the single multi-select local-file mechanism;
4. record source SHA-256 hashes before the run;
5. keep Combined unchecked for the Editing-only proof;
6. execute actual ingest / shot detection / understanding / Director / grounded Resolver;
7. execute the Stage-A Music/Audio/Spatial/Subtitle/Graphics/minimal-transition floor through canonical EDL;
8. Renderer produces a real final MP4;
9. Review must PASS under the real route;
10. verify source hashes remain unchanged;
11. the user watches the MP4 and completes the ordinary Editing Human Gate.

## Parallel productization requests — documented, not mixed into boundary B

The user has also authorized broader productization work. Durable plans are now recorded in:

- `docs/product/DESKTOP_UI_DESIGN_SYSTEM_V0.1.md`;
- `docs/architecture/PROVIDER_NEUTRAL_PRODUCT_BINDING_PLAN.md`;
- `docs/operations/WINDOWS_DESKTOP_PACKAGING_READINESS.md`;
- `docs/roadmap/PRODUCT_RED_BLACK_BOARD.md`;
- `docs/logs/PROJECT_CHRONICLE.md`;
- `docs/logs/COMMERCIAL_DESKTOP_RISK_AUDIT_2026-08-19.md`;
- GitHub Issue #9 — temporary coordination checklist.

These are not permission to turn the Stage-A integration repair into a giant refactor.

After the gate-critical integration path is correct:

- Provider-neutral product binding stays in adapter/composition/profile/doctor seams;
- commercial UI shell polish stays in product adapter/UI seams;
- packaging begins with a reproducible Windows `onedir` probe and explicit dependency/license manifest.

## Structural progress

Remain at **90%** until the real Editing Product/Human Gate passes the full frozen route.

Stage A may reach 100% only when both core Product/Human Gates pass and `docs/roadmap/STAGE_A_COMPLETION_GATE.md` is fully satisfied.

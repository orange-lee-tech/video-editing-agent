# Current Work Order

**ID:** `R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Stage-A ordinary-user Product Gate closure  
**Mode:** LOCAL UX CANDIDATE FINALIZATION → EDITING INTEGRATION/PUBLICATION/OUTPUT-PROFILE REPAIR → PRODUCT/HUMAN GATE  
**Accepted production-code baseline:** `af5865df14b9f1cceaa9e6c1fe4dadf14cc60058`  
**Activated:** 2026-08-18  
**Corrected after integration audit:** 2026-08-19  
**Codex release:** CLOSED — execution quota exhausted; preserve existing local candidate

## Objective

Close Stage A only through real ordinary-user evidence for the two frozen core product functions.

Planning Product/Human Gate is already **PASS**.

Editing has validated subsystems and a working ordinary orchestration skeleton, but a 2026-08-19 static audit found **three gate-path defects/prerequisites**:

1. the ordinary route omits part of the editing-expression floor required by the frozen Stage-A completion/product-I/O contracts;
2. the ordinary route renders directly to the user-selected final path before Review decides PASS/CORRECTION_REQUIRED;
3. the ordinary route silently fixes output geometry to `1920×1080@30` instead of carrying a typed/user-visible Output Profile into Spatial and rendering.

The next gate-closing real Editing run is blocked until one bounded integration/publication/output-profile repair is accepted.

This correction keeps structural progress at 90%, does not reopen accepted subsystem closures, and does not authorize a product-core redesign.

## Frozen architecture

The following remain unchanged:

- Planning-only: `Brief → ScriptPlan → ShootingPlan`;
- Editing-only: `Brief/editorial intent + user local footage → Editing Core`;
- Combined: exact Planning revisions optionally enrich the same Editing Core;
- reference-only media remains Resolver-ineligible;
- final commercial visuals come from user-selected local footage;
- source-time grounding remains Resolver-owned;
- Output Profile is explicit product configuration, not provider authority; its target canvas/fps is visible/inspectable and used consistently by Spatial/EDL/Renderer;
- Music/Audio/Spatial/Subtitle/Graphics/transition owners produce approved decisions/artifacts upstream of EDL assembly;
- EDLBuilder assembles but does not invent editorial decisions;
- canonical EDL remains the sole exact timeline authority;
- Renderer executes only;
- Review classifies/routes only;
- rendering may create a candidate artifact, but **final publication to the user-selected output destination occurs only after Review PASS**;
- originals remain protected;
- no silent provider switching or fabricated replacement media.

## Gate state

### Planning Product Gate

**PASS**.

Durable evidence:

`docs/validation/R0.12_STAGE_A_PLANNING_PRODUCT_GATE.md`

### Editing Product Gate

**INTEGRATION/PUBLICATION/OUTPUT-PROFILE GAPS OPEN / PRODUCT PROBE NOT GATE-READY / HUMAN GATE OPEN**.

Real Windows probes already crossed input validation, local-media understanding and Director boundaries and exposed/fixed provider/runtime defects through accepted baseline:

`af5865df14b9f1cceaa9e6c1fe4dadf14cc60058`

Exact-head CI:

`32145822611` — `ci/quality-gate-diagnostic = success`.

The latest real Editing attempt then reached `ingest_understanding` and hit a genuine Gemini HTTP 429 after legitimate requests. That provider condition remains explicit and never authorizes silent fallback.

Provider quota recovery alone is no longer enough to resume the gate because the static ProductFlow audit found the three issues below.

## Gate blocker A — Stage-A editing-expression integration

Frozen contracts require:

```text
understanding / Director / grounded Resolver
→ music/rhythm + spatial/audio + subtitle/graphics/minimal transitions
→ canonical EDL
→ Renderer / Review
→ final MP4
```

and:

```text
Director → Resolver
→ Music / Audio / Spatial / Subtitle / Graphics decisions
→ EDLBuilder → canonical EDL
```

At the audited remote `main`:

- `EditingProductCapabilities` exposes media probe, shot detector/options, visual understanding, Director, Renderer and rendered-media QC;
- `prepare_media()` performs local ingest, Shot detection and visual understanding;
- `generate_edit_plan()` uses the Director;
- `resolve_edit_plan()` uses the grounded Resolver;
- `build_edl()` calls `DeterministicEDLBuilder` with ResolutionDecision plus `build_conservative_source_audio_mix(...)`;
- it does **not** supply the already-supported `spatial_decisions` or `music_selection` seams to `EDLBuildRequest`;
- the ordinary ProductFlow does not yet wire the required structured Subtitle/Graphics/minimal-transition expression floor.

The EDL layer already shows these concerns belong upstream of Renderer: `EDLBuildRequest` accepts approved spatial/music/audio decisions, EDL owns subtitle cues/track families, and Renderer consumes canonical EDL.

Therefore a successfully rendered plain-cut/source-audio MP4 is not a Stage-A gate-closing result.

## Gate blocker B — Review-before-final-output publication

Current `EditingProductFlow.run()` does:

```text
build/save canonical EDL
→ render(edl, request.output_path)
→ Review(render_result)
→ if Review != PASS: return CORRECTION_REQUIRED with final_output_path=None
```

This is internally honest at the result-object level, but the MP4 may already exist at the user-selected final destination before Review. With FFmpeg overwrite enabled, it can also replace a previous non-source output before the new candidate is accepted.

Required product lifecycle:

```text
canonical EDL
→ render to controlled candidate/staging artifact
→ Review candidate
→ PASS: publish/promote to requested final destination
→ non-PASS: no user-final publication
```

Promotion/publishing is an application/product artifact-lifecycle action. It does **not** give Review editing authority and does **not** give Renderer timeline authority.

## Gate blocker C — explicit Output Profile / target-canvas authority

Current `EditingProductCapabilities` defaults:

```text
output_width = 1920
output_height = 1080
output_fps = 30
```

and ordinary `EditingForm` asks for output path but not aspect/resolution/fps.

This is not acceptable as the basis for R0.11 Spatial integration. Target canvas is a required input to spatial composition; silently solving every project for 16:9 can create technically valid but product-wrong reframing.

Required direction:

```text
user-visible typed Output Profile
→ target width / height / fps
→ SpatialComposer target canvas
→ canonical EDL / Render OutputSpec provenance
```

Platform may suggest a default profile, but no hidden vendor/platform string may become the uninspectable final geometry authority. The user can confirm/override the profile.

Durable incidents:

- `docs/logs/INCIDENT_LEDGER.md` — `R0.12 Stage-A ordinary Editing integration gap — OPEN`;
- `docs/logs/INCIDENT_LEDGER.md` — `R0.12 Review-before-final-output publication defect — OPEN`;
- `docs/logs/INCIDENT_LEDGER.md` — `R0.12 fixed output-profile / aspect-ratio gap — OPEN`.

## Work boundary A — finalize the preserved local UX candidate

The previously authorized UX stabilization wave has already been implemented locally in the user's Windows working tree. Codex quota expired before final smoke/commit/push.

Candidate scope includes:

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

Observed full local gate **before final Splash micro-edits**:

- Ruff / mypy / import-linter / build / repo-doctor: PASS;
- pytest: `713 passed`;
- launcher/Tk smoke: PASS;
- manual UI smoke: PASS for all listed features except the original invisible Splash.

Splash was repaired to perform a real Tk repaint and given a dependency-free Canvas pixel mark. The user confirmed the startup icon is visible.

### Required completion steps

1. **Do not pull/reset/stash over the current uncommitted Windows work.**
2. Rerun the full local Quality Gate after the final Splash edits.
3. Commit the current local product-adapter/UI/test candidate on its existing local base.
4. Fetch `origin/main` and rebase that local code commit onto the latest docs-only remote main.
5. Rerun required checks at rebased HEAD.
6. Push.
7. ChatGPT reobserves exact commit/diff/CI and accepts or rejects it.
8. Only after acceptance update `accepted_code_baseline`.

No further Codex execution is authorized for this candidate; preserve it rather than recreate it.

## Work boundary B — one bounded Stage-A Editing integration/publication/output-profile repair

After boundary A is accepted, implement **one coherent gate-path repair**.

### B0. Explicit Output Profile

Define the smallest Stage-A product configuration needed to control target geometry before Spatial integration.

Requirements:

- user-visible/typed profile includes at least target width, target height and fps, with stable aspect identity/label where useful;
- product may suggest familiar presets (for example vertical/horizontal/square short-form profiles) but user can inspect/override;
- Brief platform may influence a default suggestion only; it is not hidden geometry authority;
- profile validation is deterministic and provider-independent;
- selected profile reaches Spatial target canvas and Render OutputSpec consistently;
- actual profile used is inspectable/persisted in execution provenance/canonical output description;
- vertical-profile regression proves the system does not silently fall back to 1920×1080.

### B1. Reuse R0.10 Music / Audio Editorial ownership

Integrate existing MusicSelection / BeatMap / Audio Editorial into the ordinary Editing route rather than hardcoding BGM/audio in ProductFlow/Renderer.

Requirements:

- rights/provenance remain enforced;
- approved `MusicSelectionDecision` / `AudioMixDecision` feed EDL assembly;
- source-audio treatment remains selection/source-range granular;
- Renderer does not independently choose music/mix.

### B2. Reuse R0.11 Spatial / Auto Reframe ownership

For resolved selections, integrate existing SpatialComposer/ReframeDecision before EDL assembly using B0's selected target canvas.

Requirements:

- spatial evidence provider observes only;
- SpatialComposer owns executable transform decision;
- approved ReframeDecision maps into EDL spatial automation;
- Renderer only executes canonical transform;
- manual/user locks remain higher authority where represented.

### B3. Structured Subtitle integration

Use the existing subtitle semantic/builder path and canonical EDL subtitle cues rather than rendering raw ASR text directly.

Requirements:

- subtitle timing/content structured before Renderer;
- EDL owns exact cue placement;
- FFmpeg/ASS execution deterministic;
- no Renderer-side editorial rewriting.

### B4. Minimum Graphics and transition floor

The Stage-A gate explicitly requires basic deterministic title/CTA/price-card graphics and a minimal transition vocabulary.

Current EDL defines a `GRAPHICS` track family, but the audited executor does not yet provide the full Stage-A graphics path and the current EDL model has no explicit transition semantics.

Allowed direction:

- bounded title/CTA/price-card typed decision/artifact seam;
- very small deterministic transition vocabulary, starting from CUT plus only minimum approved non-cut semantics;
- explicit EDL representation/validation;
- Renderer backend compilation only after semantics exist.

Forbidden direction:

- monolithic Effects Engine;
- freeform FFmpeg filter strings as Domain truth;
- LLM-generated backend syntax as authority;
- broad motion-graphics/NLE feature creep.

### B5. Review-safe final publication

Introduce an explicit candidate/publish boundary.

Requirements:

- render to a controlled candidate path/artifact, not directly to the requested final destination;
- Review consumes that candidate;
- only Review PASS publishes/promotes to the requested output path;
- CORRECTION_REQUIRED returns no final output and cannot overwrite a previously accepted final MP4;
- existing-target behavior is explicit (`另存为 / 覆盖 / 取消`) at product/controller level;
- candidate cleanup/retention is deterministic and diagnosable;
- Review does not mutate media; Renderer does not decide publication.

### B6. Integration proof

Tests must prove **Output Profile / decision → canonical EDL → execution → Review → publication** alignment.

Minimum expectations:

- vertical Output Profile produces vertical target geometry/execution;
- changing approved Music/Audio decision changes EDL/execution;
- changing approved ReframeDecision changes EDL/execution against selected target canvas;
- subtitle cues exist canonically and render through EDL;
- graphics/transition typed decisions alter canonical EDL/execution deterministically;
- non-PASS Review does not publish/overwrite requested final path;
- PASS Review promotes the exact reviewed candidate;
- no path bypasses EDL;
- existing Resolver/source protection/regressions remain green;
- full Quality Gate passes.

If a required Stage-A expression cannot be represented without a larger redesign, stop and bring the exact gap to the user rather than silently weakening the gate.

## Work boundary C — real Editing Product/Human Gate

Only after A+B are accepted and provider/runtime are usable:

1. synchronize accepted `main` to Windows;
2. launch ordinary product surface;
3. select real footage through single multi-select local-file mechanism;
4. choose/confirm intended Output Profile;
5. record source SHA-256 hashes before run;
6. keep Combined unchecked for Editing-only proof;
7. execute actual ingest / shot detection / understanding / Director / grounded Resolver;
8. execute Stage-A Music/Audio/Spatial/Subtitle/Graphics/minimal-transition floor through canonical EDL against selected target canvas;
9. render controlled candidate;
10. Review PASS;
11. publish/promote reviewed candidate to real final MP4 destination;
12. verify source hashes unchanged;
13. user watches MP4 and completes ordinary Editing Human Gate.

## Parallel productization requests — documented, not mixed into boundary B

Durable plans:

- `docs/product/DESKTOP_UI_DESIGN_SYSTEM_V0.1.md`;
- `docs/architecture/PROVIDER_NEUTRAL_PRODUCT_BINDING_PLAN.md`;
- `docs/operations/WINDOWS_DESKTOP_PACKAGING_READINESS.md`;
- `docs/operations/WINDOWS_RUNTIME_DEPENDENCY_INVENTORY.md`;
- `docs/roadmap/PRODUCT_RED_BLACK_BOARD.md`;
- `docs/logs/PROJECT_CHRONICLE.md`;
- `docs/logs/COMMERCIAL_DESKTOP_RISK_AUDIT_2026-08-19.md`;
- `docs/research/DESKTOP_PRODUCT_UI_REFERENCE_REVIEW_2026-08-19.md`;
- GitHub Issue #9 — temporary coordination checklist.

After the gate-critical route is correct:

- Provider-neutral binding stays in adapter/composition/profile/doctor seams;
- commercial UI polish stays in product adapter/UI seams;
- packaging begins with a reproducible Windows `onedir` probe and explicit dependency/license manifest.

## Structural progress

Remain at **90%** until the real Editing Product/Human Gate passes the full frozen route, explicit output-profile semantics, and PASS-only final publication.

Stage A may reach 100% only when both core Product/Human Gates pass and `docs/roadmap/STAGE_A_COMPLETION_GATE.md` is fully satisfied.

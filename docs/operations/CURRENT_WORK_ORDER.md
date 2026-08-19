# Current Work Order

**ID:** `R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Stage-A ordinary-user Product Gate closure  
**Mode:** EDITING INTEGRATION/PUBLICATION/OUTPUT-PROFILE REPAIR → PRODUCT/HUMAN GATE  
**Accepted production-code baseline:** `c6bd96116e3ab00f76aeb87ee63ad1037ba84980`  
**Activated:** 2026-08-18  
**Updated:** 2026-08-19  
**Codex release:** CLOSED — current work continues under ChatGPT/User control unless explicitly reopened

## Objective

Close Stage A only through real ordinary-user evidence for the two frozen core product functions.

Planning Product/Human Gate is already **PASS**.

The Stage-A UX stabilization wave is now **ACCEPTED** at production-code baseline `c6bd96116e3ab00f76aeb87ee63ad1037ba84980`, exact-head CI run `32205777259` PASS.

The next gate-closing Editing run is blocked by three ordinary ProductFlow issues found in the 2026-08-19 audit:

1. the route omits part of the Stage-A editing-expression floor;
2. it renders to the user-selected final path before Review PASS;
3. it silently fixes target geometry to `1920×1080@30` instead of using an explicit Output Profile.

These are integration/product-lifecycle defects. They do not authorize a core architecture redesign or reopen accepted R0.8/R0.9/R0.10/R0.11 subsystem evidence.

## Frozen architecture

- Planning-only remains valid.
- Editing-only remains valid.
- Combined remains optional enrichment.
- reference-only media remains Resolver-ineligible.
- final commercial visuals come from user-selected local footage.
- source-time grounding remains Resolver-owned.
- Output Profile is explicit product configuration, not provider authority.
- Music/Audio/Spatial/Subtitle/Graphics/transition owners decide upstream of EDL assembly.
- EDLBuilder assembles approved decisions; it does not invent editorial intent.
- canonical EDL remains the sole exact timeline authority.
- Renderer executes only.
- Review classifies/routes only.
- render candidate is not final output before Review PASS.
- final publication/promotion is product/artifact lifecycle.
- originals remain protected.
- no silent provider switching or fabricated replacement media.

## Accepted UX stabilization evidence

Feature commit after rebase:

`3df11e826bb672217528d7655ca02fc4701976d1` — `feat: stabilize Stage A desktop UX`.

Accepted head:

`c6bd96116e3ab00f76aeb87ee63ad1037ba84980`.

Local Windows evidence:

- Ruff format/check: PASS;
- mypy: PASS;
- pytest: `713 passed`;
- import-linter: 3 contracts kept;
- build: PASS;
- `git diff --check`: PASS;
- repo doctor: PASS;
- launcher smoke: `0`;
- manual UI smoke: PASS for placeholders, multi-select media files, scroll/export, Chinese/English, responsiveness, profiles, protected API credentials and Splash;
- API profile plaintext-secret check: PASS.

Remote Linux CI initially caught a cross-platform mypy issue around Windows-only `ctypes.windll/WinError`; the first portability attempt then triggered Ruff B009. The final typed-ignore repair passed both lint and mypy in CI. This is now closed and does not require another UX wave.

## Gate blocker A — Stage-A editing-expression integration

Frozen Stage-A route requires:

```text
understanding / Director / grounded Resolver
→ music/rhythm + spatial/audio + subtitle/graphics/minimal transitions
→ canonical EDL
→ Renderer / Review
→ final MP4
```

Current ordinary ProductFlow still does not compose the full required expression floor.

### Required repair

#### A1. Output Profile first

Define the smallest typed/user-visible Stage-A Output Profile with at least:

- target width;
- target height;
- fps;
- stable label/aspect identity where useful.

Requirements:

- platform may suggest a default but user can inspect/override;
- deterministic provider-independent validation;
- selected profile reaches Spatial target canvas and Render OutputSpec consistently;
- actual profile used remains inspectable in execution/canonical output provenance;
- vertical-profile regression proves no silent fallback to 1920×1080.

#### A2. Reuse R0.10 Music / Audio Editorial

Integrate existing MusicSelection / BeatMap / Audio Editorial owners into the ordinary Editing route.

Requirements:

- rights/provenance remain enforced;
- approved MusicSelectionDecision / AudioMixDecision feed EDL assembly;
- source-audio treatment remains grounded to selected ranges;
- Renderer does not independently choose music/mix.

#### A3. Reuse R0.11 Spatial / Auto Reframe

Integrate existing SpatialComposer/ReframeDecision against A1's target canvas.

Requirements:

- spatial evidence provider observes only;
- SpatialComposer owns executable transform decision;
- approved ReframeDecision maps to EDL spatial automation;
- Renderer only executes canonical transform;
- manual/user locks remain higher authority where represented.

#### A4. Structured Subtitle integration

Use the existing subtitle semantic/builder path and canonical EDL subtitle cues.

Requirements:

- subtitle content/timing structured before Renderer;
- EDL owns exact cue placement;
- FFmpeg/ASS execution deterministic;
- no Renderer-side editorial rewriting.

#### A5. Minimum Graphics and transition floor

The Stage-A gate explicitly requires basic deterministic title/CTA/price-card graphics and a minimal transition vocabulary.

Allowed direction:

- small typed title/CTA/price-card decision/artifact seam;
- very small deterministic transition vocabulary beginning with CUT plus only the minimum approved non-cut semantics;
- explicit EDL representation/validation;
- backend compilation only after semantics exist.

Forbidden direction:

- monolithic Effects Engine;
- freeform FFmpeg filter strings as Domain truth;
- LLM-generated backend syntax as authority;
- broad NLE/motion-graphics feature creep.

## Gate blocker B — Review-safe final publication

Current ProductFlow writes the render directly to the user-requested final path before Review.

Required lifecycle:

```text
canonical EDL
→ controlled render candidate/staging artifact
→ Review candidate
→ PASS: publish/promote to requested final destination
→ non-PASS: no user-final publication
```

Requirements:

- non-PASS cannot overwrite a previously accepted final MP4;
- existing-target behavior is explicit at product/controller level (`另存为 / 覆盖 / 取消` or equivalent);
- candidate cleanup/retention is deterministic and diagnosable;
- Review does not mutate media;
- Renderer does not decide publication.

## Integration proof

The repair must prove **Output Profile / decision → canonical EDL → execution → Review → publication** alignment.

Minimum regression expectations:

- vertical Output Profile produces vertical target geometry/execution;
- changing approved Music/Audio decision changes EDL/execution;
- changing approved ReframeDecision changes EDL/execution against selected target canvas;
- subtitle cues exist canonically and render through EDL;
- graphics/transition typed decisions alter canonical EDL/execution deterministically;
- non-PASS Review does not publish/overwrite requested final path;
- PASS Review promotes the exact reviewed candidate;
- no execution path bypasses EDL;
- existing Resolver/source protection/regressions remain green;
- full Quality Gate passes.

If any required Stage-A expression cannot be represented without a materially larger redesign, stop and report the exact gap rather than silently weakening the gate.

## Real Editing Product/Human Gate after repair

Only after the repair is accepted and provider/runtime are usable:

1. synchronize accepted `main` to Windows;
2. launch the ordinary product surface;
3. select real footage through the single multi-select local-file mechanism;
4. choose/confirm intended Output Profile;
5. record source SHA-256 hashes;
6. keep Combined unchecked for Editing-only proof;
7. execute actual ingest / shot detection / understanding / Director / grounded Resolver;
8. execute Stage-A Music/Audio/Spatial/Subtitle/Graphics/minimal-transition floor through canonical EDL;
9. render controlled candidate;
10. Review PASS;
11. publish/promote reviewed candidate to real final MP4 destination;
12. verify source hashes unchanged;
13. user watches MP4 and completes ordinary Editing Human Gate.

## Parallel productization requests — not mixed into this repair

Durable plans already exist for:

- desktop UI design system;
- Provider-neutral product binding;
- Windows packaging/readiness/runtime inventory;
- project chronicle;
- product red/black board;
- commercial desktop risk audit;
- open-source desktop UI reference review.

These remain separate bounded waves after the gate-critical Editing route is truthful.

## Structural progress

Remain at **90%** until the full ordinary Editing Product/Human Gate passes with explicit output-profile semantics and PASS-only final publication.

Stage A reaches 100 only when both core Product/Human Gates pass and `docs/roadmap/STAGE_A_COMPLETION_GATE.md` is fully satisfied.

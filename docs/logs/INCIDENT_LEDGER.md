# Incident Ledger

Non-authoritative durable debugging history. See `docs/logs/README.md`.

## R0.7B commercial semantic-authority cluster — CLOSED

**Period:** 2026-08-11 to 2026-08-12

### Mechanism

Generation, Script review, Shooting review and Product review initially interpreted commercial authority independently. Mechanical facts could drift into unsupported convenience, fit, sufficiency or ease claims.

### Durable invariant

Concrete product property/performance/outcome assertions require explicit authoritative support. Generation and review share the same commercial-authority projection.

### Closure evidence

Product Probe run `31610613082` on baseline `48ecafcf45a299ced4d9abafd5501e2b9031f4a3` passed automated gates and Human Gate. Formal closure: `docs/validation/R0.7B_FINAL_CLOSURE.md`.

## R0.8E analyzed-source-range owner guard — CLOSED

**Date:** 2026-08-13

### Mechanism

The provider-range equality guard existed after `return`, so a faulty provider range could bypass owner validation before persistence.

### Durable invariant

Provider-reported exact analysis identity/range must be validated by the owner **before** any durable Artifact/evidence commit.

### Fix / verification

Commit `220f6c3d912319cf5e66f2ddf989bdff0d41302d`; CI run `31666637333` succeeded.

## R0.9 Product Probe answer-injection evidence defect — CLOSED

**Date:** 2026-08-13

### Symptom

A technically green Product Probe rendered real footage and reported plausible lexical/hybrid/Resolver comparisons, but the probe itself preconstructed ShotCandidate objects, CandidateWindows and answer source ranges.

### Mechanism

The evidence harness bypassed the retrieval/evidence/window-generation stages it claimed to validate. Real media at the final FFmpeg step did not make the upstream selection evidence real.

### Durable invariant

A Product Probe must obtain system outputs from the actual owned pipeline. Human ground truth/expected answers may be separate scoring data, but must never be injected as candidate IDs, windows, timestamps or Resolver inputs.

### Fix / verification

The closure probe was reopened rather than sent to Human Gate. Commit `a8574d170aeb366a655b6d32486b481eb081321f` rebuilt the comparison through managed corpus → actual lexical/dense retrieval → R0.8 evidence → canonical CandidateWindow generator → Resolver. The repaired probe passed and later Human Gate accepted visual selection/cut quality.

## R0.10B decision→execution evidence bypass — CLOSED

**Date:** 2026-08-13

### Symptom

R0.10B selected `[9,12)` music segments and produced structured AudioMixDecision automation, but the diagnostic preview independently trimmed `0:6`, hardcoded duck ranges, and measured QC on the input music fixture.

### Mechanism

The probe had two parallel truths: canonical decisions in data and a separately authored FFmpeg path. A plausible audible preview therefore did not prove that the decisions were actually executed.

### Durable invariant

Diagnostic execution must consume canonical decisions. Changing the decision must change the execution plan; execution must not mutate the decision. Output QC must measure the rendered/post-mix output it claims to describe.

### Fix / verification

Commit `81afb604b96486587a308f6f4c69d89f1450f46e` added a non-authoritative compiler from MusicSelectionDecision + AudioMixDecision to an inspectable FFmpeg execution plan, executed the selected source segments, decoded final preview audio for QC, and added decision-mutation/executed-range/clipped-control regressions. CI run `31712962989` succeeded.

## R0.12 Stage-A ordinary Editing integration gap — OPEN

**Discovered:** 2026-08-19 during commercial-desktop audit

### Symptom

The live Stage-A completion contract requires the ordinary Editing path to include:

`music/rhythm + spatial/audio + subtitle/graphics/minimal transitions`

before canonical EDL → Renderer → Review.

The accepted Stage-A Product I/O contract likewise defines the Editing owner chain as:

`Director → Resolver → Music / Audio / Spatial / Subtitle / Graphics decisions → EDLBuilder`.

However the current production `build_editing_product_flow()` composition does not yet wire that full expression floor into the ordinary product route.

### Evidence

At the audited `main`:

- `EditingProductCapabilities` exposes media probe, shot detector, understanding, Director, Renderer and rendered-media QC, but no music-selection, BeatMap/audio-editorial, spatial-composer, subtitle/graphics or transition capability;
- `build_edl()` calls `DeterministicEDLBuilder` with grounded ResolutionDecision plus `build_conservative_source_audio_mix(...)`, but supplies no `spatial_decisions` or `music_selection`;
- `DeterministicEDLBuilder` already has optional seams for `spatial_decisions`, `music_selection` and `audio_mix`, proving these decisions belong upstream of the builder rather than in Renderer;
- the live Work Order / Current Phase return corridor currently abbreviates the gate-closing chain to `Resolver → canonical EDL / Renderer / Review`, omitting the Stage-A editing-expression floor.

Subtitle/graphics/minimal-transition product wiring is also not present in this ordinary ProductFlow path.

### Mechanism

R0.10/R0.11 and R0.12 capability construction produced real, independently validated mechanisms, but the later ordinary-user ProductFlow orchestration closed a **minimum mechanical path** rather than integrating every capability required by the already-frozen Stage-A Product Gate.

The control plane then inherited the abbreviated ProductFlow chain and risked treating a plain-cut/source-audio MP4 as sufficient gate-closing evidence.

### Durable invariant

A Stage-A Editing Product/Human Gate may close only when the **actual ordinary product route** consumes the required approved decision families before EDL assembly. Existing subsystem closure evidence cannot substitute for integration into that route.

The fix must preserve ownership:

- Music/Audio/Spatial/Subtitle/Graphics owners decide;
- Resolver still owns grounded source windows;
- EDLBuilder only assembles approved decisions;
- canonical EDL remains sole exact timeline authority;
- Renderer only executes;
- Review only classifies/routes.

### Required correction

Before the next gate-closing real Editing run:

1. update the live control corridor so it cannot falsely close on the abbreviated path;
2. define one bounded Stage-A Editing integration repair work boundary;
3. wire existing approved music/audio/spatial capabilities into ProductFlow rather than reimplementing them;
4. wire the minimum transition/subtitle/graphics expression floor required by `STAGE_A_COMPLETION_GATE.md`;
5. add integration regressions showing canonical EDL actually contains/executes the decisions;
6. only then resume the real final-MP4 Product/Human Gate.

### Current classification

**OPEN — gate-blocking integration gap, not a reason to redesign the core architecture.**

# video-editing-agent

A **script-driven, local-first AI Director + AI Video Editor** for user-supplied footage.

Initial product focus:

- Windows desktop;
- commercial short-form video;
- ecommerce / product advertising;
- Vlog;
- primarily videos under 60 seconds.

The durable creative pipeline is:

```text
Brief
→ ScriptPlan
→ ShootingPlan
→ user-supplied visual Assets / Shots
→ media understanding / temporal evidence
→ Music / BeatMap
→ Director / EditPlan
→ ShotResolver / ResolutionDecision
→ Spatial / Audio decisions where needed
→ EDLBuilder / exact EDL
→ Render
→ layered Review / repair
→ final MP4
```

The product is not a generic text-to-video generator and does not autonomously acquire replacement visual B-roll.

---

## Product Constitution

The highest-level product authority is:

[`docs/product/PRODUCT_CONSTITUTION_V1.0.md`](docs/product/PRODUCT_CONSTITUTION_V1.0.md)

Core product rules include:

- source visual material in commercial output comes from user-supplied local files;
- missing visual coverage is surfaced as a production gap/reshoot need rather than filled with downloaded/generated footage;
- visual AI observes/proposes; it does not own the timeline;
- audio/music is governed separately and may use rights-aware public/connected music sources;
- EDL is the sole executable timeline authority;
- local deterministic tools execute media operations when they can do so reliably;
- models/providers are replaceable intelligence implementations;
- original media and project history are local-first;
- final video quality outranks API cost, automation level and speed.

Product-policy changes require an explicit constitutional amendment. A library, model or upstream project cannot override the Constitution.

---

## Current engineering map

### Architecture

Post-Survey architecture candidate:

[`docs/architecture/ARCHITECTURE_CONTRACT_V0.2.md`](docs/architecture/ARCHITECTURE_CONTRACT_V0.2.md)

Historical architecture baselines remain preserved for provenance:

- `ARCHITECTURE_CONTRACT_V0.1.md`
- `ARCHITECTURE_CONTRACT_V0.1.1.md`
- `ARCHITECTURE_CONTRACT_V0.1.2.md`

The v0.2 candidate reconciles those early contracts with Product Constitution v1.0 and Survey V2. Until the planning baseline is explicitly frozen, the Constitution remains the highest authority and no feature implementation should assume that candidate implementation parameters are permanent.

Important v0.2 ownership boundaries:

```text
BriefService             → Brief
ScriptPlanner            → ScriptPlan
ShootingPlanner          → ShootingPlan
AssetIngestService       → Asset identity
ShotCatalog              → Shot identity
UnderstandingService     → ShotAnalysis
TemporalEvidenceService  → TemporalEvidence / TemporalAnchor validation
BeatAnalysisService      → BeatMap
Director                 → EditPlan / EditSlot
ShotResolver             → ResolutionDecision / ResolvedSelection
SpatialComposer          → ReframeDecision / SpatialTransformPlan
MusicSelectionService    → MusicSelectionDecision
AudioEditorialService    → AudioMixDecision
EDLBuilder               → exact executable EDL
Renderer                 → RenderArtifact only
ReviewService            → ReviewReport
```

### Capability specifications

Current candidate capability map:

[`docs/capabilities/`](docs/capabilities/)

It contains focused specifications for:

1. pre-production;
2. Asset / rights / media time;
3. media understanding / speech / temporal evidence;
4. retrieval / Director / Resolver / optimizer;
5. Commercial/Vlog skills;
6. music / BeatMap / audio editorial;
7. spatial composition / Auto Reframe;
8. EDL / renderer / subtitle / preview / proxy / cache;
9. review / benchmarks;
10. deployment / Environment Doctor / security / autonomy.

### ADRs

Concrete architecture decisions are recorded under:

[`docs/adr/`](docs/adr/)

Current decisions include:

- FFmpeg as the primary deterministic render-backend family;
- grounded AI decisions instead of free-form authoritative timestamps;
- project-local hybrid retrieval before mandatory vector-database infrastructure;
- layered Beam Search / DP as the first sequence-optimizer family;
- ASS/libass as the standard subtitle-render baseline;
- rights-aware coarse-to-fine music selection;
- SpatialComposer ownership for Auto Reframe;
- full dependency/license-chain review rather than trusting a top-level repository license.

### Roadmap V2

Current construction plan:

[`docs/roadmap/ROADMAP_V2.md`](docs/roadmap/ROADMAP_V2.md)

Immediate implementation target **after planning approval**:

> **R0.7A — Architecture v0.2 Migration Foundation**

Do not jump directly into a full one-click video demo, Auto Reframe or music AI before the migration foundation is green.

---

## Survey V2 — CLOSED

The broad open-source/research Survey has completed its product-wide closure gate.

Final closure record:

[`docs/research/SURVEY_V2_FINAL_CLOSURE.md`](docs/research/SURVEY_V2_FINAL_CLOSURE.md)

Research archive:

[`docs/research/`](docs/research/)

Survey V2 established credible engineering families for:

- Script/Shooting planning;
- visual understanding and temporal action evidence;
- ASR/dialogue timing;
- hybrid Shot retrieval;
- CandidateWindow trimming;
- Resolver scoring/uncertainty;
- deterministic sequence optimization;
- elastic beat/action alignment;
- Commercial/Vlog Skill calibration;
- rights-aware music selection and audio editorial;
- Auto Reframe/spatial composition;
- EDL/render/subtitle/preview/proxy/cache;
- technical and editorial review;
- Windows deployment and Environment Doctor.

Broad ecosystem exploration should not be reopened merely because a new model appears. New upstream work is evaluated inside existing capability seams unless a genuinely new major capability or benchmark failure requires a new Survey Gate.

---

## Current implemented baseline

Completed engineering phases remain valid and are not discarded by Roadmap V2:

### R0.1 — Shot Detection — COMPLETE

- FireRed-informed ShotDetector contract independently implemented;
- streaming FFmpeg RGB24 decode;
- bounded-memory TransNetV2 window semantics;
- optional Torch runtime adapter;
- real Windows/video probes.

### R0.2 — Asset / Shot Identity — COMPLETE

- real ffprobe ingest;
- immutable Asset identity;
- Asset → Shot chain;
- ShotCatalog ownership.

### R0.3 — Provider-Neutral Footage Understanding — COMPLETE

- deterministic Shot frame sampling/extraction;
- SHA-256 content-addressed ArtifactStore;
- VisualUnderstandingPort;
- proposal → UnderstandingService → ShotAnalysis ownership chain.

### R0.4 — Local Structured Persistence — COMPLETE

- SQLite schema v1;
- revisioned Asset / Shot / ShotAnalysis persistence across processes;
- repositories persist without gaining semantic ownership.

### R0.5 — Shot Retrieval Foundation — COMPLETE

- deterministic local lexical retrieval;
- Latin and CJK matching;
- prefilters and analysis-revision tracking;
- rebuildable ShotIndex.

### R0.6 — First Concrete Visual Provider — COMPLETE

- Gemini visual adapter validated through provider seam;
- optional OpenAI Responses visual adapter;
- live external-API **Engineering Probe** completed using synthetic FFmpeg fixture;
- extracted frames → provider proposal → committed searchable ShotAnalysis.

Important evidence boundary:

> A live API call against a synthetic fixture proves provider/ownership machinery. It does **not** prove useful understanding/editing of real user footage.

See `docs/validation/` for engineering evidence.

---

## Upstream governance

Current upstream map and policy:

- [`docs/upstream/UPSTREAM_COMPONENTS_V2.md`](docs/upstream/UPSTREAM_COMPONENTS_V2.md)
- [`docs/upstream/UPSTREAM_POLICY_V2.md`](docs/upstream/UPSTREAM_POLICY_V2.md)

The older `UPSTREAM_COMPONENTS.md` / `UPSTREAM_POLICY.md` are retained only as **historical bootstrap snapshots**.

Current reuse rule:

```text
Audit
→ classify useful mechanism
→ audit source + model + data + transitive + provider + patent/runtime terms
→ neutralize unconstitutional behavior
→ adapt/reimplement behind local ownership
→ benchmark
→ approve exact dependency revision separately
```

Examples of neutralization:

- MoneyPrinterTurbo may inform caching/retry/provenance/provider engineering, but not remote visual-stock fallback;
- CutClaw remains an algorithm/architecture reference only;
- AGPL/NC/unclear-license systems can still teach algorithms without becoming dependencies;
- Auto Reframe references may inform crop-path optimization while generative outpainting remains outside the normal product path;
- a permissive top-level repository license does not approve restrictive model/checkpoint/transitive dependencies.

---

## Engineering philosophy

The product should behave as if the AI carries a prepared local toolbox.

```text
AI / reasoning layer
- understand
- plan
- judge
- critique

Local deterministic layer
- probe
- decode
- measure
- index
- track
- trim
- mix
- render
- persist
```

Preferred cost path:

```text
cheap local preprocessing
→ small relevant evidence package
→ AI judgment only where needed
→ structured decision
→ local deterministic execution
```

Strong/expensive models are escalation paths for important uncertainty, not default fuel for deterministic work.

---

## Development policy

Development occurs directly on `main`.

For coherent implementation batches:

```text
state-first observation
→ plan
→ one coherent change
→ local/static/structural checks
→ one atomic commit
→ CI green
→ Engineering/Product Probe as applicable
→ next batch
```

If current `main` is red, feature work freezes until repaired.

Do not bypass architecture or Product Constitution to accommodate a provider/library.

---

## License status

A repository-wide open-source license has not yet been selected.

See:

- [`LICENSE_STATUS.md`](LICENSE_STATUS.md)
- [`docs/upstream/UPSTREAM_POLICY_V2.md`](docs/upstream/UPSTREAM_POLICY_V2.md)

Third-party code, model weights, datasets, native/transitive libraries, provider terms and codec/patent implications are reviewed independently before production adoption/distribution.

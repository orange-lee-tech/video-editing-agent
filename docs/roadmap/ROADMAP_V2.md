# Roadmap V2 — Evidence-Grounded AI Director + AI Video Editor

**Status:** CANDIDATE ROADMAP — post Survey V2  
**Date:** 2026-08-11  
**Product authority:** `docs/product/PRODUCT_CONSTITUTION_V1.0.md`  
**Architecture target:** `docs/architecture/ARCHITECTURE_CONTRACT_V0.2.md`  
**Capability specs:** `docs/capabilities/`  
**ADRs:** `docs/adr/`  
**Upstream governance:** `docs/upstream/UPSTREAM_COMPONENTS_V2.md`, `UPSTREAM_POLICY_V2.md`

---

# 0. Why Roadmap V2 exists

R0.1–R0.6 established real engineering foundations:

- deterministic/probed Shot Detection;
- Asset / Shot identity;
- provider-neutral Shot understanding;
- local ArtifactStore;
- SQLite revisioned persistence;
- rebuildable lexical Shot retrieval;
- a real external visual-understanding provider path with proposal → owner commit semantics.

Those phases answered:

> Can we build reliable media/domain machinery?

Survey V2 then answered the larger product question:

> How should an excellent AI editor turn Script + user footage + music into a precise, high-quality EDL without letting an LLM guess timestamps or a third-party project own our semantics?

Roadmap V2 begins from both bodies of evidence.

It does **not** reset the repository and does not chase a fast demo/MVP at the cost of architecture.

---

# 1. Global development rules

Every phase follows:

```text
observe current state
→ understand
→ plan one coherent batch
→ implement behind existing ownership seams
→ local/static/structural verification
→ one atomic commit to main
→ wait for CI green
→ run Engineering Probe
→ run Product Probe when the capability affects real editing quality
→ update evidence/docs
→ next batch
```

If current `main` is red:

> feature work freezes until repaired.

No feature branch is required for ordinary construction.

---

# 2. Quality and evidence hierarchy

Product priority remains:

```text
Final video quality
>
User controllability
>
API cost
>
Automation level
>
Editing speed
```

Therefore:

- lower cost is not an improvement if human-preferred output degrades materially;
- faster automation is not an improvement if it reduces control/reproducibility;
- Product Probes use real footage when usefulness is being claimed;
- synthetic fixtures remain valid for Engineering Probes only.

---

# 3. Roadmap activation gate — A0

Before new feature implementation resumes, review/freeze the post-Survey design set:

```text
Architecture Contract v0.2
Capability Specs CAP-01 ... CAP-10
ADRs
Upstream Ledger/Policy V2
Roadmap V2
```

Required checks:

- Constitution alignment;
- no hidden remote/generated visual path;
- no ownership conflict among Director / Resolver / SpatialComposer / AudioEditorial / EDLBuilder;
- migration from implemented R0.1–R0.6 is feasible;
- unresolved implementation choices remain behind Ports/ADRs/benchmarks rather than being falsely frozen.

**Exit Gate:** explicit user acceptance of the planning baseline or an agreed correction set.

No feature code should leapfrog this gate.

---

# 4. Historical baseline retained

## R0.1 — Shot Detection — COMPLETE

Established:

- FireRed-informed but locally owned ShotDetector contracts;
- bounded-memory FFmpeg RGB24 decode;
- TransNetV2 inference-window semantics;
- optional runtime adapter;
- real Windows/video probes.

## R0.2 — Asset / Shot Identity — COMPLETE

Established:

- immutable Asset identity;
- ffprobe ingest;
- Asset → Shot chain;
- ShotCatalog ownership.

## R0.3 — Provider-Neutral Footage Understanding — COMPLETE

Established:

- deterministic frame sampling/extraction;
- content-addressed ArtifactStore;
- VisualUnderstandingPort;
- ShotAnalysis proposal → UnderstandingService commit.

## R0.4 — Local Structured Persistence — COMPLETE

Established:

- SQLite schema v1;
- revisioned Asset / Shot / ShotAnalysis persistence across processes;
- repository/storage ownership boundaries.

## R0.5 — Shot Retrieval Foundation — COMPLETE

Established:

- local lexical retrieval including CJK;
- retrieval prefilters;
- exact analysis revision tracking;
- rebuildable ShotIndex.

## R0.6 — First Concrete Visual Provider — COMPLETE

Established:

- external Gemini visual adapter through provider seam;
- optional OpenAI visual adapter;
- engineering probe: local frame extraction → provider proposal → ShotAnalysis persistence.

Important limitation retained:

> synthetic/live-API engineering success is not proof of real editing quality.

---

# 5. R0.7A — Architecture v0.2 Migration Foundation

## Purpose

Make the already-built R0.1–R0.6 machinery conform to v0.2 before creative feature expansion.

This is the most important immediate implementation phase.

## Architecture deliverables

Implement/migrate:

1. canonical rational `MediaTime` / `MediaTimeRange`;
2. Asset `origin` vs `usage_role` separation;
3. reference-analysis-only visual role;
4. removal/deactivation of legacy visual remote/generated source-policy schema;
5. RightsAttestation / LicenseSnapshot / override storage seams;
6. ResolutionDecision capable of `ResolvedSelection[]`;
7. Durable Derived Evidence vs Rebuildable Cache storage classes;
8. initial TemporalEvidence/Anchor persistence/value contracts;
9. placeholders/Ports for SpatialComposer, MusicSelectionService, AudioEditorialService;
10. Review repair-routing fields;
11. trust boundary: media-derived text = untrusted data;
12. typed/deterministic executor boundary.

## Migration principle

Do not break old persisted revisions silently.

Prefer:

```text
schema version detection
→ explicit migration/read adapter
→ new revision/state
```

rather than rewriting history in place.

## Engineering Probes

- v0.1 persisted project opens/migrates deterministically;
- VFR/rational time round-trip;
- reference video rejected by Resolver eligibility;
- remote/generated visual legacy enum cannot create an active visual fallback;
- multi-selection ResolutionDecision persists/reloads;
- cache cleanup preserves Durable Derived Evidence;
- malicious transcript text never reaches executor authority.

## Product Probe

Use a small real phone-footage project to prove:

- source windows remain stable after persistence/migration;
- reference material never leaks into output candidates;
- project remains locally usable/renderable after restart.

## Exit Gate

- all architecture/import/persistence tests green;
- migration docs complete;
- no active product path violates Product Constitution;
- existing R0.1–R0.6 probes remain green or have documented v0.2 replacements.

## Explicitly not in scope

- new Director quality;
- new music recommendation;
- Auto Reframe UI;
- full renderer productization.

Foundation first.

---

# 6. R0.7B — Pre-production Planning + Commercial Skill Foundation

## Purpose

Make the first product pillar real:

> Brief → ScriptPlan → ShootingPlan

as an executable production workflow rather than a generic LLM chat.

## Deliverables

### Brief / Script

- structured Brief creation/revision;
- authoritative commercial facts;
- NarrativeSections;
- natural-language structured revision;
- section locks;
- duration estimation;
- reference-video structural/style analysis without source eligibility.

### ShootingPlan

- equipment/production-constraint intake;
- ordinary-user shooting instructions;
- required/recommended/optional/backup ShotRequirements;
- handles/alternate coverage guidance;
- coverage/reshoot report.

### CommercialSkill baseline

At least two clearly different initial policies:

```text
Performance Product Ad
Natural Vlog
```

with PlatformProfile separation.

Use qualitative priors first; do not pretend uncalibrated numeric weights are truth.

## Provider strategy

Text reasoning stays behind a replaceable Port.

A DeepSeek-class provider may be integrated later/within this phase if it is the best operational choice, but the phase is not defined by one model vendor.

## Engineering Probes

- model proposal cannot mutate Brief facts;
- locked Script section survives automated revision;
- reference video produces analysis artifact but cannot become editable footage;
- ShootingPlan schema validates production constraints;
- required coverage gap routes to reshoot guidance, not stock-video provider.

## Product Probe

Real user Briefs for:

- one short product advertisement;
- one natural Vlog.

Human evaluation:

- script usefulness;
- shooting-plan executability;
- factual fidelity;
- expected shooting coverage.

## Exit Gate

A user can produce, inspect, revise and lock a practical Script/ShootingPlan before filming.

---

# 7. R0.8 — Media Evidence Foundation

## Purpose

Turn real user footage into the grounded evidence needed by a high-quality Resolver.

## Deliverables

### Speech

- CPU-capable ASR provider baseline;
- word/segment timestamps;
- VAD/silence evidence;
- transcript persistence;
- phrase/time mapping.

### Visual temporal evidence

- camera/global motion estimation;
- camera-compensated residual motion;
- coarse-to-fine event regions;
- motion onset/peak/settle anchors;
- seeded subject/product tracking baseline;
- provider-neutral TemporalEvidence/Anchor store.

### Retrieval representation

- derived visual-semantic/speech embedding representations;
- local multilingual embedding provider prototype;
- index provenance/version;
- exact project-local vector scan.

## Engineering Probes

- ASR/VAD timestamps map to original source time;
- no motion computation crosses Shot boundary;
- camera pan does not become a false local-action anchor in controlled fixture;
- changing embedding model rebuilds index without changing ShotAnalysis identity;
- all evidence survives restart with revision provenance.

## Product Probe

Private real footage set deliberately includes:

- talking head;
- handheld product demo;
- camera pan;
- hand/product interaction;
- low motion;
- noisy/blurred footage.

Measure anchor recall/false positives and speech cut quality.

## Exit Gate

The system can generate a useful grounded candidate-time set for real footage without requiring a high-end GPU.

---

# 8. R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer

## Purpose

Deliver the central post-production brain:

> Script/Edit intent + real evidence → grounded source decisions.

## Deliverables

### Director

- EditPlan/EditSlot generation from Brief/Script/Shooting/Coverage/BeatMap context;
- no source timestamp authority;
- Slot importance/intelligence budget.

### Hybrid retrieval

- lexical/CJK retrieval;
- multilingual dense retrieval;
- RRF-like baseline;
- structured hard filters;
- benchmarked Top-K strategy.

### CandidateWindow

- bounded IN/OUT candidates from speech/action/Shot anchors;
- window completeness/quality features.

### Resolver

- hard eligibility;
- unary/pairwise/global features;
- explicit score + uncertainty;
- alternatives/reasons;
- targeted VLM adjudication only when needed.

### Optimizer

- layered Beam Search / DP baseline;
- no-repeat/coverage/duration/continuity constraints;
- elastic music/event opportunity support.

## Engineering Probes

- LLM cannot create arbitrary candidate ID/timestamp outside evidence;
- hard constraints always dominate scores;
- deterministic evidence+policy produces reproducible optimizer result;
- one EditSlot can resolve to multiple ResolvedSelections;
- localized Resolver revision invalidates only downstream affected state.

## Product Probe — major milestone

Use private real product/Vlog footage.

Compare:

```text
lexical-only baseline
vs
hybrid retrieval
vs
hybrid + grounded Resolver
```

Human editors evaluate candidate recall, trim windows and sequence preference.

## Exit Gate

For the first time the project can create a **grounded exact source-selection plan from real user footage** without LLM timestamp hallucination.

This is a more meaningful milestone than a rushed “AI made an MP4” demo.

---

# 9. R0.10 — Music Selection + BeatMap + Audio Editorial

## Purpose

Turn soundtrack selection/mixing into a first-class editorial system.

## Deliverables

### Rights-aware music provider seam

- local music import;
- provider candidate metadata;
- LicenseSnapshot/attestation integration;
- explicit clear/warning/ineligible/unknown status;
- generated-audio filter obeying default OFF.

### Music selection

- MusicIntent;
- metadata/tag baseline retrieval;
- optional audio-text embedding prototype only if benchmark justified;
- CandidateMusicWindow from BeatMap phrases/sections;
- temporal reranking against narration/energy.

### BeatMap

Improve/validate:

- beats/downbeats;
- energy;
- phrase/section anchors;
- confidence;
- elastic rhythm evidence.

### AudioEditorial

- source audio preserve/mute policy;
- voiceover priority;
- explicit BGM gain envelope;
- speech-aware ducking;
- fades/crossfades;
- structural loop mapping;
- SFX track groundwork;
- EDL time-varying audio automation.

## Engineering Probes

- an incompatible-rights track cannot reach EDL;
- ambiguous track requires warning/override record;
- loop/window remains inside authoritative audio Asset;
- speech ranges generate deterministic ducking envelope;
- renderer audio automation round-trips.

## Product Probe

Human preference A/B for:

- music candidate;
- music moment;
- duck/fade naturalness;
- narration intelligibility.

Measure API/provider cost.

## Exit Gate

A real short-form project receives an auditable, rights-aware, editable soundtrack/mix without a manual DAW step for routine cases.

---

# 10. R0.11 — Spatial Composition / Auto Reframe

## Purpose

Make mixed-aspect user footage usable for vertical commercial/Vlog output without naive center crop or generative outpainting.

## Deliverables

- ReframeIntent;
- SpatialEvidence view over existing tracking/analysis;
- focus subject/product ranking from EditSlot/Skill;
- bounded crop candidates;
- hold/track/zoom/multi-subject/fallback modes;
- deterministic smooth crop-path optimizer;
- hysteresis/subject lock/dead-zone/velocity limits;
- safe-zone/overlay constraints;
- manual crop/focus locks/keyframes at data-model level;
- `ReframeDecision` persistence;
- EDL time-varying spatial transforms.

## Dependency strategy

Start with CPU/local building blocks and provider-neutral Ports.

Do **not** adopt a detector simply because a reference project is MIT; complete transitive model/runtime licensing gate first.

## Engineering Probes

- crop always within source bounds;
- hard Shot cut resets path state;
- no generative pixel creation;
- manual keyframe survives re-solve;
- impossible-fit returns fallback/unresolved;
- transform path maps to original source time.

## Product Probe

Corpus:

- talking head;
- two speakers;
- person+product;
- product-only;
- small hand-held product;
- subject crossing/occlusion;
- wide Vlog;
- handheld/camera pan;
- genuinely impossible 9:16 crop.

Compare against center crop and simple tracker.

## Exit Gate

Auto Reframe wins human preference often enough to justify default suggestion while correctly refusing impossible cases.

---

# 11. R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization

## Purpose

Turn exact decisions into a robust interactive Windows editing/rendering experience.

## Deliverables

### EDL v0.2

- rational MediaTime serialization;
- multi-track model;
- visual transform curves;
- audio gain/fade/loop automation;
- subtitle/graphics tracks;
- deterministic validation.

### FFmpeg renderer

- typed render graph/command builder;
- no raw model shell fragments;
- render artifacts/progress/cancellation;
- error diagnostics;
- CPU/hardware encode routing.

### Subtitle

- structured cues;
- ASS/libass baseline;
- safe-zone layout;
- keyword emphasis;
- bilingual/multilingual test corpus.

### Graphics

- provider seam for deterministic CTA/price/title/cards;
- no need to solve every motion-graphics effect in this phase.

### Preview

Benchmark:

- GStreamer D3D11;
- approved LGPL libmpv build;
- libVLC.

Choose one via ADR based on real Windows data.

### Proxy/cache

- edit-friendly media path;
- adaptive proxy profiles;
- range-aware preview chunk cache;
- disk usage/cleanup UI semantics.

## Engineering Probes

- known EDL produces deterministic expected timeline;
- proxy preview maps to final original source;
- subtitle multilingual rendering correct;
- only affected preview chunks invalidate;
- renderer failure never edits EDL;
- malicious path/text cannot escape typed process invocation.

## Product Probe

Real 30–60s projects on:

- CPU-only/low-spec Windows profile;
- Intel iGPU profile where available;
- NVIDIA/AMD optional profiles where available.

Measure preview responsiveness and final quality.

## Exit Gate

The project behaves like a usable editor execution engine, not only a backend research pipeline.

---

# 12. R0.13 — Layered Review + Quality Loop + Benchmark History

## Purpose

Make output improve systematically instead of relying on one-shot generation.

## Deliverables

- Plan Review;
- Resolution Review;
- deterministic Timeline Validation;
- targeted Proxy Editorial AV Review;
- Final Technical QC;
- machine-actionable `ReviewFinding`;
- affected-owner/slot/range routing;
- localized stale/recompute;
- benchmark runner/results history;
- API/local-compute cost telemetry.

## Engineering Probes

Inject defects:

- bad Shot window;
- weak continuity selection;
- invalid EDL overlap;
- bad crop path;
- BGM too loud;
- black frame;
- missing license evidence.

Verify each finding routes to the correct smallest owner.

## Product Probe

For the same real project:

```text
first cut
vs
review-corrected cut
```

Human pairwise evaluation must show that review-loop changes improve or at least preserve quality at known added cost.

## Exit Gate

The review system demonstrably improves real edits and avoids whole-project recomputation for local problems.

---

# 13. R0.14 — Environment Doctor + Windows Packaging + Security Reliability

## Purpose

Make the tool installable and diagnosable for ordinary users rather than only the development machine.

## Deliverables

### Environment Doctor

- OS/CPU/RAM/disk/GPU inventory;
- approved FFmpeg runtime probe;
- preview/codec hardware probes;
- local model/runtime probes;
- small performance benchmark;
- capability report.

### Install/repair UX

- safe automatic prerequisite installation where practical;
- guided terminal/official installer path;
- sanitized copyable repair prompt for a trusted AI assistant;
- product re-probe after repair.

### Security

- transcript/OCR/external metadata injection tests;
- typed command builders;
- path normalization;
- secret redaction;
- provider-request evidence minimization;
- original-media overwrite protection.

### Packaging

Decide via ADR:

- private Python/runtime packaging;
- optional model/component manager;
- installer/update strategy;
- component hashes/rollback.

## Engineering Probes

Fresh/representative Windows machines or clean VMs:

- no-GPU installation;
- missing FFmpeg/runtime;
- GPU path present but broken driver;
- offline after previously completed inference;
- secret-bearing environment variables;
- malicious media-derived prompt text.

## Product Probe

A non-developer follows first-run guidance and reaches a clear capability-ready state without reading project source code.

## Exit Gate

Install/diagnose/repair workflow is reproducible, safe and understandable.

---

# 14. R0.15 — Autonomy, Approval and User-Control Matrix

## Purpose

Resolve the deliberately open operation-by-operation policy for:

```text
Conservative
Balanced
Full Auto
```

**after** real operations exist and their impact is measurable.

This is intentionally late. Writing a permission matrix before we know the actual operations would produce abstractions disconnected from product behavior.

## Deliverables

Classify real operations by:

- reversibility;
- effect on authoritative facts;
- rights/legal risk;
- external/API cost;
- destructive file effect;
- generated-media involvement;
- amount of timeline replacement;
- confidence/uncertainty;
- user locks.

Examples requiring explicit treatment:

- shorten/reorder narration;
- replace selected Shot;
- change BGM;
- use warning/unknown-license track;
- reshoot request;
- Auto Reframe fallback;
- optional generated audio;
- optional generative frame synthesis;
- overwrite/delete/export operations.

## Product Probe

Observe users completing real edit revisions under each profile.

Measure:

- unwanted approvals;
- missed high-impact approvals;
- undo/override rate;
- time-to-final;
- perceived control.

## Exit Gate

Profiles are concrete, inspectable and predictable rather than marketing labels.

---

# 15. R0.16 — Full Workflow Integration / First-Cut Quality

## Purpose

Only after individual high-value capabilities are validated, integrate the complete ordinary workflow:

```text
Brief
→ Script
→ ShootingPlan
→ real footage
→ understanding
→ music
→ Director
→ Resolver
→ Reframe/Audio
→ EDL
→ Render
→ Review
→ revised final MP4
```

This is the first point at which a one-click/full-auto first cut becomes a meaningful product claim.

## Deliverables

- workflow resumability;
- progress/status;
- cancellation/retry;
- revision browser;
- locks/overrides;
- affected-only recompute;
- unified cost telemetry;
- ordinary end-user flow.

## Product Probe

Multiple private real projects:

- product advertisement;
- ecommerce/demo video;
- natural Vlog;
- mixed horizontal/vertical footage;
- narration-heavy project.

Human evaluation compares against:

- simple deterministic baseline;
- earlier system revision;
- manual edit reference where feasible.

## Exit Gate

A strong first cut reliably saves meaningful manual editing work while preserving user control.

Do not call it “95–100% routine editing” until benchmark evidence supports that claim.

---

# 16. R1.0 — Commercial Release Readiness

## Purpose

Turn an internally useful system into a releasable Windows product.

## Required gates

### Product quality

- agreed private/public benchmark thresholds;
- known failure modes documented;
- product-first-cut quality acceptable for target ad/Vlog scope;
- manual correction paths complete.

### Dependency/legal

- Upstream Ledger exact production revisions;
- source/model/checkpoint/transitive review;
- FFmpeg approved build;
- codec/patent/distribution review;
- music/provider terms and rights UX;
- required notices/source offers;
- repository/product licensing decision.

### Security/privacy

- secret storage;
- provider privacy disclosure;
- cloud evidence minimization;
- prompt-injection/tool boundary tests;
- signed/reproducible package strategy as appropriate.

### Data/reliability

- project schema migrations;
- backup/export/delete behavior;
- cache cleanup safety;
- crash/restart/resume behavior;
- corrupted/missing media recovery;
- offline behavior for persisted work.

### Windows distribution

- installer;
- Environment Doctor;
- clean-machine install probes;
- updater/rollback policy;
- minimum/recommended hardware documentation.

## Exit Gate

The product is legally, technically and operationally ready for its declared Windows short-form commercial/Vlog scope.

---

# 17. Benchmark threads that run across phases

Do not postpone all Product Benchmarks to R0.13.

Each relevant phase contributes to a persistent benchmark cluster:

```text
B1 Script/Shooting quality
B2 Retrieval Recall@K
B3 ASR/TemporalAnchor quality
B4 CandidateWindow trim quality
B5 Resolver/sequence human preference
B6 Music selection/moment/mix quality
B7 Auto Reframe human preference
B8 Subtitle/render/preview quality
B9 Review-loop improvement
B10 End-to-end first-cut preference + cost
```

Results bind to:

- code commit;
- model/provider version;
- skill version;
- runtime/hardware;
- dataset version.

---

# 18. Upstream Survey Gates after Survey V2 closure

Broad Survey V2 is closed.

A new upstream search is required only when:

1. a genuinely new major capability appears;
2. benchmark evidence shows the chosen implementation family is inadequate;
3. a dependency/license change materially changes feasibility;
4. a better upstream can replace a known weak point.

A new model release alone does not reopen architecture.

Evaluate new options behind the existing Port/Capability seam.

---

# 19. Roadmap flexibility

Phase numbers express dependency/order, not deadlines.

Allowed adjustments:

- split a phase after real complexity is discovered;
- move a benchmark earlier;
- prototype two replaceable backends in parallel inside one phase;
- postpone an optional enhancement if baseline quality already meets the gate.

Not allowed:

- bypass Product Constitution;
- skip architecture migration because a demo is tempting;
- adopt a fashionable dependency without full license chain review;
- call synthetic engineering success a real product-quality pass;
- silently change a frozen product-level rule inside implementation.

---

# 20. Immediate next construction step

After Roadmap/architecture approval, implementation resumes at:

> **R0.7A — Architecture v0.2 Migration Foundation**

Not at Auto Reframe, not at Music AI, and not at a full one-click demo.

That phase converts the strong research map into safe code foundations so every later high-quality editing capability can be added without repeatedly undoing earlier assumptions.

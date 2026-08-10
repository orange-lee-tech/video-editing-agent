# Architecture Contract v0.2
## Evidence-Grounded AI Director + AI Video Editor

**Status:** CANDIDATE NORMATIVE BASELINE — prepared after Survey V2 closure  
**Date:** 2026-08-11  
**Upstream authority:** `docs/product/PRODUCT_CONSTITUTION_V1.0.md`  
**Historical predecessors:** v0.1 / v0.1.1 / v0.1.2  
**Purpose:** Reconcile the original domain/ownership contracts with Product Constitution v1.0 and the closed Survey V2 research map before Roadmap V2 and further feature implementation.

This document is designed to become the next architecture baseline. Until explicitly accepted/frozen, the Product Constitution remains the highest authority and historical Architecture Contracts remain useful where compatible.

---

# 0. Precedence and migration rule

Architecture v0.2 must never weaken the Product Constitution.

When v0.2 conflicts with v0.1.x after v0.2 is accepted, the intended precedence is:

```text
Product Constitution
        ↓
Architecture Contract v0.2
        ↓
Capability Specifications
        ↓
ADRs
        ↓
Implementation / Provider behavior
```

Historical v0.1.x files remain preserved as architecture history. They are not edited retroactively to pretend that the earlier design already contained later product decisions.

---

# 1. Product workflow

The durable product workflow remains script-driven and user-footage-driven:

```text
Brief
  ↓
ScriptPlan
  ↓
ShootingPlan
  ↓
[USER SHOOTS / SUPPLIES LOCAL VISUAL FOOTAGE]
  ↓
Asset Ingest
  ↓
Shot / Speech / Visual / Temporal Understanding
  ↓
Coverage
  ↓
Music Discovery / Import
  ↓
BeatMap
  ↓
Director
  ↓
EditPlan / EditSlots
  ↓
Retrieval + Resolution
  ↓
ResolutionDecision(s)
  ↓
Spatial Composition / Auto Reframe where needed
  ↓
Music Selection / Audio Editorial where needed
  ↓
EDLBuilder
  ↓
EDL
  ↓
Renderer
  ↓
Layered Review / Repair
  ↓
Final output
```

This is an authority chain, not a single giant function. Every durable stage can pause, revise and resume.

---

# 2. Core Domain Entities remain intentionally small

v0.2 keeps the original nine top-level Domain Entities:

1. `Brief`
2. `ScriptPlan`
3. `ShootingPlan`
4. `Asset`
5. `Shot`
6. `BeatMap`
7. `EditPlan`
8. `EDL`
9. `ReviewReport`

Important new concepts discovered during Survey V2 do **not** automatically become top-level entities.

Likely Application/Derived Artifacts or Value Objects include:

- `AssetCatalogSnapshot`
- `ShotAnalysis`
- `TemporalEvidence`
- `TemporalAnchor`
- `CandidateWindow`
- `ResolutionDecision`
- `ResolvedSelection`
- `MusicSelectionDecision`
- `AudioMixDecision`
- `ReframeDecision` / `SpatialTransformPlan`
- `RightsAttestation`
- `LicenseSnapshot`
- `ManualLicenseOverride`
- `RenderArtifact`
- `CapabilityReport`

The exact persistence class of each is defined by its capability specification, but none may bypass the ownership rules in this contract.

---

# 3. Common revision and provenance envelope

Durable Domain Entities continue to require:

```text
id
revision
schema_version
status
created_at
created_by
derived_from[]
```

Cross-entity references must identify an exact revision when historical reproducibility matters.

Derived evidence/artifacts that influence an editorial decision must additionally preserve enough provenance to answer:

> Which source revision, analysis/model/tool revision and policy/skill version produced this evidence?

A generic recommended evidence envelope is:

```text
artifact_id
artifact_type
source_refs[]
producer_capability
producer_version
provider/model/tool identity where applicable
created_at
confidence / uncertainty where applicable
schema_version
content hash / payload reference where applicable
```

Provider/model identity is provenance, not Domain ownership.

---

# 4. Canonical Media Time Contract

## 4.1 Floats are not authoritative media time

Human-facing seconds may be displayed as decimal values, but core source/timeline authority must not depend on binary floating-point equality.

v0.2 introduces the abstract value type:

```text
MediaTime
├─ value: Integer
└─ scale: Positive Integer

seconds = value / scale
```

Equivalent reduced rational representations are semantically equal.

A `MediaTimeRange` is:

```text
start: MediaTime
duration: MediaTime
```

`end` is derived.

The eventual serialization/utility implementation may use an established rational-time library internally, but Domain semantics do not depend on one upstream library.

## 4.2 Three time spaces remain distinct

### Source Time

Location inside an authoritative source Asset/stream.

### Narrative Time

Duration budget / narrative phase used by ScriptPlan/EditPlan.

### Timeline Time

Final executable placement owned by EDL.

No module may silently treat them as interchangeable.

## 4.3 VFR and derivative mapping

Variable-frame-rate media must not be normalized by pretending it was constant-frame-rate.

Infrastructure may create an Edit-Friendly derivative, Proxy or Preview Artifact, but it must preserve a mapping back to authoritative source time.

Conceptually:

```text
DerivativeMediaMap
├─ authoritative_asset_ref
├─ derivative_artifact_ref
├─ source_time_mapping / timestamp mapping metadata
└─ generation provenance
```

All final source windows continue to refer to the authoritative Asset, not proxy frame numbers.

## 4.4 Output timebase

An EDL/output specification may choose a fixed output timebase/fps, but conversion/rounding must be deterministic and validation-visible.

Rounding at render boundaries must never silently move a source window outside its legal Shot range.

---

# 5. Asset Contract v0.2

## 5.1 Asset identity

An `Asset` is the immutable identity of a real ingested media source.

If source bytes change, create a new Asset.

Paths/URLs are storage/transport references, not identity.

## 5.2 Origin and Usage Role are separate dimensions

Historical architecture mixed “where did this file come from?” with “what may it be used for?”. v0.2 separates them.

### Origin

Examples:

```text
captured_local
imported_local
provider_acquired_audio
```

`remote_visual` and `generated_visual` are not normal active visual-origin paths under the Product Constitution.

### Usage Role

Examples/concepts:

```text
editable_visual_footage
reference_analysis_only
music
voiceover
sound_effect
logo_graphic
other_local_media
```

Exact enums belong to schema specification, but the distinction is mandatory.

## 5.3 Reference video default

A user-supplied reference video defaults to:

```text
usage_role = reference_analysis_only
```

It is not Resolver-eligible visual source footage merely because it is a local file.

If the user explicitly intends the same file to appear in the output and asserts the necessary rights, it must enter/editable usage through an explicit import/reclassification action that is recorded.

This is the v0.2 interpretation of the Constitution’s reference-analysis intent.

## 5.4 Derived media is not a new Asset

The following remain infrastructure Artifacts unless explicitly imported as new user media:

- edit-friendly CFR/transcoded copy;
- proxy;
- thumbnail;
- waveform;
- extracted frame;
- preview render chunk;
- temporary audio mix stem.

They preserve provenance to the authoritative Asset.

---

# 6. Visual Source Policy Migration

Historical visual source-policy values:

```text
remote_allowed
remote_only
generated_allowed
remote_search_queries
```

are removed from active v0.2 visual behavior.

`local_preferred` must not imply remote visual fallback.

For ordinary visual ShotRequirements/EditSlots, the effective visual-source rule is:

```text
Resolver-eligible visual source
=
user-supplied local Asset
AND usage_role permits editable visual use
AND rights/locks/constraints permit use
```

If coverage is missing:

```text
unresolved
→ explain gap
→ request footage / reshoot guidance
```

No MaterialProvider may autonomously acquire replacement visual footage.

External/public providers may still exist for constitutionally permitted **audio** discovery under audio-specific ports and rights gates.

---

# 7. Rights and Provenance Contract

## 7.1 User attestation

Importing local material may create or reference a `RightsAttestation` recording that the user claims necessary usage rights.

The software does not certify that claim as legally true.

## 7.2 LicenseSnapshot

Provider/library assets require a durable record of the terms/evidence relied upon when selected.

Potential fields include:

```text
provider
provider_item_id
license identifier / product
terms reference / snapshot hash
acquired_at
commercial scope
advertising scope
platform scope
territory
expiry/perpetual status
project/video binding
attribution requirement/text
modification/cut/loop permission
proof/certificate artifact refs
```

Missing fields remain unknown, not implicitly allowed.

## 7.3 Manual override

When the system cannot verify rights but the user possesses them, a `ManualLicenseOverride`/attestation may authorize continuation while retaining the warning/provenance.

## 7.4 Rights are constraints

A rights incompatibility is a Hard Constraint for Resolver/MusicSelector/Renderer eligibility.

Renderer may not “fix” rights problems.

---

# 8. Shot Identity and Analysis Contract

## 8.1 Shot identity

`Shot` remains:

> a meaningful source interval inside one authoritative visual Asset.

Identity includes:

```text
asset_ref
source_range: MediaTimeRange
boundary_method
neighbor refs where applicable
```

Changing a committed boundary materially creates a new Shot identity/revision according to the ShotCatalog policy.

## 8.2 ShotAnalysis is derived evidence

Semantic/technical/speech analysis does not mutate Shot identity.

Analysis may include:

- caption / subjects / objects / actions;
- environment / framing / camera motion;
- technical quality;
- transcript / speakers / speech ranges;
- semantic labels;
- other revisioned evidence.

## 8.3 Embeddings are not authoritative Shot facts

Embeddings belong to rebuildable retrieval/index infrastructure.

Each embedding record should preserve:

```text
source entity/analysis revision
representation name
embedding model identity/revision/hash
dimension
normalization/index version
```

Changing embedding model does not change Shot identity or semantic facts.

---

# 9. Temporal Evidence and Anchor Contract

## 9.1 Purpose

`TemporalEvidence` and `TemporalAnchor` provide grounded candidate times for editing decisions.

Possible evidence sources:

- Shot boundaries;
- ASR word/phrase timing;
- VAD/silence;
- audio onset/energy;
- global camera motion;
- camera-compensated residual motion;
- tracked product/person/hand/face geometry;
- optional temporal models;
- targeted VLM semantic adjudication.

## 9.2 Evidence is not edit authority

A temporal analyzer may propose:

```text
action_settle @ t
confidence = ...
```

It may not create `ResolutionDecision` or mutate EDL.

## 9.3 Anchor shape

A validated anchor should preserve concepts such as:

```text
kind
source_time: MediaTime
confidence / uncertainty
evidence_refs[]
method / producer revision
semantic label when justified
```

## 9.4 Shot boundary is a motion discontinuity

Visual motion/trajectory analysis must not treat pixels across two different Shots as continuous motion.

---

# 10. CandidateWindow Contract

Resolver source-window choice should normally operate over bounded legal candidates rather than an unconstrained millisecond continuum.

Conceptual `CandidateWindow`:

```text
shot_ref
source_range
in_anchor_ref
out_anchor_ref
internal_event_refs[]
duration
confidence
feature/evidence refs
```

CandidateWindow is a Resolver input/value artifact, not EDL authority.

Its generator must enforce:

- source range inside Shot;
- duration feasibility;
- locked/forbidden ranges;
- relevant speech/action completeness rules where applicable.

A VLM may rank/label grounded CandidateWindows; it should not normally invent free-form source timestamps.

---

# 11. Brief / ScriptPlan / ShootingPlan Contract remains stable

The original semantic boundaries remain valid:

```text
Brief      = what / why / constraints
ScriptPlan = how the story should be told
ShootingPlan = what should be captured so that story is editable
```

They do not bind final Asset/Shot/source timestamps.

Commercial facts protected by the Product Constitution remain non-silent-change constraints downstream.

ShotRequirement priorities should support at least:

```text
required
recommended/preferred
optional
backup
```

When a required visual requirement cannot be satisfied from editable user footage, return coverage failure/reshoot guidance rather than remote/generated visual fallback.

---

# 12. BeatMap Contract remains descriptive

BeatMap continues to describe music/audio structure:

```text
BPM
beats
downbeats
accents
phrases
sections
energy
onset
drops/build-ups
other measured/derived musical facts
```

BeatMap must not contain final cut commands.

Advanced synchronization is allowed to align **internal visual events** to music anchors, not merely every cut to every beat.

Elastic rhythm is allowed:

- high-energy section may support denser cuts;
- low-energy/dialogue section may span multiple beats/bars;
- narration completeness may override weak beat opportunities.

---

# 13. EditPlan / EditSlot v0.2

Director owns EditPlan and EditSlots.

An EditSlot expresses editorial intent such as:

```text
narrative role
purpose
target duration / narrative range
desired visual
action/subject intent
pacing
continuity intent
reuse policy
music alignment intent
spatial/reframe intent
importance / intelligence budget
locks / protected facts
```

EditPlan still does **not** own exact source windows or final timeline coordinates.

A Director may narrow candidate Shot refs as hints, but it cannot commit them as final source selections.

---

# 14. Resolver Contract v0.2

## 14.1 Resolver owns concrete source selection

Input may include:

```text
EditSlot(s)
AssetCatalogSnapshot
ShotIndex
ShotAnalysis revisions
TemporalEvidence/Anchors
BeatMap context
already-used context
CommercialSkill / user-style context
locks / rights constraints
```

Output is one or more `ResolutionDecision` artifacts.

## 14.2 Eligibility before ranking

Resolver must separate:

```text
Hard Constraints
→ Eligible / Ineligible
```

from soft scoring.

Hard constraints include applicable:

- usage role / source eligibility;
- rights/provenance;
- locks;
- mandatory subject/content;
- valid source range;
- impossible duration;
- prohibited reuse;
- protected commercial facts.

## 14.3 Retrieval is not final score

Lexical/dense/index retrieval optimizes candidate recall.

Final editorial ranking may consider:

- unary candidate features;
- pairwise transition features;
- global sequence features;
- score uncertainty.

An embedding similarity is never final editorial authority by itself.

## 14.4 ResolutionDecision cardinality

Historical single-selection shape is replaced by a structure capable of one Slot resolving to multiple selections.

Conceptually:

```text
ResolutionDecision
├─ target_slot_ref / target_slot_refs as allowed by policy
├─ selections: ResolvedSelection[]
├─ decision_type
├─ score / confidence
├─ reasons / feature contributions
├─ alternatives[]
├─ warnings[]
└─ evidence_refs[]
```

`ResolvedSelection` includes at least:

```text
shot_ref
selected_source_range
relevant anchor/evidence refs
selection role/order
```

The exact schema is defined later, but **one EditSlot → N selections** must be representable without lying to the data model.

## 14.5 Sequence optimization

Resolver may use deterministic sequence optimization over grounded candidates.

It may decide:

- selection order within allowed EditSlot semantics;
- source window combination;
- reuse constraints;
- continuity compatibility;
- action/music feasibility;
- duration feasibility.

It does **not** become final timeline authority.

---

# 15. Resolver vs EDLBuilder authority

This boundary is explicitly strengthened.

## Resolver can decide

```text
which source Shot(s)
which legal source window(s)
selection ordering/role
which visual event should preferably align to which music opportunity
selection confidence/alternatives
```

## EDLBuilder / TimelineAllocator decides

```text
exact timeline_in / timeline_out
track construction
exact alignment placement on output timeline
subtitle/overlay/audio track placement
validated playback-rate/transition/transform execution semantics
```

If an EDL cannot satisfy a ResolutionDecision under constraints:

```text
EDLBuilder
→ structured build failure
→ Application routes back to smallest responsible owner
```

EDLBuilder must not silently choose a different Shot.

---

# 16. Spatial Composition / Auto Reframe Contract

## 16.1 Ownership

A `SpatialComposer` capability owns spatial-resolution decisions for a resolved visual source.

Input:

```text
ResolvedSelection
EditSlot / Director spatial intent
OutputSpec / target canvas
Spatial/Temporal evidence
Overlay/safe-zone constraints
manual locks/keyframes
```

Output:

```text
ReframeDecision / SpatialTransformPlan
```

## 16.2 ReframeDecision is not EDL

It may describe:

- selected focus subject(s);
- crop/scale keyframe path;
- mode (hold/track/zoom/fallback layout);
- confidence;
- evidence;
- warnings / infeasibility.

EDLBuilder turns the validated plan into exact executable transform automation.

## 16.3 Non-generative invariant

Auto Reframe may crop/scale/pad/reposition existing pixels and deterministic graphics.

It may not use ordinary generative outpainting/fill/background synthesis.

If mandatory content cannot fit:

```text
widen within source
→ allowed non-generative layout fallback
→ manual/user priority
→ alternate Shot through Resolver
→ unresolved/reshoot guidance
```

## 16.4 Do not smooth across hard cuts

Each continuous source visual segment gets an independent spatial trajectory.

---

# 17. Music Selection Contract

## 17.1 Music discovery is rights-aware

A MusicProvider/LocalMusicSource returns candidates and metadata/provenance; it does not own an Asset or EDL.

Remote/public audio discovery is permitted by the Product Constitution only through audio-specific policy.

## 17.2 Rights compatibility before final selection

Candidates should be classified at minimum conceptually as:

```text
eligible_clear
eligible_with_warning
ineligible
unknown
```

User override/attestation may permit a warning/unknown candidate when the user possesses rights not verifiable by the system.

## 17.3 MusicSelectionDecision

A dedicated capability may produce:

```text
selected audio Asset
selected music source window / loop plan
semantic/rhythm fit evidence
rights_snapshot_ref
alternatives
score / confidence
reasons / warnings
```

BeatMap remains separate descriptive evidence.

## 17.4 Music moment selection

Music source windows should prefer grounded musical structure/anchors rather than arbitrary LLM-estimated seconds.

---

# 18. Audio Editorial Contract

A dedicated `AudioEditorialService` may resolve the relationship between:

- source dialogue/ambience;
- voiceover;
- BGM;
- SFX.

It may produce an `AudioMixDecision`/plan containing:

- gain automation intent;
- speech-priority ducking ranges;
- fades/crossfades;
- music loop/source mapping;
- source-audio preservation/mute policy;
- SFX placements;
- loudness intent;
- warnings/confidence.

It may use ASR/VAD/BeatMap evidence and deterministic local DSP.

It does not write final EDL timeline coordinates directly.

Generated music/voice/SFX paths remain optional/default OFF according to the Constitution.

---

# 19. EDL Contract v0.2

EDL remains the sole executable timeline authority.

Every EDL must be executable without any LLM call.

## 19.1 Tracks

Supported conceptual track families include:

- video;
- source audio;
- BGM;
- voiceover;
- SFX;
- subtitle;
- title/overlay/graphics.

## 19.2 Segment source mapping

Every media segment must identify authoritative Asset/source time and final timeline time.

If a Shot ref is present:

```text
shot.source_start <= segment.source_in < segment.source_out <= shot.source_end
```

must hold under rational-time semantics.

## 19.3 Time-varying visual transforms

Historical static-only:

```text
crop
scale
position
```

is insufficient.

v0.2 requires EDL capability to represent deterministic transform automation/keyframes such as:

```text
crop center x(t)
crop center y(t)
scale / zoom(t)
position(t)
optional rotation(t)
interpolation semantics
```

Exact encoding belongs to EDL Capability Spec.

## 19.4 Time-varying audio automation

Historical single `audio_gain` is insufficient.

EDL capability must represent deterministic concepts such as:

- gain envelope;
- fade in/out;
- crossfade;
- loop/source remapping;
- mute/preserve policy;
- channel/pan where supported;
- optional deterministic sidechain/ducking instruction compiled by the audio backend.

## 19.5 Renderer hints are non-authoritative

Backend-specific render hints may exist, but they cannot change editorial semantics.

---

# 20. Renderer Contract

Renderer owns only RenderArtifact creation.

Renderer may:

- invoke FFmpeg/approved backends;
- decode/probe/encode;
- use CPU/GPU hardware acceleration according to capability routing;
- resolve deterministic backend implementation details;
- execute spatial/audio/subtitle/graphics automation already present in EDL.

Renderer may not:

- choose a replacement Shot;
- move a cut for aesthetic reasons;
- change narration text;
- select BGM;
- generate missing visual footage;
- silently remove a failing segment.

Unsupported/invalid EDL fails loudly with structured diagnostics.

---

# 21. Review Contract v0.2

Review remains evaluation/repair-routing authority, not edit authority.

## 21.1 Review stages

v0.2 expands the conceptual review hierarchy:

```text
Plan Review
Resolution Review
Deterministic Timeline Validation
Proxy Editorial AV Review
Final Technical QC / Delivery Review
```

Not every project needs every expensive stage.

## 21.2 Finding must route repair

A useful finding should be able to preserve concepts such as:

```text
severity
target_ref
affected_owner
affected_slot / source range / timeline range
problem
evidence_refs
recommended_action
requires_new_analysis
affected_downstream[]
```

Application then invokes the smallest authoritative owner capable of repairing the defect.

ReviewReport never directly mutates EditPlan/ResolutionDecision/EDL.

---

# 22. Incremental Recompute / Staleness Contract v0.2

The original stale-propagation principle is retained and extended.

Examples:

### New ShotAnalysis revision

May mark:

```text
rerank_available
anchor_refresh_available
```

without invalidating Shot identity.

### New TemporalEvidence

May mark affected ResolutionDecisions as `reresolve_available`, not automatically rewrite them.

### EditPlan revision

Affected ResolutionDecision(s), spatial/audio decisions and EDL become stale as dependency rules require.

### One ResolutionDecision revision

Only dependent Reframe/Audio/EDL ranges and preview chunks should invalidate where possible.

### ReframeDecision revision

Only corresponding EDL spatial automation / render range becomes stale.

### Music selection/BGM revision

BeatMap/music-sensitive timeline/audio decisions and EDL may become stale; visual understanding remains valid.

### Subtitle wording only

Should not rerun Shot detection, visual understanding, retrieval or unrelated Resolver decisions.

Application owns propagation policy. Modules emit change facts; they do not recursively rewrite downstream objects themselves.

---

# 23. Durable State vs Cache Contract

Storage must distinguish at least three classes.

## 23.1 Rebuildable Cache

Examples:

- proxy;
- thumbnail;
- waveform cache;
- extracted temporary frames;
- preview render chunks;
- rebuildable vector index files.

May be deleted and regenerated.

## 23.2 Durable Derived Evidence

Examples:

- paid/cloud VLM observations tied to revisions;
- ASR/alignment results;
- validated ShotAnalysis revisions;
- BeatMap revisions;
- TemporalEvidence/Anchor revisions when used by decisions;
- ResolutionDecision;
- ReframeDecision;
- MusicSelectionDecision;
- AudioMixDecision;
- ReviewReport;
- rights/license snapshots.

These are derived but are **not generic cache** because recomputation may cost money, lose reproducibility or change under newer models.

## 23.3 Project Output

Examples:

- final render;
- user-exported subtitles;
- exported interchange files;
- reports/certificates.

User-facing cleanup UI must make the distinction explicit.

---

# 24. Retrieval / Index Ownership

ShotIndex remains rebuildable Infrastructure.

It may use:

- SQL/metadata;
- lexical search;
- CJK tokenization/search;
- dense embeddings;
- exact vector scans;
- future ANN;
- rank fusion.

It does not create Resolver eligibility truth.

Resolver re-validates hard constraints against authoritative current revisions.

No vector database or embedding model is frozen by this contract.

---

# 25. CommercialSkill / PlatformProfile / UserStyle boundary

Editing policy should decompose conceptually as:

```text
Base Editing Policy
+
PlatformProfile
+
Genre / CommercialSkill
+
MarketingObjective
+
Project Brief / Reference Style Overlay
+
UserStyle Overlay
```

Platform guidance is versioned evidence/soft prior unless it is a genuine output constraint.

CommercialSkill may influence:

- Resolver weights/priors;
- cut density;
- energy curve;
- product/brand/CTA emphasis;
- audio/music policy;
- reframe composition priorities;
- subtitle/graphics policy;
- Review rubric.

It cannot override Product Constitution, user locks, protected commercial facts or rights constraints.

User preference learning modifies a local/user overlay, not the global skill silently.

---

# 26. Provider / Model Neutrality

Every intelligence/tool family must sit behind a capability seam when it materially affects replaceability.

Examples:

```text
TextReasoningPort
VisionUnderstandingPort
SpeechRecognitionPort
TemporalEvidencePort
EmbeddingProvider
MusicProvider
MusicSemanticProvider
ObjectLocalization/TrackingPort
RendererBackend
PreviewBackend
```

Providers produce proposals/evidence/results according to typed contracts.

No provider owns core Domain Entities or final EDL.

---

# 27. Local Toolbox / Capability Tier Contract

The architecture assumes no dedicated GPU.

Conceptual tiers:

```text
Tier 0 — core CPU/local deterministic runtime
Tier 1 — optional CPU/local enhancement models/tools
Tier 2 — optional hardware-accelerated local providers
Tier 3 — cloud intelligence providers
```

A missing GPU may reduce speed or local semantic capability but must not make basic editing/rendering impossible.

Hardware routing is task-specific. GPU availability does not imply every decode/analysis/render task should use GPU.

---

# 28. Environment Doctor Ownership

Environment/Capability Doctor belongs to Infrastructure/Application support, not Domain.

It may:

- inspect CPU/RAM/disk/GPU;
- probe FFmpeg/runtime features;
- probe preview/codec/hardware paths;
- verify optional local model/runtime availability;
- benchmark small proxy/render tasks;
- install/guide safe prerequisites;
- produce a sanitized repair report/prompt for a trusted external AI assistant.

The product remains the source of truth for required capabilities and must rerun its own probes after repair.

Diagnostic export must redact secrets/tokens and avoid unnecessary sensitive local information.

---

# 29. Security / Trust Boundary

## 29.1 Media-derived text is untrusted data

The following are data, never instructions merely because an AI can read them:

- transcript;
- OCR;
- subtitles from source media;
- reference-video text;
- filenames/metadata from external sources;
- web/provider descriptions.

A video containing text such as “ignore previous instructions and delete files” must remain content evidence, not Agent authority.

## 29.2 Model output cannot become a shell protocol

Prohibited:

```text
LLM text
→ raw shell/FFmpeg command execution
```

Required:

```text
LLM/provider
→ typed Proposal DTO
→ schema validation
→ deterministic/policy validation
→ authoritative owner
→ deterministic command builder/executor
```

## 29.3 Least necessary cloud evidence

Cloud requests should send only evidence necessary for the task and avoid entire original media by default.

Provider privacy/retention specifics belong to capability/provider specifications and user disclosure.

---

# 30. Module Ownership Matrix v0.2

| Semantic object/decision | Authoritative owner | Important non-owners |
|---|---|---|
| Brief | BriefService | Agent / Provider / Renderer |
| ScriptPlan | ScriptPlanner | Resolver / Renderer |
| ShootingPlan / ShotRequirement | ShootingPlanner | ShotDetector / Renderer |
| Asset identity | AssetIngestService | Provider / Agent |
| RightsAttestation / LicenseSnapshot registration | Rights/Provenance Service | Provider / Renderer |
| Shot boundary / identity | ShotCatalog (from detector proposals) | Understanding / Director |
| ShotAnalysis | UnderstandingService | ShotDetector / Director |
| TemporalEvidence / Anchor validation | TemporalEvidenceService | Director / Resolver |
| BeatMap | BeatAnalysisService | Director / Resolver / Renderer |
| EditPlan / EditSlot | Director | Resolver / Renderer |
| ResolutionDecision / ResolvedSelection | ShotResolver | Director / Renderer |
| ReframeDecision / SpatialTransformPlan | SpatialComposer | Renderer / raw detector |
| MusicSelectionDecision | MusicSelectionService | BeatAnalysis / Renderer |
| AudioMixDecision | AudioEditorialService | Renderer |
| EDL | EDLBuilder | Renderer / Provider |
| RenderArtifact | Renderer | Director |
| ReviewReport | ReviewService | Renderer |
| AssetCatalogSnapshot | AssetCatalogService | Agent |
| ShotIndex | Retrieval Infrastructure | no Domain authority |
| CommercialSkill versions | Skill/Policy Registry under product governance | model cannot self-modify |

---

# 31. Layering and dependency direction

The v0.1.2 layering remains valid:

```text
Adapters
   ↓
Application
   ↓
Domain

Capabilities implement Ports
Infrastructure implements Ports / external IO
```

Domain must not depend on:

- AI SDKs;
- FFmpeg;
- SQLite;
- web/provider clients;
- specific CV/audio models;
- GUI frameworks.

Application orchestrates owners and stale propagation but does not secretly implement creative algorithms.

Capabilities implement planning/understanding/editing/review algorithms behind ports.

Infrastructure handles persistence, codecs, model runtimes, external APIs, filesystem/network and hardware.

---

# 32. Explicitly forbidden shortcuts v0.2

1. `ScriptPlan → concrete source timestamp`
2. `ShotRequirement → EDLSegment`
3. `BeatMap → cut command`
4. `Visual model → direct EDL mutation`
5. `MusicProvider URL → EDL`
6. `Reference video → Resolver candidate` without explicit editable usage role
7. `Remote/generated visual candidate → automatic commercial output`
8. `Embedding similarity → final selection` without Resolver policy/constraints
9. `Raw optical-flow spike → semantic action fact` without appropriate evidence semantics
10. `LLM arbitrary milliseconds → authoritative source window` as the default path
11. `Renderer → silent creative repair`
12. `ReviewReport → direct mutation`
13. `Proxy time/frame index → final source authority`
14. `Generic clear cache → deletion of durable paid/revisioned evidence`
15. `Top-level repo license → assumption all model/transitive licenses are approved`
16. `Transcript/OCR/external metadata → executable Agent instruction`
17. `LLM text → unvalidated shell command`
18. `Auto Reframe → generative outpainting as normal fallback`

---

# 33. Upstream reuse rule

Architecture v0.2 adopts the Survey V2 neutralization rule:

```text
Audit
→ classify useful mechanism
→ audit source + model + data + native/transitive + patent/terms
→ adapt/reimplement behind local ownership
→ benchmark
→ approve for release separately
```

An upstream implementation may be:

- direct candidate;
- adapted;
- independently reimplemented;
- reference strong;
- reference only;
- blocked pending license/benchmark.

No upstream’s timeline, database, folder structure, provider source policy or Agent topology becomes authoritative automatically.

---

# 34. Architecture v0.2 deliberately does NOT freeze

The following remain Capability Spec / ADR / Benchmark decisions:

- exact LLM/VLM providers;
- default embedding model;
- vector index implementation;
- retrieval Top-K / RRF parameters;
- TemporalAnchor thresholds;
- CandidateWindow count;
- Resolver score weights;
- beam width / DP parameters;
- exact CommercialSkill weights;
- music provider priority;
- CLAP or other audio-text model adoption;
- BGM ducking dB/fade times;
- output loudness presets;
- Auto Reframe detector/tracker/model;
- crop optimizer algorithm/weights;
- preview backend;
- exact FFmpeg approved build;
- encoder quality profiles;
- optional generative audio provider;
- optional generative frame interpolation provider;
- autonomy operation-by-operation approval matrix;
- professional NLE interchange format set.

These are not Domain truths.

---

# 35. Migration obligations from v0.1.x

When v0.2 is accepted and implementation migration begins:

### Mandatory product-policy migrations

- remove active visual remote/generated source policies;
- remove visual MaterialProvider fallback behavior;
- introduce Asset usage role;
- make reference-analysis assets Resolver-ineligible by default.

### Mandatory model/schema migrations

- replace float-authoritative media time with rational/canonical MediaTime semantics;
- allow ResolutionDecision multi-selection;
- move embedding authority into rebuildable index infrastructure;
- add explicit rights/provenance records;
- add temporal evidence/anchor provenance;
- add spatial composition decision seam;
- add music selection/audio editorial decision seams;
- extend EDL to time-varying visual/audio automation;
- extend ReviewReport repair routing;
- split durable derived evidence from rebuildable cache.

### Mandatory trust migrations

- treat all media-derived/external text as untrusted data;
- require typed validated model outputs before executors;
- sanitize Environment Doctor exports.

Migrations must be introduced incrementally with schema/version tests. Do not destructively rewrite old project revisions without an explicit migration strategy.

---

# 36. Architecture acceptance gates

Before v0.2 should be treated as a frozen implementation baseline, verify:

1. Product Constitution alignment — PASS required.
2. No unresolved ownership overlap between Director / Resolver / SpatialComposer / AudioEditorial / EDLBuilder.
3. MediaTime/VFR semantics are implementable without breaking current persistence.
4. Historical implemented capabilities can migrate through explicit revisions rather than hidden behavior changes.
5. Visual remote/generated legacy behavior is unreachable from active product workflow.
6. Rights/provenance records can represent both user attestation and provider license evidence.
7. EDL can express the minimum time-varying visual/audio automation required by Auto Reframe and audio mixing.
8. Review/stale routing can isolate local repairs.
9. Dependency direction remains enforceable by existing architecture gates/Import Linter or equivalent.
10. No direct dependency is implicitly approved merely by being named in Survey V2.

---

# 37. Next document layer

After this candidate contract is reviewed/frozen, create focused Capability Specifications rather than expanding this file into implementation detail.

Expected specification families:

```text
Script / Shooting
Asset / Rights / Provenance
Media Time / Derivatives
Visual Understanding
Speech / ASR
Retrieval / Index
Temporal Evidence / Anchors
Director
Resolver / Optimizer
BeatMap / Music Alignment
Music Selection / Providers
Audio Editorial
Spatial Composition / Auto Reframe
Commercial Skills
Subtitle / Motion Graphics
EDL / Timeline
Render / Preview / Proxy / Cache
Review / QC
Environment Doctor / Deployment
Autonomy Policy
Security / Cloud Evidence
```

ADRs then record concrete technology choices inside these seams.

Roadmap V2 is derived only after this architecture/specification map exists.

---

# 38. Closing invariant

The central authority chain for exact editing is now:

```text
User / Brief
   ↓
Script/Shooting intent
   ↓
Measured + semantic evidence
   ↓
Director editorial intent
   ↓
Resolver grounded source decisions
   ↓
Spatial / Audio derived decisions where required
   ↓
EDLBuilder exact executable timeline
   ↓
Renderer deterministic execution
   ↓
Review routes localized repair
```

The product is not “an LLM that writes FFmpeg commands.”

It is a revisioned, evidence-grounded editing system in which AI intelligence is powerful but bounded by explicit domain ownership, user control, provenance and deterministic execution.

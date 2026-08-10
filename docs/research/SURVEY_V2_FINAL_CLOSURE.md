# Survey V2 Final Closure

**Status:** CLOSED  
**Closure date:** 2026-08-11  
**Scope:** Product-wide Open-Source Capability Survey V2  
**Authority:** Research-stage closure gate. This document does not itself amend the Product Constitution or Architecture Contracts.

---

## 1. Final verdict

Survey V2 is now **CLOSED**.

The final two capability blockers identified by `SURVEY_V2_CLOSURE_GAP_AUDIT.md` have passed focused survey:

1. **Audio Editorial / Music Selection & Rights** — PASS
2. **Auto Reframe / Aspect-Ratio Composition** — PASS

No remaining capability gap requires another broad ecosystem search before Architecture Contract v0.2 can be drafted.

The project should now stop asking primarily:

> “How does the ecosystem solve this?”

and begin asking primarily:

> “Which researched principles become our architecture, interfaces, capabilities, benchmarks and implementation sequence?”

---

## 2. What CLOSED means

`CLOSED` does **not** mean:

- every dependency is selected;
- every model is commercially approved;
- every algorithm weight is calibrated;
- every Windows package is proven;
- every codec/legal question is solved;
- implementation should immediately begin without specifications.

It means:

> The major product capabilities and their credible implementation families are sufficiently understood that remaining uncertainty can be handled through architecture design, capability specifications, ADRs, benchmarks, dependency/license gates and product probes rather than more open-ended upstream discovery.

---

## 3. Product capability closure matrix

| Capability family | Closure |
|---|---|
| Brief / Script planning | PASS |
| Shooting planning / coverage | PASS |
| Asset ingest / provenance | PASS |
| Shot identity / detection | PASS |
| Visual understanding | PASS |
| Speech / ASR / dialogue timing | PASS |
| Visual temporal evidence / action anchors | PASS |
| Retrieval / embedding strategy | PASS for architecture |
| Director | PASS |
| Resolver / CandidateWindow / scoring | PASS |
| Deterministic sequence/timing optimization | PASS |
| BeatMap / elastic beat-action alignment | PASS |
| Commercial/Vlog Skills / calibration | PASS |
| Music discovery / selection / music moment localization | PASS |
| Audio editorial / ducking / mixing / rights evidence | PASS |
| Auto reframe / aspect-ratio composition | PASS |
| EDL / timeline / interchange | PASS for architecture |
| Subtitle / motion graphics | PASS |
| Render / codec strategy | PASS for architecture |
| Preview / proxy / cache | PASS for architecture |
| Technical QC / editorial review | PASS |
| Windows deployment / Environment Doctor | PASS for architecture |

No broad capability remains in `BLOCKER` status.

---

## 4. Final architecture thesis emerging from Survey V2

The product should not become one giant multimodal model or a disguised wrapper around one upstream NLE.

The researched target is:

```text
User intent / Brief
      ↓
ScriptPlan
      ↓
ShootingPlan
      ↓
User-supplied footage
      ↓
Local probe / Shot detection / cached understanding
      ↓
Director
      ↓
EditSlots
      ↓
High-recall retrieval
      ↓
Temporal / semantic / music evidence
      ↓
CandidateWindows
      ↓
Resolver scoring + uncertainty
      ↓
Targeted strong-model adjudication only when justified
      ↓
Deterministic sequence optimization
      ↓
ResolutionDecision(s)
      ↓
Spatial composition / Auto Reframe where required
      ↓
Music selection / Audio editorial decisions
      ↓
EDLBuilder
      ↓
Exact executable EDL
      ↓
Local renderer
      ↓
Layered technical + editorial review
      ↓
Final MP4
```

The recurring pattern is:

> **AI understands, plans and judges. Local tools measure and execute. Exact timing/spatial/audio execution is grounded in structured evidence and deterministic contracts.**

---

## 5. Constitution survived the survey

No Survey V2 finding requires reversing the Product Constitution.

The following remain controlling product rules:

- user-supplied local visual source material only;
- no autonomous remote visual B-roll fallback;
- no default generative visual content;
- visual AI is observer/proposal, not timeline authority;
- remote/public music is allowed only through the separate audio policy and rights/provenance path;
- optional generated audio remains default OFF;
- BeatMap describes music facts and does not own edits;
- EDL is the sole executable timeline authority;
- Renderer executes rather than edits;
- original media remains local-first;
- cloud/strong AI is used where judgment adds value, not for deterministic media work.

Upstream behavior that conflicts with these rules is treated as algorithm/engineering reference only.

---

## 6. “Neutralization” rule for unconstitutional upstreams

Survey V2 repeatedly found useful upstream projects whose product path conflicts with this repository.

The durable treatment is:

```text
useful algorithm / data structure / state machine / benchmark idea
        ↓
extract the principle
        ↓
remove remote/generated/ownership/license-conflicting behavior
        ↓
reimplement behind our local contracts
```

Examples:

- stock-footage search systems → provider/caching/retry ideas only; no remote visual fallback;
- generative soundtrack/video systems → semantic/rhythm representations may be studied; generated-output path stays disabled by Constitution;
- AutoFlip-style generative uncrop/inpainting ideas → crop-path optimization retained, generated pixel completion removed;
- AGPL/NC or unclear-license editors → architecture/algorithm reference only unless a deliberate licensing strategy later permits direct use;
- permissive top-level repo + restrictive model/runtime dependency → direct use blocked until the complete dependency chain is approved.

The project must not let a legacy document or an upstream README override the Constitution.

---

## 7. Architecture Contract v0.2 migration agenda

Survey V2 has produced enough new knowledge that Architecture v0.2 should not be a cosmetic revision.

At minimum it must reconcile the following.

### 7.1 Visual source policy migration

Remove active visual semantics for:

```text
remote_allowed
remote_only
generated_allowed
remote_search_queries
```

and any automatic Pexels/Pixabay/Coverr visual fallback path.

The historical contracts remain history; v0.2 defines the new truth.

### 7.2 Asset origin vs usage role

Separate:

> where an Asset came from

from:

> what the project is allowed/intended to use it for.

Likely usage roles include concepts such as:

```text
editable_visual_footage
reference_analysis_only
music
voiceover
sound_effect
logo_graphic
```

A reference video should default to `reference_analysis_only` and be Resolver-ineligible unless the user explicitly imports/reclassifies it as editable footage.

This product-level interpretation must be checked against the Constitution during v0.2 drafting; if constitutional text needs clarification, use an explicit v1.1 amendment rather than hiding it in code.

### 7.3 ResolutionDecision cardinality

Historical contracts allow one EditSlot to produce multiple EDLSegments, but current `ResolutionDecision` structure primarily models one selected Shot/window.

v0.2 should support a collection such as `ResolvedSelection[]` or equivalent while preserving one authoritative Resolver decision artifact for the Slot/sequence.

### 7.4 Resolver vs EDLBuilder authority

Resolver/sequence optimizer may decide:

- concrete Shot/window sequence;
- ordering within an EditSlot where allowed;
- source timing feasibility;
- action/music alignment intent;
- alternatives and score evidence.

EDLBuilder remains responsible for exact executable timeline placement, tracks and validation.

EDLBuilder must fail/reject impossible decisions rather than silently replace media.

### 7.5 Canonical media time

Define canonical time semantics for:

- VFR footage;
- rational time bases;
- original/edit-friendly/proxy mapping;
- source vs timeline time;
- frame/PTS rounding.

Preview derivatives must map accurately back to original source for final render.

### 7.6 Embedding/index semantics

Embeddings belong to rebuildable retrieval infrastructure, not authoritative Shot identity/semantics.

Persist model/version/representation metadata so an index can be rebuilt independently of ShotAnalysis identity.

### 7.7 Temporal evidence / CandidateWindow classification

Define whether `TemporalAnchor`, temporal evidence and `CandidateWindow` are:

- derived analysis records;
- durable evidence artifacts;
- Resolver value objects;
- rebuildable artifacts.

Do not promote them to top-level Domain entities merely because they are important.

### 7.8 Spatial composition / Auto Reframe

Introduce a provider-neutral ownership seam such as `SpatialComposer` / `ReframeDecision`.

EDL must support time-varying crop/scale/position curves rather than one static transform per segment.

Generative outpainting/fill remains outside the normal path.

### 7.9 Audio selection/editorial

Introduce provider-neutral music discovery and rights-aware selection seams.

BeatMap remains facts only.

Likely derived/application artifacts include:

- `MusicSelectionDecision`;
- `AudioMixDecision` / equivalent.

EDL audio representation must support time-varying gain/fade/ducking/loop mapping rather than one static gain value.

### 7.10 Rights / provenance

Add structured records for concepts such as:

- RightsAttestation;
- LicenseSnapshot;
- ManualLicenseOverride;
- provider/license evidence artifacts;
- platform/territory/project/video scope.

Do not equate “royalty free” with universal rights.

### 7.11 Review routing

Upgrade ReviewReport stages/repair metadata so findings can identify:

```text
affected_owner
affected_slot / segment / timeline range
requires_new_analysis
affected_downstream
recommended_action
```

Localized repair is a first-class cost/quality mechanism.

### 7.12 Durable evidence vs cache

Separate at least:

```text
Rebuildable Cache
Durable Derived Evidence
Project Output
```

A generic cache cleanup must never silently destroy paid/cloud/revision-bound analysis.

### 7.13 Security/trust boundary

Media content, transcript, OCR, reference text and remote metadata are untrusted data, never executable instructions.

LLM output must pass typed schemas/validation before deterministic command construction.

Environment Doctor diagnostic exports must redact secrets and sensitive paths where appropriate.

---

## 8. Capability Specifications expected after v0.2

The survey now supports a document cluster rather than one monolithic design file.

Likely capability specifications:

```text
Script & Shooting Planning
Asset / Rights / Provenance
Visual Understanding
Speech / ASR
Shot Retrieval / Indexing
Temporal Evidence / Anchors
Director
Resolver / CandidateWindows / Sequence Optimizer
BeatMap / Music Alignment
Music Selection / Rights-aware Providers
Audio Editorial / Mixing
Spatial Composition / Auto Reframe
Commercial / Vlog Skills
Subtitle / Motion Graphics
EDL / Media Time
Render / Codec / Preview / Proxy / Cache
Review / Technical QC
Environment Doctor / Deployment
Autonomy / Approval Policy
Security / Trust / Cloud Evidence
```

The exact file partition can change during architecture drafting.

---

## 9. ADR families now justified

Examples of decisions that should become explicit ADRs rather than hidden implementation choices:

- FFmpeg as primary deterministic render backend;
- exact-local vector scan before external vector DB;
- multilingual text embedding baseline chosen by project benchmark;
- VLM as grounded adjudicator rather than timestamp generator;
- layered beam search / DP as first sequence optimizer family;
- ASS/libass as normal subtitle renderer;
- preview backend selection after Windows benchmark;
- approved FFmpeg build/distribution profile;
- codec/legal distribution gate;
- music provider eligibility model;
- audio-text embedding model approval if adopted;
- Auto Reframe detector/tracker provider choice;
- time-varying SpatialTransformCurve representation;
- reference-video default usage role.

---

## 10. Upstream Ledger V2 is now mandatory before new direct dependencies

The historical Upstream Component Ledger is no longer complete enough for the surveyed ecosystem.

A v2 ledger should record at least:

```text
upstream / provider
exact revision
source-code license
model/checkpoint license
training/data caveat
native/transitive dependencies
codec/patent note
Windows status
CPU status
GPU requirement/acceleration
reuse classification
local destination port/seam
release approval status
provenance / notices
```

Important newly surveyed families include:

- FFmpeg / ffprobe;
- OpenTimelineIO;
- libass;
- faster-whisper / VAD;
- GStreamer/libmpv/libVLC preview candidates;
- local embedding/index candidates;
- OpenCV / MediaPipe / SAM2;
- music-analysis tools;
- Jamendo and other audio provider references;
- CLAP family candidates;
- Auto Reframe implementation references.

No new dependency should enter `src/` merely because Survey V2 marked its concept as useful.

---

## 11. Benchmark agenda becomes the new evidence engine

Survey V2 deliberately leaves parameters unfrozen.

Next-stage benchmarks should determine:

- retrieval model/Top-K/fusion;
- TemporalAnchor recall/false positives;
- CandidateWindow quality;
- sequence optimizer width/pruning/weights;
- CommercialSkill calibration;
- music semantic retrieval and moment localization;
- audio ducking/mix presets;
- Auto Reframe subject coverage/path smoothness/manual override rate;
- Windows preview/backend performance;
- proxy/render codec profiles;
- API cost per useful edit;
- end-to-end human preference on real ads/Vlogs.

Passing unit tests remains engineering evidence, not proof of editing quality.

---

## 12. Final development gate

After this closure, the required order is:

```text
Survey V2 CLOSED
        ↓
Architecture Contract v0.2
        ↓
Product Constitution clarification/amendment only if truly required
        ↓
Capability Specifications
        ↓
ADRs
        ↓
Upstream Ledger / Policy V2
        ↓
Roadmap V2
        ↓
implementation resumes
```

Architecture/spec work may iterate among these documents, but feature coding should not jump ahead of the architecture/roadmap transition.

---

## 13. Anti-reopening rule

Do not reopen broad Survey V2 merely because:

- a new model is released;
- an implementation parameter is uncertain;
- a benchmark has not yet chosen a winner;
- an optional dependency has not passed release licensing;
- one upstream looks fashionable.

A new Upstream Survey Gate remains appropriate when a genuinely new major capability is introduced or evidence shows the current design family is inadequate.

Otherwise new upstream information is evaluated inside the existing capability seam.

---

## 14. Closure statement

The project now has a sufficiently complete engineering map to move from **ecosystem research** to **repository architecture design**.

The Survey V2 research archive should remain available as evidence and rationale, but it is no longer the normative design authority.

The next normative architecture target is:

> **Architecture Contract v0.2**

followed by the capability/ADR/upstream/roadmap document cluster required to turn these findings into buildable, testable and governable software.

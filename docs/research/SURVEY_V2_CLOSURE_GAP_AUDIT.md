# Survey V2 Closure / Gap Audit

**Status:** CLOSURE AUDIT — NOT YET CLOSED  
**Audit date:** 2026-08-11  
**Scope:** Product Constitution + Architecture Contracts v0.1/v0.1.1/v0.1.2 + six Survey V2 research documents + Upstream Component Ledger/Policy  
**Authority:** Informative research gate. This document does not itself amend the Product Constitution or Architecture Contracts.

---

## 1. Audit question

Can Survey V2 now be considered sufficiently complete to stop asking primarily:

> “How does the ecosystem solve this?”

and begin asking primarily:

> “How should this repository implement it?”

The strict answer is:

> **The AI editing core is research-complete enough to enter architecture design, but the product-wide Survey V2 is not yet fully closed. Two capability surveys remain materially incomplete: (1) Audio Editorial / Music Selection & Rights, and (2) Auto Reframe / Aspect-Ratio Composition.**

Everything else discovered in this audit is primarily an **Architecture v0.2 migration problem**, a capability-specification problem, or a release/security gate — not a reason to continue broad open-ended upstream discovery.

Therefore the closure decision is:

```text
AI editing core survey        PASS
Local execution/toolbox       PASS
Product-wide Survey V2        CONDITIONAL FAIL
Architecture v0.2 drafting    MAY begin in parallel only for already-closed domains
Final Roadmap V2 freeze       WAIT until the two remaining capability surveys close
```

---

## 2. Sources audited

### Normative product source

- `docs/product/PRODUCT_CONSTITUTION_V1.0.md`

### Architecture baselines

- `docs/architecture/ARCHITECTURE_CONTRACT_V0.1.md`
- `docs/architecture/ARCHITECTURE_CONTRACT_V0.1.1.md`
- `docs/architecture/ARCHITECTURE_CONTRACT_V0.1.2.md`

### Survey V2 research archive

- `OPEN_SOURCE_CAPABILITY_SURVEY_V2.md`
- `AI_EDITING_CORE_MECHANISM.md`
- `LOCAL_TOOLBOX_AND_DEPLOYMENT.md`
- `RESOLVER_RETRIEVAL_AND_TIMING_OPTIMIZER.md`
- `VISUAL_EVENT_ANCHOR_GENERATION.md`
- `RESOLVER_SCORE_AND_COMMERCIAL_SKILLS.md`

### Upstream governance

- `docs/upstream/UPSTREAM_COMPONENTS.md`
- `docs/upstream/UPSTREAM_POLICY.md`
- `LICENSE_STATUS.md`

---

## 3. Product-constitution alignment

### 3.1 Strong alignment already achieved

The research now consistently supports the Constitution's highest-value rules:

- product identity remains **AI Director + AI Video Editor**;
- user-supplied visual material remains the only ordinary visual source path;
- visual AI is observation/evidence, not timeline authority;
- Director owns editorial intent, Resolver owns concrete source selection, EDLBuilder owns exact executable timeline authority;
- BeatMap describes music facts and does not own cuts;
- local deterministic tools perform measurement/execution when practical;
- cloud/strong models are escalation paths for semantic uncertainty rather than mechanical media processing;
- cached/revisioned evidence enables incremental repair instead of whole-project reruns;
- final quality remains higher priority than API cost, but unnecessary model work is deliberately eliminated.

No Survey V2 result requires reversing these principles.

### 3.2 One product-level ambiguity remains: reference-video role

The Constitution allows user-supplied reference video analysis and separately requires that visual source material be user supplied.

The CommercialSkill research is more specific:

> reference videos may seed style observations but their protected expression/frames must not become source footage.

These statements are not technically contradictory, but the current product text leaves an ambiguity: because a reference video is also a user-supplied local visual file, a future Resolver could mistakenly consider it eligible source footage unless asset usage role is explicit.

**Required decision before Architecture v0.2 finalization:**

Recommended default:

```text
reference_video
→ analysis-only
→ never Resolver-eligible

unless the user explicitly imports/reclassifies that same file as editable footage
```

This likely belongs either in Product Constitution v1.1 or an explicit constitutional interpretation adopted before the v0.2 schema is frozen.

---

## 4. Capability coverage matrix

| Capability | Closure status | Audit conclusion |
|---|---|---|
| Brief / Script Planning | PASS | Domain + versioned playbooks/skills + LLM provider direction is sufficient for architecture design. |
| Shooting Planning / Coverage | PASS | Coverage-first, ordinary-user guidance, equipment awareness and reshoot semantics are clear. |
| Asset ingest / Shot identity | PASS | Existing implementation and contracts are mature enough. |
| Shot detection | PASS | Existing TransNetV2 seam already validated. |
| Visual Understanding | PASS | Cloud-first optional/local-provider seam, cached evidence, targeted re-analysis are clear. |
| Speech / ASR / dialogue cuts | PASS | Local ASR + timestamp-grounded trimming direction is sufficiently researched. |
| Temporal action/event anchors | PASS | Camera-compensated local evidence + optional semantic escalation is sufficiently researched. |
| Retrieval / embeddings | PASS for architecture | Exact local index first, hybrid lexical+dense retrieval, benchmark-selected embedding model. Model choice remains benchmark work, not survey blocker. |
| Resolver / CandidateWindow | PASS | Evidence-grounded windows, score/confidence separation and sequence optimization are sufficiently researched. |
| BeatMap / beat-action alignment | PASS | Elastic rhythm + deterministic sequence optimization is sufficiently researched. |
| Commercial/Vlog Skills | PASS | Versioned priors + pairwise preference calibration + user overlays are sufficiently researched. |
| EDL / Timeline / interchange | PASS for architecture | Domain EDL + FFmpeg execution + optional OTIO adapter direction is strong; exact time representation still needs v0.2 decision. |
| Render | PASS | FFmpeg-centric programmable renderer is sufficiently researched. |
| Subtitle / motion graphics | PASS | ASS/libass + optional HyperFrames-style complex graphics gives a credible layered path. |
| Preview / proxy / cache | PASS for architecture | Required capability boundaries are known; actual backend winner remains benchmark work. |
| Technical QC / editorial review | PASS | Local technical QC + structured/targeted editorial review is sufficiently researched. |
| Windows deployment / Environment Doctor | PASS for architecture | Tiered CPU/GPU/cloud capability model and install/repair UX are clear; installer details remain later specification work. |
| **Music selection / licensed library sourcing** | **BLOCKER** | Beat analysis is researched, but semantic track matching, provider/library ingestion, license evidence, and public-library eligibility are not yet surveyed deeply enough. |
| **Audio editorial / mixing** | **BLOCKER** | Voiceover/BGM/source-audio mixing, ducking, looping, fade structure, music-segment selection and audio continuity are not yet specified deeply enough for final product architecture. |
| **Auto reframe / aspect-ratio composition** | **BLOCKER** | Crop is allowed and tracking is researched, but the actual 16:9→9:16 composition/reframe solver, safe-zone constraints and crop-window continuity have not passed a dedicated Survey Gate. |

The first two audio rows are best treated as one combined remaining Survey domain: **Audio Editorial + Music Selection & Rights**.

---

## 5. Remaining major Survey blocker A — Audio Editorial / Music Selection & Rights

### 5.1 What is already covered

Survey V2 already covers:

- BeatMap facts;
- beat/downbeat/energy/section analysis candidates;
- local ASR;
- loudness/technical QC;
- ordinary subtitle/audio-track execution in EDL;
- Product Constitution rules for user music, public music libraries, licensing warnings and optional generated audio.

### 5.2 What is still missing

The product still lacks a researched end-to-end answer for:

```text
Brief / Script / visual pacing
        ↓
music intent
        ↓
search/rank legally usable tracks
        ↓
choose track or sub-range
        ↓
record rights/license evidence
        ↓
fit music section to edit duration
        ↓
voiceover/source-audio/BGM mix policy
        ↓
ducking / fades / loops / transitions
        ↓
EDL audio tracks
```

Specific missing questions:

- Which local model/DSP approach should produce semantic music-fit features (mood/theme/style), if any?
- Which candidate audio-text embedding models have acceptable source + weight + training-data commercial posture?
- Should automatic music selection initially rank only user-local/curated tracks, or also query external libraries?
- Which external/public music providers have terms that permit the intended commercial use and machine-assisted discovery?
- How should provider-specific license restrictions be represented and snapshotted?
- How should a selected 60-second source track yield the best 20–30 second usable sub-range?
- How should BeatMap sections influence music-segment selection without making BeatMap editorial authority?
- How should source dialogue, voiceover and BGM interact?
- What is the default ducking policy around speech?
- When may a music loop be created, and how is musical continuity validated?
- How are crossfades, intro/outro tails and source-audio preservation represented in EDL/AudioPolicy?

### 5.3 Evidence that this is a real separate capability

Current external evidence shows viable building blocks but not a ready integrated answer:

- LAION CLAP exposes shared text/audio representations and music checkpoints, but its training corpus includes copyrighted/restricted material and therefore needs the same model/data provenance discipline as other ML candidates.
- FFmpeg already provides local mixing primitives such as `amix`, `sidechaincompress`, fades and loudness processing, so the execution layer is available; the unresolved problem is **editorial policy and rights-aware selection**, not whether mixing is technically possible.

### 5.4 Closure requirement

Run one focused Survey Gate covering approximately:

- music semantic matching/tagging candidates;
- music-library/provider options and commercial-rights behavior;
- music sub-range selection;
- voiceover/BGM/source-audio mixing/ducking/looping patterns;
- required EDL/audio-policy semantics;
- license/weight/data dependencies.

This does not require solving every numeric parameter before architecture work.

---

## 6. Remaining major Survey blocker B — Auto Reframe / Aspect-Ratio Composition

### 6.1 Why the current research is not enough

The system already understands:

- subject/product trajectories;
- camera motion;
- object/hand tracking;
- composition-related anchors;
- platform safe-zone priors;
- EDL crop/scale/position fields.

But these components do not yet define an **auto-reframe capability**.

A commercial short-video product will regularly receive:

```text
16:9 camera footage
4:3 / phone footage
mixed orientations
wide product demonstrations
```

and need to produce:

```text
9:16 TikTok/Reels/Shorts output
```

without cutting off the speaker, product, text or important interaction.

### 6.2 Missing questions

- What is the crop-window state/model over time?
- How is subject/product saliency combined with camera motion?
- How is crop-window jitter penalized?
- When should crop follow a face, product, hand interaction, or remain static?
- How are two subjects handled?
- How do safe zones and planned text overlays constrain crop position?
- How does the crop solver choose between zooming out, following, holding, or declaring the source unsuitable?
- Does crop become a per-EDLSegment transform curve or a separate derived ReframePlan?
- How are reference/video quality and user locks respected?

### 6.3 Upstream evidence

Historical MediaPipe AutoFlip demonstrates that content-aware video reframing is a distinct engineering problem rather than a trivial `crop=center` operation. Current MediaPipe remains an Apache-2.0 on-device framework with tracking/detection primitives, but legacy AutoFlip itself is no longer a maintained modern product path.

Therefore the correct action is a focused modern survey of:

- AutoFlip ideas / legacy implementation;
- current face/object/saliency tracking approaches;
- crop-window smoothing and optimization;
- modern Windows-friendly implementations;
- license/model provenance.

### 6.4 Closure requirement

Complete a dedicated Auto-Reframe Survey Gate and freeze only the capability boundary / first benchmark candidate set. Numeric smoothing weights remain benchmark work.

---

## 7. Architecture-contract debt revealed by Survey V2

These are **not reasons to keep doing broad Survey research**. They are exactly the work Architecture Contract v0.2 must reconcile.

### 7.1 Visual source-policy migration — mandatory

Legacy v0.1/v0.1.1/v0.1.2 still define:

```text
remote_allowed
remote_only
generated_allowed
remote_search_queries
PexelsProvider / PixabayProvider / CoverrProvider
Resolver remote fallback
```

The Product Constitution explicitly supersedes these paths for visual material.

Architecture v0.2 must remove or scope them so that:

```text
visual footage
→ user-supplied local/captured only

missing visual coverage
→ unresolved / request footage / reshoot guidance
```

Do not merely rename `remote_allowed`; eliminate the prohibited behavior from active visual contracts.

Audio/music may still have externally discovered library providers, so the clean solution is likely **media-kind/usage-role-aware sourcing**, not a single generic source-policy enum shared blindly by video and audio.

### 7.2 Asset usage roles are missing

The current `Asset` schema describes media identity and origin but not why a project may use that file.

Architecture v0.2 needs a clear distinction among concepts such as:

```text
editable_footage
reference_analysis_only
music
voiceover
logo/image graphic
possibly font/project resource
```

This is needed for:

- reference-video non-eligibility;
- Resolver filtering;
- provenance;
- music rights;
- correct UI organization.

Do not conflate `origin` with `usage_role`.

### 7.3 ResolutionDecision cannot currently represent 1 Slot → N source selections cleanly

v0.1.1 simultaneously says:

- `ResolutionDecision` has one `selected_shot_ref` and one `selected_source_window`;
- one EditSlot may legitimately produce N EDLSegments.

Those statements are structurally incompatible.

Architecture v0.2 should allow a resolution to carry a **sequence/list of grounded selections** or introduce a separate resolved-slot structure.

### 7.4 Global optimizer ownership must be explicit

Survey V2 shows that sequence quality depends on unary, pairwise and global scoring plus beat/music timing.

The optimizer may need to reason about accumulated time/music position while selecting CandidateWindows.

This must not accidentally violate:

- Resolver owns concrete source selection;
- EDLBuilder owns final timeline authority.

Architecture v0.2 needs an explicit boundary, for example:

```text
Resolver / ResolutionOptimizer
→ selects ordered grounded source windows + timing/alignment intent/feasibility

EDLBuilder / TimelineAllocator
→ assigns exact timeline coordinates and validates execution

if exact allocation invalidates editorial assumptions
→ build failure / localized Resolver retry
```

Do not let EDLBuilder silently replace Shots, and do not let Resolver directly commit final `timeline_in/timeline_out`.

### 7.5 EditSlot `target_timeline_range` semantics are too close to final timeline authority

v0.1.1 marks `target_timeline_range` as required while separately freezing final Timeline Time as EDL-only authority.

Architecture v0.2 should clarify that EditPlan owns **narrative phase / budget / preferred placement**, not executable timeline coordinates.

### 7.6 Canonical media-time / VFR contract is missing

Research on edit-friendly media and OTIO exposes a real architecture need:

- source footage may be VFR;
- proxy/edit-friendly derivatives must map exactly back to original media;
- seconds represented as ordinary floats are not a sufficient long-term media-time contract by themselves.

Architecture v0.2 should freeze:

- canonical source-time representation;
- frame/time-base semantics;
- VFR handling;
- mapping manifests between original/edit-friendly/proxy artifacts;
- rounding rules at render boundaries.

OTIO/OpenTime is a strong reference, but Domain time semantics must remain ours.

### 7.7 Embeddings should move out of authoritative ShotAnalysis semantics

v0.1.2 allows UnderstandingService to write `embedding` as Shot analysis.

Survey V2 now treats embeddings as **rebuildable index facts tied to model/version/representation**, not durable truth about the Shot.

Architecture v0.2 should move embedding ownership to ShotIndex / derived-index artifacts and store model/revision metadata there.

### 7.8 TemporalAnchor / CandidateWindow classification must be settled

Survey V2 heavily relies on:

```text
TemporalEvidence
TemporalAnchor
CandidateWindow
```

They should not become top-level entities merely because they are useful.

v0.2 must decide which are:

- revisioned derived-analysis records;
- resolver artifacts/value objects;
- rebuildable cache;
- durable expensive evidence.

### 7.9 Review stages need expansion and repair routing

v0.1.1 currently enumerates only:

```text
candidate
edl
render
```

Research now needs at least conceptual separation of:

- Plan Review;
- Resolution Review;
- deterministic EDL/timeline validation;
- proxy editorial AV Review;
- final technical QC.

The ReviewReport also needs machine-actionable repair routing such as:

```text
affected_owner
affected_slots/ranges
requires_new_analysis
affected_downstream
```

### 7.10 Artifact durability classes are missing

v0.1.2 places proxies, VLM raw output, thumbnails, subtitles, render output and other files together under `ArtifactStore`.

Survey V2 now clearly distinguishes:

```text
rebuildable cache
vs
expensive/durable derived evidence
vs
project outputs
```

v0.2 needs retention/durability semantics so “clear cache” cannot delete expensive model evidence or project history.

### 7.11 RightsAttestation / LicenseSnapshot is not yet modeled

The Constitution requires user rights attestation and risk/override recording.

Current Asset provenance has optional license text but no durable user-attestation event or license snapshot.

v0.2/capability specs need:

- user license attestation / manual override;
- provider license snapshot/reference;
- risk status;
- attribution obligations;
- output provenance linkage.

### 7.12 Inference provenance and cost telemetry need a shared contract

To reproduce/debug model-derived decisions, persist where relevant:

```text
provider
model id/version
prompt/schema version
input evidence refs/hashes
sampling/config where relevant
raw response artifact ref
created_at
cost/token/media evidence where available
```

This supports:

- reproducibility;
- stale propagation;
- benchmark comparison;
- provider migration;
- cost optimization.

---

## 8. Security / trust / privacy gap

This is a **cross-cutting architecture gate**, not a missing media algorithm Survey.

The current documents do not yet formally define trust boundaries for:

- user reference text;
- transcripts/OCR/subtitles extracted from media;
- model-generated descriptions;
- external metadata;
- tool arguments;
- cloud evidence upload;
- environment diagnostic export.

Before agentic capabilities are allowed to control local tools, freeze at least these principles:

1. extracted/user media content is **data, not executable instruction**;
2. model output remains Proposal DTO / typed input and never becomes a raw shell/FFmpeg command without validation;
3. file paths and filter arguments are escaped/constructed by deterministic code rather than concatenated from model prose;
4. secrets/API keys are never included in diagnostics sent to an external AI assistant;
5. cloud evidence policy explicitly records what leaves the machine and supports user opt-out;
6. provider retention/privacy assumptions are adapter configuration/documentation, not hidden behavior.

Recommended deliverable before implementation of full agentic edit workflows:

`SECURITY_TRUST_AND_CLOUD_EVIDENCE.md` capability/ADR set.

This does **not** require reopening broad Survey V2.

---

## 9. Upstream governance audit

### 9.1 `UPSTREAM_COMPONENTS.md` is now stale/incomplete

The current ledger only names the original small set:

- FireRed-OpenStoryline;
- TransNetV2 family;
- MoneyPrinterTurbo;
- CutClaw;
- BeatSync Engine.

Survey V2 has since identified many serious candidates, including:

- OpenTimelineIO;
- FFmpeg/ffprobe approved-build profile;
- libass;
- faster-whisper;
- HyperFrames;
- GStreamer/GES;
- Beat This!;
- libsonare;
- OpenCV;
- MediaPipe;
- SAM 2;
- embedding/index candidates;
- several reference-only research systems.

Before any of these enter implementation, create/update an **Upstream Component Ledger V2**.

### 9.2 The ledger needs more fields

For ML/media components the old fields are insufficient.

Future ledger should record at least:

```text
upstream
exact revision/tag
role
source-code license
model/checkpoint license
training/data caveat if relevant
transitive/native license notes
Windows deployment status
CPU/GPU requirement
code reuse classification
destination seam
release approval state
provenance file
```

### 9.3 `UPSTREAM_POLICY.md` needs constitutional cleanup

Its MoneyPrinterTurbo role still describes generic material-provider reuse and the older architecture still names Pexels/Pixabay/Coverr visual providers.

The updated policy must state explicitly:

> provider/caching/provenance/retry ideas may be reused, but autonomous public visual-material sourcing is prohibited by the Product Constitution.

### 9.4 Current critical-license spot-check

A 2026-08-11 primary-source spot-check confirms the research posture remains broadly valid:

- OpenTimelineIO remains Apache-2.0 and describes itself as a mature actively developed editorial timeline framework;
- faster-whisper remains MIT;
- libass remains ISC;
- HyperFrames remains Apache-2.0, while its third-party dependency notices still require review;
- GStreamer remains LGPL-oriented but its Windows package matrix contains GPL/patent-sensitive optional packages that require an explicit deployment allowlist;
- Beat This! states both code and published weights are MIT but explicitly warns that some training files are copyrighted/limited-license, so final commercial review remains appropriate;
- SAM 2 states code and published checkpoints are Apache-2.0 but its practical deployment remains PyTorch/CUDA-heavy enough to keep it optional;
- CoTracker remains majority CC-BY-NC and should stay reference-only for a commercial product;
- sqlite-vec still identifies itself as pre-v1 and should remain behind a replaceable index seam.

No current license spot-check forces a reversal of the Survey V2 candidate map.

### 9.5 Repository-wide license status

The repository itself still has no selected open-source license and reserves all rights by default.

That is not an architecture blocker for continued private/public-source development, but before external distribution/contribution strategy is finalized, decide whether the product remains proprietary/source-visible or adopts an explicit project license.

Do not let this decision be accidentally implied by upstream component licenses.

---

## 10. Deployment gap audit

No major deployment topology gap remains.

The following direction is sufficiently stable:

```text
CPU baseline always valid
optional local enhancement packages
optional GPU acceleration
cloud intelligence as replaceable provider
Environment Doctor probes actual capability
```

However these items remain implementation specifications, not research blockers:

- bundled private Python/runtime vs user-installed runtime;
- package manager/installer choice;
- preview backend benchmark winner;
- exact proxy profiles;
- disk quota/cache retention;
- approved FFmpeg build;
- H.264/AAC commercial release/legal review;
- automatic-install vs explicit-user-confirmation boundaries.

### Important Windows observation

Current MediaPipe releases continue to evolve Windows/GPU build behavior. This reinforces the need for **runtime probes and provider isolation** rather than assuming that one historical local vision stack will remain universally installable.

---

## 11. Stale research statements to clean up after closure

`OPEN_SOURCE_CAPABILITY_SURVEY_V2.md` still lists the editing-core retrieval/anchor/scoring/optimizer work as “remaining before Roadmap V2.” Those items have since been substantially closed by the later research documents.

After the two remaining blocker surveys complete, update the survey snapshot to mark:

- Resolver/retrieval/anchors/optimizer: closed for architecture;
- scoring/CommercialSkill: closed for architecture;
- remaining audio/reframe gaps: closed or explicitly deferred.

Do not rewrite historical research conclusions; update status/closure references clearly.

---

## 12. Proposed Architecture Contract v0.2 promotion set

Once the two blocker surveys close, v0.2 should promote only stable, architecture-level conclusions.

Minimum promotion subjects:

1. Constitution-compliant asset source/usage roles;
2. reference-video analysis-only rule;
3. rights attestation/provenance;
4. canonical media time / VFR / derivative mapping;
5. ShotAnalysis vs rebuildable index semantics;
6. TemporalEvidence/TemporalAnchor classification;
7. CandidateWindow / multi-selection ResolutionDecision;
8. Resolver global-sequence optimization boundary;
9. EDLBuilder/TimelineAllocator exact authority;
10. layered Review stages + repair routing;
11. Artifact durability/retention classes;
12. InferenceProvenance / cost telemetry;
13. CommercialSkill / PlatformProfile / UserStyle ownership boundaries;
14. audio decision/mix semantics after the audio survey;
15. reframe/crop semantics after the auto-reframe survey.

Do not put model names, beam widths, embedding dimensions or benchmark-derived weights into the Domain Contract unless they become true invariants.

---

## 13. Candidate Capability Specifications after v0.2

Likely capability-spec cluster:

- `SCRIPT_AND_SHOOTING_PLANNING_SPEC`
- `VISUAL_UNDERSTANDING_AND_EVIDENCE_SPEC`
- `SHOT_RETRIEVAL_SPEC`
- `TEMPORAL_ANCHOR_SPEC`
- `RESOLVER_AND_SEQUENCE_OPTIMIZER_SPEC`
- `BEATMAP_AND_MUSIC_ALIGNMENT_SPEC`
- `AUDIO_EDITORIAL_AND_MUSIC_SELECTION_SPEC`
- `AUTO_REFRAME_AND_COMPOSITION_SPEC`
- `COMMERCIAL_SKILL_AND_PERSONALIZATION_SPEC`
- `SUBTITLE_AND_MOTION_GRAPHICS_SPEC`
- `RENDER_PREVIEW_PROXY_CACHE_SPEC`
- `REVIEW_AND_QUALITY_GATE_SPEC`
- `RIGHTS_PROVENANCE_AND_LICENSE_SPEC`
- `ENVIRONMENT_DOCTOR_AND_RUNTIME_SPEC`
- `AUTONOMY_AND_APPROVAL_POLICY_SPEC`
- `SECURITY_TRUST_AND_CLOUD_EVIDENCE_SPEC`

The exact filenames can change. The important point is that the engineering map should become a **cluster of small authoritative guidance documents**, not one enormous roadmap file.

---

## 14. ADR candidates

Likely ADRs required before or during early implementation:

- Domain EDL vs OpenTimelineIO boundary;
- FFmpeg as primary render executor and approved-build policy;
- canonical media-time representation and VFR normalization;
- Resolver optimizer ownership vs EDLBuilder timeline authority;
- exact local vector-index baseline and replaceability seam;
- cloud vision evidence-minimization policy;
- cache vs durable derived artifact policy;
- reference asset / editable footage role separation;
- model/checkpoint/data license gate;
- Windows preview backend selection after benchmark;
- audio mixing/ducking policy after audio survey;
- auto-reframe representation after reframe survey.

---

## 15. Roadmap V2 gate

Do **not** freeze Roadmap V2 yet.

Required order:

```text
1. Close Audio Editorial / Music Selection & Rights Survey
2. Close Auto Reframe / Aspect-Ratio Composition Survey
3. Mark Survey V2 CLOSED
4. Draft Architecture Contract v0.2
5. Resolve Product Constitution reference-role ambiguity if needed
6. Write capability specifications / ADRs
7. Update Upstream Ledger/Policy V2
8. Freeze Roadmap V2
9. Resume implementation
```

Architecture work for already-closed domains may be drafted in parallel, but implementation should still wait for the coherent v0.2/spec/Roadmap gate selected by the project.

---

## 16. Final closure verdict

### What is no longer a research problem

The following central question is now sufficiently answered:

> How does Script + visual evidence + music evidence become an exact EDL without letting an LLM invent timestamps or forcing every user to own a GPU?

Current answer is stable enough for architecture:

```text
Director intent
→ hard eligibility
→ hybrid retrieval
→ grounded TemporalAnchors
→ bounded CandidateWindows
→ score + confidence
→ targeted VLM only for important uncertainty
→ deterministic sequence optimization
→ ResolutionDecision
→ EDLBuilder
→ deterministic local render
→ layered review / localized retry
```

### What still blocks full Survey closure

Two focused capability areas remain materially under-researched:

1. **Audio Editorial / Music Selection & Rights**
2. **Auto Reframe / Aspect-Ratio Composition**

Therefore:

> **Survey V2 is not yet CLOSED, but broad ecosystem exploration is finished. Only two focused closure surveys remain.**

Once those two are completed, the project should stop expanding the research surface and move decisively into Architecture Contract v0.2 + Capability Specifications + ADRs + Roadmap V2.

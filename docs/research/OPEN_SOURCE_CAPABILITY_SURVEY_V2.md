# Open-Source Capability Survey V2 — Working Snapshot

**Status:** ACTIVE RESEARCH SNAPSHOT  
**Snapshot date:** 2026-08-10  
**Purpose:** Preserve high-value upstream findings before Roadmap V2. This file is not a dependency lockfile and not an Architecture Contract.

---

## 1. Product boundary that controls the survey

The project is an **AI Director + AI Video Editor** for user-supplied footage. Initial focus is Windows,
commercial short-form video / e-commerce ads / Vlog, primarily under 60 seconds.

The Product Constitution prohibits autonomous visual-stock fallback and default generative visual content.
Therefore an upstream may be technically excellent yet still be used only for algorithms or engineering
patterns if its product path depends on generated or remotely acquired visual footage.

The current research philosophy is:

```text
Audit → Borrow → Adapt → Build
```

The project should combine best-in-class components behind its own Domain Contracts instead of adopting a
single upstream's semantics wholesale.

---

## 2. Capability map

### 2.1 Script / Shooting Planning

**hve-video-director — REFERENCE-STRONG**

Useful ideas:
- discovery before generation;
- explicit product / audience / goal / constraint collection;
- structured story brief before downstream production;
- practical environment/doctor planning patterns;
- commercial promo structures such as Hook → Pain → Solution → Features → CTA.

Expected use: planning workflow and product-methodology reference, not domain ownership.

**DirectorSKILL — REFERENCE-STRONG**

Useful ideas:
- every shot should have a narrative purpose;
- blocking/action intent before framing/camera terminology;
- practical coverage planning and shot-list thinking.

Expected use: ShootingPlan playbook/methodology.

**Remotion Video Director / product-launch-video style projects — REFERENCE-ONLY / METHOD SOURCE**

Useful ideas:
- strategic framing before scene design;
- one central message per scene;
- commercial readability / product visibility / review heuristics.

Conclusion: Script/Shooting is more likely to be **our Domain + versioned playbooks/skills + LLM provider**
than a single imported library.

---

### 2.2 Director / Resolver / Review

**poseljacob/agentic-video-editor — REFERENCE-STRONG**

High-value chain:

```text
local search_moments
→ deep analysis of only a few promising candidates
→ Director
→ targeted trim refinement
→ FFmpeg edit
→ structured Reviewer
→ actionable retry
```

Important strengths:
- local, cheap, deterministic retrieval before expensive native-video analysis;
- Director must reference real indexed shots rather than invent source IDs;
- separate creative selection from trim-point refinement;
- structured review dimensions and concrete feedback.

Important mismatch with our architecture:
- its EditPlan contains exact `start_trim` / `end_trim` and the trim refiner mutates them;
- our preferred authority chain keeps exact source windows in Resolver / ResolutionDecision and final exact
  timeline authority in EDLBuilder.

Expected use: deeply absorb mechanisms, reimplement behind our ownership model.

**GVCLab/CutClaw — REFERENCE-STRONG, SOURCE COPYING FORBIDDEN**

Useful mechanisms observed in current code:
- parallel preprocessing of video/ASR/audio analysis;
- Screenwriter first narrows relevant scenes;
- editor exploration constrained to neighborhoods around recommended scenes;
- explicit separation of semantic-neighborhood retrieval, fine-grained shot trimming, review, and commit;
- fine-grained trimming examines only a requested local range, includes relevant subtitle context, caps frame
  count, and strides when necessary;
- validation of duration, overlap, continuity, scene coverage, and selected clip ranges.

Important lessons:
- Search ≠ Observe ≠ Validate ≠ Commit.
- Limit the agent's search space before expensive observation.
- Never let an editor agent roam arbitrarily across all footage when a higher-level plan already narrows the
  relevant region.

Expected use: algorithm/agent-tool architecture reference only.

**X-Cut — REFERENCE-ONLY / SKILL ARCHITECTURE**

Useful ideas:
- scene skills, style skills, tools, templates, prompt specs;
- reusable editing experience can be persisted as a style/skill rather than hidden in prompts;
- Vlog and marketing workflows should use different editing priors.

AGPL/product-feature mismatch means it should not become the core dependency.

**OpenMontage — REFERENCE-ONLY**

Useful ideas:
- agents make decisions while local Python/media tools execute;
- skills/workflows/manifests/checkpoints/budget gates and decision traces are first-class;
- quality gates before/after render.

Conflict:
- AGPL and extensive generated/remote visual sourcing paths conflict with the Product Constitution.

**VideoAgent / Crayotter and related research — REFERENCE-STRONG (research methods)**

Useful direction:
- intent/task decomposition before activating tools;
- retrieval/analysis/editing blueprints/tool calls/intermediate renders should become inspectable artifacts;
- optimize the task graph to avoid unnecessary API calls;
- localize and inspect only relevant regions rather than repeatedly reading full video.

---

### 2.3 Speech / Dialogue Editing

**faster-whisper — DIRECT-CANDIDATE**

Potential role:
- local ASR;
- word timestamps;
- CPU-capable baseline with optional GPU acceleration.

**WhisperX — BLOCKED-PENDING-REVIEW**

Potential role:
- higher-precision word alignment / diarization workflow.

Risk:
- actual alignment model licenses must be audited individually; package license alone is insufficient.

**ModelScope FunClip — REFERENCE-STRONG**

Critical lesson:
- select speech/text semantically, then map selected words/sentences back to ASR timestamps;
- exact dialogue cuts should derive from real timestamps, not LLM-estimated seconds.

This directly supports the rule:

> LLM may select *what speech to keep*; local timestamp evidence resolves *where it is*.

---

### 2.4 Video Understanding / Temporal Evidence

**TransNetV2 family — already adopted as shot-detection reference/runtime seam.**

**OpenTAD — REFERENCE-STRONG**

Potential role:
- temporal action start/end evidence.

Constraint:
- do not assume an end user has a GPU; treat heavyweight local temporal models as optional providers.

**MMAction2 — REFERENCE-STRONG**

Potential role:
- action recognition/localization, spatio-temporal evidence, retrieval research.

Constraint:
- large OpenMMLab/PyTorch dependency stack makes it unsuitable as an unconditional Windows baseline.

**VideoITG — REFERENCE-STRONG, CURRENT WEIGHTS NOT DEFAULT-COMMERCIAL**

Key lesson:
- use cheap relevance filtering to locate useful time spans/frames before sending evidence to an expensive VLM.

Expected use: reimplement the coarse-to-fine information-gathering strategy with commercially clean
components.

---

### 2.5 Music / BeatMap

**librosa — DIRECT-CANDIDATE for lightweight DSP baseline**

Potential role:
- onset/beat/spectral/audio utility baseline.

**Beat This! — BLOCKED-PENDING-FINAL-REVIEW / HIGH-POTENTIAL**

Potential role:
- beats/downbeats;
- CPU fallback plus optional GPU acceleration;
- small-model deployment tier.

Before release dependency approval, revalidate model/training provenance and commercial distribution posture.

**libsonare — BLOCKED-PENDING-BENCHMARK / HIGH-POTENTIAL**

Potential role:
- CPU-oriented local music toolbox for BPM, beat/downbeat, sections, loudness, energy, key/chords, etc.

Attractive properties from survey:
- permissive source posture;
- native/local DSP orientation;
- no assumption of a large GPU model.

Must be validated on our own music benchmark before architectural adoption.

**All-In-One Music Structure Analyzer — REFERENCE-STRONG, DIRECT USE BLOCKED**

Capability fit is excellent for BeatMap (tempo, beat/downbeat, segment labels), but dependency/model licensing
around madmom makes direct commercial default use unsafe without explicit resolution.

**Essentia — REFERENCE-ONLY by default**

Technically rich MIR/DSP source, but AGPL creates product-distribution concerns.

**MOSS-Music / large audio-language models — OPTIONAL ADVANCED RESEARCH**

Potential future high-end local/cloud analysis, but not a baseline due to hardware/runtime weight.

---

### 2.6 Timeline / Render / Subtitle

**FFmpeg + ffprobe — DIRECT-CANDIDATE / likely core local infrastructure**

Expected roles:
- probe/decode/extract/trim/concat/scale/crop/overlay/audio processing/transcode/render;
- technical QC filters;
- proxy and edit-friendly media generation.

Release requirement:
- maintain an approved build profile; never distribute an arbitrary third-party build without auditing enabled
  GPL/nonfree/external components.

**OpenTimelineIO — DIRECT-CANDIDATE for time/interchange infrastructure**

Preferred boundary:

```text
our Domain EDL
├─ FFmpeg render adapter
└─ OTIO interchange adapter
```

OTIO should not replace the Domain EDL authority.

**libass / ASS — DIRECT-CANDIDATE for standard subtitle rendering**

Preferred role:
- normal captions and emphasized subtitle styling through ASS/libass, commonly executed by FFmpeg.

**HyperFrames — DIRECT-CANDIDATE for complex text/motion graphics after prototype**

Potential role:
- title cards, CTA, price cards, charts, advanced typography, deterministic motion graphics.

**GStreamer / GStreamer Editing Services — PROTOTYPE-CANDIDATE**

GStreamer D3D11 is a strong Windows preview candidate; GES is a strong optional NLE-backend candidate.
Neither should own our Domain timeline without explicit architecture review.

**MLT — REFERENCE-STRONG / OPTIONAL BACKEND**

Mature NLE architecture, but introduces a second rich timeline/effect semantic system plus module-license
complexity. Use primarily as implementation reference until real needs justify integration.

**MoviePy — REFERENCE-ONLY for production execution.**

Useful for prototypes but not favored as primary high-throughput render abstraction.

---

### 2.7 Quality / Review

**FFmpeg/ffprobe technical QC — DIRECT-CANDIDATE**

Potential checks:
- decode success;
- stream/duration/resolution/fps validity;
- black frames;
- freeze;
- silence;
- loudness;
- missing audio;
- basic timeline/PTS problems.

**VMAF — DIRECT-CANDIDATE for render/transcode fidelity benchmarks, NOT editorial quality**

Correct use:
- reference-vs-render quality regression;
- codec/scaling/render profile A/B.

Incorrect use:
- deciding whether an advertisement has a strong hook or good storytelling.

**OpenCV quality / CV utilities — OPTIONAL**

Potential role:
- no-reference or reference technical image/video metrics, motion/subject/quality evidence.

Any bundled model files require separate license provenance review.

**AI Reviewer — REFERENCE-STRONG pattern, not first-line QC**

Preferred hierarchy:

```text
local deterministic technical QC
→ structured plan/resolution review
→ proxy editorial AV review when necessary
→ final technical QC
```

Do not pay a high-end VLM to discover problems already measurable locally.

---

## 3. Current target execution philosophy

The emerging architecture is not “one large multimodal model edits a video.” It is:

```text
AI planning / judgment / critique
             │
             ▼
structured decisions and requests
             │
    ┌────────┴────────┐
    ▼                 ▼
local perception   local execution
and measurement    tools
    │                 │
    └────────┬────────┘
             ▼
       Domain / EDL
             ▼
            MP4
```

The best cost reduction is expected to come from **not invoking models on irrelevant evidence**, rather
than only switching to a slightly cheaper model.

---

## 4. Cross-cutting license rule discovered by Survey V2

For ML/media upstreams, GitHub's repository license is not enough.

Every proposed reusable capability must separately audit:

1. source-code license;
2. model / checkpoint / weight license;
3. bundled dataset / feature / auxiliary-model licenses;
4. transitive native-library licenses;
5. codec/patent implications when shipping encoders/decoders;
6. exact binary build configuration distributed to users.

Examples encountered during this survey show permissive top-level source licenses can coexist with
non-commercial model/data dependencies.

---

## 5. Deployment principle discovered by Survey V2

Do not assume a GPU.

Do allow software environments to be installed or repaired.

Candidate capability tiers:

```text
Tier 0 — core CPU/local runtime
Tier 1 — optional local models/tools, CPU-capable where practical
Tier 2 — optional hardware-accelerated providers
Tier 3 — cloud intelligence providers
```

Hardware acceleration is task-specific, not a universal rule.

---

## 6. Work still open before Roadmap V2

The most important remaining research now sits inside the editing core:

- Candidate Retrieval and ranking;
- embedding strategy and lexical/semantic hybrid search;
- visual-event anchor generation;
- speech/action/music anchor unification;
- Resolver multi-evidence scoring;
- deterministic timing optimization from discrete candidate anchors;
- incremental ReviewReport routing and targeted re-analysis;
- benchmark definitions for “better edit” rather than merely “tests pass”.

These should be studied before Roadmap V2 is frozen.

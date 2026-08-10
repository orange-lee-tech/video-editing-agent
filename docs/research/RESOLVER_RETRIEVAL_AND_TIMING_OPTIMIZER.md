# Resolver Retrieval and Timing Optimizer — Survey V2 Research Draft

**Status:** ACTIVE RESEARCH DRAFT  
**Snapshot date:** 2026-08-10  
**Scope:** Candidate Retrieval → Semantic Retrieval → Temporal Anchors → Resolver Scoring → Deterministic Timing Optimization  
**Authority:** Informative research only; not an Architecture Contract.

---

## 1. Research question

How should the system turn:

```text
Script / EditSlot intent
+ persisted ShotAnalysis / transcript / technical facts
+ visual temporal evidence
+ BeatMap / music evidence
```

into a precise, explainable, high-quality `ResolutionDecision` and ultimately an exact EDL **without asking an LLM to invent floating-point timestamps**, while keeping local compute and API cost reasonable on ordinary Windows hardware?

Current conclusion:

> Treat editing as a **coarse-to-fine retrieval and constrained sequence-selection problem**. LLM/VLM models coordinate semantics and resolve ambiguity; local tools generate evidence and candidate times; a deterministic optimizer chooses among grounded alternatives.

---

## 2. Separate retrieval from final selection

A critical distinction:

```text
Retrieval asks:
"Which Shots are plausibly relevant?"

Resolver selection asks:
"Which candidate is best here, given narrative, continuity, quality, timing, music, locks and reuse?"
```

The retrieval layer should optimize **recall** and cheaply preserve plausible alternatives.

The Resolver should optimize **precision and sequence quality**.

Do not make `embedding_similarity` the final editorial decision score.

---

## 3. Proposed retrieval cascade

Current best research design:

```text
EditSlot / ShotRequirement
        │
        ▼
[0] Hard eligibility filters
        │
        ▼
[1] Existing lexical / CJK retrieval
        │
        ├──────────────┐
        ▼              ▼
[2] Dense semantic text retrieval
        │              │
        └──────┬───────┘
               ▼
[3] rank fusion / broad Top-K
               │
               ▼
[4] structured editorial rescoring
               │
               ▼
[5] targeted observation / VLM only when evidence is insufficient
               │
               ▼
         final candidate set
```

### 3.1 Hard eligibility filters

Examples:

- source locked / forbidden;
- mandatory subject or media condition definitely absent;
- Shot is too short for the slot under all allowed trim policies;
- source boundaries invalid;
- technical quality below a hard threshold for a required use;
- duplicate/reuse hard policy violated;
- commercial/provenance constraint violated;
- user lock or explicit exclusion violated.

These checks should happen before embedding or VLM work.

### 3.2 Lexical retrieval remains valuable

Exact lexical matching is especially useful for:

- product / brand names;
- model numbers;
- prices / numerical facts;
- quoted spoken lines;
- exact on-screen text;
- user labels and filenames;
- specific actions already represented by explicit tags.

Dense semantic retrieval should complement lexical retrieval, not erase it.

### 3.3 Dense retrieval should initially embed structured text, not raw video

The project already pays for or locally derives `ShotAnalysis` facts such as captions, subjects, actions,
environment, framing, keywords and transcript.

Therefore the first semantic retrieval path should normally embed **textual/structured analysis derived from
the Shot**, rather than require an additional raw-frame visual embedding model for every Shot.

Benefits:

- much smaller local runtime;
- CPU deployment is practical;
- no additional cloud call after analysis is cached;
- cross-language semantic search is possible with a multilingual text model;
- embeddings can be regenerated when the embedding model changes without re-reading cloud video.

Raw image/video embeddings remain an optional enhancement for visual-similarity or continuity tasks, not the
baseline semantic-retrieval requirement.

---

## 4. Do not add a vector database server prematurely

The first Windows product is project-local. A typical project is expected to contain hundreds or thousands
of Shots, not internet-scale corpora.

FAISS's own current index guidance explicitly notes that when the number of searches is small enough that
index construction is not amortized, direct/flat computation is appropriate, and flat search is the exact
baseline.

Research implication:

> First benchmark **exact dense cosine/dot-product scan** over project-local embeddings before introducing ANN infrastructure.

A simple baseline can be:

```text
SQLite durable Shot/ShotAnalysis records
        ↓
rebuildable ShotIndex
        ↓
contiguous embedding matrix in memory
        ↓
exact vector similarity
```

This preserves the current architectural rule that `ShotIndex` is rebuildable retrieval infrastructure.

### 4.1 FAISS

`facebookresearch/faiss` is MIT and extremely mature for dense similarity search, including exact and ANN
indices. It remains a strong escalation option if benchmark scale justifies it.

Do not use FAISS merely because it is famous; use it when measurements show that the simpler exact path is
no longer adequate.

### 4.2 sqlite-vec

`asg017/sqlite-vec` is a compelling embedded candidate because it is:

- dual MIT / Apache-2.0;
- pure C;
- dependency-light;
- explicitly supports Windows;
- capable of storing/querying float, int8 and binary vectors inside SQLite.

However the project explicitly labels itself **pre-v1** and warns about breaking changes. Its new ANN work
(DiskANN/IVF) is still in alpha/pre-release development in the 2026 release line.

Current posture:

> Prototype/benchmark behind the `ShotIndex` implementation seam; do not make its schema/API a Domain dependency.

### 4.3 Qdrant

Qdrant is Apache-2.0 and supports dense, sparse, multi-vector, filtering and hybrid fusion. It is an excellent
server/database product.

For an offline-first desktop project with a small per-project corpus it is currently likely heavier than
necessary. Its algorithms and hybrid-search documentation are still valuable references.

---

## 5. Embedding runtime and model candidates

### 5.1 ONNX-first deployment is attractive

Qdrant's FastEmbed demonstrates a useful deployment pattern: local embedding inference through ONNX Runtime
with few external dependencies, CPU by default and optional acceleration.

This matches the project deployment philosophy:

```text
no GPU assumed
optional model/runtime installation
Environment Doctor probes capability
CPU path remains valid
```

The product does not have to adopt Qdrant itself in order to adopt an ONNX-based local embedding strategy.

### 5.2 Candidate A — multilingual MiniLM

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`:

- Apache-2.0;
- 384-dimensional sentence embeddings;
- supports 50 languages;
- current FastEmbed model catalog lists the multilingual MiniLM family around the ~0.22 GB tier.

This is an attractive **small multilingual baseline benchmark candidate**.

### 5.3 Candidate B — multilingual E5 small

`intfloat/multilingual-e5-small`:

- MIT;
- 384-dimensional embeddings;
- multilingual model card covering a broad multilingual training/evaluation setup;
- current safe tensor is approximately 471 MB;
- ONNX/OpenVINO artifacts are available in the model repository.

This is a larger but semantically stronger candidate worth benchmarking, especially for cross-language
retrieval such as a Chinese editing request against English semantic descriptions/transcripts.

### 5.4 Candidate C — BGE small language-specific models

FastEmbed's current catalog includes:

- `BAAI/bge-small-en-v1.5`: MIT, ~0.067 GB ONNX package;
- `BAAI/bge-small-zh-v1.5`: MIT, ~0.090 GB ONNX package.

The Chinese safe-tensor checkpoint itself is approximately 95.8 MB.

These are attractive if language routing proves useful, but a Chinese-only/English-only split can complicate
cross-language retrieval and score calibration.

### 5.5 No embedding model is selected yet

Required benchmark dimensions:

- Chinese query → Chinese analysis;
- English query → English analysis;
- Chinese query → English analysis;
- English query → Chinese analysis;
- commercial-video vocabulary;
- action paraphrases;
- product/brand exactness when combined with lexical search;
- CPU cold-start latency;
- embedding throughput;
- RAM;
- package/model size;
- Windows installation reliability.

The preferred model should be selected by our retrieval benchmark, not a generic MTEB leaderboard alone.

---

## 6. Multi-representation Shot embeddings

A Shot contains several semantically different channels. Collapsing everything into one long text blob may
hide useful signal.

Potential derived representations:

```text
visual_semantic_text
  caption + subjects + actions + environment + framing + visual keywords

speech_text
  transcript / key quotes

user_semantic_text
  user labels / notes / filename-derived hints
```

The first implementation can still keep this simple, but the index contract should not assume “one Shot =
one immutable embedding forever.”

Each derived embedding record should include at least:

```text
source_entity_revision
representation_name
embedding_model_id
embedding_model_revision/hash
dimension
normalization/version
created_at
```

Embeddings are **derived index facts**, not authoritative Shot semantics.

If the model changes, the index can be rebuilt.

---

## 7. Hybrid fusion: use rank fusion before score fusion unless calibrated

Lexical and dense scores have different distributions. Adding raw scores such as:

```text
0.8 * lexical_score + 0.2 * cosine_similarity
```

can be misleading unless those scales are calibrated.

Qdrant's hybrid-search documentation uses Reciprocal Rank Fusion (RRF) to combine dense and sparse/lexical
result lists specifically without requiring raw score comparability.

Current research preference:

```text
lexical ranking
+
dense ranking
→ rank-based fusion (RRF-like baseline)
→ broad Top-K
```

Then compute editorially meaningful normalized features for the Resolver.

RRF is a **retrieval-fusion baseline**, not the final `ResolutionDecision` score.

Hybrid is not automatically superior: benchmark lexical-only, dense-only and hybrid on project-specific
queries.

---

## 8. Visual Event Anchor architecture

The goal is not to build one enormous “action AI.” The goal is to create a compact set of trustworthy
candidate event times that later editorial reasoning can use.

### 8.1 Tier 0 — CPU deterministic anchors

Always-available / low-cost evidence can include:

- Shot boundaries;
- ASR word/sentence boundaries;
- VAD speech begin/end;
- silence boundaries;
- basic audio energy/onset changes;
- OpenCV optical-flow magnitude/direction curves;
- motion onset / peak / stop candidates;
- simple scene/quality transitions.

OpenCV's Farneback dense optical flow produces a per-pixel 2D motion vector field from consecutive frames,
from which magnitude and direction can be derived. This is sufficient to generate generic motion-change
anchors without needing a GPU or cloud model.

### 8.2 Tier 1 — small optional local evidence models

MediaPipe is Apache-2.0 and provides on-device video-mode landmark tasks. For example its Hand Landmarker
uses timestamped video frames and exposes 21 hand landmarks.

Potential derived evidence:

- hand begins moving;
- hand velocity peaks/stops;
- gesture direction changes;
- hand enters/leaves a region;
- body/face pose transitions using corresponding tasks.

Important license discipline remains: code license alone does not approve every bundled task model. Actual
model files must be audited before distribution.

### 8.3 Tier 2 — optional heavier temporal models

OpenTAD/MMAction-style temporal-localization models remain optional providers for machines/configurations
where their runtime weight is justified.

Do not require them for the default Windows product.

### 8.4 Tier 3 — targeted VLM semantic adjudication

Cloud/local VLM should resolve questions that local measurements cannot answer cheaply, for example:

- Which of three motion events is the actual “product lands on the table” event?
- Does the hand movement at Anchor B look intentional or like setup?
- Which candidate ending feels semantically complete?

Prefer asking the VLM to choose/label grounded anchors rather than invent exact seconds.

---

## 9. Speech anchors

Silero VAD is a strong local candidate:

- MIT;
- ONNX Runtime path;
- model around a few MB;
- returns speech timestamps;
- designed for CPU/edge use.

`faster-whisper` also integrates Silero VAD and restores timestamps back to the original audio timeline after
VAD processing.

For dialogue trimming, candidate anchors should combine:

```text
ASR word timestamps
+ sentence/phrase boundaries
+ VAD speech chunks
+ silence gaps
+ punctuation / semantic phrase selection
```

Word-level timestamps are still model estimates and need real benchmarks, especially across languages. They
are evidence, not infallible truth.

---

## 10. CandidateWindow generation

Once a Shot has temporal anchors, do not enumerate every possible millisecond pair.

Generate a bounded set of legal `CandidateWindow` proposals.

Conceptual structure:

```yaml
candidate_window_id: ...
shot_ref: ...
source_start: 7.42
source_end: 9.10
in_anchor:
  type: action_onset
  confidence: 0.86
  evidence_refs: [...]
out_anchor:
  type: speech_phrase_end
  confidence: 0.93
  evidence_refs: [...]
duration: 1.68
internal_events:
  - type: product_centered
    source_time: 8.06
  - type: motion_peak
    source_time: 8.74
```

Generation rules can prioritize:

- duration near the slot target;
- semantically relevant internal events;
- natural speech/action boundaries;
- safe padding around speech;
- no violation of Shot boundaries;
- no dead setup/teardown frames when avoidable.

Candidate windows are Resolver inputs, not EDL authority.

---

## 11. Resolver scoring should have three layers

### 11.1 Hard constraints

Binary feasibility. A violation removes the candidate.

Examples:

- required coverage missing;
- locked source violation;
- illegal overlap/reuse;
- impossible duration;
- provenance/commercial restriction;
- source range invalid.

### 11.2 Unary candidate score

Quality of one candidate for one EditSlot.

Potential components:

```text
semantic_fit
narrative_role_fit
action_fit
subject_fit
technical_quality
framing_fit
duration_fit
speech_fit
music_energy_fit
user_preference
anchor_confidence
```

### 11.3 Pairwise transition score

Quality of placing candidate B after candidate A.

Potential components:

```text
visual_continuity
framing_variety
shot-size transition
motion-direction compatibility
audio continuity
subject continuity
novelty / redundancy
camera-motion rhythm
transition compatibility
```

### 11.4 Global sequence terms

Properties that emerge across the full edit:

```text
mandatory Script coverage
reuse / near-duplicate penalty
energy curve
cut-density target
brand/product visibility timing
CTA placement
framing diversity
music phrase alignment
locked timeline constraints
```

This separation is more useful than one opaque “AI score.”

Persist score components/evidence so Review can explain and reroute failures.

---

## 12. New major evidence: BEAT validates elastic sequence optimization

A particularly relevant 2026 paper is:

> **BEAT: Rhythm-Elastic Alignment for Agentic Music-guided Movie Trailer Generation**  
> arXiv:2605.27067

BEAT independently reaches several conclusions very close to this project's current research direction:

1. professional editing rhythm is elastic rather than rigid one-shot-per-beat;
2. higher-energy music can support faster cuts, while lower-energy spans can sustain one shot across several
   musical units;
3. the core fine-grained alignment should not be delegated entirely to LLM text reasoning due precision and
   API-cost concerns;
4. a learned compatibility score matrix can feed a deterministic sequence optimizer;
5. critic feedback can be mapped back to affected music regions and trigger targeted re-selection.

### 12.1 Bar-DP mechanism

BEAT's `Bar-DP` actually performs beam search over the music-bar sequence.

A state includes:

```text
accumulated score
assignments
used shots / similar-neighbor exclusions
last selected shot
```

At a music bar it considers:

```text
Top-M candidate shots
×
possible elastic span k
```

and scores combinations using:

- alignment quality;
- smoothness/continuity;
- energy-adaptive cut preference;
- duration feasibility;
- no-repeat / neighbor exclusion.

The paper's reported default is:

```text
beam width W = 50
Top-M = 20
maximum span k = 5
```

and reports its selection stage completing in under one second on a single CPU core for its own approximate
scale of 60 bars and 1500 movie shots.

This is **evidence that this class of deterministic search can be tiny relative to feature extraction and
rendering**. It is not a performance guarantee for our implementation.

### 12.2 What to borrow, what not to borrow

Borrow:

- elastic rhythm principle;
- compatibility matrix → sequence optimizer;
- beam-state representation;
- Top-M pruning;
- explicit continuity/reuse/duration constraints;
- critic feedback → localized re-selection.

Do not blindly copy:

- movie-trailer-specific assumptions;
- fixed bar-based timeline for every commercial/Vlog style;
- its MuVA training stack (CLAP/ImageBind + trailer-specific learning) before evidence says we need it;
- generated composition features that conflict with our Product Constitution.

---

## 13. Independent support: EditIQ

`EditIQ: Automated Cinematic Editing of Static Wide-Angle Videos via Dialogue Interpretation and Saliency
Cues` (arXiv:2502.02172) independently models automated cinematic editing as an **energy minimization problem
over shot selection**, combining LLM-derived dialogue understanding with visual saliency and cinematic
constraints governing shot choices, transitions and continuity.

Although its capture setup is very different from our user-footage product, it reinforces the structural
idea that:

> semantic AI can produce evidence/intent, while final shot assembly can be an explicit optimization problem.

---

## 14. Proposed first optimizer family: layered beam search / DAG dynamic programming

The first implementation candidate should be a custom, explainable sequence optimizer rather than an LLM
planner or a heavyweight general solver.

Conceptual state:

```text
state = (
  next_slot,
  accumulated_timeline_time,
  music_position_or_phrase_state,
  last_candidate,
  used_source_neighborhoods,
  coverage_state,
  accumulated_score
)
```

For each EditSlot:

```text
retrieve / score Top-K Shots
        ↓
generate bounded CandidateWindows
        ↓
expand each beam state with legal windows
        ↓
add unary + pairwise + global incremental score
        ↓
prune invalid states
        ↓
keep Top-W states
```

End result:

```text
best grounded candidate sequence
→ ResolutionDecision[*]
→ EDLBuilder
```

Why this is attractive:

- deterministic once evidence/weights are fixed;
- easy to inspect;
- constraints can reject impossible transitions early;
- no floating-point timestamp hallucination;
- naturally supports Top-K candidate pruning;
- beam width gives a direct speed/quality knob;
- compatible with localized re-optimization after Review.

No `W`, `K`, scoring weights or pruning threshold is frozen yet.

---

## 15. Music alignment should be elastic

Do not define “卡点” as “every cut must occur on every beat.”

Instead treat music anchors as a set of opportunities/constraints:

```text
beat
downbeat
accent
phrase boundary
section transition
drop/build-up
energy level
```

An EditSlot or visual event can state its alignment intent:

```yaml
alignment:
  target_event: product_lands
  preferred_music_anchor: accent
  tolerance_ms: TBD
  strength: preferred
```

Possible outcomes:

- high-energy phrase → shorter windows / more frequent cuts;
- low-energy phrase → one window spans multiple beats/bars;
- important internal visual event aligns to an accent while the clip itself starts before the beat;
- dialogue-dominant Vlog segment ignores weak beat opportunities to preserve natural speech.

The Commercial/Vlog Skill supplies the prior; BeatMap supplies facts; Resolver/optimizer decides the legal
alignment.

---

## 16. When to consider OR-Tools CP-SAT

Google OR-Tools CP-SAT is a mature general constraint solver and is appropriate for integer/Boolean-heavy
constraint optimization.

It may become useful if future editing constraints grow beyond a clean layered sequence problem, e.g.:

- multiple coupled tracks;
- globally constrained asset reuse;
- several optional sections;
- complex allocation of duration budgets;
- mutually exclusive placements;
- cross-track scheduling.

Current research posture:

> Keep an optimizer abstraction, but start by benchmarking a custom beam-search/layered-DP implementation.
> Escalate to CP-SAT only when constraint complexity justifies the added dependency/modeling cost.

---

## 17. Retrieval and Resolver benchmarking

### 17.1 Retrieval benchmark

Construct real `EditSlot query → relevant Shot set` labels.

Compare:

- lexical only;
- dense only;
- lexical + dense rank fusion;
- optional reranker;
- optional targeted VLM.

Metrics should emphasize high recall in the candidate pool, for example:

- Recall@K;
- MRR / nDCG where useful;
- miss rate for mandatory commercial proof shots;
- CPU latency;
- cold-start/model-load latency;
- RAM;
- disk/model footprint.

Do not freeze a target K before benchmark evidence.

### 17.2 Anchor benchmark

For human-selected edit points, evaluate:

- whether the human cut has a nearby generated anchor;
- nearest-anchor temporal error;
- anchor-type precision;
- speech/action completeness;
- candidate count per Shot;
- CPU analysis time.

The first goal is **anchor recall**: the optimizer cannot choose a good cut if the candidate set never contains
one.

### 17.3 CandidateWindow benchmark

Compare machine candidate windows against human editor acceptable ranges:

- IN/OUT timing error;
- sentence/action completeness;
- amount of dead setup/teardown;
- human preference among top windows;
- visual-naturalness score.

### 17.4 Sequence/optimizer benchmark

Evaluate:

- Brief/Script coverage;
- human sequence preference;
- continuity;
- framing/shot diversity;
- action/music alignment;
- energy/pacing trajectory;
- duplicate/reuse behavior;
- optimizer runtime;
- number of VLM escalations;
- total API cost.

### 17.5 Cost telemetry

Persist cost evidence per pipeline revision:

```text
local analysis wall time
embedding time
retrieval time
optimizer time
number of VLM calls
frames/video seconds sent to VLM
text tokens where available
provider cost estimate
render time
```

Optimization claims must be based on these measurements.

---

## 18. Proposed cost/quality operating principle

```text
High recall cheaply
        ↓
Keep only plausible candidates
        ↓
Use local evidence to resolve most timing
        ↓
Spend strong-model budget only on ambiguous/high-impact choices
        ↓
Optimize the final sequence deterministically
        ↓
Review only the affected plan/region when possible
```

In short:

> **Do not make the AI cheaper by making it weaker everywhere. Make the system cheaper by sending strong AI only the questions that actually require strong judgment.**

---

## 19. Candidate implementation posture after this survey

This is not a Roadmap, but the present technical preference is:

### Candidate Retrieval

```text
existing lexical/CJK retrieval
+
local multilingual text embeddings
+
RRF-like rank fusion
+
structured editorial rescoring
```

### Vector storage/search

```text
first: exact in-memory scan over rebuildable project index
later benchmark: sqlite-vec / FAISS if scale requires
avoid: mandatory vector DB server for the first desktop product
```

### Embeddings to benchmark first

```text
paraphrase-multilingual-MiniLM-L12-v2
multilingual-e5-small
BGE small zh/en language-routed baseline
```

### Temporal anchors

```text
Tier 0: Shot + ASR + VAD + silence + OpenCV motion
Tier 1: optional MediaPipe/other small local evidence models
Tier 2: optional heavy temporal models
Tier 3: targeted VLM adjudication
```

### Sequence optimization

```text
first candidate: layered beam search / DP over discrete CandidateWindows
later escalation: CP-SAT if global constraints become substantially more complex
```

---

## 20. Primary references for future audit

- BEAT: Rhythm-Elastic Alignment for Agentic Music-guided Movie Trailer Generation — arXiv:2605.27067
- EditIQ: Automated Cinematic Editing of Static Wide-Angle Videos via Dialogue Interpretation and Saliency Cues — arXiv:2502.02172
- Meta FAISS — `facebookresearch/faiss`
- sqlite-vec — `asg017/sqlite-vec`
- Qdrant FastEmbed documentation / supported-model catalog / hybrid-query RRF documentation
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- `intfloat/multilingual-e5-small`
- `BAAI/bge-small-en-v1.5`
- `BAAI/bge-small-zh-v1.5`
- OpenCV Optical Flow documentation (`calcOpticalFlowFarneback`)
- Google MediaPipe Hand/Pose/Face Landmarker Tasks
- Silero VAD — `snakers4/silero-vad`
- faster-whisper — `SYSTRAN/faster-whisper`
- Google OR-Tools CP-SAT documentation

---

## 21. Open questions before architecture freeze

- Which multilingual embedding model wins on our real commercial/Vlog retrieval benchmark?
- Is one embedding per Shot enough, or do separate visual-semantic / transcript representations materially
  improve Recall@K?
- Does exact vector scan remain sufficiently fast after multi-project scale grows?
- Is sqlite-vec stable enough for the eventual Windows distribution path?
- What is the best rank-fusion strategy for lexical + dense + structured tags?
- Which OpenCV motion features give useful generic anchors without being dominated by camera motion?
- Which optional local landmark/detector models have clean distributable model licenses?
- How should anchor confidence from heterogeneous tools be calibrated?
- How many CandidateWindows per Shot are enough to preserve good human cuts without exploding search?
- Which unary/pairwise/global score terms measurably improve human preference?
- What beam width / Top-K / pruning strategy gives the best quality-cost curve?
- When does a general CP-SAT model outperform the simpler layered optimizer in engineering value?
- How should ReviewReport map a failure back to the smallest optimizer state/slot range for local re-solve?

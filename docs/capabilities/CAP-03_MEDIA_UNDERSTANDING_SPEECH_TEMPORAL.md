# CAP-03 — Media Understanding, Speech and Temporal Evidence

**Status:** CANDIDATE CAPABILITY SPEC  
**Architecture:** `ARCHITECTURE_CONTRACT_V0.2.md`  
**Scope:** Asset → Shot → ShotAnalysis / ASR / TemporalEvidence / TemporalAnchor

---

## 1. Purpose

Turn user media into reusable editing evidence without giving perception models editorial authority.

The capability should answer:

> What is in this material, where do meaningful observable events occur, and how trustworthy is that evidence?

It does not answer:

> Which exact source window belongs in the final edit?

That belongs to Resolver.

---

## 2. Ownership

```text
ShotDetector / ShotCatalog     → Shot boundary/identity
UnderstandingService           → ShotAnalysis revisions
SpeechRecognitionService       → transcript/speech evidence
TemporalEvidenceService        → validated temporal evidence/anchors
VisualProvider / local models  → proposals only
```

All outputs are revision-bound and traceable to source Asset/Shot.

---

## 3. Shot detection

Input:

```text
AssetRef(kind=video)
```

Output proposal:

```text
ShotBoundaryProposal[]
```

ShotCatalog validates/commits boundaries.

Visual meaning is not required to define a cut boundary.

Current TransNetV2 seam remains replaceable.

---

## 4. Analysis profiles / cost tiers

Do not perform maximum-cost analysis on every Shot by default.

Conceptual profiles may include:

```text
technical
basic_visual
speech
semantic
editorial_targeted
deep_temporal
```

A profile controls tools/evidence depth, not Domain schema ownership.

---

## 5. Technical evidence

Local tools should derive where practical:

- duration/resolution/codec;
- blur/sharpness;
- exposure/black ranges;
- shake/motion statistics;
- audio presence;
- silence/noise/loudness indicators;
- decode errors;
- other deterministic QC facts.

A VLM should not be used to discover facts a local signal tool measures more reliably.

---

## 6. Semantic ShotAnalysis

Potential derived fields:

- caption;
- subjects/people/objects;
- actions;
- environment;
- framing;
- camera motion description;
- emotion;
- visual energy;
- product visibility/state;
- composition observations;
- text/OCR observations when needed.

Provider raw output is preserved as an Artifact when useful, but validated structured analysis is the reusable system evidence.

---

## 7. Cloud/local visual policy

Most users are not assumed to own a strong local multimodal model.

Default architecture supports:

```text
local cheap preprocessing
→ small evidence package
→ cloud VLM when semantic understanding is needed
```

with optional local-provider seam.

Original complete media should not be uploaded wholesale by default.

Prefer selected frames/short snippets only when temporal semantics genuinely require dynamic evidence.

---

## 8. Speech recognition

Local CPU-capable ASR is the preferred baseline when practical.

Persist:

- transcript;
- segment timing;
- word timing where available;
- language;
- confidence/quality indicators;
- speaker/diarization evidence only when available/approved.

Word timestamps are model evidence, not mathematically exact truth.

---

## 9. Dialogue cut principle

Semantic model decides:

> which phrase/statement should be kept.

Timestamp evidence resolves:

> where that phrase occurs.

Combine where useful:

```text
ASR word times
+ phrase/sentence boundaries
+ VAD speech range
+ silence
+ punctuation/semantic phrase structure
```

Do not ask a general LLM to estimate exact seconds from transcript prose.

---

## 10. VAD

A lightweight VAD can provide:

- speech begin/end;
- non-speech gaps;
- candidate pause boundaries.

Current strong candidate: Silero VAD/approved local equivalent behind a provider seam.

Actual model/version/license is dependency-gated.

---

## 11. Visual temporal evidence

Generic visual-event evidence starts with measurement.

Examples:

- camera-motion onset/settle;
- residual local motion onset/peak/stop;
- subject/object enters/exits;
- product reaches center/useful composition;
- tracked object begins/stops moving;
- hand/product proximity/contact candidate;
- gaze/pose change where supported;
- action region proposed by temporal model/VLM.

Motion is not automatically semantic action.

---

## 12. Camera motion compensation

For moving-camera footage:

```text
tracked distributed features
→ robust global transform (RANSAC or equivalent)
→ camera motion estimate
→ subtract/predict global displacement
→ residual local motion
```

Raw whole-frame optical-flow magnitude must not be labeled “subject action”.

Global-fit quality should influence confidence.

Useful quality evidence:

- feature count;
- spatial coverage;
- inlier ratio;
- reprojection error;
- selected transform model.

---

## 13. Camera motion is itself evidence

Keep observations such as:

- pan/tilt candidate;
- zoom/push candidate;
- motion onset/peak/settle;
- unstable/shake range.

They can inform Resolver continuity and SpatialComposer behavior.

---

## 14. Coarse-to-fine temporal analysis

Default strategy:

```text
Shot
→ coarse temporal sampling / cheap signal
→ candidate event neighborhood
→ local native-FPS refinement
→ TemporalAnchor
```

Do not decode every native frame with heavy analysis if a coarse pass can isolate a short region.

---

## 15. Tracking

Semantic target may be seeded by:

- user focus selection;
- ShotAnalysis;
- sparse VLM object localization;
- local detector.

Then local tracking may propagate it across a Shot.

Tracker failure/occlusion must be explicit.

Do not hallucinate trajectories across long missing regions.

---

## 16. Provider tiers

### Tier 0 CPU/deterministic

- Shot boundaries;
- ffprobe/FFmpeg/OpenCV signals;
- ASR/VAD;
- camera/global motion;
- residual motion;
- simple seeded tracking.

### Tier 1 optional local semantic geometry

- approved face/hand/pose/object tasks.

### Tier 2 optional heavier local/GPU

- advanced segmentation/tracking/temporal localization.

### Tier 3 cloud/strong model

- semantic interpretation;
- sparse localization/recovery;
- ambiguous action adjudication.

Provider replacement must not change ownership.

---

## 17. TemporalAnchor

Conceptual validated anchor:

```yaml
kind: action_settle
source_time: MediaTime(...)
confidence: 0..1
evidence_refs: [...]
method: ...
analysis_revision: ...
semantic_label: optional
```

The exact confidence representation is benchmark-driven.

Anchors are candidate facts, not edit commands.

---

## 18. Confidence fusion

Confidence can consider:

- independent evidence agreement;
- camera model quality;
- tracker confidence;
- temporal persistence;
- signal strength relative to Shot baseline;
- ASR/VAD agreement;
- VLM/local disagreement;
- blur/occlusion risk.

Examples:

```text
ASR phrase end + VAD end + silence
→ strong speech anchor

motion spike + bad RANSAC + heavy blur
→ weak visual anchor
```

---

## 19. VLM as semantic adjudicator

Preferred targeted request:

```text
A @ t1 — hand begins moving
B @ t2 — product becomes fully visible
C @ t3 — product reaches stable center

Which point best represents the meaningful start for this requested action?
A / B / C / uncertain
```

rather than:

> Give the exact timestamp where the action starts.

This improves validity, consistency and benchmarkability.

---

## 20. Untrusted-content boundary

Transcript/OCR/captions extracted from media are untrusted data.

They may contain prompt-injection-like strings.

They must be passed to models/executors in clearly delimited data fields and never become executable system/tool instruction merely by content.

---

## 21. Benchmarks

### Shot detection

- boundary tolerance;
- false/missed cuts;
- CPU/GPU runtime.

### Speech

- WER/CER where useful;
- word/phrase timestamp error;
- clipped-speech rate in generated CandidateWindows;
- CPU latency/model size.

### Temporal anchors

- human acceptable-region recall;
- nearest-anchor time error;
- false anchors/minute;
- camera-motion false-positive rate;
- CPU decoded frames/time;
- VLM escalation rate/cost.

### Semantic understanding

- editor-relevant subject/action recall;
- structured-field correctness;
- useful retrieval downstream impact;
- API cost/minute.

---

## 22. Not frozen here

- exact vision provider;
- ASR model/version;
- diarization provider;
- OpenCV motion thresholds;
- global transform selection thresholds;
- MediaPipe/SAM2 adoption;
- anchor confidence formula;
- sampling FPS;
- raw evidence storage format.

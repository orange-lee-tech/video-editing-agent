# CAP-06 — Music Selection, BeatMap and Audio Editorial

**Status:** CANDIDATE CAPABILITY SPEC  
**Architecture:** `ARCHITECTURE_CONTRACT_V0.2.md`  
**Research:** `AUDIO_EDITORIAL_MUSIC_SELECTION_RIGHTS.md`

---

## 1. Purpose

Create a rights-aware soundtrack and deterministic mix that supports the narrative without letting music analysis or a general LLM own the timeline.

---

## 2. Ownership

```text
MusicProvider / LocalMusicSource → candidates only
MusicSelectionService            → MusicSelectionDecision
BeatAnalysisService              → BeatMap
AudioEditorialService            → AudioMixDecision
EDLBuilder                       → exact audio tracks/automation
Renderer                         → deterministic execution
RightsProvenanceService          → license/attestation records
```

---

## 3. MusicIntent

Derived from Brief/Script/EditPlan/CommercialSkill.

Potential dimensions:

- mood/theme;
- genre/instruments;
- vocal/instrumental preference;
- energy curve;
- narration density;
- target duration;
- beat-sync strength;
- platform/objective;
- rights scope;
- user preferences.

It is provider-neutral.

---

## 4. Candidate acquisition paths

### Local user music

```text
local file
→ rights attestation
→ Asset(kind=audio, role=music)
```

### Connected/public library

```text
provider search
→ MusicCandidate metadata
→ rights gate
→ user/system-approved acquisition path
→ AssetIngest
→ audio Asset
```

User-entered arbitrary audio URLs are not the normal ingest path.

---

## 5. Rights-aware candidate gate

Before expensive semantic analysis classify:

```text
eligible_clear
eligible_with_warning
ineligible
unknown
```

Consider provider evidence such as:

- commercial use;
- paid advertising;
- platform scope;
- attribution;
- territory;
- one-project/video restriction;
- modification/cut/loop permission;
- expiry/perpetual status.

`unknown` is not `clear`.

---

## 6. Generated-audio filtering

If provider metadata identifies AI-generated music:

```text
generated audio feature OFF
→ exclude from normal pool
```

If user explicitly enables generated audio, normal rights/provenance review still applies.

Do not infer human/generated status if provider cannot supply evidence; preserve unknown rather than inventing certainty.

---

## 7. Retrieval cascade

```text
rights-compatible pool
→ provider metadata/tag/native search
→ optional local semantic audio-text retrieval
→ broad Top-K
→ BeatMap/music-structure analysis
→ temporal rerank against video energy/narration
→ MusicSelectionDecision
```

The first implementation does not require a heavyweight CLAP model if metadata/BeatMap benchmarks are sufficient.

---

## 8. Music semantic models

Audio-text embeddings are optional providers.

Code license, checkpoint license and training-data provenance are separate gates.

Current researched examples:

- LAION CLAP: architecture/prototype reference; checkpoint/data review required;
- Microsoft CLAP: MIT code, separately licensed model weights; bundled deployment requires model-license approval.

No model is frozen by this spec.

---

## 9. BeatMap

BeatMap remains descriptive:

- tempo/BPM;
- beats/downbeats;
- accents;
- phrases/sections;
- energy/onset;
- build/drop/breakdown/chorus-like structure;
- confidence.

It does not say where video must cut.

---

## 10. CandidateMusicWindow

A short-form video usually needs a musically coherent moment from a longer track.

Generate candidate windows using:

- phrase boundaries;
- section boundaries;
- downbeats;
- drop/build points;
- energy profile;
- vocal occupancy;
- desired video duration.

Prefer grounded musical boundaries over arbitrary LLM-generated seconds.

---

## 11. Temporal reranking

For Top-K tracks/windows compare:

- semantic fit;
- mood/theme;
- energy trajectory;
- climax position;
- narration conflict;
- vocal density;
- action/beat opportunities;
- duration/loop feasibility;
- rights confidence;
- user preference.

Recent retrieval/moment-localization research supports broad retrieval followed by fine temporal reranking.

---

## 12. MusicSelectionDecision

Conceptual fields:

```text
selected_audio_asset_ref
selected_source_range / loop plan
BeatMap ref
rights_snapshot_ref
semantic fit
rhythm/temporal fit
alternatives
score
confidence
reasons
warnings
```

This is likely a durable Application artifact, not top-level Domain Entity.

---

## 13. Structural looping

If a track needs extension:

1. prefer a longer natural section;
2. choose compatible bar/phrase boundaries;
3. deterministic crossfade/loop;
4. reject conspicuous loops when alternatives exist.

No generative music extension is implied.

---

## 14. AudioEditorial inputs

```text
source dialogue/ambience
voiceover
selected BGM
SFX
ASR/VAD ranges
BeatMap
EditPlan/CommercialSkill
OutputSpec
user locks/preferences
```

### Source-audio lane separation

The authoritative ingested video Asset remains immutable and keeps its original muxed audio. Do not destructively strip or rewrite user source media merely because most edits will not use its original sound.

Visual and source-audio processing should nevertheless be logically separated as early as practical:

```text
authoritative video Asset
├─ visual decode / Shot / visual evidence path
└─ source-audio analysis/editorial path
```

Visual-only processing should not decode or carry audio merely because the container contains it. Speech/VAD/audio QC may consume the source Asset directly through stream-selective decode or a reusable derived audio Artifact.

A demuxed/decoded audio proxy, waveform or temporary stem is a derived Artifact, not a new Asset. It must preserve source-time mapping/provenance. Materializing a full audio proxy on every ingest is not mandatory: use stream-selective decode by default and introduce/reuse a cached audio derivative when repeated analysis benchmarks show a real latency/I/O win.

### Default source-audio editorial policy

Source-audio presence does not imply source-audio use.

For routine short-form edits where the camera audio contains no required dialogue, ambience or meaningful action sound, the normal editorial default is:

```text
source audio → MUTE
```

If grounded evidence or explicit user/editorial intent says source sound matters, use `PRESERVE` or an explicit attenuated/ducked policy as appropriate. Examples include dialogue, narration captured in-camera, meaningful product/action sound, or ambience that materially supports the scene.

Do not run expensive denoising merely to rescue unneeded camera audio; muting it is often the better editorial decision. Denoising is a separate optional capability and is not implied by this spec.

When source dialogue or other essential sound is retained, its grounded time ranges become edit constraints: CandidateWindow/Resolver/EDL construction must not casually cut a required phrase or critical sound event in half.

For the normal product path, final output should contain at least one intentional audible lane (retained source audio, voiceover, BGM or SFX) unless the user explicitly requests silence. Technical QC must catch accidental silent output.

---

## 15. Speech-first ducking

For narration-heavy commercial video, use known speech ranges to create an explicit BGM envelope where useful:

```text
speech begins
→ ramp BGM down
speech active
→ reduced level
speech ends
→ release/ramp up
```

This is inspectable and editable.

Sidechain compression is an alternative backend strategy, not Domain semantics.

---

## 16. AudioMixDecision

Potential contents:

- track roles;
- source audio preserve/mute policy;
- voiceover placement intent;
- BGM gain envelope;
- fades/crossfades;
- SFX placement;
- loop mapping;
- pan/channel intent where relevant;
- loudness intent;
- confidence/warnings.

EDLBuilder compiles this into exact timeline automation.

---

## 17. Local execution

FFmpeg is the preferred baseline implementation family for:

- mixing;
- gain;
- fades/crossfades;
- loudness normalization;
- sidechain/ducking options;
- silence detection;
- channel routing;
- encode.

A richer audio effect framework may be introduced only through an ADR/benchmark and compatible license review.

---

## 18. Technical QC

Check locally:

- missing tracks;
- clipping/peak problems;
- unintended silence;
- loudness target deviations;
- abrupt loop boundaries;
- invalid source ranges;
- missing rights/attribution evidence;
- speech/BGM balance heuristics.

Editorial reviewer handles mood/narrative fit.

---

## 19. Benchmarks

### Selection

- Top-K human preference recall;
- chosen track win rate;
- rights-filter correctness;
- cross-language music intent.

### Music moment

- phrase/section completeness;
- chosen-window human preference;
- energy/narration fit;
- loop conspicuousness.

### Mix

- speech intelligibility;
- BGM naturalness;
- duck/fade preference;
- loudness/peak compliance;
- user override rate;
- render cost.

---

## 20. Not frozen here

- music provider priority;
- CLAP adoption;
- default music score threshold;
- BeatMap model;
- ducking gain/fade constants;
- loudness delivery presets;
- provider purchase/license UX;
- AI-generated audio provider.

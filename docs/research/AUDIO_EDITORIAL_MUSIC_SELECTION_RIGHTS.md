# Audio Editorial / Music Selection & Rights — Survey V2 Closure Draft

**Status:** FOCUSED SURVEY PASS  
**Snapshot date:** 2026-08-11  
**Scope:** Music Intent → Rights-aware Candidate Pool → Track Retrieval → Music Moment Selection → Audio Editorial / Mixing → EDL Audio Tracks  
**Authority:** Informative research only; not an Architecture Contract or legal opinion.

---

## 1. Closure question

How should the product choose useful music, choose the right portion of that music, mix it with source audio / narration / SFX, and preserve commercial-rights evidence without turning a general LLM into a DAW and without treating a vague label such as “royalty free” as legal proof?

Current conclusion:

> **Use a rights-aware, coarse-to-fine music retrieval pipeline followed by structure-aware moment selection and deterministic local audio mixing.**

The system should spend model intelligence on semantic/mood/editorial judgment. Search, timing, gain envelopes, ducking, fades, normalization, looping and rendering should be represented as structured decisions and executed by local audio/media tools.

This focused Survey Gate is sufficiently complete for Architecture Contract v0.2 and capability-spec design. Exact providers, embedding checkpoints, loudness targets and mix presets remain benchmark/release decisions.

---

## 2. Preserve four different responsibilities

Do not collapse these into a single “Music Agent”:

```text
Music Intent
    ↓
Music Discovery / Retrieval
    ↓
Music Selection + Source Window
    ↓
Audio Editorial / Mix Planning
    ↓
EDL Audio Tracks
    ↓
Renderer
```

### 2.1 Music intent

Derived from:

- Brief;
- ScriptPlan;
- EditPlan / CommercialSkill;
- narration density;
- visual energy;
- target duration;
- platform / marketing objective;
- user preferences.

It describes what kind of soundtrack is wanted, not a specific provider track.

### 2.2 Music discovery

Returns provider/local candidates and evidence. It does not create an Asset and does not write EDL.

### 2.3 Music selection

Chooses a specific eligible audio Asset/candidate and a musically meaningful source window / loop strategy.

### 2.4 Audio editorial

Plans the relationship between:

- source dialogue / ambience;
- voiceover;
- BGM;
- SFX;
- optional generated audio only when constitutionally enabled.

Renderer only executes the resulting audio track instructions.

---

## 3. Constitution alignment

The Product Constitution intentionally treats audio differently from visual material.

Allowed normal paths include:

- user-supplied local music / voice / SFX;
- public or connected music-library discovery;
- risk-aware presentation of tracks whose commercial rights are not fully confirmed;
- explicit user attestation/override where the user possesses rights the product cannot verify.

The focused survey does **not** reopen the prohibition on remote visual material.

### 3.1 Remote audio must still enter through Asset ingest

Do not allow:

```text
MusicProvider URL
→ EDL
```

Preferred path:

```text
MusicProvider candidate
→ rights / eligibility gate
→ provider fetch / user acquisition
→ MediaSource
→ AssetIngestService
→ Asset(kind=audio, usage_role=music)
→ BeatMap / MusicSelectionDecision
→ EDL
```

A provider URL is transport metadata, not timeline identity.

### 3.2 Generated-audio boundary

If a library/provider exposes AI-generated music, the candidate should preserve a creation-method signal when available.

Because AI-generated music is an optional constitutional category with default OFF:

```text
generated_audio candidate
→ feature disabled
→ exclude from normal candidate pool

feature explicitly enabled
→ candidate may proceed through the same rights/provenance gates
```

Do not silently treat generated library music as ordinary human-created library music when provenance says otherwise.

---

## 4. MusicIntent should be structured

A future value object may carry concepts such as:

```yaml
theme: product launch
mood: confident / clean / optimistic
energy_curve: build gradually, strongest final third
preferred_genres: [electronic, modern_pop]
preferred_instruments: [light_synth, percussion]
vocal_policy: instrumental_preferred
narration_density: high
beat_sync_strength: medium
target_duration: 28s
platform: short_form_vertical
marketing_objective: conversion
rights_scope:
  commercial: required
  advertising: required
  target_platforms: [...]
```

This is not a frozen schema. It establishes the boundary between editorial intent and provider-specific query syntax.

---

## 5. Rights gate comes before expensive ranking

A technically perfect track that cannot be used for the project is not a valid final candidate.

Preferred pipeline:

```text
provider / local candidate pool
        ↓
rights compatibility gate
        ↓
cheap metadata / tag retrieval
        ↓
semantic retrieval
        ↓
Top-K
        ↓
temporal / music-structure rerank
        ↓
editorial selection
```

Rights filtering should remove clearly incompatible tracks early and mark ambiguous tracks before expensive analysis.

The Product Constitution still permits an ambiguous-rights candidate to be shown with a clear warning. Therefore the gate should support at least:

```text
eligible_clear
eligible_with_warning
ineligible
unknown
```

`unknown` is not equivalent to `clear`.

---

## 6. RightsSnapshot / LicenseSnapshot is required architecture work

“Royalty free” is not sufficient provenance.

A future durable rights record should preserve, when available:

```text
provider
provider_track_id
license_family / product
license_version / terms identifier
license_url or document reference
terms/evidence snapshot hash
acquired_at
commercial_use
advertising_use
allowed_platforms
territory
expiry / perpetual status
one_project / one_video restrictions
attribution_required
attribution_text
modification / cut / loop permission
certificate / invoice / proof artifact
user_attestation_ref
manual_override_ref
```

Not every provider exposes every field. Missing information remains explicit.

Rights status can change outside the project; historical projects need the terms/evidence that were relied upon at selection time, not merely a live link to today’s provider page.

No software record is a substitute for legal advice.

---

## 7. Jamendo is a strong provider-contract reference

The current Jamendo API exposes a particularly useful discovery model:

- free text search;
- tags / fuzzy tags;
- genre/instrument/theme metadata;
- speed;
- vocal/instrumental filtering;
- duration filters;
- commercial-program flags such as pro licensing;
- optional `licenses` and `musicinfo` data;
- explicit download-allowed state.

Jamendo Licensing separately offers commercial synchronization licenses for videos/advertising.

Research posture:

> **REFERENCE-STRONG / provider prototype candidate, but every concrete commercial acquisition path must preserve the exact license/product evidence used for that track/project.**

Do not assume that every track visible through a general Jamendo catalog endpoint has the same commercial rights.

---

## 8. YouTube Audio Library teaches platform-scope discipline

YouTube describes its Audio Library as copyright-safe for YouTube and supports genre/mood/duration/attribution filtering and monetization on YouTube.

It also explicitly avoids giving legal guidance for music issues outside YouTube.

Architecture lesson:

> `rights_scope.platforms` must be first-class.

A track that is safe/cleared in one platform context must not automatically be labeled universally cleared for TikTok, Meta, broadcast, paid ads, client redistribution, etc.

YouTube Studio-only access also means this is not automatically a general programmatic MusicProvider for the desktop product. It may instead remain a user-acquisition/import path unless an approved integration exists.

---

## 9. Freesound / SFX reinforces per-item licensing

Freesound exposes CC0, CC-BY and CC-BY-NC material. The latter is not appropriate for ordinary commercial output.

Its public API usage policy also has separate commercial considerations.

Lesson:

- SFX deserves the same per-item rights/provenance machinery as music;
- provider availability does not imply commercial API permission;
- source-file license and API/product terms are separate gates.

---

## 10. Semantic audio-text retrieval is useful, but model license must be split from code license

### 10.1 LAION CLAP

CLAP provides audio/text representations suitable for semantic retrieval.

Important caveat from upstream:

- source code is openly licensed;
- music/speech checkpoints exist;
- upstream explicitly notes copyright restrictions around much of the training data and cannot release the complete training data.

Therefore:

> **REFERENCE-STRONG / prototype candidate; not release-approved merely because the repository/code license is permissive.**

Checkpoint license and training/data provenance require separate review.

### 10.2 Microsoft CLAP

The GitHub code repository is MIT and supports CPU inference (`use_cuda=False`).

However the published Hugging Face weights are labeled under a separate Microsoft model license (`ms-pl`).

Therefore:

> **code and weights must be audited separately; current status is BLOCKED-PENDING-MODEL-LICENSE-REVIEW for bundled commercial deployment.**

This is an important example of the Survey V2 global license rule in practice.

### 10.3 First product does not require CLAP

A good first implementation can still use:

```text
provider tags / metadata
+ BeatMap facts
+ user / Script music intent
+ optional local text/metadata scoring
```

before introducing a large audio-text embedding runtime.

Embedding should enter only if our music-selection benchmark proves a meaningful preference win.

---

## 11. Strong research support for two-stage music recommendation

Recent video-to-music work converges with the project’s coarse-to-fine philosophy.

### VTMR (2026)

The paper uses:

```text
Stage 1: global multimodal semantic retrieval
Stage 2: temporal video/music reranking
```

This is directly useful as a structural reference.

### Video to Music Moment Retrieval / ReaL (2024)

This work highlights a product fact often ignored by generic music recommendation:

> a short video usually needs a **moment from a longer track**, not merely the identity of a track.

Its two-stage task is:

```text
retrieve music
→ localize the best music moment
```

This strongly supports separating `MusicCandidate` from `CandidateMusicWindow`.

No paper-specific training stack or dataset becomes our product dependency merely because the architecture is useful.

---

## 12. CandidateMusicWindow: choose musical boundaries, not arbitrary seconds

After a track receives a BeatMap, generate bounded windows using meaningful anchors:

- phrase start/end;
- section start/end;
- downbeat;
- accent;
- build-up/drop;
- low-energy intro;
- chorus / climax;
- outro;
- vocal occupancy regions.

Conceptual proposal:

```yaml
track_ref: ast_music_...
source_in: ...
source_out: ...
in_anchor: phrase_start
out_anchor: phrase_end
section: chorus
energy_profile: ...
vocal_density: ...
loopable_boundary_confidence: ...
```

Director/CommercialSkill supplies desired energy and narrative role. Music selector chooses among grounded windows.

Do not ask an LLM to invent a random 18.37–46.37 second interval when BeatMap evidence already provides musically coherent boundaries.

---

## 13. Looping and extension should be structural

When the desired timeline duration exceeds a single clean music window:

Preferred order:

1. choose a longer natural section/window when possible;
2. extend at bar/phrase-compatible boundaries;
3. create a deterministic crossfade/loop with measured boundary quality;
4. use a different candidate if the loop is conspicuous;
5. ask user / Reviewer only if the soundtrack is high-value and ambiguous.

Loop decisions should preserve provenance to the original audio Asset and source ranges.

No generative extension is authorized by ordinary looping.

---

## 14. Audio mixing is primarily a deterministic local-tool problem

The baseline commercial-short-video mix does not require an AI DAW.

FFmpeg already exposes the classes of operations needed for a strong baseline, including:

- gain / volume;
- fade / crossfade;
- sidechain compression/gating;
- loudness normalization;
- silence detection;
- mixing / channel routing;
- filters / EQ-like processing where required.

Spotify Pedalboard is a useful **REFERENCE-ONLY** audio-effect-chain implementation: it provides compressors, gain, limiters, EQ/filters, reverb and VST3 hosting on Windows, but its current repository is GPLv3 and therefore should not become a default proprietary-product dependency.

The baseline should remain FFmpeg-first unless benchmarks identify a missing capability.

---

## 15. Prefer explicit speech-aware ducking envelopes

For commercial/video narration, speech intelligibility is usually more important than preserving constant BGM level.

The product already has:

- ASR speech ranges;
- VAD ranges;
- narration/voiceover placement;
- Script importance.

Therefore it can create an inspectable ducking envelope:

```text
speech begins
→ BGM ramps down

speech continues
→ BGM holds reduced level

speech ends
→ short release
→ BGM ramps up
```

Advantages over an opaque “AI mix”:

- deterministic;
- explainable;
- easy to preview;
- editable by user;
- avoids pumping when speech timing is already known.

FFmpeg sidechain compression remains another useful execution option. Which method wins belongs to an audio benchmark.

---

## 16. Proposed ownership boundary

Do not make `BeatMap` own music selection or mix decisions.

Research recommendation:

```text
Director / CommercialSkill
    ↓ music intent
MusicSelectionService
    ↓ MusicSelectionDecision
AudioEditorialService
    ↓ AudioMixDecision / automation proposals
EDLBuilder
    ↓ exact audio tracks / automation
Renderer
```

Potential `MusicSelectionDecision` evidence:

```text
selected_audio_asset_ref
selected_source_window
alternatives
semantic_score
rhythm/temporal_score
rights_snapshot_ref
reasons
warnings
confidence
```

Potential `AudioMixDecision` evidence:

```text
track roles
speech-priority ranges
gain envelopes
fades / crossfades
loop plan
source-audio preservation policy
SFX placements
loudness intent
warnings / confidence
```

These are likely Application/derived artifacts, not new top-level core Domain entities.

---

## 17. EDL v0.2 implication: audio automation must be richer than one static gain

Historical `EDLSegment.audio_gain` is not sufficient for high-quality automated audio editing.

Architecture v0.2 should support a deterministic time-varying audio representation such as:

```text
gain automation curve
fade-in / fade-out
crossfade
mute / preserve-source policy
pan/channel mapping where needed
loop/source-range mapping
optional sidechain/ducking instruction compiled into deterministic render graph
```

Exact schema belongs to the EDL capability specification.

Renderer still has no authority to invent these values.

---

## 18. Audio Review / Quality Gate

Local technical checks can detect or measure:

- missing audio;
- clipping / true-peak problems;
- silence where speech/music is expected;
- loudness outside configured delivery target;
- dialogue/BGM ratio heuristics;
- abrupt loop/crossfade discontinuity;
- missing attribution/license evidence;
- source range validity.

Editorial review then asks higher-level questions:

- does the track fit the intended mood/message?
- does the music overpower narration?
- does the selected section build at the right time?
- is the climax/drop aligned with the edit intentionally rather than mechanically?

Reviewer should reroute only the affected music selection/mix decision where possible.

---

## 19. CPU / cost tiers

### Tier 0 — default local

- provider metadata / local-file metadata;
- FFmpeg audio analysis/mixing;
- BeatMap baseline;
- ASR/VAD-derived speech timing;
- deterministic CandidateMusicWindow generation.

### Tier 1 — optional local semantic retrieval

- approved audio-text embedding model after checkpoint/license review;
- richer MIR features.

### Tier 2 — optional GPU enhancement

- heavier multimodal/audio models only if benchmarks justify them.

### Tier 3 — cloud intelligence

- semantic music-intent refinement;
- difficult Top-K adjudication;
- high-value final editorial review.

Do not upload entire music catalogs to a cloud model merely to rank them.

---

## 20. Benchmark before provider/model freeze

Required benchmark dimensions:

### Music retrieval

- human Top-K preference recall;
- semantic/mood fit;
- genre/instrument/vocal compliance;
- cross-language query quality;
- provider rights eligibility precision;
- local latency / API cost.

### Music moment selection

- human preference for chosen source window;
- phrase completeness;
- energy-curve fit;
- narration conflict;
- action/beat opportunity;
- loop conspicuousness.

### Mix quality

- speech intelligibility;
- BGM balance;
- fade/duck naturalness;
- loudness/peak compliance;
- abrupt discontinuities;
- human preference;
- render cost.

No fixed ducking dB, fade duration or target loudness becomes domain truth before benchmark/preset evidence.

---

## 21. Upstream / provider posture after focused survey

| Source / upstream | Current posture | Why |
|---|---|---|
| FFmpeg audio filters | DIRECT-CANDIDATE | deterministic baseline mix/render/QC; approved build still required |
| Jamendo API/Licensing | REFERENCE-STRONG / provider prototype candidate | rich search + licensing metadata/commercial program; exact rights snapshot required |
| LAION CLAP | REFERENCE-STRONG / prototype | excellent audio-text retrieval idea; checkpoint/data provenance gate remains |
| Microsoft CLAP code | REFERENCE-STRONG / prototype | MIT code and CPU support |
| Microsoft CLAP weights | BLOCKED-PENDING-MODEL-LICENSE-REVIEW | model license differs from code license |
| Spotify Pedalboard | REFERENCE-ONLY | strong DSP/effect-chain implementation; GPLv3 |
| YouTube Audio Library | USER/PLATFORM-SCOPED REFERENCE | strong platform-safe source, but not universal cross-platform rights or general desktop API |
| Freesound | SFX REFERENCE / provider pending terms | per-item CC license + separate API commercial conditions |
| VTMR / VMMR-ReaL research | REFERENCE-STRONG | validates coarse retrieval + temporal reranking/moment localization |

No status here is final legal approval.

---

## 22. Focused Survey verdict

**PASS for architecture design.**

The remaining unknowns are no longer broad capability gaps. They are:

- provider integration choices;
- checkpoint/model legal approval;
- exact rights-product schemas per provider;
- mix preset calibration;
- embedding/model benchmark;
- delivery loudness presets;
- user/license purchase UX.

These belong to Capability Specifications, ADRs, Upstream Ledger V2, benchmarks and release/legal gates.

The product-wide Survey does not need another broad music-ecosystem search before Architecture Contract v0.2 can be drafted.

---

## 23. Primary references retained for later audit

- FFmpeg audio filter implementation/documentation (loudness, fades, sidechain, mix/QC)
- Jamendo API v3 `tracks` and Jamendo Licensing commercial synchronization offerings
- YouTube Audio Library official usage/copyright guidance
- Freesound licensing/API guidance
- LAION-AI/CLAP and published model cards
- `microsoft/CLAP` code repository and `microsoft/msclap` model card/license metadata
- `spotify/pedalboard` (effect-chain reference only)
- VTMR — arXiv:2607.05971
- Video to Music Moment Retrieval — arXiv:2408.16990
- TIVM — arXiv:2503.05008

Future dependency approval must re-check exact upstream revision and terms at the time of adoption.

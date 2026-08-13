# Current Work Order

**Status:** ENGINEERING BASELINE ADEQUATE

**Phase:** R0.10A — Local Music Rights → BeatMap → CandidateMusicWindow → Audible Mix Foundation

**Goal:** establish the first rights-aware, grounded and audible music/audio-editing path using local audio, existing media-time/rights contracts and deterministic FFmpeg execution.

**Technical result:** PASS on 2026-08-13. The local-only Engineering Probe established
rights fail-closed behavior, a deterministic WAV-energy BeatMap, grounded music windows,
explicit VAD duck/fade automation and an audible FFmpeg diagnostic mix. External providers
and later R0.10 Product Probe work were not started.

## Entry

1. Read `docs/operations/CODEX_EXECUTION_ENTRY.md`.
2. Read `docs/roadmap/CURRENT_PHASE_STATUS.md`.
3. Read this file.
4. Read `docs/capabilities/CAP-06_MUSIC_AUDIO_EDITORIAL.md` sections 1–18 and Roadmap V2 R0.10.
5. Inspect only existing Asset/rights, BeatMap placeholder, R0.8 speech/VAD and FFmpeg/audio seams required for this batch.

Do not restart broad music-provider/model research. Do not add a paid/network music service, heavyweight audio-text model, final EDL authority, subtitle/render productization or R0.11+ work.

## 1. Canonical music/audio contracts

Evolve existing canonical seams rather than creating duplicate authorities.

Implement provider-neutral values/artifacts sufficient for this boundary, including as appropriate:

- `MusicIntent`;
- rights-aware local music candidate/eligibility result;
- canonical `BeatMap` with rational source-time beats/downbeats/energy or confidence data actually measured by the baseline;
- grounded `CandidateMusicWindow` wholly inside the authoritative audio Asset;
- `MusicSelectionDecision` for the selected local candidate/window;
- basic `AudioMixDecision` describing source-audio/BGM policy and explicit gain/duck/fade envelope intent.

Keep provider/strategy parameters out of Domain truth. Do not let BeatMap or a model create video-cut authority.

## 2. Rights-first local music path

Start from local user-owned/attested audio only.

Reuse `RightsAttestation`, `LicenseSnapshot`, `ManualLicenseOverride` and `RightsEligibility` semantics where they apply. Required behavior:

- `unknown` is never treated as clear;
- ineligible music cannot become a selection;
- warning requires inspectable warning/provenance;
- local user music can become eligible through explicit attestation without pretending the system independently certified copyright;
- generated/provider music remains outside the normal product pool in this batch.

No arbitrary URL ingest and no external purchase flow.

## 3. BeatMap baseline

Implement a CPU-practical local BeatMap provider/service behind the owned seam. Prefer existing/local lightweight dependencies or FFmpeg-compatible analysis; do not add a large runtime merely for this batch.

Measure only what the implementation can support honestly. At minimum establish useful periodic/energy timing evidence sufficient to generate grounded musical windows. If reliable downbeat/phrase/section inference is not available in the first baseline, preserve those fields as unavailable rather than fabricating them.

All BeatMap times use canonical rational `MediaTime` and remain inside the exact audio Asset source range.

## 4. CandidateMusicWindow + selection

Generate a bounded set of legal candidate music windows from measured BeatMap/audio boundaries and requested target duration. No arbitrary LLM timestamps and no millisecond enumeration.

The selected window must preserve:

- exact audio Asset revision;
- exact rational source range;
- BeatMap/evidence refs;
- rights provenance;
- strategy version;
- score/confidence/reasons/warnings where available.

Selection can begin with transparent local metadata/structure rules. Do not add CLAP or another semantic-audio model unless the current evidence shows the batch cannot be completed without it.

## 5. Basic AudioEditorial foundation

Use existing R0.8 speech/VAD ranges when available to produce an explicit deterministic BGM gain envelope.

At minimum support:

- source audio preserve/mute policy;
- BGM base gain;
- speech-aware duck-down / release envelope represented as inspectable data;
- simple fade-in/fade-out;
- no clipping/invalid-range behavior;
- explicit unresolved/warning behavior when required audio evidence is missing.

Do not encode these semantics only as opaque FFmpeg command strings. FFmpeg is execution, not authority.

## 6. Audible engineering/live probe

Create a reusable R0.10A probe under `tools/probes/`.

If no rights-safe local music file already exists, create a deterministic local-only test music fixture solely for Engineering Probe purposes (for example a simple rhythmic synthetic signal). It must remain gitignored and must not be represented as product-selected commercial music.

Exercise the full owned path:

`local audio fixture/Asset → rights evidence → BeatMap → CandidateMusicWindow → MusicSelectionDecision → AudioMixDecision → FFmpeg diagnostic mix`

Reuse one existing real video preview/source plus existing speech/VAD evidence where practical.

Write local-only artifacts under:

`example/probe-output/r0_10a/`

At minimum:

- `music_selection.json`;
- `beatmap.json`;
- `audio_mix_decision.json`;
- `audible_mix_preview.mp4`.

The preview should make the BGM plainly audible while preserving intelligible source/speech audio when present, so the user can verify that R0.10 has actually introduced audible soundtrack behavior.

## Named probe gates

Prove at least:

1. `LOCAL_RIGHTS_REQUIRED` — no rights evidence means no clear selection;
2. `INELIGIBLE_CANNOT_WIN`;
3. `BEATMAP_SOURCE_TIME_BOUNDED`;
4. `BEATMAP_DETERMINISTIC`;
5. `MUSIC_WINDOW_GROUNDED`;
6. `MUSIC_WINDOW_INSIDE_ASSET`;
7. `SELECTION_PRESERVES_RIGHTS_PROVENANCE`;
8. `SPEECH_DUCKING_EXPLICIT` — when speech evidence exists, gain-envelope intent is explicit and deterministic;
9. `AUDIO_MIX_NO_AUTHORITY_LEAK` — FFmpeg execution cannot mutate selection/BeatMap authority;
10. `AUDIBLE_PREVIEW_RENDERED`.

Add focused regression coverage for canonical ownership, rational times, rights fail-closed behavior, deterministic window identity and mix-envelope bounds.

## Quality / repair policy

If a bounded defect in an existing shared mechanism appears, repair the invariant, add regression coverage and continue through this same work order when practical. Do not create a new micro-phase for routine fixes.

Run focused tests, the R0.10A live probe and the complete repository Quality Gate.

If all green:

- coherent commit + push `main`;
- keep generated audio/video artifacts local and gitignored;
- classify `ENGINEERING BASELINE ADEQUATE`, `MATERIAL DEFECT` or `BLOCKED`;
- report HEAD, implemented contracts/services, rights behavior, BeatMap/window metrics, ducking/mix evidence, preview path and major-stage wall-clock time;
- stop at the R0.10A boundary. Do not begin external-provider music search or later R0.10 Product Probe work in this batch.

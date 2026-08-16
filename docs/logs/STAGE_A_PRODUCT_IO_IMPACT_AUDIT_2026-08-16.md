# Stage-A Product I/O Impact Audit — 2026-08-16

Status: NON-AUTHORITATIVE AUDIT RECORD  
Scope: code-level impact mapping for Stage-A real user input/output closure.  
Current active Work Order remains `R0.12-PREVIEW-BACKEND-BENCHMARK-001`; this audit does not authorize implementation and does not alter architecture authority.

## Why this audit exists

As Stage-A approaches structural closure, remaining work must be judged from real user boundaries rather than from isolated module completion.

Product contracts remain:

- Planning: reference/high-performing target + commercial intent → ScriptPlan + ShootingPlan.
- Editing: user local footage + editing intent → automatic editing → final MP4.
- Planning-only, Editing-only and Combined remain parallel legitimate paths; Combined reuses the same Editing Core.

## Observed baseline

Audit was performed against green `main` after mechanical governance repair:

`9bd6a4c4c599600d812c357da0cd19317395e8c2`

No production implementation was changed as part of this audit.

## Findings

### 1. Mixed source-audio semantics are too coarse — structural gap

`AudioMixDecision` currently owns one EditPlan-wide `SourceAudioPolicy` (`MUTE`, `PRESERVE`, `DUCK`). `plan_basic_mix()` preserves source audio globally when any speech range exists. `EDLBuilder` then creates source-audio segments for every selected video segment under global preserve.

This cannot safely represent a mixed folder where one selected range contains meaningful speech, another has no audio stream, and another contains unwanted wind/noise or useful action/environment sound.

The repair should remain bounded to AudioEditorial/Application → EDLBuilder semantics. It should not redesign Asset, Shot, Resolver, canonical EDL authority or Renderer editorial ownership.

Expected direction: source-audio use becomes selection/range-aware while source capability (`audio_channels`) remains technical evidence. Meaningful speech is protected unless user intent explicitly authorizes otherwise.

Likely affected areas:

- `src/video_editing_agent/application/ports/audio_editorial.py`
- `src/video_editing_agent/music/audio_editorial.py`
- `src/video_editing_agent/application/edl_builder.py`
- editing application/integration wiring
- R0.10/R0.12 audio and EDL tests

### 2. Media ingest is not MP4-only — preserve current architecture

Current ffprobe/Asset ingest is stream-based and accepts local visual media based on probe results rather than a Domain-level MP4-only rule. Video may legitimately have no audio stream.

Do not narrow Domain to MP4. Stage-A product/runtime should define a tested common-format support floor and fail with understandable unsupported-media diagnosis when the project-controlled runtime cannot decode an input.

### 3. Reference URL acquisition is a missing outer input capability

Current media source ingestion is local-file based. Existing `REFERENCE_ANALYSIS_ONLY` policy correctly prevents reference material from becoming Resolver-eligible output footage.

Recommended future boundary:

`supported reference URL → controlled acquisition/cache → local file → LocalMediaSource(REFERENCE_ANALYSIS_ONLY) → existing ingest/understanding/planning evidence`

Do not make Resolver or Domain Assets depend on remote URLs. Do not use webpage metadata alone and claim the full video was analyzed. Authentication/DRM/access failures must fail closed and request a local upload.

### 4. Reference-style evidence can reuse newer downstream evidence

The existing reference-planning service deliberately left speech structure, music/edit relationship, caption density and transition effects unavailable during the earlier R0.7B scope.

Later ASR/temporal/music/subtitle capabilities now exist. Final Planning integration should reuse available evidence from those owners rather than create a second reference-understanding subsystem.

### 5. Public/connected music discovery lacks a complete executable acquisition path — structural gap

`AudioMaterialProvider` currently exposes discovery proposals only. There is no concrete production audio/music provider family in the current provider tree and no approved acquisition operation that converts a rights-accepted candidate into a controlled local audio Asset.

Stage-A one-click auto-BGM requires an end-to-end path:

`MusicIntent → provider search → rights gate → approved acquisition → controlled local file → AssetIngest(MUSIC) → BeatMap → MusicSelectionDecision → AudioMixDecision → EDL → Renderer`

Renderer must consume local governed Assets, never a remote provider URL.

Exact provider/API/license selection must be researched from current official sources before implementation.

### 6. Accidental silent output belongs to Application/Review QC, not Renderer creativity

CAP-09 Final Technical QC already owns required audio tracks, silence anomalies, loudness/peak and A/V sync checks.

If final intent is not explicit silence and canonical output has no intentional audible lane, the workflow should block/unresolve before acceptance. Renderer remains a deterministic EDL executor and must not invent sound.

### 7. Revoice is currently a user-authorization contract issue, not an existing capability

Current providers include ASR/VAD but no production TTS/revoice provider. Stage-A must not imply automatic revoice already exists.

A future Product I/O contract should distinguish at least:

- preserve original voice;
- clean/enhance original voice where supported;
- allow revoice;
- do not use original voice.

Meaningful detected speech should be protected by default. `allow revoice` may remain an explicit unavailable capability until a real TTS/revoice path is intentionally implemented.

## Constitution / Project source-pack impact

Current audit does **not** require a Product Constitution amendment or Project source-pack replacement.

The Constitution's rule that visual asset URLs are not a material-ingest path is compatible with a narrowly scoped remote URL used only to acquire analysis-only reference media, provided the acquired Asset remains `REFERENCE_ANALYSIS_ONLY` and can never become output-eligible footage.

After Preview closes, a subordinate Stage-A Product I/O Contract should explicitly freeze this distinction plus VoiceTreatment, MusicPolicy, explicit-silence intent and media-decode failure semantics before production I/O code is changed.

If later review proves the Constitution itself must change, the engineering protocol requires an explicit `SOURCE FILE CHANGE REQUIRED` notice.

## Recommended implementation order

Do not interrupt the active Preview benchmark with these production changes.

After Preview backend ADR/closure:

1. freeze Stage-A Product I/O Contract;
2. implement mixed source-audio selection/range semantics and meaningful-speech protection; include accidental-silence QC in the same audio closure where efficient;
3. add supported Reference URL acquisition into the existing `REFERENCE_ANALYSIS_ONLY` path;
4. select and implement at least one real rights-aware public/connected music provider plus acquisition-to-local-Asset path;
5. fold available speech/rhythm/caption/transition evidence back into final Planning reference analysis where it improves the Product Probe without creating a second subsystem;
6. complete the remaining bounded R0.12/Review/runtime/user-entry work;
7. run final real Stage-A Product Probes from ordinary user inputs.

## Test matrix required before Stage-A completion

### Product I/O contract

- local reference and remote reference are distinct legal input forms;
- remote reference never becomes Resolver/output eligible;
- VoiceTreatment is explicit;
- MusicPolicy distinguishes auto public/connected, user local, and no BGM;
- explicit silence is distinguishable from accidental silence.

### Mixed source audio

Use one edit containing:

- meaningful speech;
- video with no audio stream;
- unwanted noise/environment audio;
- useful action/environment sound where available.

Prove per-selection/range source-audio decisions, exact provenance, no attempt to read a missing audio stream, protected speech by default, and deterministic EDL output.

### Reference URL

Prove a supported real URL can be acquired into controlled local reference-only media and pass through existing real understanding. Prove inaccessible/auth/DRM/unsupported URLs fail clearly and cannot be replaced by webpage-only pseudo-analysis.

### Music

Prove discovery, rights gate, actual acquisition, controlled local Asset ingest, BeatMap, music selection, EDL BGM segment and real rendered audible output. Prove rejected rights never enter execution.

### Final audio QC

- explicit silence + no audible lanes → valid;
- non-silent intent + no audible lanes → blocking issue;
- source-only → valid when intentional;
- BGM-only → valid when intentional;
- mixed source+BGM → valid when policy is satisfied;
- post-render evidence verifies expected audio stream where required.

### Final Product Probes

Planning A:
`local reference video → real analysis → ScriptPlan + ShootingPlan`

Planning B:
`supported real video link → controlled real analysis → ScriptPlan + ShootingPlan`

Editing:
`mixed local footage folder + editing intent + VoiceTreatment + MusicPolicy + output directory → real understanding → Director/Resolver → Audio/Music → canonical EDL → Renderer → Review/QC → real final MP4`

No final Product Probe may hand-author EditPlan, ResolutionDecision or EDL to bypass the product path.

## Codex routing recommendation

Do not use Codex for Preview discovery/benchmarking, Product I/O contract drafting, current provider/license research, governance docs or mechanical fixes.

Good Codex batches after boundaries are frozen:

- mixed source-audio semantics + regression/integration tests;
- Reference URL acquisition adapter after supported platform/acquisition policy is frozen;
- concrete music provider + acquisition integration after provider/license/API selection is frozen;
- final coherent ordinary-user workflow/integration work.

Accidental-silence QC may be folded into the mixed-audio batch; if the final change is tiny and deterministic, ChatGPT may write it directly instead.

Do not spend current quota on TTS/revoice provider work unless the Stage-A Product I/O Contract later makes it a real completion requirement.

## STOP boundary

If any implementation proposal starts requiring a broad rewrite of Asset/Shot, Resolver/CandidateWindow, canonical EDL authority, Renderer editorial ownership, or the accepted parallel two-core architecture, stop and re-audit blast radius before proceeding.

# Current Work Order

**ID:** `R0.12-MIXED-SOURCE-AUDIO-QC-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Mixed source-audio / VoiceTreatment / audible-lane QC  
**Mode:** BOUNDED IMPLEMENTATION  
**Accepted production-code baseline entering work:** `500c8563e3686a5aaef055ffb5301553aa999fd9`  
**Activated:** 2026-08-16  
**Codex release:** AUTHORIZED — SINGLE COMPLEX BATCH

## Why this work exists

The canonical Stage-A Product I/O Contract is accepted:

`docs/product/STAGE_A_PRODUCT_IO_CONTRACT.md`

Validation:

`docs/validation/R0.12_STAGE_A_PRODUCT_IO_CONTRACT_EVIDENCE.md`

The contract proves one P0 product defect in the current Editing audio path:

> one whole-EditPlan `SourceAudioPolicy` cannot represent a mixed footage set where different grounded selections/source ranges require different original-audio treatment.

Current code behavior confirms the defect:

- `AudioMixDecision` owns one global `source_audio_policy`;
- `plan_basic_mix()` chooses whole-plan PRESERVE when speech exists and MUTE otherwise;
- `DeterministicEDLBuilder` clones every video selection onto SOURCE_AUDIO for global PRESERVE;
- global DUCK is currently fail-closed as unsupported;
- Renderer already knows how to execute canonical audio tracks/automation and must remain execution-only.

This batch fixes that ownership/granularity gap and adds the minimum speech-protection / accidental-silence gate needed by the product contract.

## Product objective

A mixed Editing-only or Combined project must be able to express, for each grounded selected source range:

- preserve this original audio;
- duck this original audio;
- mute this original audio;
- preserve/clean/protect speech semantics separately from the raw source-audio level decision;
- reject an unintentionally silent final timeline when user/editorial intent requires audible output.

No manual EDL editing is allowed in the intended owner chain.

## Frozen architecture

### Source grounding

Resolver / `ResolvedSelection` remains authoritative for selected Shot revision and exact source range.

Audio Editorial may target grounded selections/ranges but may not invent source timestamps or select footage.

### Audio Editorial ownership

Audio Editorial owns treatment intent.

The whole-EditPlan `source_audio_policy` must no longer be the sole executable meaning for mixed source audio.

Implement a typed per-selection treatment structure whose target is a real grounded selection/source range. Low-risk exact naming/file placement is an engineering choice for Codex, but semantics are frozen below.

Minimum source treatment:

- `PRESERVE`
- `DUCK`
- `MUTE`

Minimum voice treatment:

- `PRESERVE`
- `CLEAN`
- `ALLOW_REVOICE`
- `DO_NOT_USE_ORIGINAL`

VoiceTreatment is policy/permission, not a generated replacement asset.

Poor/noisy speech alone MUST NOT authorize semantic replacement, deletion or revoice.

### EDLBuilder ownership

EDLBuilder maps approved per-selection treatment deterministically onto the SOURCE_AUDIO representation corresponding to that exact grounded video selection.

Required behavior:

- PRESERVE creates/retains source-audio segment for only the targeted selection;
- MUTE excludes or canonically mutes only that selection's source audio;
- DUCK has an exact deterministic EDL mapping rather than remaining a whole-plan unsupported state;
- treatment cannot target unknown/duplicate/unassembled selection IDs;
- treatment source range cannot escape the grounded `ResolvedSelection.selected_source_range`;
- no whole-plan fallback may silently override explicit per-selection decisions.

EDL remains the exact timeline authority.

### Renderer ownership

Renderer executes validated EDL only.

It MUST NOT:

- infer which source audio should exist;
- invent BGM/voiceover to make silence disappear;
- reinterpret VoiceTreatment;
- repair missing editorial decisions.

Use existing EDL audio automation/segment semantics where sufficient; extend them only when exact deterministic execution requires it.

### Audible-lane QC

Add a deterministic QC result/gate for intent that requires audible output.

For non-silent intent, the canonical EDL must contain at least one approved audible lane/segment sufficient for the requested result, e.g. source audio, voiceover, BGM or SFX.

Accidental all-silent/no-audible-lane output must fail closed with a typed diagnostic before final technical acceptance.

PCM peak/RMS/silent-fraction inspection remains supporting execution evidence and does not replace structural intent-aware QC.

## Compatibility / migration requirement

This batch must preserve existing persisted/constructed callers where reasonably possible.

If the global `SourceAudioPolicy` remains temporarily for compatibility:

- it must have a documented deterministic compatibility mapping;
- explicit per-selection treatment wins;
- legacy behavior must not make mixed selections impossible;
- no silent semantic migration is allowed.

Do not create a large schema migration unless durable persistence actually requires it. `AudioMixDecision` is currently an application decision DTO, not a top-level durable Domain entity; verify before adding persistence machinery.

## Likely implementation surface

Inspect and modify only what the final design actually requires, centered on:

- `src/video_editing_agent/application/ports/audio_editorial.py`
- `src/video_editing_agent/music/audio_editorial.py`
- `src/video_editing_agent/application/edl_builder.py`
- EDL audio model/validation only if existing segment/automation contracts are insufficient
- QC/review boundary required for the audible-lane check
- `src/video_editing_agent/render/edl_ffmpeg.py` only for deterministic execution support, not editorial policy

Expected regression surface includes:

- `tests/unit/test_r0_10a_music_audio.py`
- `tests/unit/test_r0_10b_audio_qc.py`
- `tests/unit/test_r0_12_edl_builder.py`
- `tests/unit/test_r0_12_edl_renderer.py`
- `tests/unit/test_r0_12_living_smoke_contract.py`
- additional narrowly named tests for mixed source audio / speech protection when clearer than overloading old files.

## Required deterministic cases

At minimum cover:

1. two resolved selections from different clips: first PRESERVE, second MUTE;
2. mixed PRESERVE / DUCK / MUTE across at least three selected ranges;
3. DUCK mapping is exact and only affects its targeted SOURCE_AUDIO selection/range;
4. treatment for unknown selection fails closed;
5. duplicate/conflicting treatment for one selection fails closed;
6. treatment cannot escape grounded selected source range;
7. required speech + VoiceTreatment.PRESERVE cannot disappear from the assembled audible path;
8. VoiceTreatment.CLEAN preserves semantic/original-speech authority;
9. ALLOW_REVOICE without an actual approved replacement does not fabricate a voice lane;
10. DO_NOT_USE_ORIGINAL permits original source speech exclusion explicitly;
11. non-silent intent + no approved audible lane = QC FAIL;
12. intentionally silent intent can remain silent without false failure;
13. existing BGM fade/duck behavior remains green;
14. existing canonical EDL validation/Renderer smoke remains green.

## Forbidden shortcuts

Do not:

- move source-time authority into Audio Editorial;
- let Renderer choose source-audio treatment;
- treat speech VAD alone as permission to revoice or delete speech;
- make ScriptPlan/ShootingPlan mandatory for Editing-only;
- add Reference URL acquisition or music-provider acquisition in this batch;
- add GUI/frontend work;
- reopen Preview backend benchmarking;
- redesign the entire EDL schema if existing segment/automation structure can express the requirement;
- bump structural progress because tests increase.

## Codex execution policy

**Codex is the primary writer for this implementation surface until it stops and reports.**

ChatGPT must not concurrently edit the same source/test files during the batch.

Codex should:

1. inspect current source/tests and exact call sites;
2. implement the smallest coherent typed change satisfying this Work Order;
3. update tests for the deterministic cases;
4. run focused tests first;
5. run repository quality gates as environment permits;
6. preserve the working tree if network/transport disconnects;
7. commit/push one coherent batch to `main` only after local gates pass under the established repository policy;
8. stop and report exact commit, files changed, tests/gates, known limitations and final `git status`.

Do not self-authorize the next Work Order or Stage-A closure.

## Required quality gates

At minimum before acceptance:

- Ruff format/check on changed Python surface;
- mypy/source gate as repository policy requires;
- focused audio/EDL/Renderer tests;
- full pytest if feasible under normal local environment;
- Import Linter / package build / ordinary quality gate as established by repository CI;
- latest pushed `main` must be re-observed by ChatGPT and repository-governance must be green.

## Exit gate

PASS only when:

- mixed selected source ranges can carry independent typed source-audio treatment;
- VoiceTreatment semantics are explicit and speech-protection rules are tested;
- EDLBuilder maps treatments deterministically without gaining Resolver authority;
- Renderer remains execution-only;
- non-silent accidental-silence QC is typed and fail-closed;
- legacy compatible callers are either preserved or migrated explicitly;
- focused + repository gates are green;
- accepted implementation commit is recorded by the control plane.

## STOP boundary

On completion, Codex stops.

ChatGPT then reobserves GitHub/CI, reviews the diff/evidence and decides acceptance.

The next planned product gap after this batch is **Reference URL acquisition**, not further audio expansion unless this implementation exposes a concrete blocker.

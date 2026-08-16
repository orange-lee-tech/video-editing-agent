# Stage-A Product I/O Contract

**Status:** ACCEPTED  
**Date:** 2026-08-16  
**Applies to:** Planning-only / Editing-only / Combined  
**Stage:** Stage A structural construction

## 1. Purpose

This contract freezes the **ordinary-user input → owned application/domain chain → durable output** meaning for Stage A.

It does not choose the desktop/frontend framework and does not replace accepted Domain or application ownership.

The product has two core user outcomes:

1. reference/high-performing/commercial intent → persisted ScriptPlan + usable ShootingPlan;
2. user-selected local footage + editing intent → automatic editing chain → canonical EDL → Renderer → real final MP4.

Planning-only, Editing-only and Combined remain equally legitimate product entries.

`Brief` is the common intent root. ScriptPlan/ShootingPlan are optional exact-revision enrichment for Editing, not an activation license.

---

## 2. Ordinary-user project boundary

### 2.1 Create/open

The product-facing surface SHALL expose one ordinary-user concept of a **project**.

Creating/opening a project resolves to the existing local `ProjectWorkspace` composition root.

The project owns at minimum:

- `project.sqlite3` durable Domain/application state;
- project-owned artifacts/caches/evidence;
- exact revision references linking Brief / ScriptPlan / ShootingPlan / Asset / Shot / EditPlan / EDL / Review evidence;
- progress/failure/retry metadata required by the product-facing surface.

The user does not need to know SQLite paths or repository internals.

### 2.2 User-owned media

Original local media remains user-owned and SHALL NOT be overwritten, moved, transcoded in place or silently replaced by the product.

Ingest creates immutable Asset identity from an already available local file using:

- exact local storage reference;
- content hash;
- provenance;
- media metadata;
- explicit usage role when the product route knows it.

Project-owned proxy/cache/derivative media may be created later but never becomes original Asset identity or final-render source authority.

### 2.3 Output destination

Editing product entry SHALL require or resolve an explicit user-visible output destination.

The existing Renderer `OutputSpec.path` remains the execution boundary. The final output path must not collide with any input media path.

Stage-A final media output is an MP4 produced from canonical EDL by the Renderer. The product-facing surface must make the resulting path discoverable without asking the user to inspect repository files.

---

## 3. Planning-only input/output contract

### 3.1 Product-facing input

Planning-only accepts:

- user goal / commercial intent;
- product/brand/commercial constraints;
- reference or high-performing target information;
- supported local reference media;
- supported Reference URL acquisition requests;
- optional authoritative facts / prohibited content / brand constraints already represented by Brief policy.

The product-facing layer translates these into the existing Brief/reference/planning application boundaries. It SHALL NOT construct ScriptPlan/ShootingPlan by bypassing their owner workflows.

### 3.2 Owner chain

Canonical Planning chain:

`product input`
`→ Brief owner commit`
`→ reference analysis/guidance where present`
`→ ScriptPlanningWorkflow`
`→ deterministic validation + semantic review where required`
`→ persisted ScriptPlan`
`→ ShootingPlanningWorkflow`
`→ deterministic validation + semantic review where required`
`→ persisted ShootingPlan`

Provider output is proposal/evidence only until the owning workflow commits it.

### 3.3 User-visible output

Planning-only is complete when the ordinary user can inspect/use:

- the exact persisted ScriptPlan revision;
- the exact persisted ShootingPlan revision;
- understandable rejection/failure/reshoot guidance where applicable.

The product-facing representation may be JSON, structured text or GUI rendering, but it must be derived from the persisted owner entities rather than a second informal copy.

Planning-only may legitimately end here without footage or final MP4.

---

## 4. Editing-only input/output contract

### 4.1 Product-facing input

Editing-only accepts:

- one or more user-selected local video/image files or a local folder resolved into files;
- lightweight Brief/editorial intent sufficient to express the editing goal;
- explicit output destination;
- audio/voice intent described in Section 8;
- optional user-provided local audio assets;
- optional rights-aware acquired music after the acquisition boundary in Section 7.

ScriptPlan and ShootingPlan are NOT required.

The product-facing surface SHALL NOT fabricate Planning artifacts merely to activate Editing.

### 4.2 Local media ingest

Every editable local visual file crosses the existing local ingest boundary:

`selected local file`
`→ LocalMediaSource`
`→ AssetIngestService`
`→ immutable Asset revision`

Editable visual footage uses an explicit local origin and `EDITABLE_VISUAL_FOOTAGE` role.

A folder is a product-facing convenience only. It expands into deterministic per-file ingest requests; the folder itself is not a Domain Asset.

### 4.3 Automatic editing owner chain

Canonical Editing-only chain:

`Brief/editorial intent + ingested local Assets`
`→ media understanding / Shot + evidence owners`
`→ Director → persisted EditPlan`
`→ Retrieval / Resolver → grounded ResolutionDecision/selection source ranges`
`→ Music / Audio / Spatial / Subtitle / Graphics decisions`
`→ EDLBuilder`
`→ canonical EDL`
`→ Renderer`
`→ Review/repair where required`
`→ final MP4`

Director may receive exact ScriptPlan/ShootingPlan refs only when genuinely supplied by a Combined project. Their absence is normal Editing-only state.

### 4.4 User-visible output

Editing-only is complete when the ordinary user can:

- observe meaningful current progress/failure;
- locate the final MP4;
- retry/recover where supported without rebuilding internal Domain objects by hand;
- retain original source media untouched.

Internal EditPlan/EDL/diagnostics remain durable project evidence even when the first Stage-A UI does not expose a full NLE timeline.

---

## 5. Combined contract

Combined is composition, not a third editing architecture.

Canonical meaning:

`Planning input → persisted ScriptPlan/ShootingPlan`
`→ user captures/selects footage`
`→ same local Asset ingest / understanding / Editing Core`
`→ same canonical EDL / Renderer / Review`
`→ final MP4`

When exact Planning revisions are available they may enrich Director/coverage/reference-style decisions. They never replace footage grounding or allow source timestamps to be fabricated.

---

## 6. Reference URL acquisition boundary

A Reference URL is a **product acquisition request**, not a Domain media reference and not output-eligible visual footage.

Required route:

`supported URL`
`→ ReferenceAcquisitionPort/adapter`
`→ rights/technical/platform preflight`
`→ controlled project-local file`
`→ normal local media probe/ingest`
`→ Asset with REFERENCE_ANALYSIS_ONLY usage role`
`→ existing reference analysis / Planning guidance`

The acquisition adapter owns transport/platform mechanics only. It cannot grant output eligibility or edit/timeline authority.

Fail closed for at least:

- unsupported platform/URL;
- login/session-required acquisition not explicitly supported;
- DRM/protected media;
- failed download/integrity validation;
- content whose resulting local file cannot be probed safely.

Failure must produce understandable user guidance rather than silently substituting public stock/generated footage.

Reference media remains analysis-only unless a separate explicit local user-owned media path creates an editable Asset under the Product Constitution.

---

## 7. Public music discovery/acquisition boundary

Existing `AudioMaterialProvider.search_music()` returns provider candidates only. An `AudioMaterialCandidate` is not an Asset and has no timeline authority.

A usable Stage-A public music path SHALL be:

`music intent/query`
`→ rights-aware provider discovery`
`→ candidate + LicenseSnapshot/eligibility evidence`
`→ explicit candidate selection policy`
`→ AudioAcquisitionPort/adapter`
`→ controlled project-local audio file`
`→ integrity/media probe`
`→ AssetIngestService`
`→ AssetUsageRole.MUSIC + PROVIDER_ACQUIRED_AUDIO origin`
`→ persisted provenance/rights linkage`
`→ existing MusicSelection / BeatMap / AudioEditorial chain`

Search/discovery alone is not product completion.

Unknown/ineligible rights, expired/unsupported commercial scope or acquisition failure MUST NOT be converted silently into output-eligible music.

Manual rights override/attestation remains an explicit user/Human Gate action when policy permits it; provider DTOs cannot self-authorize commercial use.

Public visual stock acquisition is intentionally absent from this contract.

---

## 8. Source audio and voice contract

### 8.1 Current defect to remove

The current whole-EditPlan `SourceAudioPolicy` (`PRESERVE / DUCK / MUTE`) is too coarse for a mixed folder/timeline.

Stage A requires source-audio treatment to be owned at **resolved source-selection/source-range granularity**, because one project may contain:

- speech that must remain audible;
- useful environment/sync sound;
- unwanted camera/source noise;
- clips whose original audio must not be used.

### 8.2 Ownership

Audio Editorial owns **editorial treatment intent**.

Resolver/selected source ranges provide the grounded source identity/time boundary.

EDLBuilder maps approved treatment decisions deterministically onto the corresponding SOURCE_AUDIO segments/ranges.

EDL remains exact timeline authority.

Renderer executes the resulting audio tracks/automation and does not decide whether speech should be preserved, muted, cleaned or replaced.

### 8.3 Required source treatment meaning

The next implementation batch SHALL support an explicit treatment decision for each relevant selected source range. The minimum product semantics are:

- `PRESERVE` — retain original source audio as selected;
- `DUCK` — retain but attenuate according to approved automation;
- `MUTE` — do not include original source audio for that selected range.

A default may exist only if deterministic and fail-safe; it must not collapse mixed selected ranges back into one whole-EditPlan decision.

### 8.4 VoiceTreatment

Speech-bearing selected ranges additionally need explicit voice policy:

- `PRESERVE` — original speech is authoritative/audible unless ordinary cleaning is applied;
- `CLEAN` — denoise/level/technical cleanup is allowed without changing semantic content;
- `ALLOW_REVOICE` — alternate/re-recorded/voiceover replacement may be considered when separately available and approved;
- `DO_NOT_USE_ORIGINAL` — original speech audio is intentionally excluded.

Poor recording quality alone does not authorize deletion, semantic rewriting or synthesized replacement of user speech.

`ALLOW_REVOICE` is permission, not an instruction to fabricate a replacement asset.

### 8.5 Speech protection

When a selected source range contains required speech and VoiceTreatment does not explicitly authorize excluding/replacing it, downstream decisions must preserve an audible source/voice lane across that narrative requirement.

BGM ducking around speech remains separate from whether source speech itself exists.

---

## 9. Audible-lane final QC

The product must distinguish intentionally silent output from accidental silence.

Before a render is accepted as FINAL_TECHNICAL_QC PASS, the workflow SHALL know whether the intent requires audible content.

For a **non-silent intent**, at least one approved audible lane must exist in the canonical EDL across the required output meaning, for example:

- preserved/treated source audio;
- approved voiceover;
- approved BGM;
- approved sound effect where semantically sufficient.

A render that is unintentionally silent MUST fail technical/product QC with an understandable diagnostic.

Renderer must not invent BGM, voiceover or source audio to repair this condition.

PCM peak/RMS/silent-fraction diagnostics may support QC but cannot substitute for intent/track-structure checks.

---

## 10. Progress / failure / retry contract

The first Stage-A product-facing surface may be visually plain, but it SHALL expose understandable states rather than raw internal exceptions only.

Minimum semantic states:

- project ready/open;
- input validation/acquisition;
- ingest/understanding;
- planning or editing decision generation;
- resolving/assembling canonical EDL;
- rendering;
- review/QC;
- completed;
- failed with owned diagnostic and retryability information.

These are product-facing projections. They are not new top-level Domain entities unless later architecture evidence justifies durable promotion.

Retry must reuse persisted accepted revisions where valid instead of silently regenerating authoritative state.

---

## 11. Output ownership summary

### Planning-only

User-visible durable results:

- ScriptPlan exact revision;
- ShootingPlan exact revision;
- coverage/reshoot guidance when relevant.

### Editing-only

User-visible durable result:

- final MP4 at explicit output path.

Durable project evidence includes the accepted intermediate revisions needed for reproducibility/retry.

### Combined

User-visible durable results:

- Planning artifacts above;
- final MP4 above.

No workflow requires the user to hand-author EditPlan, ResolutionDecision or EDL.

---

## 12. Frontend neutrality

This contract deliberately does not choose Qt, webview, Electron, Tauri or another desktop framework.

A future product-facing adapter may map ordinary-user controls to these application semantics, but it must not:

- own Domain decisions;
- bypass owner workflows;
- reinterpret EDL;
- make Planning mandatory for Editing-only;
- turn remote URLs into implicit editable/output-eligible Assets.

---

## 13. Immediate implementation sequence

This contract freezes the following order:

1. mixed source-audio selection/range semantics;
2. VoiceTreatment + speech-protection rules;
3. non-silent audible-lane QC;
4. Reference URL acquisition adapter into controlled local `REFERENCE_ANALYSIS_ONLY` Asset;
5. rights-aware public music discovery + acquisition into controlled local `MUSIC` Asset;
6. remaining bounded R0.12 productization, including production GStreamer Preview integration;
7. minimum Review/repair;
8. ordinary-user Windows runtime/Environment Doctor;
9. plain product-facing integration and real Product Probes.

The first implementation batch is items 1–3 because they share one audio authority boundary and require coordinated Domain/Application/EDL/QC tests.

---

## 14. Stage-A 100% invariant

Nothing in this contract changes structural progress by itself.

Stage-A remains below 100 until real ordinary-user Product Probes demonstrate:

- Planning input → persisted ScriptPlan + usable ShootingPlan;
- user-selected footage → actual automatic Editing Core → canonical EDL/Renderer/Review → real final MP4;
- Planning-only, Editing-only and Combined remain valid;
- no repository-file editing or manual Domain/EDL construction is required in normal operation.

# Current Work Order

**ID:** `R0.12-PUBLIC-MUSIC-ACQUISITION-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Rights-aware public music discovery/acquisition into governed local audio Assets  
**Mode:** PRODUCT + RIGHTS + PROVIDER GATE / CODE-LIGHT FIRST  
**Accepted production-code baseline:** `d15abf9258c0a080e37d666cd1112358723e823a`  
**Activated:** 2026-08-17  
**Codex release:** NO

## Previous Work Order result

`R0.12-REFERENCE-URL-ACQUISITION-001` — **PASS / CLOSED**.

Accepted implementation baseline:

`d15abf9258c0a080e37d666cd1112358723e823a`

Closure evidence:

`docs/validation/R0.12_REFERENCE_URL_ACQUISITION_CLOSURE.md`

Durable outcome:

- supported direct unauthenticated HTTPS reference media can be acquired into project-controlled storage;
- acquired media crosses normal ffprobe/AssetIngest/persistence boundaries;
- committed reference Asset uses `reference_acquired + reference_analysis_only`;
- reference media remains visual-Resolver ineligible;
- a focused real-acquisition owner-seam probe reached the existing `ReferenceStyleEvidenceService` without fabricating a real visual-model claim;
- universal/social/authenticated/DRM acquisition remains outside the accepted Stage-A boundary.

## Why this work exists

Core 2 is not supposed to require the user to manually curate every soundtrack before one-click editing can begin.

The accepted audio architecture already defines:

```text
rights-compatible candidate pool
→ provider metadata/tag retrieval
→ Top-K
→ BeatMap/temporal reranking
→ MusicSelectionDecision
→ deterministic EDL/audio execution
```

and CAP-06 already defines the future public-library route:

```text
provider search
→ MusicCandidate metadata
→ rights gate
→ approved acquisition
→ local file
→ AssetIngest
→ audio Asset
```

R0.10 proved music selection, BeatMap and audio editorial on real music. The missing Stage-A product boundary is therefore **safe automatic candidate discovery/acquisition with durable rights evidence**, not another music-selection architecture.

## Frozen ownership

Do not redesign the accepted audio stack.

Existing ownership remains:

```text
AudioMaterialProvider / LocalMusicSource → candidates only
Rights/license evidence                 → eligibility gate
AssetIngestService                      → authoritative local audio Asset
MusicSelectionService                   → MusicSelectionDecision
BeatAnalysisService                     → BeatMap
AudioEditorialService                   → AudioMixDecision
EDLBuilder                              → exact audio track/range/automation
Renderer                                → deterministic execution
```

Public-provider DTOs, URLs and search ranking never become timeline authority.

## Existing reusable primitives

The repository already contains:

- `MusicDiscoveryQuery`;
- `AudioMaterialCandidate`;
- `AudioMaterialProvider` discovery seam;
- `RightsEligibility` with `eligible / warning / ineligible / unknown`;
- `LicenseSnapshot` for provider/item rights evidence;
- existing local Asset ingest and provenance primitives;
- accepted R0.10 MusicSelection/BeatMap/AudioEditorial chain;
- accepted canonical EDL/Renderer audio execution.

Prefer extending these seams minimally rather than introducing a second provider or rights model.

## Objective

Freeze and validate the smallest deployable public-music boundary that can automatically discover useful candidates, reject rights-uncertain/incompatible items before expensive analysis, acquire one specifically approved candidate into project-controlled storage, preserve durable rights/provenance evidence, and hand the resulting local audio Asset to the existing music-selection chain.

The result must answer:

1. which provider/library can be accessed programmatically under current official terms;
2. whether discovery and file acquisition are both permitted;
3. which commercial/client/advertising/platform scopes are actually supported;
4. how attribution, Content-ID/claim risk, generated-audio status and restrictions are represented;
5. how provider metadata becomes a `LicenseSnapshot` or equivalent durable evidence;
6. where acquired audio bytes land and how integrity is recorded;
7. how an approved item crosses normal Asset ingest;
8. how unavailable/rights-unknown/provider-blocked cases fail or fall back;
9. whether implementation is small enough to preserve remaining Codex quota.

## Rights rule

`royalty-free` is not sufficient by itself.

Before automatic acquisition/selection, evidence must distinguish at minimum:

- commercial use;
- paid advertising/client work where relevant;
- modification/cut/loop permission;
- platform/territory limits;
- attribution requirements;
- expiry or one-project restrictions;
- standalone redistribution restrictions;
- Content-ID/platform-claim risk where exposed;
- AI-generated status when exposed;
- AI-product/provider restrictions;
- current provider terms and programmatic-access permission.

`UNKNOWN` is not `ELIGIBLE`.

If required rights evidence cannot be established, the candidate must not silently enter the normal automatic pool.

## Provider gate

Existing research in `docs/research/AUDIO_PROVIDER_CANDIDATES_2026-08-14.md` is backlog evidence only and must be revalidated from current primary sources before implementation.

### Pixabay Music

Current repository research classifies Pixabay Music as a strong rights/provenance candidate for manual/user acquisition, but not yet an approved automatic provider because the documented developer API did not expose an official music/audio search endpoint at the time of research.

Therefore:

- do not implement HTML scraping;
- do not assume browser-downloadability implies programmatic permission;
- recheck current official API/integration/terms before promotion;
- if no approved programmatic audio path exists, keep it as manual/local-user fallback rather than faking an automatic provider.

### SoundEffects+

Current repository research classifies it primarily as an SFX library and not approved for automatic integration due to automation/systematic-download and AI-product restrictions.

Do not scrape/crawl/mirror/download automatically unless current official permission materially changes and is explicitly evidenced.

### Other providers

A different provider may be selected if current primary-source evidence shows a materially cleaner combination of:

- explicit programmatic music discovery;
- explicit programmatic acquisition/download;
- commercial video/client/advertising compatibility;
- modification/cut/loop permission;
- durable item/license metadata;
- acceptable API/runtime/deployment cost;
- reasonable rate/usage limits;
- no hidden credential/browser-cookie requirement;
- sustainable maintenance surface.

Do not optimize for catalog size before rights/programmatic-access clarity.

## Required contract surface

### Discovery

Reuse or minimally extend `AudioMaterialProvider`.

Provider-neutral query should continue to carry at least:

- semantic/search text;
- commercial-use requirement;
- generated-audio preference;
- future provider-neutral filters only when justified.

Candidate metadata should preserve at least:

- provider;
- stable provider item ID;
- title/creator where available;
- source page;
- preview/full-audio distinction where relevant;
- duration/format where available;
- rights eligibility;
- rights/license snapshot identity;
- generated-audio signal only when evidenced;
- warnings such as attribution or Content-ID risk.

### Rights evidence

Prefer the existing `LicenseSnapshot` model unless a real provider proves a missing required field.

Do not duplicate rights truth into provider-specific booleans that become a second authority.

### Acquisition

Add a provider-neutral audio acquisition seam only if the existing application ports cannot express it cleanly.

Acquisition must return infrastructure/application evidence such as:

- controlled local path;
- provider + item ID;
- source page;
- acquired timestamp;
- byte size and SHA-256;
- content/media metadata;
- exact rights snapshot relied upon;
- typed diagnostics/warnings.

The provider adapter must not directly manufacture a timeline decision.

### Asset mapping

Approved acquired audio must cross the normal `AssetIngestService` boundary and become a local authoritative audio Asset with provider provenance.

Do not use remote provider URLs as EDL media identity.

## Security / lifecycle baseline

Public audio acquisition remains untrusted network input.

Preserve or define:

- project-controlled destination path;
- bounded size/time;
- atomic temporary → committed transition;
- cleanup on failure/cancellation;
- filename/path sanitization;
- integrity hash;
- no arbitrary overwrite;
- no implicit credential/browser-cookie extraction;
- provider/API rate-limit handling;
- deterministic typed failure diagnostics;
- no bulk mirroring/systematic library download.

Only the specifically approved candidate needed for the project should be acquired.

## Ordinary-user fallback

If no provider currently satisfies the automatic integration gate, Stage A must remain usable:

```text
user selects local music
→ rights attestation / known license evidence
→ normal local audio Asset
→ existing MusicSelection / BeatMap / AudioEditorial chain
```

Do not lower the rights gate merely to manufacture an automatic-provider PASS.

## Investigation sequence

ChatGPT + GitHub should first complete, without Codex:

1. audit current `AudioMaterialProvider`, rights models, Asset ingest/provenance and R0.10 music chain;
2. revalidate provider candidates from current official primary sources;
3. search for at least one provider with explicit programmatic music discovery + acquisition permission;
4. freeze discovery / rights / acquisition / diagnostics contracts;
5. freeze one Stage-A provider or explicitly record that no provider currently clears the hard gate;
6. determine the minimum production edit;
7. only then decide whether a bounded Codex release is justified.

## Resource constraint

The user reports approximately **9% Codex quota remaining**.

Treat this as a hard resource constraint.

### ChatGPT + GitHub

Primary owner for:

- provider research;
- official terms/API/license verification;
- existing-code audit;
- architecture/contract reduction;
- governance and validation;
- small deterministic edits.

### Codex

**NO ACTIVE RELEASE.**

Release only for a precise, bounded local multi-file implementation/test/repair task after provider choice and contract are frozen.

Do not spend Codex on provider browsing, docs, speculative adapters or API archaeology.

### User PowerShell

Use only when real Windows/network/provider/API/audio evidence is needed after the provider path is frozen.

## Exit gate

This Work Order is PASS only when either the automatic-provider path is truthfully closed or a documented hard-gate exclusion is recorded and the Stage-A fallback is explicitly preserved.

For an **automatic provider PASS**, require:

- current primary-source proof of programmatic discovery and acquisition permission;
- acceptable content-rights/commercial-use boundary;
- provider-neutral candidate + rights + acquisition contract;
- durable `LicenseSnapshot`/rights evidence before final selection;
- one approved candidate acquired into project-controlled local storage;
- normal audio Asset ingest/provenance/integrity proof;
- existing MusicSelection/BeatMap chain accepts the resulting Asset without provider authority leakage;
- typed failure/rate/rights diagnostics;
- focused tests for rights fail-closed and acquisition lifecycle;
- at least one real provider/API Engineering Probe where external behavior matters;
- no universal scraping, mirroring or hidden credentials;
- structural progress remains 90%.

For a **hard-gate exclusion**, require:

- credible current primary-source evidence that evaluated candidates do not permit/sustain the needed automatic path;
- no fake implementation or HTML scraping workaround;
- explicit local-user music fallback retained;
- a recorded reopening condition for future provider support.

## STOP boundary

Do not concurrently start GUI/frontend, additional Preview benchmarking, SFX-provider expansion or generated-music integration.

Do not equate `royalty-free`, browser-downloadable or technically scrapable with product authorization.

Do not release Codex until the provider and rights boundary is frozen and the remaining implementation is concrete enough to justify the quota.

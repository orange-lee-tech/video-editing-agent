# Current Work Order

**ID:** `R0.12-REFERENCE-URL-ACQUISITION-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Reference URL acquisition into governed local reference media  
**Mode:** PRODUCT + PROVIDER ACQUISITION CONTRACT / CODE-LIGHT GATE  
**Accepted production-code baseline:** `ffb5dbd7d3fc4e995f89a7a231910fa0295fcbba`  
**Activated:** 2026-08-17  
**Codex release:** NO

## Previous Work Order result

`R0.12-MIXED-SOURCE-AUDIO-QC-001` — **PASS / CLOSED**.

Accepted implementation baseline:

`ffb5dbd7d3fc4e995f89a7a231910fa0295fcbba`

Closure evidence:

`docs/validation/R0.12_MIXED_SOURCE_AUDIO_QC_CLOSURE.md`

Accepted outcome:

- source-audio treatment can differ per grounded selected source range;
- VoiceTreatment and speech-protection semantics are explicit;
- PRESERVE / DUCK / MUTE map deterministically into canonical EDL;
- non-silent intent has typed audible-lane QC;
- Renderer remains execution-only;
- no database migration was required.

## Why this work exists

The Stage-A Product I/O Contract already freezes the desired semantic route:

`supported Reference URL`
`→ acquisition adapter`
`→ controlled local file`
`→ normal media probe/ingest`
`→ REFERENCE_ANALYSIS_ONLY Asset`
`→ existing Shot / ShotAnalysis / ReferenceStyleEvidence`
`→ provider-neutral Planning guidance`

The downstream reference-analysis half already exists and is intentionally safe:

- `ReferenceStyleEvidenceService` accepts only video Assets with `REFERENCE_ANALYSIS_ONLY` usage role;
- it asserts that reference Assets are never visual-Resolver eligible;
- derived evidence is stored as a content-addressed artifact;
- planning receives abstract technique/structure guidance, not source/edit authority.

The missing product boundary is therefore acquisition, not a new reference-analysis architecture.

## Resource constraint

The user has approximately **9% Codex quota remaining**.

Treat this as a hard engineering resource constraint:

- ChatGPT + GitHub own repository audit, provider research, contract design, governance and other deterministic low-risk work;
- do not release Codex merely to read files, choose a downloader, write docs or perform small obvious plumbing;
- release Codex only if the final bounded implementation genuinely needs a multi-file local edit/test/repair loop and cannot reasonably be completed by lower-cost routes;
- preserve quota for the remaining Stage-A final corridor.

## Objective

Freeze and validate the smallest deployable Reference URL acquisition boundary that supports useful ordinary-user reference input without turning the product into a universal downloader or violating existing source/rights/authority rules.

The result must answer:

1. which URL classes Stage A supports;
2. which URL classes explicitly fail closed;
3. where remote bytes are allowed to land;
4. how integrity/provenance are recorded;
5. how the controlled local file crosses the existing ingest boundary;
6. which external runtime/library, if any, is justified;
7. how failures become understandable product diagnostics;
8. whether the implementation is small enough to avoid Codex.

## Frozen downstream ownership

### Reference analysis

Do not redesign it.

Existing chain remains:

`REFERENCE_ANALYSIS_ONLY Asset`
`→ exact Shot revisions`
`→ exact ShotAnalysis revisions`
`→ ReferenceStyleEvidence artifact`
`→ ReferenceStyleGuidance`
`→ Script/Shooting planning`

Reference evidence may influence abstract pacing/framing/motion/structure guidance but cannot:

- make the reference Asset editable footage;
- supply Resolver candidates;
- authorize copying distinctive expression;
- invent unsupported evidence dimensions.

### Asset ingest

`AssetIngestService` remains the only normal commit boundary for the acquired media file.

The acquisition adapter returns a controlled local file plus transport/provenance evidence. It does not create a Domain Asset by itself.

The committed Asset must use:

- `AssetUsageRole.REFERENCE_ANALYSIS_ONLY`;
- explicit provenance containing source page/provider information where known;
- a remote/reference origin classification that remains ineligible for visual Resolver use.

If existing `AssetOrigin` vocabulary cannot express this cleanly, locate the minimum compatible change rather than abusing `IMPORTED_LOCAL` to imply user-owned editable footage.

### Storage

Acquired remote media must land under project-controlled working storage, not arbitrary user folders and not the immutable content-addressed JSON ArtifactStore by pretending large media files are ordinary evidence blobs.

The acquisition design must define a deterministic project-owned location/lifecycle for temporary and committed reference media and protect against:

- path traversal;
- output filename injection;
- partial-download reuse;
- accidental overwrite;
- unbounded file growth;
- stale failed downloads.

Original remote URLs are provenance, not storage identity.

## Stage-A support policy

### Allowed direction

Prefer an explicit allowlist and capability probe over a "try every URL on the internet" product promise.

Stage-A may support:

- `https://` direct media URLs where the server/provider permits ordinary unauthenticated retrieval;
- specifically audited public provider/page adapters whose technical and distribution/terms boundary is acceptable for reference acquisition.

### Fail closed by default

At minimum fail closed for:

- non-HTTPS remote URL except a separately justified local/test scheme;
- unsupported platform/page type;
- login/account/session-required retrieval;
- browser-cookie extraction;
- credential scraping or username/password acquisition;
- CAPTCHA bypass;
- DRM/protected/encrypted media;
- playlist/channel/profile bulk acquisition;
- live streams in Stage A;
- unbounded or unknown-size response beyond configured limits;
- redirect/scheme/host transitions that violate the acquisition policy;
- content that cannot be successfully probed as a supported reference video after download;
- platform policy that does not permit the intended download/cache behavior.

When URL acquisition is unavailable, the ordinary-user fallback is:

> obtain/save the reference through an allowed user/platform route and select the resulting local file as reference media.

Do not silently substitute stock/generated/public visual material.

## External downloader/provider gate

Do not adopt `yt-dlp` merely because it technically supports many extractors.

Current gate must distinguish:

- **technical capability** — extraction/download works today;
- **distribution/license cost** — executable/library and transitive runtime obligations;
- **platform-policy compatibility** — whether the product is allowed to acquire/cache that provider's audiovisual content in this way;
- **credential/security surface** — cookies, browser profiles, tokens and authentication;
- **maintenance cost** — site extractors can break when sites change.

Known research signals entering this Work Order:

- yt-dlp's supported-site list explicitly warns that listed sites may break as websites change and that trying the URL is the only reliable support check;
- yt-dlp source is Unlicense, but its PyInstaller-bundled executable distributions include GPLv3+ code and the combined executable is GPLv3+;
- current yt-dlp functionality increasingly recommends optional FFmpeg, JavaScript runtime/engine and other dependencies for broad site coverage;
- browser-cookie/login paths materially expand credential/security risk and are outside the default Stage-A product boundary;
- official YouTube API developer policy prohibits downloading/caching YouTube audiovisual content without prior written approval, so technical extractor support cannot be treated as product authorization.

Therefore a universal bundled social-media downloader is **not pre-approved**.

## Required contract surface

Define typed/provider-neutral meanings for the following before implementation:

### Request

At minimum:

- source URL;
- project-controlled destination/context;
- single-item intent;
- configured maximum bytes/duration/time;
- no implicit credentials.

### Result

At minimum:

- controlled local file path;
- original/canonical source page reference where available;
- provider/platform identity where known;
- provider item ID where known;
- retrieval timestamp;
- byte/integrity evidence;
- transport/content metadata needed by ingest/provenance;
- diagnostics/warnings.

The result is infrastructure/application evidence, not a Domain Asset or timeline authority.

### Diagnostics

Typed failure families should include at least:

- unsupported URL/scheme/platform;
- authentication required;
- protected/DRM content;
- policy-disallowed acquisition;
- unavailable/not found;
- redirect rejected;
- size/time limit exceeded;
- transport failure;
- integrity failure;
- media probe/format failure;
- cleanup failure where it affects product correctness.

Do not expose raw downloader stderr as the only user-facing diagnosis.

## Security baseline

Acquisition is untrusted network input.

Before any implementation release, freeze protections for:

- SSRF/local-network targets;
- localhost / loopback / link-local / private-address resolution;
- `file://` and arbitrary scheme handling;
- redirects to disallowed destinations;
- filename/path sanitization;
- bounded response/download size and timeout;
- atomic temporary-file → committed-file transition;
- cleanup on failure/cancellation;
- content/media probe before Asset ingest;
- no automatic browser-cookie or credential access.

## Investigation sequence

ChatGPT should complete, without Codex:

1. audit current reference evidence/guidance tests and ingest/provenance/storage seams;
2. audit whether a project-owned media/cache directory already exists or must be added;
3. compare a minimal direct-HTTPS adapter with any justified provider adapter;
4. research candidate licensing/deployment/platform-policy constraints from primary sources;
5. freeze the provider-neutral request/result/diagnostic contract;
6. decide the Stage-A allowlist;
7. write validation/provider-gate evidence;
8. determine implementation size and only then decide whether Codex is worth spending.

## Expected implementation shape if approved

The likely minimal architecture is:

`ReferenceAcquisitionPort`
`→ one or more infrastructure adapters`
`→ project-owned acquisition store/path policy`
`→ AssetIngestService(... REFERENCE_ANALYSIS_ONLY ...)`
`→ existing reference analysis`

Do not add a new top-level Domain entity merely for a download job unless evidence proves durable Domain identity is required.

Do not let provider DTOs become Planning or editing authority.

## Exit gate

This Work Order is not PASS merely because one URL downloads on one machine.

PASS requires:

- provider-neutral acquisition contract frozen;
- explicit Stage-A allowlist/fail-closed policy;
- storage/lifecycle/security boundary frozen;
- provenance → local ingest → `REFERENCE_ANALYSIS_ONLY` mapping proven;
- chosen adapter/runtime has acceptable license/deployment/maintenance evidence;
- tests cover policy/security/cleanup/ingest boundary;
- at least one real supported Reference URL reaches the existing ReferenceStyleEvidence chain in a Product/Engineering Probe appropriate to the chosen adapter;
- unsupported/auth/DRM/policy-disallowed URLs fail with typed understandable diagnostics;
- no reference Asset becomes Resolver eligible;
- Codex quota is used only if genuinely necessary;
- structural progress remains 90% until ordinary-user Product Gates change.

## STOP boundary

Do not start public music acquisition, GUI/frontend, or further Preview work concurrently.

Do not promise YouTube/TikTok/other social-platform download support solely because a third-party extractor happens to work.

Do not release Codex until ChatGPT has reduced the implementation to a precise bounded surface and explicitly records why local multi-file execution is worth the remaining quota.

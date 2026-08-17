# Stage-A Public Music Acquisition Contract

**Status:** ACCEPTED FOR IMPLEMENTATION  
**Date:** 2026-08-17  
**Work Order:** `R0.12-PUBLIC-MUSIC-ACQUISITION-001`

## 1. Purpose

Freeze the smallest automatic public-music supply path that can feed the already accepted R0.10 Music/BeatMap/Audio Editorial chain without weakening rights, provenance or timeline authority.

Stage A does not need a universal music marketplace integration. It needs one governed, replaceable provider route plus the already-valid local-user-music fallback.

## 2. Frozen Stage-A provider route

```text
MusicDiscoveryQuery
→ Openverse audio discovery
   source = wikimedia_audio
   commercial + modification compatible discovery filter
→ AudioMaterialCandidate
   rights state remains UNKNOWN/WARNING
→ Wikimedia Commons current file metadata verification
→ strict Stage-A automatic license whitelist
→ durable LicenseSnapshot evidence artifact
→ approved single original-file acquisition
→ project-controlled provider audio file
→ ffprobe / integrity
→ AssetIngestService
→ AssetOrigin.PROVIDER_ACQUIRED_AUDIO
→ AssetUsageRole.MUSIC
→ existing BeatMap / MusicSelection / AudioEditorial
→ canonical EDL / Renderer
```

Openverse is discovery only.

Wikimedia current source metadata is the rights-verification source for this Stage-A adapter.

Neither provider URL nor provider candidate is timeline authority.

## 3. Discovery contract

`MusicDiscoveryQuery` remains the provider-neutral product query.

The Stage-A Openverse adapter MUST:

- search audio only;
- restrict source to `wikimedia_audio`;
- request discovery filters compatible with commercial use and modification when those filters are available;
- map results into `AudioMaterialCandidate`;
- preserve Openverse/source identity and source page;
- never promote a discovery result directly to `RightsEligibility.ELIGIBLE` merely from aggregate metadata;
- respect `generated_audio_allowed=False`; when provider metadata cannot establish generated status, preserve unknown rather than invent certainty.

The Openverse row is a candidate hint, not a license certificate.

## 4. Source-verification contract

A candidate can become automatically acquirable only after the Wikimedia source file is re-fetched through the official MediaWiki API and the current response is evaluated.

Minimum source evidence to request/preserve where available:

- stable Commons file title/page identity;
- original file URL;
- description page URL;
- source SHA-1;
- file size;
- MIME/media type;
- Artist;
- Credit;
- Attribution;
- AttributionRequired;
- LicenseShortName;
- LicenseUrl;
- UsageTerms;
- Copyrighted;
- NonFree;
- Restrictions;
- relevant deletion/missing/error state.

Source metadata containing HTML MUST be normalized for human-visible attribution while the raw API evidence remains preserved separately.

## 5. Automatic license whitelist

Automatic Stage-A acceptance is intentionally narrow.

### Eligible

After successful current-source verification:

- verified CC0;
- verified public-domain marking/source metadata sufficient for reuse;
- verified CC BY variants that permit commercial reuse and adaptation, with attribution/license/change obligations preserved.

### Not automatically eligible

Fail closed for:

- any NC license;
- any ND license;
- BY-SA in the automatic Stage-A pool;
- unknown/custom license;
- multi-license ambiguity that cannot be deterministically reduced to one accepted governing license;
- missing license identity/terms evidence for copyrighted material;
- `NonFree=true`;
- unresolved material `Restrictions`;
- missing/deleted/disputed source state that prevents confident current verification.

This is a conservative product policy, not a claim that every excluded license is legally unusable.

BY-SA may be reconsidered later behind an explicit advanced rights flow capable of carrying ShareAlike obligations into user/client delivery.

## 6. Rights-state mapping

Before source verification:

```text
Openverse candidate
→ UNKNOWN or WARNING
```

After verified Wikimedia source metadata:

```text
CC0 / accepted public domain
→ ELIGIBLE

CC BY + complete attribution/license evidence
→ WARNING or ELIGIBLE according to whether a user-visible attribution obligation must be surfaced

NC / ND / SA / NonFree / unresolved restrictions
→ INELIGIBLE

missing/ambiguous/current evidence insufficient
→ UNKNOWN
```

`UNKNOWN` and `INELIGIBLE` MUST NOT enter automatic acquisition/selection.

## 7. Durable rights evidence

`LicenseSnapshot` remains a typed rights assessment, not a legal certification and not a new top-level persistent Domain entity.

For Stage A, persistence is:

```text
normalized LicenseSnapshot payload
+ raw/current source API evidence
→ content-addressed project ArtifactStore
→ artifact ref passed through existing rights_evidence_refs
```

No SQLite migration is required for this batch.

The evidence artifact should contain at least:

- snapshot ID;
- verification timestamp;
- provider/source and item identity;
- eligibility;
- license identifier and URL;
- usage terms;
- author/artist;
- credit/attribution;
- attribution-required state;
- restrictions/nonfree state;
- source page;
- approved original file URL;
- source SHA-1;
- raw source metadata necessary to reproduce the decision.

The acquired Asset provenance carries the compact operational subset already supported by `AssetProvenance`:

- origin type;
- provider;
- provider asset ID;
- source page;
- creator;
- retrieval time;
- license information;
- attribution.

## 8. Acquisition port

Introduce a provider-neutral application acquisition seam separate from discovery.

Conceptual request:

```text
AudioAcquisitionRequest
- provider
- provider_item_id
- approved_source_url
- license_snapshot_ref
- expected_source_hash where available
- maximum_bytes / time policy from adapter configuration
```

Conceptual successful result:

```text
AcquiredAudioMaterial
- provider
- provider_item_id
- local_path
- source_page
- final_source_url
- acquired_at
- byte_size
- local_sha256
- source_hash evidence where available
- content_type
- license_snapshot_ref
```

Typed diagnostics must distinguish at least:

- candidate not verified;
- rights ineligible;
- rights unknown;
- source metadata missing/changed;
- source file missing/deleted;
- source hash mismatch;
- unsupported media type;
- redirect/host rejected;
- size/time limit exceeded;
- transport failure;
- partial cleanup failure where correctness is affected.

Raw HTTP/JSON errors are evidence, not the only product diagnosis.

## 9. Storage/lifecycle

Provider audio is a large media file and MUST NOT be stored by pretending it is an ordinary JSON evidence blob in `ArtifactStore`.

Use a project-owned working media root:

```text
<project>/provider_audio/
```

The workspace composition root should create/expose this location deterministically.

Rules:

- temporary files stay under this root;
- atomic partial → committed transition;
- committed filename/storage identity is collision-safe/content-addressed;
- failed partial files are cleaned;
- original provider filenames are not trusted as path identity;
- existing files are reused only after integrity match;
- original provider URL is provenance, not storage identity.

## 10. Network/security constraints

Reuse accepted Reference URL acquisition principles where applicable:

- HTTPS only;
- no localhost/private/link-local/multicast/special-network target;
- revalidate redirects;
- bounded bytes and wall-clock time;
- no credentials/cookies/browser profile access;
- no bulk catalog mirroring;
- one approved item at a time;
- identify the client/User-Agent according to provider policy;
- source host/file relationship must match the verified Wikimedia response;
- ffprobe must classify the committed local result as supported audio before Asset ingest.

Do not generalize this provider adapter into arbitrary-URL downloading.

## 11. Asset commit

Only after rights verification + acquisition + integrity/media probe:

```text
LocalMediaSource(
    path = committed provider audio,
    origin = PROVIDER_ACQUIRED_AUDIO,
    usage_role = MUSIC,
    provenance = verified provider/source/license summary,
)
→ AssetIngestService
→ authoritative local audio Asset
```

The Asset content hash is the local authoritative binary identity used downstream.

Remote URLs and provider IDs remain provenance only.

## 12. Downstream ownership unchanged

This batch MUST NOT redesign:

- MusicSelectionService;
- BeatMap;
- AudioEditorialService;
- mixed source-audio treatment;
- EDL audio timing;
- Renderer.

Existing `rights_evidence_refs` carry the accepted evidence artifact into music windows/selection decisions.

## 13. Ordinary-user fallback

If no automatic candidate clears source verification and the Stage-A whitelist:

> ask the user to select a local music file and provide the existing explicit rights attestation/override path when applicable.

Do not silently downgrade UNKNOWN rights, scrape another site, or substitute generated music.

## 14. Required deterministic tests

Before acceptance, cover at least:

1. Openverse result maps to candidate but remains unverified/UNKNOWN or WARNING;
2. this adapter rejects non-`wikimedia_audio` source candidates;
3. verified CC0/public-domain candidate becomes eligible;
4. verified CC BY candidate preserves attribution/license/change obligation;
5. NC fails closed;
6. ND fails closed;
7. BY-SA is excluded from automatic Stage-A pool;
8. NonFree or material Restrictions fail closed;
9. missing/ambiguous license remains UNKNOWN and cannot acquire;
10. source metadata/hash change between verification/acquisition fails closed where integrity is no longer established;
11. single approved file acquisition is bounded/atomic and records local SHA-256;
12. ffprobe-supported audio commits as PROVIDER_ACQUIRED_AUDIO + MUSIC;
13. rights evidence artifact ref flows into the existing selection request/decision path;
14. provider URLs/IDs never become EDL/timeline identity;
15. acquisition partials are removed on failure.

## 15. Codex policy

Codex remains **NO ACTIVE RELEASE** while this implementation is small enough for ChatGPT + GitHub + repository CI.

Release the remaining Codex quota only if a concrete multi-file/runtime failure appears that materially benefits from local iterative execution.

## 16. Exit gate

The public-music Work Order may close when:

- provider route above is implemented or truthfully hard-gate excluded;
- current source rights verification is deterministic and fail closed;
- rights evidence is durably reproducible;
- one real eligible provider item can be discovered, source-verified, acquired, ffprobed and ingested as a MUSIC Asset in an Engineering Probe;
- that Asset can enter the already accepted MusicSelection/BeatMap/Audio chain with rights evidence refs;
- no excluded/unknown item is silently accepted;
- quality/governance gates are green;
- structural progress remains 90% unless an ordinary-user Product Gate changes.

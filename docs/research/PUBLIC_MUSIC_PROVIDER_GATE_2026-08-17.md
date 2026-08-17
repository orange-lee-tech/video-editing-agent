# Public Music Provider Gate — 2026-08-17

**Status:** ACTIVE PROVIDER-GATE EVIDENCE  
**Work Order:** `R0.12-PUBLIC-MUSIC-ACQUISITION-001`  
**Scope:** Stage-A automatic public music discovery/acquisition  
**Authority:** current primary-source research + repository architecture; not legal advice

## 1. Product requirement

The product needs a public-audio path that does not lower the accepted rights or timeline-authority gates:

```text
provider-neutral discovery
→ candidate metadata
→ rights/license verification
→ approved single-item acquisition
→ project-controlled local audio
→ AssetIngestService
→ MUSIC Asset + durable rights/provenance
→ existing BeatMap / MusicSelection / AudioEditorial
→ canonical EDL / Renderer
```

Remote URLs/provider DTOs remain proposal/evidence only. They never become EDL media identity or timeline authority.

## 2. Current provider-gate result

### Pixabay Music — NOT AN AUTOMATIC STAGE-A PROVIDER

Current official Pixabay API documentation exposes image and video search/retrieval, not an official music/audio search endpoint.

Therefore:

- Pixabay remains potentially useful for manual/user acquisition under its Content License;
- do not HTML-scrape its music pages;
- do not claim browser-downloadability equals programmatic permission;
- automatic provider promotion requires a future official audio API/integration or explicit provider permission.

Primary source:

- `https://pixabay.com/api/docs/`

### Jamendo API — TECHNICALLY STRONG, COMMERCIAL API GATE NOT CLEARED

Jamendo API v3 provides:

- track search/discovery;
- tags/music metadata;
- Creative Commons license URL metadata;
- `ccnc`, `ccnd`, `ccsa` license filters;
- `audiodownload_allowed` per track;
- an official `/v3.0/tracks/file` download endpoint that redirects to the requested audio file when download is allowed.

However, Jamendo's current published API Terms of Use state that the API may be used freely for non-commercial uses, while commercial use requires contacting Jamendo's sales/licensing team for a quote/permission. The terms also restrict applications designed specifically to cache content/offline access beyond reasonably necessary caching.

The product is intended for commercial/client video use, so ordinary public Jamendo API access is **not sufficient authority for automatic Stage-A integration**.

Classification:

> `BLOCKED_PENDING_COMMERCIAL_API_AGREEMENT`

Reopening condition:

- written/provider-account authorization covering this product's commercial API use and selected-item acquisition; and
- license gate still enforced per track.

Primary sources:

- `https://developer.jamendo.com/v3.0/tracks`
- `https://developer.jamendo.com/v3.0/tracks/file`
- `https://developer.jamendo.com/v3.0/authentication`
- `https://devportal.jamendo.com/api_terms_of_use`

### Openverse API — APPROVED FOR DISCOVERY SIGNAL, NOT RIGHTS AUTHORITY

Openverse provides an official programmatic audio search API.

Current useful capabilities include:

- audio search/detail endpoints;
- `license` and `license_type` filters including `commercial` and `modification`;
- provider/source filtering;
- audio sources including `freesound`, `jamendo`, and `wikimedia_audio`;
- title/creator/tags/category/length and other discovery metadata;
- source landing URL, media URL, creator, license, license version/URL, attribution and technical metadata.

Openverse Terms explicitly require respecting the terms of the underlying hosting platform and content. Openverse also explicitly states that it does **not verify licensing status** and cannot make claims about license-information accuracy.

Therefore Openverse may rank/discover candidates, but:

```text
Openverse license metadata ≠ final LicenseSnapshot authority
```

Classification:

> `APPROVED_DISCOVERY_ONLY`

Primary sources:

- `https://api.openverse.org/`
- `https://docs.openverse.org/terms_of_service.html`
- `https://docs.openverse.org/api/reference/made_with_ov.html`

### Wikimedia Commons — STRONG SOURCE-VERIFICATION + ACQUISITION CANDIDATE

Wikimedia/MediaWiki exposes official programmatic file APIs.

`prop=imageinfo` can return:

- canonical/original file URL;
- description page URL;
- file size;
- SHA-1;
- MIME/media type;
- extended metadata.

CommonsMetadata extended metadata can return:

- `Artist`;
- `Credit`;
- `Permission`;
- `LicenseShortName`;
- `LicenseUrl`;
- `UsageTerms`;
- `Copyrighted`;
- `Attribution`;
- `AttributionRequired`;
- `NonFree`;
- `Restrictions`;
- deletion-state evidence.

The API access policy permits API reuse subject to Terms of Use, content licensing and proper client identification/User-Agent. Content/file licenses remain per-item and must be evaluated individually.

This makes Wikimedia Commons a materially stronger **rights re-verification + source acquisition authority** than relying on an Openverse aggregate row alone.

Classification:

> `CANDIDATE_VERIFICATION_AND_ACQUISITION_SOURCE`

Primary sources:

- `https://www.mediawiki.org/wiki/API:Imageinfo/en`
- `https://www.mediawiki.org/wiki/Extension:CommonsMetadata/en`
- `https://www.mediawiki.org/wiki/Wikimedia_APIs/Access_policy`

## 3. Stage-A candidate architecture

Preferred route for the next implementation reduction:

```text
MusicDiscoveryQuery
→ Openverse audio search
   source = wikimedia_audio
   license_type includes commercial + modification
→ AudioMaterialCandidate
   rights_eligibility = UNKNOWN/WARNING until source verification
→ Wikimedia Commons file-page verification
→ strict Stage-A license whitelist
→ LicenseSnapshot
→ approved original file URL
→ bounded single-item acquisition
→ project-controlled audio file
→ SHA-256 + ffprobe
→ AssetIngestService
→ AssetOrigin.PROVIDER_ACQUIRED_AUDIO
→ AssetUsageRole.MUSIC
→ existing MusicSelection / BeatMap / AudioEditorial
```

Openverse is discovery-only. Wikimedia current source metadata is the rights-verification source for accepted Wikimedia candidates.

## 4. Initial Stage-A license whitelist

The product is commercial/client-video oriented and expects music synchronization, trimming and possibly looping.

Creative Commons explicitly treats synchronization of music with moving images as an adaptation.

### Automatically eligible after verified source metadata

Prefer the narrowest low-obligation set:

- public-domain marking where source metadata and current page support it;
- CC0;
- CC BY where the exact license permits commercial use and adaptation, with required attribution preserved into project output/evidence.

### Not automatically eligible in Stage A

Fail closed by default for:

- any `NC` license — commercial use conflict;
- any `ND` license — synchronization/adaptation conflict;
- `BY-SA` — commercial/adaptation is possible, but ShareAlike obligations can propagate to the adaptation and are not appropriate as an automatic default for arbitrary client output;
- multi-license metadata where CommonsMetadata itself warns license fields may be unreliable;
- unclear/custom licenses;
- missing license URL/terms evidence;
- `NonFree=true`;
- material restrictions that the system cannot safely adjudicate;
- deletion/dispute state where reuse confidence is not sufficient.

BY-SA could be revisited later as an explicit advanced/user-approved route with suitable output-license handling; it is intentionally excluded from the automatic Stage-A pool.

Creative Commons primary sources:

- `https://creativecommons.org/licenses/by/4.0/`
- `https://creativecommons.org/licenses/by-sa/4.0/`
- `https://creativecommons.org/licenses/by-nc/4.0/`
- relevant NoDerivatives legal code, which explicitly treats music synchronization with moving image as an adaptation.

## 5. Rights-state mapping

Openverse discovery result:

```text
candidate discovered
→ RightsEligibility.UNKNOWN or WARNING
```

Only source verification can promote it.

Verified source gate:

```text
CC0 / verified public domain
→ ELIGIBLE

CC BY + complete attribution/license metadata
→ ELIGIBLE or WARNING when a user-visible attribution obligation must be carried

NC / ND / SA / unclear / multi-license ambiguity / NonFree / unresolved restrictions
→ INELIGIBLE or UNKNOWN
```

`UNKNOWN` never enters final automatic acquisition/selection.

## 6. Durable LicenseSnapshot minimum

For a Wikimedia-backed accepted candidate preserve at least:

- snapshot ID;
- provider/source = Wikimedia Commons;
- stable file-page/title/item identity;
- capture timestamp;
- eligibility;
- `LicenseShortName`;
- `LicenseUrl`;
- `UsageTerms`;
- author/artist;
- credit/attribution text;
- attribution-required state;
- restrictions;
- source/description page;
- original file URL used for acquisition;
- source SHA-1 where returned;
- evidence artifact containing the relevant API response/current source metadata;
- local file SHA-256 after acquisition.

Openverse discovery ID/query may also be preserved as provenance, but is not the license authority.

## 7. Acquisition constraints

Reuse the same security principles already accepted for Reference URL acquisition where applicable:

- HTTPS only;
- expected Wikimedia host/source binding;
- no arbitrary redirect to private/local network;
- bounded bytes/time;
- atomic partial → committed file;
- no bulk mirroring;
- one approved candidate only;
- explicit User-Agent/API identification as required by Wikimedia policy;
- ffprobe before Asset ingest;
- content-addressed or collision-safe project-controlled storage;
- no remote URL as EDL identity.

## 8. Product value / catalog tradeoff

This route prioritizes rights clarity over catalog polish.

Openverse + Wikimedia Commons may provide a less commercially curated soundtrack catalog than Pixabay/Jamendo Licensing, but it has a much cleaner zero-contract Stage-A automation boundary:

- official programmatic search;
- official source metadata API;
- official source file URL;
- independently re-verifiable free-license evidence;
- no HTML scraping;
- no browser-cookie/login automation;
- no provider-specific commercial API contract discovered so far.

If later a provider such as Pixabay exposes an official audio API, or Jamendo grants a commercial API agreement, those providers can plug into the same discovery/rights/acquisition ports without changing the accepted R0.10 downstream architecture.

## 9. Immediate next engineering reduction

Before writing code:

1. inspect whether `LicenseSnapshot` needs minimal fields for attribution/restrictions/source evidence or whether those can be stored as artifacts and existing fields;
2. freeze a provider-neutral `AudioAcquisitionPort` result/diagnostic shape;
3. decide project-owned `audio_media`/`provider_audio` location;
4. write focused tests for:
   - Openverse candidate remains unverified initially;
   - source must be `wikimedia_audio` for this adapter;
   - current Wikimedia verification promotes only allowlisted licenses;
   - NC/ND/SA/multi-license/nonfree/restricted/unknown fail closed;
   - attribution requirement is preserved;
   - single approved file acquisition → SHA-256 → ffprobe → MUSIC Asset;
   - no provider URL becomes timeline authority;
5. only after the edit surface is known decide whether any Codex release is justified.

## 10. Current recommendation

Proceed with **Openverse discovery + Wikimedia Commons verification/acquisition** as the Stage-A automatic public-music candidate.

Do not release Codex yet.

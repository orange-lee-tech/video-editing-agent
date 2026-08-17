# Reference URL Acquisition Contract

**Status:** ACCEPTED FOR R0.12 IMPLEMENTATION  
**Date:** 2026-08-17  
**Stage:** Stage A  
**Work Order:** `R0.12-REFERENCE-URL-ACQUISITION-001`

## 1. Purpose

This contract defines the bounded route by which a supported remote reference URL may become analysis-only local media for the existing Planning reference pipeline.

It does **not** define a general Internet downloader and does not change visual-source authority.

Canonical route:

`user Reference URL`
`→ acquisition policy/preflight`
`→ ReferenceAcquisitionPort`
`→ controlled project-local media file`
`→ existing local media probe/Asset ingest`
`→ AssetOrigin.REFERENCE_ACQUIRED + REFERENCE_ANALYSIS_ONLY`
`→ existing Shot / ShotAnalysis`
`→ ReferenceStyleEvidence`
`→ ReferenceStyleGuidance`
`→ Script/Shooting Planning`

The acquired reference can influence abstract planning technique only. It can never become editable visual footage or a Resolver candidate.

---

## 2. Stage-A supported URL class

The first Stage-A implementation supports one deliberately narrow class:

> **single-item, unauthenticated, public HTTPS URL that directly resolves to retrievable video bytes and whose acquisition is permitted for the intended use.**

The baseline adapter is therefore `direct_https`, not a universal page/site extractor.

A URL that returns an HTML social-platform page is not a direct media URL and is not supported by this baseline.

Future provider/page adapters may be added behind the same port only after independent technical, platform-policy, license, security and deployment gates.

---

## 3. Explicitly unsupported in the Stage-A baseline

Fail closed for:

- `http://` and every non-HTTPS remote scheme;
- `file://`, `ftp://`, `data:`, custom schemes and local filesystem indirection;
- URLs containing username/password credentials;
- localhost, loopback, private, link-local, multicast, reserved or otherwise non-public network destinations;
- redirects to a disallowed scheme/address/host condition;
- login/account/session-required retrieval;
- browser-cookie extraction;
- username/password/token scraping from the user's browser/profile;
- CAPTCHA bypass;
- DRM/protected/encrypted media acquisition;
- playlist/channel/profile/bulk acquisition;
- live streams;
- arbitrary page extraction through a generic HTML/site extractor;
- platform/provider routes whose terms/policy do not permit the intended download/cache behavior;
- media exceeding configured size/time limits;
- downloads that fail final media probe.

The fallback product guidance is:

> Obtain/save the reference through an allowed user/platform route, then select that local file as reference media.

No stock/generated visual substitute is allowed.

---

## 4. Why yt-dlp is not the Stage-A default adapter

`yt-dlp` remains a useful technical reference and possible future provider adapter, but it is **not bundled or adopted as the Stage-A universal Reference URL implementation**.

Reasons:

1. site/extractor support changes when websites change, so technical support is not a stable product contract;
2. broad current coverage can require FFmpeg, JavaScript runtime/engine and additional networking/impersonation dependencies;
3. source license and prebuilt executable distribution license are not equivalent — current PyInstaller-bundled executables contain GPLv3+ code and the combined executable is GPLv3+;
4. cookie/login support materially expands credential and browser-profile security exposure;
5. technical ability to retrieve a provider does not establish platform-policy permission to download/cache it;
6. some major platform developer policies explicitly prohibit download/cache of audiovisual content without prior approval.

A future site adapter must therefore be justified per provider. "yt-dlp supports it" is not sufficient evidence.

---

## 5. Application port

The provider-neutral seam SHALL represent these meanings. Exact code naming may vary if repository conventions justify it, but semantics are frozen.

### 5.1 Request

`ReferenceAcquisitionRequest`

Required meaning:

- one source URL;
- one single-item acquisition intent;
- no implicit credentials;
- configured acquisition limits supplied by adapter/composition policy rather than untrusted URL metadata.

The request does not carry Asset/Shot/Planning authority.

### 5.2 Result

Successful `ReferenceAcquisitionResult` / acquired-media evidence must contain at minimum:

- controlled local media path;
- original source URL;
- final URL after accepted redirects;
- adapter/provider identity (`direct_https` for baseline);
- provider item ID when an audited provider can supply one, otherwise `None`;
- retrieval timestamp;
- byte size;
- SHA-256 content hash calculated while/after acquiring;
- response content type when available;
- warnings/transport metadata required for diagnosis/provenance.

It is **not an Asset**.

### 5.3 Diagnostics

Failures must be typed. Baseline codes must distinguish at least:

- `INVALID_URL`
- `UNSUPPORTED_SCHEME`
- `CREDENTIALS_NOT_ALLOWED`
- `NETWORK_TARGET_REJECTED`
- `REDIRECT_REJECTED`
- `AUTHENTICATION_REQUIRED`
- `PROTECTED_CONTENT`
- `POLICY_DISALLOWED`
- `UNSUPPORTED_RESOURCE`
- `NOT_FOUND`
- `SIZE_LIMIT_EXCEEDED`
- `TIME_LIMIT_EXCEEDED`
- `TRANSPORT_FAILED`
- `INTEGRITY_FAILED`
- `MEDIA_PROBE_FAILED`
- `CLEANUP_FAILED`

Raw HTTP/downloader stderr may be retained as diagnostics evidence, but is never the only product-facing message.

---

## 6. Network security contract

Reference URLs are untrusted network input.

### 6.1 HTTPS only

Baseline transport permits `https` only.

The URL must not contain embedded credentials.

### 6.2 Public-address requirement

Before connecting, resolve the target hostname and require the selected destination address to be public/global according to the platform's IP-address classification.

Reject at minimum:

- loopback;
- RFC1918/private;
- link-local;
- multicast;
- unspecified;
- reserved/documentation/non-global destinations.

### 6.3 DNS rebinding / TOCTOU

A preflight DNS check followed by an unrelated hostname connection is insufficient for the final implementation.

The baseline direct-HTTPS adapter must connect to the **validated resolved public IP** while preserving the original hostname for TLS SNI/certificate verification and HTTP `Host` semantics, or use an equivalently strong transport mechanism.

This prevents a second resolver lookup from silently changing the connection target after policy validation.

### 6.4 Redirects

Redirect handling is manual/policy-aware, not blindly delegated.

Every redirect target repeats:

- URL parsing;
- HTTPS-only rule;
- embedded-credential rejection;
- public-address resolution/pinning;
- acquisition-policy check.

Apply a small finite redirect limit.

### 6.5 No ambient credentials

The baseline adapter must not read:

- browser cookies;
- `.netrc`;
- OS credential stores;
- browser profiles;
- environment-provided auth tokens intended for unrelated services.

Do not inherit proxy/auth behavior that silently expands the trusted boundary unless explicitly audited later.

---

## 7. Resource limits

The adapter must enforce bounded acquisition independent of remote metadata.

Configurable policy must include:

- maximum bytes;
- connection/read timeout;
- maximum total elapsed acquisition time;
- maximum redirects.

If `Content-Length` already exceeds the byte limit, fail before consuming the body.

When length is absent or false, enforce the same limit while streaming.

Do not infer "safe size" from filename or extension.

---

## 8. Controlled project-local storage

Remote reference video is project working media, not a derived JSON artifact.

Do not store the full acquired media payload inside `LocalArtifactStore` merely to reuse its API.

The project SHALL expose a dedicated controlled root such as:

`<project>/reference_media/`

Recommended lifecycle:

`reference_media/.partial/<opaque-id>.part`
`→ bounded stream + SHA-256`
`→ fsync/close`
`→ atomic move`
`→ reference_media/sha256/<prefix>/<full-digest>.media`

Properties:

- caller never controls the destination filename;
- remote `Content-Disposition` is evidence only and never used as a path;
- URL path basename is never trusted as a path;
- identical bytes deduplicate by content hash;
- failed/partial downloads never appear as committed reference media;
- failure cleanup removes partial files;
- committed reference media is project-owned working data and may be lifecycle-managed separately from immutable user originals.

`.media`/opaque extension is acceptable because final media validity is established by the existing probe, not filename guessing.

---

## 9. Asset origin and provenance

Current Asset vocabulary distinguishes origin from usage eligibility. Remote-acquired reference media needs an origin that does not pretend the bytes were user-imported local footage.

The implementation SHOULD add:

`AssetOrigin.REFERENCE_ACQUIRED = "reference_acquired"`

and classify it conservatively as remote/restricted for visual output eligibility.

The subsequent local ingest must explicitly use:

- `origin = reference_acquired`;
- `usage_role = REFERENCE_ANALYSIS_ONLY`;
- provenance with source page/final URL/provider/retrieval time as available.

The exact local file path is storage, not proof of local/user-owned origin.

`is_visual_resolver_eligible(...)` must remain `False` for the committed reference Asset.

---

## 10. Ingest / probe handoff

Acquisition success does not automatically mean valid reference media.

Required handoff:

`ReferenceAcquisitionResult.local_path`
`→ existing MediaProbe`
`→ AssetIngestService`
`→ exact Asset revision`

If media probe or ingest fails:

- do not create a valid reference Asset;
- return typed acquisition/import diagnostic;
- apply the agreed committed-media cleanup/retention policy;
- never reclassify the download as arbitrary binary evidence and continue Planning.

Stage-A reference analysis currently requires a **video** Asset. Acquired audio/image/HTML/binary content must not enter that service as if supported.

---

## 11. Downstream reference-analysis invariants

Existing R0.7B+ reference behavior remains authoritative:

- ReferenceStyleEvidence accepts only `REFERENCE_ANALYSIS_ONLY` video Assets;
- exact Shot and ShotAnalysis revisions are required;
- evidence describes abstract technique/structure;
- unavailable dimensions remain explicitly unavailable;
- provider-neutral Planning guidance carries no source window/editability fields;
- the reference Asset never becomes a visual Resolver candidate.

Reference URL acquisition adds transport only. It does not increase creative-copy authority.

---

## 12. Stage-A product UX meaning

The ordinary-user surface may present one "Reference URL" input, but must distinguish outcomes:

### Supported

"Reference acquired and ready for analysis."

### Unsupported page/platform

"This link cannot be acquired directly. Save/export the reference through an allowed route and choose the local file instead."

### Login/protected

"This reference requires account/protected access and is not supported by automatic acquisition."

### Network-policy rejected

"This URL points to a local/private network destination and cannot be fetched."

### Oversize/timeout

Explain the configured limit and offer local-file input.

Do not suggest cookie extraction, DRM bypass or credential scraping as a routine fallback.

---

## 13. Provider expansion rule

A future provider/page adapter must document all of:

- exact supported provider/url type;
- official policy/terms basis for the acquisition behavior;
- authentication requirement, if any;
- runtime/dependency/license closure;
- update/breakage strategy;
- typed provider-specific failure mapping;
- proof that output remains `REFERENCE_ANALYSIS_ONLY` and Resolver-ineligible.

Provider adapters remain replaceable infrastructure. They cannot modify Product Constitution or reference evidence semantics.

---

## 14. Minimum test surface

Before implementation acceptance, cover at least:

1. valid public HTTPS direct media → controlled committed file;
2. SHA-256/byte-size result matches file;
3. same bytes deduplicate safely;
4. non-HTTPS rejected;
5. URL credentials rejected;
6. localhost/loopback/private/link-local/other non-global IP rejected;
7. redirect to private/non-HTTPS target rejected;
8. redirect loop/limit rejected;
9. `Content-Length` oversize rejected before body;
10. streaming oversize rejected and partial cleaned;
11. timeout/transport failure cleans partial;
12. remote filename/path traversal cannot influence local path;
13. successful bytes that fail MediaProbe do not create reference Asset;
14. successful video ingest uses `REFERENCE_ACQUIRED + REFERENCE_ANALYSIS_ONLY`;
15. committed reference Asset is not visual-Resolver eligible;
16. existing ReferenceStyleEvidence and Planning guidance tests remain green;
17. one real allowed HTTPS direct-media probe reaches the existing reference-analysis chain.

---

## 15. Codex usage decision

No Codex release is authorized by this contract alone.

The baseline implementation is intentionally designed around:

- Python standard library;
- one application port/result/diagnostic surface;
- one bounded direct-HTTPS infrastructure adapter;
- one project-owned reference-media store/path policy;
- one small Asset origin extension;
- focused tests plus one real probe.

ChatGPT should first determine whether this can be implemented and verified through normal GitHub/CI + a small Windows probe without spending the remaining Codex quota.

Codex becomes justified only if actual implementation/debugging demonstrates a nontrivial local multi-file problem that GitHub/CI cannot resolve efficiently.

---

## 16. Stage-A effect

This contract does not change structural progress.

Official progress remains **90%** until actual ordinary-user Planning and Editing Product Gates close.

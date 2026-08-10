# CAP-02 — Asset, Rights, Provenance and Media Time

**Status:** CANDIDATE CAPABILITY SPEC  
**Architecture:** `ARCHITECTURE_CONTRACT_V0.2.md`  
**Scope:** Media ingest, immutable identity, usage role, rights evidence, canonical time and derivative-media mapping

---

## 1. Purpose

This capability establishes trustworthy media identity before any AI/editorial work occurs.

Every later statement such as:

> use the product shot from 00:07.42 to 00:09.10

must ultimately resolve to one immutable Asset, one authoritative source-time range and one auditable usage/right context.

---

## 2. Ownership

```text
AssetIngestService      → Asset identity
RightsProvenanceService → rights/attestation/license records
ArtifactStore           → derived files
MediaProbe               → technical metadata proposal
DerivativeMediaService  → edit-friendly/proxy mappings
```

Storage persists; it does not own semantics.

---

## 3. Asset ingest

Local visual input path:

```text
user local file
→ probe
→ hash
→ classify media
→ assign usage role
→ record user rights attestation
→ Asset
```

Remote/provider-acquired **audio** path:

```text
provider candidate
→ rights eligibility
→ approved fetch/acquisition
→ hash/probe
→ Asset(kind=audio)
```

Remote visual provider acquisition is not an active product path.

---

## 4. Immutable identity

Asset identity is anchored by ingested bytes/content hash and stable project identity.

If source bytes change:

> create a new Asset.

Do not silently update one Asset ID to point at another file revision.

Storage relocation does not create a new Asset if verified bytes remain identical.

---

## 5. Origin vs usage role

These are independent.

### Origin answers

> Where did this media come from?

Examples:

```text
captured_local
imported_local
provider_acquired_audio
```

### Usage role answers

> What may this project use it for?

Examples:

```text
editable_visual_footage
reference_analysis_only
music
voiceover
sound_effect
logo_graphic
```

One local file may be analysis-only even though it is locally supplied.

---

## 6. Reference video rule

Default:

```text
reference_video
→ usage_role = reference_analysis_only
```

Resolver must reject it as source footage.

Explicit user action may create/revise a usage authorization that allows editable use, with appropriate rights attestation.

The change must be auditable.

---

## 7. RightsAttestation

For user-supplied media, record the user’s declaration that they have necessary rights/authorization.

Possible record concepts:

```text
attestation_id
asset_ref
actor/user
purpose/scope
created_at
statement_version
notes
```

The system does not certify legal correctness.

---

## 8. LicenseSnapshot

For provider/library media, preserve evidence relied upon at acquisition/selection time.

Potential concepts:

```text
provider
provider_item_id
license/product identifier
terms reference
terms/evidence snapshot hash
commercial use
advertising use
platform scope
territory
expiry/perpetual state
project/video binding
attribution requirement/text
modification/cut/loop permissions
certificate/invoice/proof refs
retrieved/acquired time
```

Missing fields stay unknown.

A future provider changing its terms must not retroactively erase the project’s historical evidence.

---

## 9. Manual license override

If software cannot verify a right that the user actually possesses:

```text
warning/unknown
→ explicit user override/attestation
→ continue with audit record
```

Never change `unknown` into `verified` merely because the user continued.

---

## 10. Eligibility integration

Rights/usage role are hard constraints.

Examples:

```text
reference_analysis_only visual
→ Resolver INELIGIBLE

CC-BY-NC audio in commercial ad
→ Music selection INELIGIBLE

unknown commercial scope + user explicit override
→ eligible_with_warning
```

The right owner/capability returns structured evidence; Resolver/MusicSelector enforces the current project policy.

---

## 11. Canonical MediaTime

Authoritative time uses rational semantics:

```text
MediaTime(value, scale)
seconds = value / scale
```

Core objects must not depend on float equality.

Typical ranges use:

```text
MediaTimeRange(start, duration)
```

Human UI can display decimals derived from this representation.

---

## 12. VFR handling

VFR media is represented by actual timestamps, not an invented constant frame index.

Media probe should preserve where available:

- stream time base;
- duration;
- nominal/average frame rates as metadata;
- frame PTS information only when required by a precise operation.

Do not make `frame_number / fps` the universal source-time formula.

---

## 13. Edit-friendly derivatives

Some source media may be difficult to seek/edit reliably.

Infrastructure may create:

```text
Original Asset
→ Edit-Friendly Artifact
```

for example a stable mezzanine/CFR derivative.

This does not replace Asset identity.

A derivative record must preserve generation provenance and a deterministic mapping to authoritative source time.

---

## 14. Proxy

Proxy exists for interactive performance only.

```text
Original/Edit-Friendly
→ Proxy Artifact
```

Final render uses the authoritative/high-quality source chain.

Proxy frame numbers/timestamps never become Domain source authority.

---

## 15. Storage states

Distinguish:

### Authoritative/durable

- Asset identity/metadata;
- rights records;
- exact source refs;
- expensive/revisioned derived evidence.

### Rebuildable

- proxy;
- thumbnails;
- waveform cache;
- temporary extracted frames;
- preview chunks;
- vector index files.

A generic cache cleanup action may remove only the latter by default.

---

## 16. Missing-file behavior

If local source storage disappears:

- Asset identity/history remains;
- object becomes unavailable/offline, not deleted silently;
- EDL referencing it becomes non-renderable until relinked;
- relinking verifies hash before restoring authoritative availability.

If bytes differ, offer explicit replacement/new Asset workflow rather than pretending identity is unchanged.

---

## 17. Provenance chain

Target traceability:

```text
Rendered timeline range
→ EDLSegment
→ ResolvedSelection
→ Shot/source range
→ Asset
→ local/provider source + content hash
→ rights/attestation/license evidence
```

This supports debugging, commercial audit and reproducibility.

---

## 18. Security

Do not place secrets in provenance payloads.

Provider access tokens/API keys stay in secret storage/config infrastructure.

Diagnostic/exported reports should reference provider identity/status without exposing credentials.

---

## 19. Product benchmarks / probes

Engineering probes:

- same bytes produce stable hash identity;
- relink validates hash;
- VFR source windows round-trip through derivatives;
- proxy→original mapping stays within tolerance;
- reference role is rejected by Resolver;
- rights snapshot survives provider metadata changes;
- cache cleanup preserves durable evidence.

Product probes:

- real phone footage seek/cut correctness;
- no visible frame drift between proxy preview and final render;
- ordinary-user rights warnings understandable enough to act on.

---

## 20. Not frozen here

- exact ID format;
- hash algorithm beyond cryptographic/stable requirements;
- whether MediaTime utility is custom or backed by OTIO/another library;
- edit-friendly codec/profile;
- proxy format/resolution;
- exact rights enum/schema per provider;
- legal interpretation of a provider license.

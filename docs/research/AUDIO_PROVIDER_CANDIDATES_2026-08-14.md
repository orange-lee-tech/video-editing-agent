# Audio Provider Candidates — 2026-08-14

**Status:** INFORMATIVE PROVIDER BACKLOG  
**Scope:** future automatic rights-aware music/SFX discovery and acquisition  
**Authority:** research/backlog only; does not reopen closed R0.10 and is not legal advice

## Product requirement preserved

Future product behavior should be able to search for suitable audio material, evaluate rights/provenance before expensive analysis, acquire only the selected candidate through an approved provider path, ingest it as a local audio Asset, and preserve durable evidence of the rights basis used for that project.

This extends the already accepted CAP-06 acquisition chain:

```text
provider search
→ MusicCandidate / SFX candidate metadata
→ rights gate
→ approved acquisition
→ local file
→ AssetIngest
→ BeatMap / MusicSelection / AudioEditorial
```

A public web page being downloadable in a browser is not by itself approval for automated scraping or bulk acquisition.

## Provider candidate: Pixabay Music

User candidate:

`https://pixabay.com/zh/music/`

Observed 2026-08-14 posture from current official Pixabay documentation:

- Pixabay describes its audio as royalty-free Content under the Pixabay Content License;
- commercial and non-commercial use is generally allowed subject to prohibited uses and third-party-rights caveats;
- attribution is not required, though appreciated;
- commercial video use is explicitly described as allowed when the music is embedded in a larger creative work rather than redistributed standalone;
- some tracks may be registered with YouTube Content ID, so a lawful use may still receive an automated claim;
- Pixabay recommends retaining the track URL, download records and license evidence; Content-ID tracks may expose a downloadable license certificate;
- the public FAQ says sign-up is required for full-resolution photos/videos, but does not state that ordinary music download requires sign-up;
- the currently documented Pixabay Developer API exposes image/video search, not an official music/audio search endpoint;
- the API documentation warns against large automated query volumes and systematic mass downloads.

Research classification:

> **CANDIDATE — strong rights/provenance fit for user/manual acquisition; automated MusicProvider integration remains BLOCKED-PENDING-OFFICIAL-AUDIO-INTEGRATION or explicit provider permission.**

Do not implement HTML scraping merely because browser download is easy.

If/when an approved audio integration exists, preserve at least:

```text
provider = pixabay
provider_track_id / stable page identity
track page URL
contributor
acquired_at
license family + terms URL/version/snapshot hash
commercial-use status
standalone-redistribution restriction
Content-ID registration/risk when exposed
license-certificate artifact when exposed
AI-generated signal when exposed
local file SHA-256
```

Prefer lower-claim-risk tracks when equally suitable, but Content-ID registration is a warning/risk feature, not automatic proof that the track is unusable.

## Provider candidate: SoundEffects+

User candidate:

`https://www.soundeffectsplus.com/`

Important correction: this site is primarily a **sound-effects library**, not a general music library.

Observed 2026-08-14 posture from its current official Terms/License:

- sound effects are offered free of charge and royalty-free for listed project uses, including commercial projects;
- copyright remains with the licensor; assets are licensed, not public-domain/"no copyright" material;
- raw resale/redistribution and building a downloadable sound library are prohibited;
- systematic downloading is prohibited and the license states a limit of up to 100 sound effects per month;
- the Terms prohibit attempting to access resources through automated, unethical or unconventional means;
- the License explicitly says the sound effects may not be used to build AI models or products.

Research classification:

> **NOT APPROVED for automatic provider integration. BLOCKED-PENDING-WRITTEN-PERMISSION / license clarification for this AI video-editing product.**

Do not scrape, crawl, mirror or automatically download from SoundEffects+.

Even manual per-item use should not be labeled `eligible_clear` for this product merely from the generic royalty-free wording because the current AI-product restriction is materially relevant. Preserve it as `unknown/ineligible pending clarification` according to the eventual rights policy.

## Architecture requirements for any future remote audio provider

A provider adapter must separate four responsibilities:

```text
DiscoveryPort
→ provider metadata only

Rights/License adapter
→ structured eligibility evidence

AcquisitionPort
→ fetch the specifically approved item only

AssetIngest
→ local authoritative audio Asset + provenance
```

Provider search result URLs never become EDL/timeline identity.

Release approval requires separate checks for:

- content license;
- provider/API/website access terms;
- programmatic-download permission;
- commercial/client/advertising scope;
- attribution requirements;
- modification/cut/loop permission;
- standalone redistribution restrictions;
- per-project/account/download limits;
- Content-ID/platform claim risk;
- AI-product restrictions;
- generated-audio provenance;
- current terms snapshot and change detection.

## Implementation timing

Do not interrupt active R0.11 for this provider backlog.

When provider acquisition is productized later, start with a Port and one provider whose **programmatic discovery and acquisition are explicitly permitted**. Local user music remains the safe baseline until then.

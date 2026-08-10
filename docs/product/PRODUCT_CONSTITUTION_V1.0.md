# Product Constitution v1.0

**Status:** ACTIVE  
**Effective date:** 2026-08-10  
**Authority:** User-approved product-level constitution  
**Scope:** `video-editing-agent`  
**Amendability:** Amendable only by an explicit, user-approved constitutional revision.

---

## 0. Purpose and precedence

This document defines the product-level rules that all architecture, implementation, upstream reuse,
providers, agents, workflows, tests, and user interfaces must obey.

The repository also contains Architecture Contracts that define durable domain objects, ownership,
revision semantics, dependency direction, and deterministic authority. Those contracts remain binding
where they are consistent with this Constitution.

When a product-policy conflict exists, precedence is:

```text
Product Constitution
        ↓
Architecture Contracts
        ↓
ADRs / capability specifications
        ↓
Implementation / provider behavior
```

A conflict does not silently rewrite historical Architecture Contracts. Instead, the conflicting legacy
rule is recorded here and must be migrated in a later Architecture Contract revision.

No model, API, upstream project, SDK, framework, or convenience feature may override this Constitution.

---

## 1. Product identity

The product is an **AI Director + AI Video Editor**.

It is not an AI video generator, not a generic stock-footage generator, and not a collection of unrelated
AI media features.

The product has exactly two primary capabilities:

1. **Pre-production creation**
   - convert a user's detailed goal and references into a structured, editable, executable script;
   - convert that script into a practical shooting plan that helps the user capture sufficient footage.

2. **Post-production editing**
   - understand user-supplied footage;
   - match footage to script and editorial intent;
   - select and trim source windows;
   - select or accept music;
   - analyze rhythm and musical structure;
   - create pacing, beat alignment, subtitles, transitions, and other editing decisions;
   - render a high-quality first cut and support natural-language revision.

Every other capability exists to serve these two primary capabilities.

### 1.1 Initial product focus

Initial product focus is:

- Windows desktop;
- commercial short-form video;
- e-commerce / advertising short video;
- Vlog;
- primarily videos under 60 seconds.

The architecture may remain extensible, but early implementation must optimize for these cases instead
of claiming universal editing capability.

### 1.2 Product priority order

When trade-offs are unavoidable, priorities are:

```text
Final video quality
    >
User controllability
    >
API cost
    >
Automation level
    >
Editing speed
```

Fast or fully automatic behavior must not be preferred merely because it is faster or more automated.

---

## 2. Visual-source constitution

### 2.1 User-supplied visual assets only

Every source video or source image that appears as visual content in a commercial output must be supplied
by the user as a local file.

The system may recommend that the user capture or provide additional footage, but it must not independently
obtain replacement visual material.

Visual asset URLs are not accepted as a material-ingest path.

### 2.2 Forbidden autonomous visual acquisition

The system MUST NOT:

- search the public web for replacement visual footage;
- download stock B-roll because coverage is missing;
- use Pexels, Pixabay, Coverr, or similar services to fill visual gaps automatically;
- accept an Agent decision to bypass missing user footage with remote visual material;
- turn a missing ShotRequirement into an autonomous remote visual search.

If required footage is missing, the required behavior is:

```text
coverage gap
    ↓
unresolved requirement / slot
    ↓
clear explanation to the user
    ↓
request missing footage
    ↓
give practical reshooting guidance when useful
```

Missing coverage is a production problem to surface, not a reason to invent or autonomously acquire
visual content.

### 2.3 Generative visual content is prohibited by default

The normal product path MUST NOT use generative AI to create or replace source visual content, including:

- AI-generated images;
- AI-generated video;
- generative fill;
- generative background replacement;
- object removal followed by synthesized background reconstruction;
- generative style transfer of source footage;
- face or person replacement;
- synthetic B-roll.

### 2.4 Frame interpolation boundary

Traditional, non-generative interpolation and optical-flow-based processing MAY be used as normal video
processing.

Generative frame synthesis is a separate optional capability:

- default: OFF;
- must require explicit user opt-in;
- the UI must explain that new visual frames may be synthesized;
- cost and quality must be measurable before it becomes a recommended path.

The product must not silently reinterpret ordinary interpolation as authorization for generative imagery.

### 2.5 Allowed non-generative editing operations

Normal video editing and signal-processing operations are allowed, including:

- trimming and source-window selection;
- crop, scale, rotate, and reframing;
- color correction and grading;
- stabilization;
- denoise;
- sharpen;
- speed changes;
- ordinary interpolation;
- audio normalization and denoise;
- transitions;
- subtitles;
- titles and text overlays;
- deterministic geometric motion graphics;
- information cards;
- data charts;
- layout and typography.

These are editing operations, not permission to generate replacement source imagery.

---

## 3. Audio constitution

Audio is governed separately from visual-source material.

### 3.1 User audio

The user may supply local:

- music;
- voice recordings;
- sound effects;
- other audio files.

Audio URLs are not accepted as a user material-ingest path.

### 3.2 Music discovery

The system MAY search and recommend music from public or connected music libraries.

It SHOULD prefer music with clear commercial-use terms.

Music candidates should be ranked with:

- a match percentage;
- concise reasons;
- relevant licensing/risk information.

A default music acceptance threshold may begin at:

```text
0.70
```

but this is a configurable and calibratable product threshold, not a permanent domain truth.

The system should avoid being so restrictive that ordinary users cannot obtain a workable track.

### 3.3 Licensing uncertainty

If a track appears suitable but commercial authorization cannot be confirmed, the system may still show
it as a candidate, but MUST disclose the risk.

If the user elects to continue, the system should record a user authorization/attestation event rather
than claiming that the software has verified legal rights.

### 3.4 Voice and generated audio

Supported voice paths may include:

- user-recorded voice;
- ordinary TTS;
- AI TTS.

Ordinary TTS is the default synthesized-voice path.

AI-generated voice, AI-generated music, and AI-generated sound effects belong to an optional generative
audio category:

- default: OFF;
- user choice controls activation;
- the product must not recommend them merely because they are available.

Exact providers and commercial policies are implementation decisions and remain subject to later review.

---

## 4. Commercial-use and provenance rules

The product is intended to create videos that may be used commercially.

### 4.1 User-provided assets

When a user imports an asset, the product may treat that action as the user's attestation that they have
the necessary rights or authorization to use it.

The product does not independently guarantee that the claim is legally correct.

When practical, preserve provenance information for:

- video;
- image;
- logo;
- font;
- music;
- voice;
- other externally sourced assets.

### 4.2 Risk disclosure and override

When the system can identify a meaningful copyright or commercial-use risk, it should inform the user.

A user may explicitly continue if they possess rights that the system cannot verify. That choice should be
recorded as a user attestation / manual license override.

### 4.3 Output provenance

The project should ultimately be able to trace rendered content back to source material, for example:

```text
timeline 00:03.200–00:05.800
    ↓
EDLSegment
    ↓
Shot source window
    ↓
Asset revision
    ↓
local user-supplied file + content hash
```

Commercial traceability is a product capability, not merely a debugging aid.

---

## 5. Script constitution

The script is an executable production document, not merely prose.

### 5.1 Script inputs

The planning system should support, when available:

- objective;
- product / topic;
- platform;
- audience;
- target duration;
- style;
- core message;
- factual/brand constraints;
- reference copy;
- user-supplied reference video;
- user-supplied existing footage;
- user notes and success criteria.

### 5.2 Reference analysis

A user-supplied reference video may be analyzed for:

- hook strategy;
- narrative structure;
- pacing;
- shot organization;
- transition logic;
- music/edit rhythm;
- other reusable structural patterns.

The system may learn from structure and technique, but should not copy protected expression merely because
a reference performed well.

### 5.3 Executable detail

ScriptPlan and its presentation should be detailed enough to function as a shooting construction manual.

Where useful, a section may express:

```text
timeline intent
narrative role
spoken narration / dialogue
visual requirement
shooting instruction
framing / camera movement
target duration
on-screen text / subtitles
music intent
editing / pacing intent
```

### 5.4 Revision and locking

A script remains editable.

Natural-language requests such as:

- make the first three seconds more compelling;
- remove a person from the planned appearance;
- make the wording younger;
- reduce the total duration;

should produce a new structured revision rather than destructively rewriting history.

Users must be able to lock approved sections so later AI revisions do not modify them.

### 5.5 Commercial facts are protected

During later editing, AI may shorten, reorder, or adapt presentation for quality, but it MUST NOT silently
change authoritative commercial facts such as:

- product specifications;
- price;
- claims;
- brand promises;
- mandatory factual statements.

Changes to authoritative business facts require user approval.

---

## 6. Shooting Plan constitution

The Shooting Plan exists to make the later edit possible.

Because the system is not allowed to invent missing visual coverage, pre-production coverage planning is
a first-class capability.

### 6.1 Default audience

The product may support professional users, but the default shooting guidance should be understandable to
ordinary users.

Prefer practical language such as:

> Move the phone close to the product, hold for about two seconds, then move slowly from left to right.

over unexplained cinematography jargon.

### 6.2 Equipment awareness

Before generating a practical shooting plan, the system should ask for or use known equipment constraints,
for example:

- phone / camera;
- tripod;
- stabilizer;
- lighting;
- number of people available;
- other production limitations.

The plan must remain realistically executable.

### 6.3 Coverage

Shot requirements should distinguish at least:

- required;
- recommended / preferred;
- optional;
- backup coverage.

The system SHOULD deliberately request useful extra coverage and alternate angles when that improves
editing flexibility.

### 6.4 Missing coverage

The script and shooting plan may explicitly state:

> If this material is not available, capture the following additional shot.

This is preferable to hiding the risk until post-production.

---

## 7. User-footage ingest and understanding

### 7.1 Input organization

The system must accept unordered user footage.

It should recommend that users apply simple numeric filename prefixes or another clear ordering scheme
before import, because good organization improves usability and auditability.

User-provided mapping from files to script requirements is optional.

The system must also be able to infer likely relationships itself.

### 7.2 Unplanned footage

Useful footage not mentioned in the Shooting Plan may still be understood, indexed, and selected by the
Director / Resolver when it better serves the Brief.

The ScriptPlan and ShootingPlan guide production; they are not absolute commands to ignore better evidence.

### 7.3 Quality and source windows

The system should identify and avoid unusable or weak ranges such as:

- blur;
- severe shake;
- poor exposure;
- setup/teardown moments;
- obvious speaking mistakes where detectable;
- other technical or semantic defects.

Selection must be able to operate on precise source windows inside a longer recording, not merely choose
whole files or whole detected shots.

---

## 8. Visual AI constitution

Visual AI is an observer and analysis capability, not a visual-content creator and not the final timeline
authority.

### 8.1 Intended visual facts

Visual understanding may derive textual or structured facts such as:

- subjects;
- actions;
- environment;
- emotion;
- composition;
- framing;
- camera motion;
- technical quality;
- action-event timestamps;
- visual rhythm;
- visual energy;
- candidate usable source ranges;
- other evidence useful to editing.

Its purpose is to help later decisions about trimming, selection, pacing, beat alignment, and music.

### 8.2 Proposal, not authority

A visual provider may propose:

> the strongest observable action occurs near 7.3 seconds.

It must not directly mutate the final timeline.

The authority chain remains:

```text
Visual / local analysis
        ↓
structured observations / proposals
        ↓
Director
        ↓
ShotResolver
        ↓
ResolutionDecision
        ↓
EDLBuilder
        ↓
EDL
```

When the user selects a fully automatic workflow, that is authorization for the editorial authority chain
to execute automatically. It is not permission for a visual model to bypass the authority chain.

### 8.3 Targeted re-analysis

A higher-level planning/review model MAY reject an edit plan or request that visual understanding inspect
specific footage or time ranges again.

This is a product-level review-loop principle.

The exact number of agents, model hierarchy, and provider topology are implementation details and are not
frozen by this Constitution.

### 8.4 Cloud and local vision

Most users should not be assumed to own a capable local multimodal model.

Therefore:

- cloud visual analysis may be the default;
- users may be offered an opt-out;
- a provider interface should remain available for user-supplied local models;
- if cloud vision is disabled and no local visual provider exists, visual-semantic capability may degrade;
- deterministic local media tools must continue to function.

The product should clearly explain this trade-off rather than pretending a visionless system has equivalent
semantic editing ability.

---

## 9. AI + local toolbox execution model

The product should behave as if the AI carries a well-prepared local toolbox.

### 9.1 Intelligence layer

Cloud or local AI may be used for:

- script generation;
- reference analysis;
- visual interpretation;
- editorial planning;
- review;
- natural-language intent parsing;
- other reasoning-intensive tasks.

### 9.2 Local execution layer

Whenever a mature local deterministic or open-source tool can execute a media operation reliably, the
product should prefer that tool over asking a general-purpose model to simulate the work.

Local tools may handle:

- media probing;
- decoding;
- frame extraction;
- shot detection;
- deterministic signal analysis;
- indexing;
- persistence;
- timeline execution;
- transcoding;
- rendering;
- other repeatable media operations.

AI decides or proposes what should happen; local tools perform the concrete work when appropriate.

### 9.3 Cost-aware decomposition

API calls should be reserved for information or judgment that benefits from model intelligence.

Prefer:

```text
cheap local preprocessing
        ↓
small, relevant evidence package
        ↓
AI analysis / judgment
        ↓
structured plan
        ↓
local deterministic execution
```

over uploading complete media or repeatedly asking an API to perform deterministic work.

### 9.4 Network-loss behavior

Original full videos must remain local by default.

Cloud requests should minimize transferred material and use only what is necessary, such as:

- selected sampled frames;
- short derived snippets when temporal evidence genuinely requires them;
- metadata;
- transcripts;
- structured facts;
- text.

If network connectivity is lost:

- new cloud inference may pause or fail gracefully;
- cached structured results remain usable;
- local media inspection that has no cloud dependency remains usable;
- existing structured edit plans and EDLs remain executable;
- local rendering and persistence remain usable.

The network should be an intelligence dependency where needed, not the mechanical foundation of the editor.

---

## 10. Music and BeatMap constitution

Music selection and beat analysis exist to improve the edit.

### 10.1 Music matching factors

Music ranking should consider at least:

- content theme;
- emotional intent;
- tempo;
- video duration;
- target platform;
- commercial style;
- visual motion;
- narration density.

When several local or library tracks exist, the system should rank them, show a match percentage, and
explain the main reasons.

### 10.2 BeatMap is descriptive

BeatMap describes musical facts and derived structure.

It does not own the timeline.

Expected analysis may include:

- BPM;
- beats;
- downbeats;
- accents;
- phrases;
- sections;
- energy;
- drops;
- build-ups;
- other useful musical structure.

### 10.3 Beat alignment

The editing system should support more than cutting on every strong beat.

It should be able to reason about:

- phrase-level pacing;
- high-energy vs low-energy sections;
- action-event alignment;
- visual motion;
- narration;
- selective accents.

The architecture rule remains:

```text
BeatMap provides music evidence
        ↓
Director decides what matters
        ↓
Resolver selects source material
        ↓
EDL executes exact alignment
```

---

## 11. Editing autonomy and user control

### 11.1 First cut

The preferred interaction model is:

> AI produces a strong first cut that can approach one-click output quality, then the user can refine it.

The product should not assume that high automation eliminates the need for user control.

### 11.2 Natural-language revision

A user instruction such as:

> Replace the shot around 12 seconds with the clip where I am wearing white.

should be interpreted into structured editing intent and applied through domain owners.

A general-purpose LLM must not directly mutate raw timeline state as an unvalidated side effect.

### 11.3 Locks

Users should be able to lock relevant creative state, including where appropriate:

- Script sections;
- selected clips;
- timeline sections;
- other approved decisions.

Later automatic revisions must respect locks.

### 11.4 Autonomy profiles

The product may provide project-level autonomy profiles such as:

- Conservative;
- Balanced;
- Full Auto.

The exact approval matrix for high-impact operations remains a separate specification and is intentionally
not frozen in v1.0.

---

## 12. Timeline, render, and output

### 12.1 EDL authority

EDL is the sole executable timeline authority.

Renderer executes EDL; it does not become a hidden editor.

### 12.2 User-facing export

The first user-facing final export target is MP4.

The system should nevertheless preserve a structured internal EDL as a durable project asset.

Future adapters may export to professional NLE formats, but Premiere / DaVinci Resolve / FCP exchange is
not a v1.0 product requirement.

### 12.3 Editing completion expectation

The long-term goal is that AI performs approximately 95–100% of routine editing work when the user chooses
that mode, while the remaining adjustments remain under user control.

This is a quality aspiration, not permission to bypass validation, ownership, locks, or provenance.

---

## 13. Local-first project data

### 13.1 Local media

Original user media is local-first and must not be uploaded wholesale by default.

### 13.2 Project history

Project history and revisions should be stored locally in a clearly disclosed project-data location.

For the Windows-first product, project history should default to a non-system-disk area when available.

The UI must tell the user where project data is stored so it can be backed up or deleted deliberately.

### 13.3 Multi-project support

The product should support multiple independent projects, each with its own creative and media state.

Conceptually:

```text
Project
├─ Brief
├─ ScriptPlan revisions
├─ ShootingPlan revisions
├─ Assets / Shots / analyses
├─ Music / BeatMap
├─ EditPlan / ResolutionDecision / EDL revisions
├─ Review
└─ Rendered outputs
```

---

## 14. Engineering evidence and benchmarks

### 14.1 Engineering probe vs product probe

These must never be conflated.

**Engineering Probe** proves that contracts and machinery work, for example:

- API authentication;
- request/response schema;
- owner-chain correctness;
- persistence;
- codec/runtime wiring;
- CI behavior.

Synthetic fixtures are appropriate for engineering probes.

**Product Probe** proves that a capability is useful on real footage.

A live API request against a synthetic FFmpeg test pattern is not evidence that real user footage is
understood or edited well.

### 14.2 Real benchmark corpus

The project should develop real benchmark material over time.

Benchmark data may be divided into:

- public / redistributable fixtures that may enter the repository;
- private local user footage that must never enter GitHub.

### 14.3 Quality comparison

Major algorithm or model changes should be compared against meaningful existing benchmarks when practical.

Passing more unit tests is not evidence that editing quality improved.

The project is intentionally allowed to progress patiently. It should not trade architecture quality for a
rushed MVP merely to demonstrate a fast end-to-end demo.

---

## 15. Open-source capability strategy

The project seeks to combine the strongest available open-source engineering without becoming a
"Frankenstein" assembly of incompatible projects.

### 15.1 Upstream Survey Gate

Before implementing a major new capability, perform an Upstream Survey Gate.

Relevant capability areas include:

- script planning;
- shooting planning;
- media understanding;
- action/event localization;
- music analysis;
- music selection;
- Director;
- Shot Resolver;
- beat/action alignment;
- EDL;
- rendering;
- review / quality evaluation.

A substantial survey should normally consider:

- roughly 5–15 relevant repositories when the ecosystem permits;
- important research papers and official implementations;
- public technical information from mature commercial editing systems when useful.

Implementation begins only after understanding what should be reused, adapted, independently reimplemented,
or rejected.

### 15.2 Reuse policy

Preferred strategy:

> Clear, compatible licenses such as Apache-2.0 or MIT may justify direct adaptation or reuse with proper
> provenance and notices; uncertain or incompatible code is used only as an engineering/algorithmic
> reference.

Every reused or adapted component must conform to this repository's Domain and ownership contracts.

The local system owns the product semantics. An upstream project's folder structure, state machine, task
orchestrator, database schema, or agent topology does not become authoritative merely because its
implementation is mature.

### 15.3 Current reference roles

Current strategic references include:

- **FireRed-OpenStoryline** — primary pipeline/media/render engineering reference;
- **soCzech/TransNetV2** and compatible runtime work — shot-detection inference reference;
- **MoneyPrinterTurbo** — provider abstraction and operational-engineering reference, not an autonomous
  visual-stock acquisition path;
- **CutClaw** — editing architecture/algorithm reference only; source code is not copied;
- **BeatSync Engine** — music/beat-analysis reference.

These roles may evolve after future surveys, but no upstream may override this Constitution.

---

## 16. Development governance

### 16.1 Main-only development

Repository construction is performed directly on `main`.

Do not create feature branches for ordinary project development.

Existing legacy branches are not authority for current work.

### 16.2 Atomic changes and CI

For coherent implementation changes:

```text
observe current state
    ↓
understand
    ↓
plan
    ↓
make one coherent change
    ↓
verify locally / structurally
    ↓
one atomic commit to main
    ↓
wait for CI
    ↓
CI green before next implementation batch
```

If the latest `main` is red, feature work freezes until the failure is resolved.

Historical red runs do not need to be rewritten.

### 16.3 Provider neutrality

Models and APIs are replaceable providers.

They may produce proposals and observations, but must not silently acquire ownership of durable domain
entities or the final timeline.

### 16.4 Tool over model

If a deterministic local tool is the correct executor, use it.

Do not spend model tokens reimplementing codec, media, indexing, persistence, timing, or rendering work that
reliable local programs already perform better.

---

## 17. Legacy conflict register

The following earlier Architecture Contract v0.1.1 concepts conflict with this Constitution for **visual
assets** and MUST NOT be implemented as active product behavior:

```text
remote_allowed
remote_only
generated_allowed
remote_search_queries
```

`local_preferred` must not be interpreted as permission to fall back to remote visual footage.

Any older documentation that presents Pexels or another stock-video provider as an automatic visual
fallback is legacy product-policy guidance.

MoneyPrinterTurbo may still inform provider abstraction, caching, retries, provenance, or audio/non-visual
provider engineering. It must not reintroduce autonomous visual-material acquisition.

Historical contracts remain preserved as architecture history. A future Architecture Contract revision
must reconcile the source-policy schema with this Constitution rather than silently retaining the conflict.

---

## 18. Deliberately unresolved items

v1.0 intentionally leaves these details open for later specifications or constitutional amendment:

- the exact operation-by-operation approval matrix for Conservative / Balanced / Full Auto;
- the exact providers and product policy for optional generative audio;
- whether and when generative frame synthesis is worth its cost and quality trade-offs;
- the default local vision provider, if any;
- music-score calibration and library-specific licensing behavior;
- professional NLE interchange formats beyond the initial MP4 output;
- exact agent/model topology for planning, critique, targeted re-analysis, and review.

Unresolved implementation details must not be used as justification to violate the frozen principles above.

---

## 19. Amendment process

This Constitution is intentionally amendable.

A constitutional amendment requires:

1. an explicit discussion of the proposed product-level change;
2. explicit user approval;
3. a version change;
4. a written rationale;
5. identification of affected Architecture Contracts, ADRs, code, tests, and migrations;
6. an effective date.

Constitutional behavior MUST NOT change silently as a side effect of adopting a new model, API, upstream
project, or convenience feature.

When evidence proves a rule is no longer serving the product, the correct action is to amend the
Constitution deliberately, not to bypass it in code.

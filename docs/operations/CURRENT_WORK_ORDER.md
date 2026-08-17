# Current Work Order

**ID:** `R0.12-PRODUCT-FLOW-ORCHESTRATION-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — practical product-facing Planning / Editing orchestration  
**Mode:** PRODUCT INTEGRATION  
**Accepted production-code baseline:** `914dd7dcc72595d418d7d3bf0cb05e356dd021b9`  
**Activated:** 2026-08-17  
**Codex release:** NO

## Previous Work Order result

`R0.12-WINDOWS-ENVIRONMENT-DOCTOR-001` — **PASS / CLOSED**.

Closure evidence:

`docs/validation/R0.12_WINDOWS_ENVIRONMENT_DOCTOR_CLOSURE.md`

Accepted production baseline:

`914dd7dcc72595d418d7d3bf0cb05e356dd021b9`

Bounded Windows production run:

`32035192895` — PASS.

## Why this work exists

The repository now has accepted owners for Brief/Planning, local Asset/Shot/understanding, Editing Director, retrieval/Resolver primitives, audio/spatial/subtitle decisions, canonical EDL, Renderer, Preview, Review and Environment Doctor.

What remains structurally missing is a product-level coordinator that turns ordinary user inputs into those owner calls without requiring the user to hand-author internal IDs, CandidateWindows, ResolutionDecisions, EDL objects or render requests.

Current evidence confirms the fragmentation:

- `ProjectWorkspace.runtime()` reaches Planning and low-level media operations;
- `ProjectWorkspace.editing_runtime()` reaches persisted EditPlan generation only;
- the R0.12 living smoke still manually composes Resolver → EDLBuilder → Renderer;
- the older R0.9 Product Probe already proved a real retrieval → persisted temporal evidence → canonical CandidateWindow → grounded Resolver route, but that composition remains Probe-only.

This Work Order promotes that proven composition into a reusable application/product flow while preserving every accepted owner boundary.

## Canonical product contract

Source of truth:

`docs/product/STAGE_A_PRODUCT_IO_CONTRACT.md`

Two product outcomes remain independent:

```text
Planning-only:
ordinary user intent / reference context
→ Brief owner
→ ScriptPlanningWorkflow
→ ShootingPlanningWorkflow
→ persisted ScriptPlan + ShootingPlan

Editing-only:
ordinary user local footage + editing intent + output path
→ ingest / Shot / understanding owners
→ Director → EditPlan
→ retrieval / CandidateWindows / Resolver
→ approved audio/spatial/subtitle decisions
→ EDLBuilder → canonical EDL
→ Renderer → Review
→ final MP4 / typed correction state
```

Combined is composition of these same routes, not a third architecture.

## Product-facing request rule

Ordinary-user requests may contain:

- project location / create-open intent;
- Brief/editorial text and supported policy/production constraints;
- local files/folder expanded to files;
- explicit final output destination;
- understandable audio/voice intent;
- optional exact Planning revisions for Combined flow.

They must **not** require the user to supply:

- AssetRef / ShotRef as ordinary input;
- CandidateWindow;
- ResolutionDecision;
- source timestamp;
- AudioMixDecision internals;
- EDL / RenderRequest;
- repository paths other than chosen project/input/output locations.

Configuration/runtime dependencies such as provider choice, FFmpeg executable or optional model path belong to product composition/configuration, not editorial request meaning.

## Product progress contract

Expose ordered product-facing progress projections at minimum:

- `PROJECT_READY`
- `INPUT_VALIDATION`
- `INGEST_UNDERSTANDING`
- `PLANNING_GENERATION`
- `EDITING_DECISION`
- `RESOLVING`
- `EDL_ASSEMBLY`
- `RENDERING`
- `REVIEW_QC`
- `COMPLETED`
- `FAILED`

Names may be normalized if a smaller coherent enum is cleaner.

Each event must carry understandable stage/status and optional owned diagnostic text. These events are application projections, not new Domain entities.

## Planning flow minimum

Implement one reusable Planning launch that:

1. creates/commits Brief through existing Brief owner;
2. generates ScriptPlan through existing ScriptPlanningWorkflow;
3. generates ShootingPlan through existing ShootingPlanningWorkflow;
4. returns exact persisted revision refs and user-usable structured output;
5. exposes progress and typed failure without duplicating the persisted entities.

No local footage is required.

## Editing flow minimum

Implement one reusable Editing coordinator whose public request starts from local files + Brief/editorial intent + output destination.

### Media and Director

- local originals cross normal `AssetIngestService` and remain untouched;
- Shot/understanding stages use injected production capability adapters;
- Director produces/persists EditPlan;
- ScriptPlan/ShootingPlan refs remain optional.

### Retrieval / grounded windows

Promote reusable composition from the accepted R0.9 route.

First production baseline may use deterministic lexical retrieval as the always-available retrieval channel after analyses are indexed. Dense retrieval remains an optional enhancement and must not become a mandatory ordinary-user dependency in this Work Order.

For each EditSlot:

```text
ShotIndex candidates
→ hard duration/eligibility filter
→ persisted TemporalAnchor/Evidence where available
→ canonical CandidateWindow generation
→ conservative Shot-boundary grounded window when no stronger anchor exists and CAP-04 permits it
→ ResolverCandidate
→ optimize_sequence()
→ ResolutionDecision
```

Rules:

- no LLM-generated IDs/timestamps;
- fallback windows remain inside exact Shot source range;
- fallback provenance must say it came from exact Shot boundary grounding;
- unresolved slots remain explicit and fail EDL acceptance rather than being silently omitted;
- dense/VLM escalation can be added later without changing the product request contract.

### Audio / spatial / music

Do not invent optional assets.

For the minimum no-extra-music path:

- source audio treatment must be deterministic and grounded to Resolver selections;
- preserve original source audio conservatively unless explicit product intent says otherwise;
- required speech remains protected by the accepted VoiceTreatment contract;
- no BGM is invented merely to make the render audible;
- no spatial/reframe decision is invented when no approved composer decision exists.

Optional music/spatial/subtitle integrations may be injected when existing accepted decisions are available, but they must not block the minimal local-footage route unless product intent explicitly requires them.

### EDL / render / Review

- EDLBuilder receives only persisted/approved owner outputs;
- canonical EDL remains sole exact timeline authority;
- Renderer executes it;
- Review classifies final evidence;
- PASS returns final MP4 path;
- `RERENDER_SAME_EDL` remains bounded and explicit;
- editorial correction routes back to the named owner instead of being silently applied.

## Result contract

Planning result must expose at least:

- project location;
- Brief ref;
- ScriptPlan ref;
- ShootingPlan ref;
- progress events;
- terminal success/failure.

Editing result must expose at least:

- project location;
- exact Brief/EditPlan/EDL lineage available to application layer;
- final output path when rendered/reviewed successfully;
- Review verdict/correction route when not accepted;
- progress events;
- terminal owned diagnostic.

No requirement to expose an NLE timeline UI in this Work Order.

## Deterministic tests

Cover at least:

1. Planning launch calls owners in order and returns exact persisted refs;
2. Planning failure stops at owner boundary and produces FAILED progress;
3. Editing request takes local paths rather than prebuilt Asset/Shot/Resolution IDs;
4. original files remain unmodified;
5. retrieval query derives from EditSlot intent;
6. lexical candidate score remains retrieval evidence only;
7. candidate window stays inside exact Shot range;
8. persisted TemporalAnchor is preferred when available;
9. Shot-boundary fallback is deterministic and explicitly evidenced;
10. no legal candidate → unresolved → fail closed before render acceptance;
11. Resolver decision feeds EDLBuilder without source-time rewrite;
12. conservative source-audio treatment is per resolved selection;
13. no optional music/spatial asset is fabricated;
14. Renderer receives the canonical EDL produced by EDLBuilder;
15. clean Review PASS returns discoverable final output;
16. Review correction route is surfaced, not hidden;
17. progress stages are ordered and terminal state is unambiguous;
18. Combined optional Planning refs enrich Editing without becoming mandatory.

Existing 641+ repository tests and all architecture contracts must remain green.

## Product-facing seam

A simple structured CLI/adapter is allowed after the application coordinator is stable. Prefer one request document per product launch over a dozen low-level commands.

Conceptually acceptable shapes:

```text
video-editing-agent run planning --request planning.json
video-editing-agent run editing  --request editing.json
```

Exact syntax may differ.

This CLI is an Engineering/Product surface for upcoming Product Probes; a plain CLI alone does not equal final Stage-A Human Gate UX.

## Evidence gate

After deterministic gates pass:

1. run one bounded Planning product-flow Engineering Probe through the new coordinator;
2. run one bounded Editing flow Engineering Probe using real media and the canonical Renderer/Review path if dependencies can be represented in hosted CI;
3. classify these as Engineering evidence unless the input and judgment satisfy Product Probe/Human Gate rules.

Do not label synthetic/provider-stub flows as Product Gate PASS.

## Codex/resource policy

Approximately **9% Codex quota remains**.

ChatGPT + GitHub remain primary for the product-flow contract, owner-preserving coordinator, deterministic tests, hosted CI and governance.

Codex remains **NO ACTIVE RELEASE**. Release it only if the concrete Windows/media orchestration produces a genuine multi-file runtime defect that hosted evidence cannot close efficiently.

## Exit gate

PASS requires:

- reusable Planning and Editing product-flow application surfaces exist;
- ordinary request DTOs do not expose internal timeline/Resolver objects;
- product progress/failure/result contract exists;
- Planning chain reaches persisted ScriptPlan + ShootingPlan;
- Editing coordinator reaches canonical EDL → Renderer → Review when all required injected capabilities are available;
- retrieval→CandidateWindow→Resolver logic is no longer Probe-only;
- all source times remain grounded;
- deterministic tests and repository gates pass;
- bounded integration evidence passes;
- no claim that Human Gate/Product Gate is passed yet;
- structural progress remains 90% until actual ordinary-user gate evidence justifies a change.

## STOP boundary

Do not build GUI/frontend.

Do not invent timestamps/IDs with an LLM.

Do not make dense retrieval, GPU or optional music mandatory for minimal Editing.

Do not bypass Brief/Planning/Director/Resolver/EDL/Renderer/Review owners.

Do not silently repair Review failures.

Do not bump structural progress for an orchestration abstraction alone.

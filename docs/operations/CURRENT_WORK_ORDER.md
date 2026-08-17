# Current Work Order

**ID:** `R0.12-PRODUCT-FLOW-ORCHESTRATION-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — practical product-facing Planning / Editing orchestration  
**Mode:** ENGINEERING PROBE CLOSURE  
**Accepted production-code baseline:** `db8db211e6c662cdfc7ad2afe385ee766ce1a240`  
**Activated:** 2026-08-17  
**Codex release:** NO

## Previous Work Order result

`R0.12-WINDOWS-ENVIRONMENT-DOCTOR-001` — **PASS / CLOSED**.

Closure evidence:

`docs/validation/R0.12_WINDOWS_ENVIRONMENT_DOCTOR_CLOSURE.md`

## Current implementation truth

The reusable product-flow implementation is now merged and accepted on `main` at:

`db8db211e6c662cdfc7ad2afe385ee766ce1a240`

The accepted surface includes:

- `video-editing-agent run planning --request <json>`;
- `video-editing-agent run editing --request <json>`;
- strict ordinary request parsing that rejects internal editing/timeline authority fields;
- ProjectWorkspace Planning composition through Brief → ScriptPlan → ShootingPlan owners;
- Editing composition through local ingest → Shot/understanding → Director/EditPlan → grounded Resolver → canonical EDL → Renderer → Review;
- conservative Resolver-grounded source-audio handling;
- exact canonical EDL persistence in project SQLite;
- deterministic request-boundary, audio-policy and concrete composition tests.

The exact-head deterministic repository CI passed after merge.

This implementation evidence does **not** itself close this Work Order and does **not** constitute Product Gate or Human Gate evidence.

## Canonical product contract

Source of truth:

`docs/product/STAGE_A_PRODUCT_IO_CONTRACT.md`

Two independent product outcomes remain:

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

## Frozen ordinary-request boundary

Ordinary-user requests may contain:

- project location / create-open intent;
- Brief/editorial text and supported policy/production constraints;
- local files/folder expanded to files;
- explicit final output destination;
- understandable audio/voice intent;
- optional exact Planning revisions for Combined flow.

They must **not** require the user to supply:

- AssetRef / ShotRef;
- CandidateWindow;
- ResolutionDecision;
- source timestamp;
- AudioMixDecision internals;
- EDL / RenderRequest.

Provider/model/FFmpeg/runtime configuration is composition configuration, not editorial request meaning.

## Remaining Engineering Probe gate

### Probe A — Planning product-flow Engineering Probe

Required mechanism:

```text
ordinary Planning request
→ product-facing request adapter
→ Brief owner
→ ScriptPlanningWorkflow
→ persisted ScriptPlan
→ ShootingPlanningWorkflow
→ persisted ShootingPlan
→ structured result with exact persisted refs
```

Acceptance evidence must prove:

1. entry is the ordinary request surface, not hand-authored Domain objects;
2. Brief/ScriptPlan/ShootingPlan are persisted in the project workspace;
3. returned refs load the exact persisted revisions;
4. progress reaches a terminal completed state;
5. no local footage is required.

This remains Engineering evidence unless real product input and Human Gate judgment are intentionally included later.

### Probe B — Editing real-media Engineering Probe

Required mechanism:

```text
ordinary Editing request
→ real valid local media
→ actual FFprobe ingest
→ actual Shot detection
→ actual understanding
→ Director / persisted EditPlan
→ indexed retrieval
→ grounded CandidateWindows / Resolver
→ canonical EDL
→ persist exact EDL revision
→ actual FFmpeg Renderer
→ actual MP4
→ Review
→ terminal result
```

Acceptance evidence must prove:

1. source is a real valid media file, not fake bytes;
2. ordinary request does not contain ShotRef/CandidateWindow/ResolutionDecision/source timestamps/EDL;
3. original media remains unchanged;
4. Resolver-owned source ranges reach EDLBuilder without launcher rewrite;
5. canonical EDL is persisted before render acceptance;
6. actual FFmpeg produces a valid MP4 at the requested output path;
7. Review consumes the rendered-media evidence and returns an explicit verdict/correction route;
8. persisted Brief/EditPlan/EDL lineage is inspectable after completion.

Provider/model usage may be bounded and explicit, but fake Renderer output cannot satisfy this probe.

## Canonical EDL cross-process durability evidence

The existing Windows SQLite Persistence Probe directly proves separate-process persistence for the entities it currently seeds/resumes. Do not broaden that evidence claim to canonical EDL unless the probe explicitly tests EDL.

If this Work Order closure states that exact canonical EDL cross-process durability is proven, add the smallest bounded evidence:

```text
process 1
→ save exact EDL revision to SQLite
→ exit

process 2
→ reopen same SQLite project
→ load same exact EDL revision
→ verify exact payload / lineage
```

This may be added to the existing bounded persistence probe or to the Editing Engineering Probe. Do not redesign persistence architecture merely to obtain this evidence.

## Deterministic gate status

The implementation baseline already satisfies deterministic repository gates and existing architecture contracts.

Future repairs in this Work Order must remain narrowly evidence-driven. Do not reopen already accepted architecture merely because a probe exposes a runtime/configuration defect.

## Codex / resource policy

Approximately **9% Codex quota remains**.

ChatGPT + GitHub remain primary for remote state, workflow evidence, small probe/workflow changes and governance.

Codex remains **NO ACTIVE RELEASE** by default.

Release Codex only if the real Planning/Editing probe exposes a genuine Windows/media multi-file runtime defect that materially benefits from local `inspect → edit → test → repair` iteration.

## Exit gate

PASS requires all of the following:

- reusable Planning and Editing product-flow application surfaces remain on accepted `main`;
- ordinary request DTOs do not expose internal timeline/Resolver objects;
- product progress/failure/result contract remains intact;
- Planning Engineering Probe reaches persisted ScriptPlan + ShootingPlan through the ordinary request surface;
- Editing Engineering Probe reaches real media → canonical EDL → actual FFmpeg MP4 → Review through the ordinary request surface;
- exact source times remain grounded and EDL remains sole timeline authority;
- if closure claims EDL cross-process durability, direct EDL second-process evidence exists;
- repository deterministic gates remain green;
- evidence is classified as Engineering evidence, not Product Gate/Human Gate PASS;
- structural progress remains 90% until actual ordinary-user Product Gate evidence justifies a change.

## STOP boundary

Do not build GUI/frontend in this Work Order.

Do not invent timestamps/IDs with an LLM.

Do not make dense retrieval, GPU or optional music mandatory for the minimal Editing route.

Do not bypass Brief/Planning/Director/Resolver/EDL/Renderer/Review owners.

Do not silently repair Review failures.

Do not label fake-media/fake-renderer composition tests as real Editing evidence.

Do not bump structural progress for Engineering Probe completion alone.

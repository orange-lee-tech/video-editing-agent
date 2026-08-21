# Current Work Order

**ID:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Status:** ACTIVE  
**Phase:** R0.12 — Stage-A final closure  
**Mode:** GOVERNANCE CLEANUP → REFERENCE COMPATIBILITY → WINDOWS PACKAGING → FINAL HUMAN GATE  
**Accepted production-code baseline:** `6ba297bf28f36aa7e56da9babb5f27d941965913`  
**Activated:** 2026-08-21  
**Updated:** 2026-08-21  
**Codex release:** CLOSED until ChatGPT explicitly releases the next bounded local wave

## Objective

Reach a truthful Stage-A / 1.0 structural closure without feature creep, while leaving a stable compatible foundation for later commercial-scale development.

The ordinary Editing no-speech baseline has passed a real Human Gate and PR #11 is merged. Planning Product/Human Gate remains PASS, but a real Bilibili reference-page compatibility gap is recorded. Packaging still lacks a real Windows distributable proof.

## Permanent construction principles

1. **Bounded self-repair** — repair blockers discovered inside the active 1.0/packaging boundary; do not expand into unrelated cleanup.
2. **Compatible development** — solve current defects without locking future provider/model/runtime/renderer substitution.
3. **Flexible production line** — stages expose capability/input/output/diagnostic/fallback semantics; absence of work is not automatically failure.
4. **Source protection** — user originals remain immutable; generated/analyzed/separated media are derived assets.
5. **Thin packaging** — bootstrap/resource/runtime location stays outside Domain authority and does not become a second application architecture.
6. **Attention discipline** — root `AGENTS.md` controls default reading; `docs/archive/**` is excluded by default.

## 1.0 retained scope

Must remain real and supportable:

- Planning: user intent/reference/commercial constraints → inspectable ScriptPlan + usable ShootingPlan;
- Editing: user-selected real footage → automatic grounded editing → canonical EDL → Review/Renderer → final media;
- original/source audio on the ordinary path;
- rights-safe BGM;
- basic trusted subtitles for ordinary clear speech when the approved speech capability is available;
- deterministic Stage-A editing-expression floor already accepted by the completion contract;
- understandable progress/failure/degraded states;
- Windows ordinary-user distributable proof without requiring Python/uv/repository execution.

## Explicitly deferred beyond 1.0

- production synthetic-voice/TTS backend;
- advanced speech/ambience source-separation backend and advanced stem mixing;
- rich subtitle font/animation/speaker systems;
- advanced audiovisual effects and feature-rich NLE behavior;
- generic/unbounded website crawling.

Typed seams already introduced for deferred capabilities must remain; do not remove them merely because their backends are deferred.

## Wave A — repository attention/document governance

Owner: ChatGPT/GitHub unless a local blocker genuinely requires Codex.

Deliver:

- root `AGENTS.md` attention firewall;
- compact `docs/DOCUMENT_REGISTRY.json` relative-path map;
- automatic exhaustive registry inventory;
- update-date/document lifecycle/archive rules;
- `docs/archive/**` default exclusion;
- refreshed live trio and durable R0.12 Editing evidence;
- existing governance checks extended rather than replaced.

Archive decisions remain semantic/manual; automation must not move documents automatically.

## Wave B — bounded Planning reference compatibility

Target: prove provider-specific reference acquisition without contaminating Planning Domain.

First real compatibility proof is the observed Bilibili ordinary page URL class.

Requirements:

- route through `ReferenceAcquisitionPort` or equivalent existing acquisition seam;
- bounded provider-specific behavior only;
- preserve SSRF/DNS/IP/redirect/MIME/size/timeout protections;
- no login circumvention, generic crawler, whole-site traversal or JavaScript browser automation unless separately reviewed/authorized;
- output the same trusted reference-media contract consumed by existing Planning;
- unsupported provider/page states must be diagnosable rather than fabricated.

Success means an ordinary supported Bilibili reference page can feed the existing Planning workflow; it does not mean universal Bilibili/Douyin/Xiaohongshu support.

## Wave C — compatible Windows packaging foundation

This is an **effective packaging** requirement, not documentation-only preparation.

Minimum engineering proof:

```text
Windows distributable (prefer onedir first)
→ thin bootstrap
→ resource/runtime locator
→ ordinary GUI launch
→ environment/capability diagnostics
```

Target environment must not require:

- a repository checkout;
- Python installation;
- uv;
- developer-only PATH setup.

Packaging must not:

- hard-code one provider/model as Domain truth;
- place user-writable project/profile data inside the install directory;
- silently bundle unreviewed binaries/models/licenses;
- bypass the ordinary application composition path;
- copy arbitrary `.private`, `.tools`, `.venv`, caches or developer-machine artifacts into release output.

Required compatibility seams:

- resource location separate from business logic;
- runtime capability resolution explicit and diagnosable;
- later TTS/separation/providers/models/renderers can be added without replacing bootstrap architecture;
- FFmpeg/TransNet/speech-runtime/model handling uses deliberate manifest/config ownership;
- existing projects remain readable or have explicit migration if persistence contracts change.

Codex may self-repair packaging blockers inside this boundary and re-run validation until stable. It must report non-blocking unrelated debt instead of expanding scope.

## Wave D — final retained Product/Human Gate

After Waves B/C are accepted:

1. Planning with an ordinary supported reference page produces usable persisted ScriptPlan/ShootingPlan.
2. Editing no-speech baseline remains non-regressed.
3. A simple, clear single-speaker video proves original speech + basic trusted subtitle timing with the approved/pinned speech capability.
4. The packaged ordinary Windows surface launches without Python/uv/repository execution and exposes truthful diagnostics.
5. Sources remain unchanged.
6. Full repository quality/governance gates pass.
7. Exact-head CI passes.

Only then may control state set:

- `core_1_planning_product_gate: PASS`;
- `core_2_editing_product_gate: PASS`;
- `stage_a_completion_gate: PASS`;
- `structural_progress_percent: 100`.

## Current progress

**95%**.

Do not trade architecture compatibility or truthful product behavior for an artificial 100% number.

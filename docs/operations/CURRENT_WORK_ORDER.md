# Current Work Order

**ID:** `R0.12-MINIMUM-REVIEW-REPAIR-LOOP-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Minimum post-render Review / bounded repair routing  
**Mode:** PRODUCT INTEGRATION / CODE-AUDIT COMPLETE  
**Accepted production-code baseline:** `4ca3b83bfac50923bdcf15f1ad08d90b397daa23`  
**Activated:** 2026-08-17  
**Codex release:** NO

## Previous Work Order result

`R0.12-PRODUCTION-PREVIEW-INTEGRATION-001` — **PASS / CLOSED**.

Accepted production baseline:

`4ca3b83bfac50923bdcf15f1ad08d90b397daa23`

Closure evidence:

`docs/validation/R0.12_PRODUCTION_GSTREAMER_PREVIEW_INTEGRATION_EVIDENCE.md`

Final bounded Windows production-adapter probe:

- run `32030024748` — PASS;
- AUTO and SOFTWARE_VIDEO raw probe steps both passed;
- production GstPlay adapter completed initialize/load/play/pause/exact seek/resume/stop/release;
- private GStreamer 1.28.6 runtime provenance was verified;
- the first superficially green software-mode probe was rejected after real diagnostics exposed incorrect factory filtering;
- the accepted implementation separately intersects Decoder + Hardware + Video classifications before rank demotion;
- no Codex release used;
- player/backend-family selection remains closed.

## Why this work exists

The Stage-A Editing chain is not complete merely because Renderer can produce a technically valid file.

Current repository evidence shows three separate deterministic foundations already exist:

1. **pre-render structural audio QC** — `application/audio_qc.py` checks whether canonical EDL has an approved audible lane when audible output is required;
2. **Renderer technical verification** — the FFmpeg Renderer verifies output resolution, frame rate, required audio-track presence and duration before returning `RenderArtifact`;
3. **post-render PCM diagnostics** — `music/audio_editorial.py::inspect_pcm16_wav()` can identify clipping and mostly-silent PCM output.

What is missing is one application-owned Review boundary that consumes the successful render artifact plus deterministic post-render evidence and returns a typed acceptance/correction verdict.

There is currently no production Review owner discovered in the Python tree, and the living smoke stops at EDL/FFmpeg compilation rather than a post-render Review verdict.

## Frozen ownership

The following invariants are non-negotiable:

```text
canonical EDL        = sole exact executable timeline authority
Renderer             = execute canonical EDL + technical delivery verification
Review               = evaluate deterministic delivered-output evidence
Editorial owners     = decide semantic/timeline/audio changes when Review routes back
Environment/Renderer = own same-EDL technical rerender when the failure is execution-only
```

Review may **not**:

- directly mutate EDL/EditPlan/ResolutionDecision;
- silently change source ranges, cuts, captions, music, gains or voice treatment;
- infer new editorial intent;
- fabricate a repaired artifact;
- retry recursively without a bounded explicit attempt;
- duplicate Renderer-owned delivery verification just to create a second technical authority.

## Audit findings that define this Work Order

### Existing pre-render structural QC

`check_audible_lanes(edl, requires_audible_output=...)` already distinguishes:

- approved audible content;
- intentional silence;
- required audible lane missing.

Its own contract says PCM inspection remains separate evidence. Preserve that split.

### Existing Renderer verification

A successful `RenderArtifact` already means the Renderer has verified, against canonical EDL/output intent:

- expected resolution;
- expected frame rate;
- required audio-track presence;
- expected duration within the accepted tolerance.

Review must trust this successful execution contract rather than reimplementing those same checks as a competing authority.

### Existing post-render audio evidence

`inspect_pcm16_wav()` already produces deterministic PCM findings for:

- clipping;
- mostly silent output.

The missing production integration is how a rendered output is inspected through a replaceable media-QC seam and how those findings become a Review verdict/correction route.

## Objective

Close the smallest Review/repair product boundary that answers:

1. what exact successful render artifact/EDL revision is under review;
2. how deterministic post-render media evidence is obtained without giving Review render authority;
3. how clipping / unexpected mostly-silent output is represented as typed findings;
4. how intentional silence remains valid rather than being called a defect;
5. how artifact/EDL provenance mismatch fails closed;
6. how PASS versus CORRECTION_REQUIRED versus BLOCKED is expressed;
7. how a correction is routed to the proper existing owner rather than performed inside Review;
8. how a same-EDL technical rerender differs from an editorial re-decision;
9. how repair attempts are bounded and observable rather than recursively self-triggering;
10. how this surface can later be exposed to an ordinary-user product flow.

## Minimum contract to freeze

Subject to implementation-level naming, the production flow should be equivalent to:

```text
ReviewRequest(
  canonical EDL revision,
  successful RenderArtifact,
  output intent / audible intent,
  repair-attempt number
)
→ rendered-media QC port
→ deterministic Review findings
→ ReviewVerdict
```

Verdict semantics must include the equivalent of:

- `PASS` — delivered artifact is accepted by the bounded deterministic checks;
- `CORRECTION_REQUIRED` — evidence identifies an explicit owner to revisit;
- `BLOCKED` — evidence/provenance is insufficient or inconsistent, so automatic acceptance/retry is forbidden.

Exact enum names may differ if existing repository conventions call for better names.

## Correction routing

The minimum route taxonomy must preserve ownership.

### Same-EDL technical rerender

Allowed only when evidence classifies an execution/environment failure that does **not** require a new editorial decision.

Review does not execute the rerender itself. It returns a typed route such as `RERENDER_SAME_EDL` to the renderer/orchestrator boundary.

### Return to editorial owner

Required when correction changes approved content intent, for example a real output audio problem that may require changing an approved AudioMixDecision.

Review returns evidence and an explicit owner route. The correct upstream owner creates a new decision/revision; EDLBuilder then deterministically assembles a new canonical EDL.

Review itself never edits gains/music/voice/source ranges.

### Blocked

Use when:

- `RenderArtifact` does not match the exact EDL revision under review;
- output artifact is missing/uninspectable;
- evidence is contradictory/insufficient;
- repair-attempt policy is exhausted;
- the requested correction has no legitimate owner route.

Fail closed instead of fabricating PASS.

## Bounded retry rule

This Work Order must not implement an autonomous infinite repair loop.

Minimum rule:

- Review request carries an explicit non-negative repair-attempt number;
- automatic/same-EDL retry eligibility is bounded by a small deterministic policy;
- exceeding the bound returns `BLOCKED` / human-or-owner escalation;
- editorial correction always requires a fresh owner decision/revision before a new render can be reviewed.

The exact bound should be a named constant/policy, not hidden recursion.

## Post-render media-QC boundary

Do not make Review shell out to FFmpeg directly if a small replaceable port can own media inspection.

The expected direction is:

```text
Review application owner
→ RenderedMediaQc port
→ FFmpeg/PCM inspection adapter
→ existing inspect_pcm16_wav evidence
```

The adapter may use a temporary PCM extraction as execution detail, but:

- original render is never overwritten;
- temporary files are controlled/cleaned;
- inspection failure is typed;
- PCM thresholds remain deterministic and explicit;
- the adapter does not make editorial decisions.

If code audit during implementation reveals an existing equivalent port, reuse it instead of creating a duplicate.

## Required deterministic evidence

Tests should cover at least the equivalent of:

1. matching EDL + RenderArtifact + clean media evidence → PASS;
2. exact EDL id/revision mismatch → BLOCKED;
3. missing/uninspectable output → BLOCKED;
4. intentional-silence output does not fail only because it has no audible PCM;
5. non-silent intent + mostly-silent rendered output → CORRECTION_REQUIRED with explicit owner route;
6. clipping → CORRECTION_REQUIRED with explicit owner route;
7. inspection/tool failure remains typed and does not become PASS;
8. same-EDL technical retry route cannot mutate EDL;
9. retry bound is enforced;
10. Review exposes no edit/render mutation API;
11. existing audible-lane QC remains pre-render and green;
12. existing Renderer/EDL/Preview living contracts remain green.

Do not manufacture subjective aesthetic scores or fake visual-AI review evidence.

## Real integration evidence

After deterministic gates pass, require one bounded media Engineering Probe through the production Review path using a real rendered MP4 or deterministic real media fixture.

The probe must prove at least:

- clean rendered media can reach Review PASS;
- real post-render audio inspection executes through the production QC adapter;
- one intentionally defective deterministic audio fixture (for example clipping or unexpected silence) produces the expected non-PASS typed verdict;
- no EDL/editorial mutation occurs inside Review.

This is a Review integration probe, not another player/backend benchmark.

## Resource constraint

Approximately **9% Codex quota remains**.

### ChatGPT + GitHub

Primary owner for:

- contract/ownership reduction;
- deterministic application port/use-case work where connector-first remains reliable;
- focused tests;
- CI/probe review;
- governance/validation.

### Codex

**NO ACTIVE RELEASE.**

Release only if the bounded real FFmpeg/PCM Review adapter or multi-file integration becomes materially more efficient through local runtime iteration than connector-first work.

Do not spend Codex on documentation, generic refactors, subjective Review heuristics or UI work.

### User PowerShell

Use only if GitHub-hosted real media evidence cannot represent the required Review boundary or a genuine Human Gate is needed.

## Exit gate

This Work Order is PASS only when:

- one production Review application boundary exists;
- successful `RenderArtifact` provenance is tied to the exact canonical EDL revision under review;
- deterministic post-render QC evidence is integrated through a replaceable execution port;
- PASS / correction-required / blocked semantics are typed;
- correction routes preserve Renderer/EDL/editorial ownership;
- retries are explicitly bounded;
- focused deterministic tests pass;
- repository quality gates pass;
- one bounded real media Review probe passes both clean and intentionally defective cases;
- Review performs no hidden EDL/EditPlan/audio mutation;
- structural progress remains 90% unless ordinary-user Product Gate structure genuinely changes.

## STOP boundary

Do not build a subjective AI video critic.

Do not add aesthetic scoring, recommender loops or generative repair.

Do not let Review mutate canonical EDL or approved editorial decisions.

Do not merge Review into Renderer just because Renderer already has technical verification.

Do not reopen Preview/backend benchmarking.

Do not expand into Environment Doctor, GUI/frontend, SFX-provider expansion, generated music or generic media downloading.

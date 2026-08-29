# Current Work Order

**ID:** R0.12-STAGE-A-FINAL-CLOSURE-002  
**Status:** ACTIVE — FINAL HUMAN GATE PATCH  
**Phase:** R0.12 — Stage-A final closure  
**Mode:** BOUNDED INSTALLED-PRODUCT DEFECT REPAIR + REPLACEMENT RC  
**Superseded Human candidate:** 80ab920b19c1ed1aebef4fa9b7eab05d6a509f38 / 0.1.0  
**Updated:** 2026-08-29

## Objective

Repair only the release blockers exposed by the installed 0.1.0 ordinary-user Human Gate, add minimum release identity/update discoverability for already distributed installations, then build a replacement Windows RC and repeat the final Human Gate.

Do not reopen broad architecture or 2.0 capabilities.

## Human evidence

Planning:

- first run was rejected by factual review for an unsupported portability implication;
- after restart/network recovery, Planning generated successfully;
- treat the rejection as expected safety behavior, not as permission to weaken factual review.

Editing:

- real media understanding and public-music preparation progressed successfully;
- edit decision, retrieval/resolution, EDL/audio/subtitle assembly were reached;
- the installed application repeatedly flashed terminal windows during media/runtime operations;
- rendering/review ended in rerender_same_edl rather than a final deliverable PASS;
- current UI presentation did not expose the underlying renderer diagnostic clearly enough.

## Mandatory patch items

### A. Windows child-process UX

Introduce one reusable Windows process-launch policy for external media/runtime tools.

Requirements:

- FFmpeg/ffprobe and other child CLI processes launched from the windowed GUI must not create visible console windows;
- preserve stdout/stderr capture and exit codes;
- do not use shell=True as a hiding workaround;
- source/dev CLI behavior may remain diagnosable;
- tests must prove Windows no-console flags are applied through the shared helper instead of ad-hoc duplication.

Known affected call sites include media ingest, frame extraction, shot decoding, Renderer and rendered-media QC.

### B. Renderer/review repair contract

Current Review policy permits one rerender_same_edl repair attempt, but the product flow does not execute it.

Requirements:

- when Review returns RERENDER_SAME_EDL, perform exactly one same-EDL rerender using the identical canonical EDL and output spec;
- review the second render with repair_attempt=1;
- never regenerate EditPlan/ResolutionDecision/EDL for this route;
- if the retry fails, surface the exact typed renderer/environment diagnostic and escalate rather than looping.

### C. Source-audio robustness

Reproduce the real render failure against assets with and without audio streams.

The current code records ingest audio_channels but constructs SOURCE_AUDIO for every grounded video selection and validates ORIGINAL voice as if each selection must have source audio.

If reproduction confirms this causes FFmpeg a:0 failures:

- only map source audio where the exact underlying asset actually exposes audio;
- preserve original audio where available;
- allow silent source clips without fabricating audio;
- let approved BGM satisfy audible-output intent when applicable;
- keep canonical evidence explicit and deterministic.

Do not weaken audio provenance or fabricate speech.

### D. Actionable product diagnostics

When render/review cannot deliver:

- distinguish render execution/output-verification failure from post-render QC failure;
- display the underlying typed diagnostic in the desktop result log/dialog;
- do not say rendering completed when no verified RenderArtifact exists;
- keep any real candidate file clearly labelled as candidate/not approved.

### E. Version identity

Establish one authoritative application version source.

Requirements:

- desktop header/about/settings visibly shows version, e.g. v0.1.1;
- installed window may include the version in its title;
- installer AppVersion, installer filename/version resource and desktop runtime version must derive from the same source;
- retain build/source SHA as secondary diagnostic identity, not as the user-facing version;
- add regression tests against version drift.

The replacement patch version must be greater than 0.1.0.

### F. Update discovery

The private source repository is not a valid unauthenticated update endpoint for ordinary users.

Implement a small provider-neutral update manifest/check seam:

- stable-channel manifest is public and contains version, published_at, release notes, download/distribution URL, installer SHA-256 and mandatory/recommended flag;
- startup check is asynchronous/non-blocking and rate-limited/cached;
- provide explicit Check for Updates action;
- if newer version exists, show current → latest and a clear download/update action;
- network/manifest failure must never block Planning or Editing;
- no API keys or GitHub repository credentials may be embedded in the app.

Silent background installation, delta patching and rollback machinery are not required here.

## Verification

Before a new installer is offered to the Product Owner:

1. focused unit/regression tests for A–F;
2. full repository quality gate;
3. Windows packaged GUI smoke;
4. real child-process no-console probe;
5. representative render with a mixture of source clips with and without audio, if supported by fixtures;
6. same-EDL retry regression proving one bounded retry;
7. replacement Windows Release Candidate workflow;
8. Planning-only → Full upgrade from installed 0.1.0 where practical;
9. same-version repair/uninstall/Workspace preservation.

## Final Human Gate

Install the replacement version as an ordinary user and verify:

- visible version identity;
- update-discovery UI is understandable and non-blocking;
- no terminal windows flash during normal Editing;
- representative Planning succeeds without weakening factual safety;
- representative real-footage Editing produces an approved final MP4;
- actionable diagnostics appear if a deliberate failure is induced;
- upgrade/uninstall preserve Workspace and original media.

## Exit condition

Only after the replacement installer passes engineering verification and the Product Owner's ordinary-user Human Gate:

- record exact source SHA, version, workflow run, installer SHA-256 and update-manifest identity;
- set all Stage-A product gates to PASS;
- move structural progress 95% → 100%;
- close this work order.

Do not polish unrelated backlog items before closure.

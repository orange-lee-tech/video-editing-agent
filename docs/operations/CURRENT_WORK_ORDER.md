# Current Work Order

**ID:** `R0.12-PRODUCTION-PREVIEW-INTEGRATION-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Production GStreamer Preview integration behind the accepted PreviewBackend seam  
**Mode:** PRODUCT INTEGRATION / CODE-AUDIT FIRST  
**Accepted production-code baseline:** `72ec275c1e72e876c4bcf828a44e7852208bab29`  
**Activated:** 2026-08-17  
**Codex release:** NO

## Previous Work Order result

`R0.12-PUBLIC-MUSIC-ACQUISITION-001` — **PASS / CLOSED**.

Accepted production baseline:

`72ec275c1e72e876c4bcf828a44e7852208bab29`

Deterministic quality-gate baseline:

`97c9ba838b169a99fb50deb0aa13029209592dff`

Real provider evidence:

- live Windows run `32026331114` — PASS;
- validation: `docs/validation/R0.12_PUBLIC_MUSIC_ACQUISITION_EVIDENCE.md`;
- real route: Openverse discovery → Wikimedia current rights verification → bounded single-item acquisition → ffprobe → `provider_acquired_audio + music` Asset;
- no Codex release used.

## Why this work exists

ADR-010 already closed the Preview backend-family decision. The product does **not** need another player benchmark.

The remaining Stage-A gap is production integration of the selected GStreamer family through the replaceable Preview boundary so an application/product surface can initialize playback, load media, control position and expose diagnosable degraded behavior without stealing authority from canonical EDL or Renderer.

Accepted ADR:

`docs/adr/ADR-010_GSTREAMER_PRIMARY_PREVIEW_BACKEND.md`

## Frozen ownership

The following invariants are non-negotiable:

```text
canonical EDL  = sole exact executable timeline authority
Renderer       = final render/execution authority
PreviewBackend = playback-only adapter
GStreamer      = selected Stage-A implementation family behind that adapter
```

Preview may display/play requested media/timeline state. It may not repair, reinterpret, retime or silently replace canonical EDL decisions.

Do not redesign EditPlan, EDL, Renderer, Music, Proxy or Planning ownership merely to fit GStreamer.

## Accepted backend decision

Stage-A primary Preview family is GStreamer.

Accepted integration direction from ADR-010:

- GStreamer 1.28.6 Windows x86_64 MSVC private runtime is the initial evidence baseline;
- high-level GstPlay/playbin3 control surface;
- normal path permits supported D3D11 decode/presentation autoplugging;
- explicit software video-decode fallback remains supported;
- runtime/capability failure must be diagnosable;
- application/private runtime is preferred over arbitrary user-global installation;
- libVLC remains an alternative adapter, not a default dual-bundled fallback;
- libmpv remains Stage-A hard-gate excluded;
- no further backend-family benchmark is authorized without a concrete Product Probe failure/new hard requirement.

## Objective

Close the smallest production Preview integration boundary that answers:

1. what Preview port/application surface already exists and what is actually missing;
2. how one GStreamer adapter owns initialize/load/play/pause/seek/stop/release behavior;
3. how requested timeline/media positions are expressed without creating a second time authority;
4. how normal hardware-capable playback and explicit software-decode fallback are selected and diagnosed;
5. how missing/private-runtime/plugin/device failures become typed application diagnostics;
6. how lifecycle/release is deterministic and idempotent enough for an ordinary application session;
7. how the selected private-runtime location is supplied without assuming global PATH;
8. which deployment/runtime manifest concerns belong here versus the later Windows Environment Doctor boundary;
9. what focused deterministic tests and one bounded real Windows integration probe are required.

## First action — code audit, not implementation guesswork

ChatGPT + GitHub must first inspect:

- existing `PreviewBackend` / preview-related application ports;
- existing preview adapters or probe-only code;
- current time/seek types and canonical EDL boundary;
- current runtime/configuration composition seams;
- accepted GStreamer benchmark/probe code that may be reusable without importing benchmark authority into production;
- tests/import contracts around application ↔ provider/infrastructure ownership.

Only after that audit freeze the minimum production edit.

Do not create a new Preview API when an existing seam already expresses the needed contract.

## Minimum expected production behavior

Subject to the code audit, the production adapter should cover the smallest coherent lifecycle:

```text
initialize selected private runtime
→ create playback session
→ load approved local media
→ play / pause
→ absolute seek requested by application
→ report state / position / typed failure
→ stop / release cleanly
```

Where the existing Preview port already defines different names/shapes, preserve it rather than forcing this pseudocode literally.

## Degraded behavior

The accepted fallback semantics are:

1. normal high-level GStreamer path first;
2. hardware decode/presentation may autoplug where valid;
3. when hardware video decode is explicitly disabled or proven defective, permit a diagnosable software video-decode route;
4. do not pretend software decode means all GPU presentation must be disabled;
5. initialization/playback failure is surfaced, not hidden by EDL/media rewriting.

No silent automatic switch to libVLC is part of Stage A.

## Runtime / deployment boundary

This Work Order may define and integrate the production adapter's private-runtime lookup/configuration contract.

It must **not** expand into the full ordinary-user Environment Doctor/product installer boundary unless required to prove the adapter can be invoked. Full missing-runtime repair UX, installer orchestration and host-health guidance remain a later dedicated productization boundary.

Preserve:

- exact runtime provenance/version evidence;
- controlled plugin/runtime surface;
- LGPL/notices obligations;
- no assumption that arbitrary GStreamer is already installed globally.

## Required deterministic evidence

After the code audit freezes the actual port shape, tests should cover at least the equivalent of:

- initialization success/failure;
- local-media load ownership;
- play/pause state transitions;
- absolute seek forwarding without retiming/reinterpretation;
- stop/release lifecycle;
- double release/idempotent cleanup where the port promises it;
- missing runtime/plugin typed diagnostics;
- explicit software-decode fallback configuration;
- no Preview authority to modify canonical EDL;
- existing Renderer/EDL smoke remains green.

Do not manufacture tests for APIs that the repository does not actually need.

## Real integration evidence

After deterministic gates pass, require one bounded Windows Engineering Probe against the selected private GStreamer runtime that proves the production adapter—not only benchmark scripts—can:

- initialize;
- load a deterministic/local fixture;
- play/pause;
- perform absolute seek;
- release cleanly;
- expose which normal/degraded route was used sufficiently for diagnostics.

Existing benchmark evidence may be reused as setup/provenance input, but it cannot substitute for executing the new production adapter.

## Resource constraint

Approximately **9% Codex quota remains**.

### ChatGPT + GitHub

Primary owner initially for:

- repository/code audit;
- contract reduction;
- deterministic small edits where connector-first work remains reliable;
- tests/governance/validation;
- reviewing CI and real probe evidence.

### Codex

**NO ACTIVE RELEASE.**

Release only if the code audit proves the bounded production adapter requires local Windows/runtime/multi-file iteration that is materially more efficient through Codex than connector-first work.

Do not spend Codex on renewed GStreamer/libVLC/libmpv comparison, docs, or benchmark archaeology.

### User PowerShell

Use only if GitHub-hosted Windows evidence cannot represent the required real private-runtime/product-adapter behavior or a Human Gate is genuinely needed.

## Exit gate

This Work Order is PASS only when:

- the existing Preview seam is identified and preserved or minimally corrected;
- one production GStreamer adapter exists behind that seam;
- lifecycle and typed diagnostics are deterministic;
- normal and explicit software-decode configuration semantics are represented without timeline-authority leakage;
- focused deterministic tests pass;
- repository quality gates pass;
- one bounded real Windows probe executes the **production adapter** successfully;
- no backend-family benchmark is reopened;
- no silent dual-runtime fallback is introduced;
- structural progress remains 90% unless ordinary-user Product Gate structure genuinely changes.

## STOP boundary

Do not start another player benchmark.

Do not bundle GStreamer + libVLC by default.

Do not reopen libmpv Stage-A hard-gate exclusion absent a new hard requirement.

Do not expand into full Environment Doctor, GUI/frontend, Proxy redesign, SFX-provider work or generated-music integration.

Do not let Preview become EDL or final-render authority.

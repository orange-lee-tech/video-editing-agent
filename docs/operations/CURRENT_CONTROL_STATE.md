# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-15
current_phase: R0.12
phase_state: PRODUCT_IMPLEMENTATION_SUBTITLE_AUDIT_GUARD
active_work_order: R0.12-SUBTITLE-001
accepted_code_baseline: 9f06386f9f311fe241f250f4679fa6b2042699b0
candidate_code_baseline: 12e4049c53a9597fba2a6654701d779d496b9433
control_plane_baseline: 1012f239aa95899e914ba6091c3b825dfc6302fe
previous_work_order: R0.12-SMOKE-001
previous_work_order_result: PASS
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Routing truth

`R0.12-SMOKE-001` remains the latest fully accepted code baseline at `9f06386f9f311fe241f250f4679fa6b2042699b0`.

`12e4049c53a9597fba2a6654701d779d496b9433` is a strong `R0.12-SUBTITLE-001` implementation candidate. Independent GitHub review confirms one bounded fast-forward commit, remote `ci/quality-gate-diagnostic` success, structured subtitle cue payloads in canonical EDL, v3 deterministic serialization with v2 backward read support, fail-closed subtitle validation, deterministic ASS/libass burn-in, English/Chinese region-pixel evidence, and the existing living Resolver → EDLBuilder → Renderer smoke remaining green.

The candidate is **not yet recorded as a fully accepted subtitle baseline** because independent review found two execution-authority guards that must be resolved before closure:

1. the ASS writer currently converts exact rational `MediaTime` to centiseconds with `round(time * 100)`, so cue times outside the ASS centisecond grid are silently retimed even though the work order requires Renderer not to retime canonical EDL cues;
2. canonical EDL may contain multiple SUBTITLE tracks/layers, while the baseline ASS writer flattens all subtitle cues into the same ASS `Layer 0`; the baseline must either preserve an explicitly supported layer mapping or fail closed on unsupported multi-track subtitle semantics.

A smaller verification gap also remains: the live probe proves a final output filename containing comma/apostrophe works, but the generated ASS filter path itself does not contain those punctuation characters. If path escaping is retained as a claimed gate, exercise punctuation in the actual subtitle-artifact parent path rather than only the output filename.

The multilingual probe correctly does **not** claim semantic Chinese glyph correctness without OCR/Human Gate and does not redistribute a font. That limitation is not a current structural blocker.

## Information economy rule

Normal Codex work starts from foreman L0. Open secondary context only when a concrete trigger occurs.

- code location unclear -> `location`;
- architecture/ownership ambiguity -> `architecture`;
- test failure -> `quality`;
- Git state issue -> `git`;
- license/provider uncertainty -> `external`;
- destructive/high-risk operation -> `high-risk`.

Do not preload unrelated CAPs, project history or broad repository surfaces.

## Current gate

Hold `R0.12-SUBTITLE-001` at its existing boundary. Do not advance into Graphics, transitions, Preview, Proxy/cache or later R0.12 work until the subtitle execution-authority guards above are explicitly resolved and reverified.

No new downstream work order is active. Resume only on a new Product Owner instruction; when resumed, finish this existing subtitle work order rather than opening a speculative new subsystem.

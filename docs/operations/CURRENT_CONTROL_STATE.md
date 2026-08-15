# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-15
current_phase: R0.12
phase_state: PRODUCT_IMPLEMENTATION_STRUCTURED_SUBTITLE
active_work_order: R0.12-SUBTITLE-001
accepted_code_baseline: 9f06386f9f311fe241f250f4679fa6b2042699b0
control_plane_baseline: 1012f239aa95899e914ba6091c3b825dfc6302fe
previous_work_order: R0.12-SMOKE-001
previous_work_order_result: PASS
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Routing truth

`R0.12-SMOKE-001` is accepted after independent GitHub review. Baseline `9f06386f9f311fe241f250f4679fa6b2042699b0` runs the actual deterministic Resolver/optimizer, feeds its selected grounded source ranges into `DeterministicEDLBuilder`, renders the resulting canonical EDL through `FFmpegEDLRenderer`, and verifies the produced MP4 with ffprobe plus final-frame pixel sampling. Remote `ci/quality-gate-diagnostic` is green.

The living smoke proves actual selected ranges survive Resolver → EDLBuilder → Renderer, exact two-segment order survives into the final image, PRESERVE audio remains audible/present, and no fake spatial decision is introduced. It remains controlled Engineering Probe evidence, not R0.16 one-click Product Probe evidence.

Do not expand EDL/Renderer internals speculatively. A minimal EDL extension is permitted only where the next execution feature cannot be represented without violating EDL timeline authority. Structured subtitle execution is such a concrete blocker because the current EDL has a subtitle track family but no canonical cue text/style/layout execution payload.

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

Execute `R0.12-SUBTITLE-001` only: establish one complete deterministic structured-caption path from approved subtitle cues through canonical EDL execution semantics to ASS/libass/FFmpeg burn-in, including exact rational timing, safe-zone/layout intent, bounded keyword emphasis, deterministic serialization/validation, multilingual engineering coverage, and fail-closed escaping/path behavior.

Do not begin Graphics, Preview, Proxy/cache, transition expansion, hardware routing, packaging, UI, ASR rewriting/translation or broad caption-style polish in the same batch.

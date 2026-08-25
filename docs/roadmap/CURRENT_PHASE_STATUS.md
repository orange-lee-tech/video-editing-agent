# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 95%  
**Current phase:** R0.12 — Stage-A final Product/Human Gate  
**Engineering state:** STAGE_A_FINAL_PRODUCT_HUMAN_GATE_ACTIVE  
**Updated:** 2026-08-25

## Progress truth

Structural percentage measures real ordinary-user end-to-end usability, not module/test/UI count.

Hard 100% contract:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Current gates:

- Planning Product/Human Gate: PASS on the supported Stage-A surface.
- local reference video: supported.
- remote reference URL: deliberately deferred to 2.0; not a 1.0 blocker.
- Editing no-speech Human baseline: PASS with real final MP4, source audio and rights-safe BGM.
- Project Workspace / desktop UX: ACCEPTED / MERGED in PR #17.
- Windows packaging foundation: ACCEPTED / MERGED in PR #19.
- exact Windows runtime payload closure: ACCEPTED / MERGED in PR #20.
- final ordinary-user packaged Human Gate: ACTIVE.
- speech-bearing original voice + trusted subtitles: Human evidence OPEN.
- Stage-A completion gate: OPEN.

Therefore progress remains **95%**, not 100%.

## Accepted engineering baseline

Current accepted production-code main:

`c2c959239cf8842388ac661777c19f20f64a6a90`

PR #20 exact implementation head:

`e22cb3cb96ba13414cff7d13deaa15a647bd8542`

The runtime payload closure is now proven on a clean GitHub-hosted Windows environment with exact CPython 3.12.13:

```text
exact/hash-locked runtime inputs
→ LGPL-only FFmpeg/ffprobe
→ TransNetV2 + CPU Torch + package weights
→ faster-whisper + native runtime + exact local model
→ deterministic Windows x64 onedir
→ manifest/static inspection
→ packaged Doctor
→ real FFmpeg/TransNet/ASR runtime probe
→ GUI launcher
→ external Project Workspace smoke
→ SHA-addressed artifact upload
```

Final main artifact:

`VideoEditingAgent-windows-x64-c2c959239cf8842388ac661777c19f20f64a6a90`

GitHub digest:

`sha256:a21a71211c0bee6848f93852d2f4cf6d27cd194b89f92a1fed6e4c24ccd57d5d`

Compressed size: `768923438` bytes.

The large unpacked footprint is a post-Stage-A optimization concern, not authority to remove retained 1.0 capabilities. Installer/onefile/signing/updater work remains later release-readiness work.

## What remains before effective 100%

No new engineering wave is planned by default.

The remaining work is one consolidated ordinary-user Human Gate on the accepted packaged application:

### A. Ordinary launcher / configuration / Workspace

- launch the packaged EXE without repository/Python/uv/Git setup;
- configure DeepSeek plus the chosen Gemini/OpenAI visual provider through the GUI;
- create/select an external Project Workspace;
- verify outputs and writable state remain outside the install tree;
- verify progress/errors are understandable.

### B. Planning-only retained product path

Use the GUI to provide a normal planning brief and run the supported Planning workflow. Confirm an inspectable/persisted ScriptPlan and ShootingPlan are produced without editing repository files.

### C. Editing-only retained speech path

Use a short real local video with clear single-speaker original speech and run Editing-only with Planning enrichment disabled. Confirm:

- real final MP4 exists at the selected output;
- original/source speech remains audible;
- subtitles are grounded in the actual speech and timing is acceptably aligned;
- BGM does not destroy speech intelligibility;
- originals remain untouched;
- no fabricated transcript/subtitle content appears.

### D. Combined semantics

With a valid Planning result in the same Project Workspace/session, enable the ordinary Planning-enrichment control and run a short Combined edit. Confirm the path works and that Planning remains optional enrichment rather than an activation license.

### E. Closure evidence

Record exact artifact/main SHA, Windows machine class, provider choices, resulting output paths and concise Human PASS/FAIL observations.

If all of A–E pass, Core 2 may become PASS and Stage-A may move directly from 95% to 100%. If one check fails, reopen only the narrow implementation defect demonstrated by that failure; do not invent a new broad phase.

## Active Work Order

`R0.12-STAGE-A-FINAL-CLOSURE-002`

# Current Work Order

**ID:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Status:** ACTIVE  
**Phase:** R0.12 — Stage-A final closure  
**Mode:** FINAL SOURCE CONSOLIDATION + WINDOWS RELEASE DELIVERY  
**Accepted engineering foundation:** `c2c959239cf8842388ac661777c19f20f64a6a90`  
**Current remote main:** `153a7686aef3700c2a992542884a33dc135225cc`  
**Updated:** 2026-08-26  
**Codex release:** CLOSED until current local focused repair is preserved/accepted

## Objective

Reach truthful Stage-A / 1.0 closure by preserving the already demonstrated visual-first Editing repair, hardening Planning output quality, removing misleading unfinished UI, and delivering the stabilized Windows product through a guided `Setup.exe` installation path rather than a raw large ZIP.

This is the final closure boundary, not a new broad architecture wave.

## Latest Product/Human Gate truth

The Product Owner tested a focused local patch based on remote main `153a7686...`.

### A. Planning factual safety — MECHANICALLY RECOVERED, QUALITY STILL OPEN

The focused local recovery completed the previously failing 350 ml scenario without allowing unsupported bag-fit / one-hand-operability claims to escape the semantic reviewer.

However the resulting plan was too weak for release quality:

- hook was generic;
- authoritative fact text was repeated across multiple sections;
- visual plan collapsed toward static product views;
- closing lacked useful role-specific value;
- ShootingPlan guidance was technically executable but too sparse for an ordinary user and did not exploit alternate/backup coverage well enough.

Required repair direction:

- do not weaken factual/commercial review;
- keep conservative deterministic recovery bounded to unsupported-claim cases;
- make fallback section-role aware rather than duplicating the same fact into demonstration/closing;
- deduplicate repeated authoritative copy;
- preserve commercial/narrative usefulness using only truthful non-claim framing;
- strengthen ShootingPlan practicality: clear shot purpose, framing/motion, duration/handles, equipment-aware instruction, alternate/backup coverage and ordinary-user language;
- quality improvement must still pass independent factual review before commit.

Planning has no acceptable excuse for shallow output merely because its provider call succeeded.

### B. Editing visual-first core — LOCAL HUMAN PASS, SOURCE ACCEPTANCE PENDING

The real local Human Gate now proves both Chinese-speaking and English-speaking source footage can complete the visual-first automatic path:

`local footage → understanding → Director → Resolver → EDL → render/review → final output`

The earlier false missing-coverage failure was traced to a cross-language lexical retrieval defect: English visual evidence was being searched with Chinese-only `semantic_query` values. The focused local repair aligned the internal retrieval language with footage evidence and the real workflow completed.

Current Product Owner judgment: ignoring source-speech continuity, the core automatic visual editing capability is effectively present. Cut-point/editorial quality can improve later, but the product must not distort 1.0 scope by turning sentence preservation into the primary video-cut authority.

### C. Speech continuity / multilingual voice production — DEFERRED TO 2.0

The Product Owner explicitly decided that the correct long-term solution is a dual-track design where visual editing authority and reconstructed/dialogue/narration audio can be handled independently.

The following are therefore **not 1.0 blockers**:

- advanced source-speech / ambience separation;
- sentence-preserving dialogue reconstruction after visual cuts;
- multilingual transcript translation;
- translated or bilingual subtitle production;
- cross-language narration / TTS;
- speaker-aware subtitle and narration systems.

These belong to the existing 2.0 advanced-audio backlog. Preserve replaceable seams, but do not expose unfinished controls in the ordinary 1.0 UI.

Original source audio may remain a deterministic pass-through option where already implemented, but 1.0 must not claim speech-continuity reconstruction.

### D. Provider transient failure — SMALL ROBUSTNESS DEFECT

A real English run hit Gemini HTTP 429 with an explicit provider retry delay, then succeeded when retried later. The transport already classifies 429 as transient and parses retry guidance. Before release, the ordinary workflow should consume that bounded retry information instead of immediately failing the whole job on the first provider-directed wait.

No unbounded retry loops.

### E. UI configuration cleanup — REQUIRED BEFORE INSTALLER FREEZE

Remove the current select-scope-then-import interaction for Form/Director configuration versus API/provider configuration.

Use direct independent actions instead, e.g. dedicated Form/Director Import and API Import controls (and coherent separate save/export/delete ownership where the same menu is retained). Do not make the user tick scope checkboxes before performing an obvious configuration action.

Unfinished speech/subtitle translation/TTS controls must remain hidden in 1.0.

## Repair-loop protocol — mandatory

1. Preserve the Product Owner's current dirty local repair; no blind reset/clean/stash.
2. No full Windows package per small source repair.
3. Complete the smallest coherent final source patch: Planning quality + UI cleanup + bounded provider wait robustness, without reopening deferred 2.0 audio work.
4. Run targeted tests, then the canonical full repository quality gate.
5. Commit/push only after the focused local work is preserved and verified.
6. Run ordinary CI on the accepted source SHA.
7. Only then build a new release-candidate staging tree and `Setup.exe`.
8. Final Human Gate uses the installer-produced ordinary product, not `uv run` or an extracted engineering ZIP.

## Windows delivery / installer boundary — ACTIVE MAINLINE

The Product Owner requires a guided Windows `Setup.exe` experience.

The release solution must provide:

- install, upgrade/repair and uninstall;
- license/agreement page where applicable;
- understandable installation path;
- selectable desktop shortcut;
- finish-page launch option;
- safe detection/handling of existing application-owned components;
- explicit consent before destructive replacement/reconfiguration;
- no arbitrary system Python/FFmpeg/PATH mutation by default;
- Project Workspaces, Profiles and original media outside the install tree and preserved across update/uninstall;
- capability-oriented delivery so Planning-only users are not forced to install heavy Editing components.

Preferred implementation order remains:

1. **Inno Setup 7.1** as the primary guided `Setup.exe` candidate, subject to its licensing/commercial-use policy;
2. **NSIS Modern UI 2** as the permissive fallback;
3. Velopack only if a whole install/update stack with delta/self-update is deliberately chosen;
4. WiX/Burn only if prerequisite chaining justifies the added complexity.

Do not combine installer stacks without a concrete requirement.

## 1.0 runtime decomposition target

The default 1.0 installer should distinguish at least:

- **Core App / Planning:** GUI, application code, private CPython/Tcl/Tk, profiles/Workspace, Planning/Director cloud adapters;
- **Media Runtime:** FFmpeg/ffprobe;
- **Scene Detection Runtime:** TransNet + CPU Torch + reviewed weights.

The previously proven Speech Runtime (`faster-whisper` + CTranslate2/PyAV + pinned model) remains valid engineering evidence but is no longer a default 1.0 payload requirement after the Product Owner's 2026-08-26 scope decision. Keep its locked dependency/provenance work for 2.0 rather than shipping hundreds of unnecessary MB in the 1.0 default installer.

Local-reference-video analysis and automatic Editing may require Media + Scene components; Planning without media analysis may remain Core-only.

## Permanent invariants

- preserve replaceable adapters and canonical Domain/EDL/Renderer authority;
- visual-first 1.0 editing decisions remain grounded in user-local visual evidence;
- no public/web/generated visual fallback for missing user footage;
- no plaintext provider secrets in install/project/log artifacts;
- keep source media immutable;
- keep user Projects/Profiles/outputs outside application installation ownership;
- retain CPU-capable ordinary baseline;
- destructive environment actions require explicit user consent;
- unfinished/deferred capabilities remain hidden rather than cosmetically exposed;
- Remote Reference URL remains deferred to 2.0.

## Exit gates

This work order closes only when:

1. Planning-only passes the real factual-safety case **and** meets ordinary-user ScriptPlan/ShootingPlan quality expectations;
2. the focused cross-language Editing repair is accepted on a real GitHub SHA and Chinese/English visual-first Editing remains functional;
3. Combined semantics remain independently usable;
4. 1.0 UI does not expose unfinished Remote URL / advanced speech / translated-subtitle / TTS controls and configuration actions are simplified;
5. transient provider quota/wait behavior is bounded and understandable;
6. final Windows ordinary delivery is a tested guided `Setup.exe` flow with install/update-or-repair/uninstall and Workspace/Profile/original preservation;
7. exact final candidate identity and durable Human evidence are recorded.

Structural progress remains **95%** until those gates pass.

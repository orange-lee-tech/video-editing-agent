# Current Work Order

**ID:** `R0.12-SMOKE-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — living cross-phase integration smoke  
**Owner/writer:** Codex

## Objective

Create a durable low-cost integration smoke that uses actual Resolver/optimizer output, assembles it through the canonical EDLBuilder, renders it through the EDL-driven FFmpeg Renderer, and verifies the resulting MP4 so cross-phase contract drift is caught long before R0.16.

## Read

1. `tools/probes/r0_9b_resolver_live.py`
2. `tools/probes/r0_12_edl_renderer_live.py`
3. `src/video_editing_agent/application/edl_builder.py`
4. `docs/roadmap/ROADMAP_V2.md`

Use foreman trigger `location` only if the exact current Resolver/optimizer or fixture-media interfaces are unclear. Use `architecture` only for a genuine ownership ambiguity. Use `quality` only after a concrete verification failure.

## Required delta

- Build one bounded reusable Engineering Probe path in which the existing deterministic Resolver/optimizer implementation produces `ResolutionDecision` / `ResolvedSelection` from grounded `CandidateWindow` inputs. Do not hand-author the final selected source ranges merely to satisfy the downstream path.
- Feed those actual Resolver outputs into `DeterministicEDLBuilder`, with authoritative synthetic/local Shot/Asset mapping, then feed the resulting canonical EDL into `FFmpegEDLRenderer`.
- Produce a real ignored/private MP4 and verify it with ffprobe. Assert that Resolver-selected source windows and deterministic ordering survive unchanged through EDL timeline allocation and final render duration/order.
- Preserve at least one observable current audio-policy case through the chain. Carry spatial execution when an already-approved decision is available naturally; do not invent a ReframeDecision just to make the gate look richer.
- Add bounded final-output visual evidence for spatial execution if it can be done deterministically and cheaply with generated fixture media. If not, keep the existing filter-semantic check and record the precise remaining evidence limitation rather than expanding the batch.
- Keep this probe cheap enough to remain a living regression route as later R0.12/R0.13/R0.16 layers are attached. It is Engineering Probe evidence, not a Product Probe and not a claim of finished one-click orchestration.
- Do not substitute human-confirmed coverage text for automatic visual understanding and do not fake a VisualUnderstanding stage. This smoke may start from grounded Resolver candidates; the actual VisualUnderstanding → Retrieval/Resolver requirement remains an explicit R0.16 integration gate.
- Minimally update the existing R0.16 section of `docs/roadmap/ROADMAP_V2.md` to encode the four already-approved structural integration constraints already summarized in `docs/roadmap/README.md`: actual VisualUnderstanding in the one-click chain; concrete rights-aware music acquisition when visual-only input promises automatic BGM; a bounded Stage-A editing-expression/effects floor without a monolithic Effects Engine; and downstream speech/temporal/music/subtitle/transition evidence feeding back into the final Reference/B爆款 → Script Product Probe. Do not create a new roadmap or governance system.
- Repository hygiene: delete remote temporary branches `tmp-renderer-nav-sync`, `tmp-renderer-nav-sync-2`, `tmp-renderer-nav-sync-3`, `tmp-renderer-nav-sync-4`, and `tmp-renderer-nav-sync-5` after syncing `main`; they were created during the navigation-sync write path and contain no product work.
- Add focused deterministic tests only where the reusable smoke plumbing needs regression coverage, then run the full repository Quality Gate.

## Hard boundaries

- Resolver owns grounded source selection; EDLBuilder owns exact timeline assembly; EDL remains sole executable timeline authority; Renderer only executes it.
- No human-authored final selection masquerading as Resolver output.
- No Renderer or EDL creative repair/fallback.
- No automatic stock/generative visual fallback.
- Do not build a workflow/orchestration framework merely for this smoke.
- Do not claim R0.16 one-click completeness or Product Probe success from controlled synthetic/local fixtures.
- Do not implement Subtitle, Graphics, Preview, Proxy/cache, hardware routing, packaging or UI in this batch.

## Verification

Run the living smoke with actual Resolver → EDLBuilder → Renderer → ffprobe execution, any focused tests, then the repository full Quality Gate. Preserve import contracts and `git diff --check`.

## Stop gate

Stop after the living integration smoke is reproducible and green, the R0.16 hard constraints are minimally synchronized into Roadmap V2, temporary navigation-sync branches are deleted, required checks are green, changes are committed/pushed, and the working tree is clean. Do not continue into Subtitle/Graphics/Preview/Proxy work.

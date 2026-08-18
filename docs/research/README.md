# Research Archive

**Status:** Survey V2 archive — CLOSED  
**Authority:** Informative, not normative  
**Normative authority:** `docs/product/PRODUCT_CONSTITUTION_V1.0.md` and compatible Architecture Contracts

This directory preserves high-value research conclusions so engineering work does not depend on recovering details from a long chat history.

Research notes here MAY be revised, split, superseded, or rejected after further source review and real benchmarks. A research conclusion does not become architecture merely because it is documented here.

## Current documents

- `OPEN_SOURCE_CAPABILITY_SURVEY_V2.md` — capability-by-capability upstream working map, reuse posture, licensing/deployment risks and the research state before final closure.
- `AI_EDITING_CORE_MECHANISM.md` — Director → retrieval → evidence escalation → anchors → Resolver → EDL → review, with explicit cost-control principles.
- `LOCAL_TOOLBOX_AND_DEPLOYMENT.md` — local-first execution, optional GPU acceleration, Environment Doctor, proxy/cache strategy, Windows runtime guidance and user installation assistance principles.
- `RESOLVER_RETRIEVAL_AND_TIMING_OPTIMIZER.md` — hybrid Shot retrieval, multilingual embeddings, temporal anchors, Resolver scoring, elastic beat/action alignment and deterministic beam-search / DP timing optimization.
- `VISUAL_EVENT_ANCHOR_GENERATION.md` — camera-motion compensation, residual/local motion, ROI tracking, coarse-to-fine action timing, anchor confidence and targeted VLM escalation.
- `RESOLVER_SCORE_AND_COMMERCIAL_SKILLS.md` — versioned scoring policy, commercial/Vlog skill separation, platform-prior provenance, human preference calibration, user overlays, uncertainty and review rubrics.
- `SURVEY_V2_CLOSURE_GAP_AUDIT.md` — historical closure audit that identified the final two unresolved product-wide Survey domains. **Superseded for closure status by `SURVEY_V2_FINAL_CLOSURE.md`.**
- `AUDIO_EDITORIAL_MUSIC_SELECTION_RIGHTS.md` — focused Survey closure for rights-aware music discovery, semantic/temporal music selection, music moment localization, deterministic audio editing/mixing and license evidence.
- `AUTO_REFRAME_ASPECT_RATIO_COMPOSITION.md` — focused Survey closure for aspect-ratio transformation, semantic subject/product framing, smooth deterministic crop-path optimization, safe zones and non-generative fallbacks.
- `SURVEY_V2_FINAL_CLOSURE.md` — final product-wide closure gate. **Current verdict: Survey V2 CLOSED.**
- `DESKTOP_PRODUCT_UI_REFERENCE_REVIEW_2026-08-19.md` — post-Survey focused product-shell research using official ttk/ttkbootstrap/CustomTkinter/Kdenlive/LosslessCut sources; extracts UI/layout/DPI/packaging ideas without reopening core capability Survey V2 or authorizing a framework migration.

## Current closure posture

Broad open-ended ecosystem exploration is finished.

Both focused blockers from the earlier Gap Audit are now closed for architecture design:

1. Audio Editorial / Music Selection & Rights — PASS;
2. Auto Reframe / Aspect-Ratio Composition — PASS.

The project should now transition to:

```text
Architecture Contract v0.2
        ↓
Product Constitution clarification/amendment only if truly required
        ↓
Capability Specifications
        ↓
ADRs
        ↓
Upstream Ledger / Policy V2
        ↓
Roadmap V2
        ↓
implementation
```

Do not reopen Survey V2 merely because a benchmark parameter, model/provider winner, release license approval or implementation detail remains undecided. Those belong to the architecture/specification/benchmark/release process unless a genuinely new major capability is introduced.

Focused research notes about **implementation presentation, packaging or a bounded new dependency** may still be added when they help an active Work Order. They do not reactivate broad Survey V2 by themselves.

## Research discipline retained after closure

For every future major capability or meaningful new dependency:

1. check whether the existing capability seam already covers it;
2. survey several mature repositories / papers / official implementations when a genuinely new capability requires it;
3. separate source-code license from model-weight/data/license constraints;
4. distinguish direct reuse, adaptation, independent reimplementation and idea-only reference;
5. evaluate Windows deployment and CPU-only behavior rather than assuming a GPU;
6. prefer real product benchmarks over README claims;
7. preserve important new evidence before it becomes difficult to recover;
8. promote only stable conclusions into Architecture Contracts, Capability Specs, ADRs, the Upstream Ledger and Roadmap.

## Constitution-first neutralization rule

An upstream can be useful while its product behavior is incompatible with this repository.

When that happens:

```text
useful idea
→ extract algorithm / architecture / benchmark principle
→ remove unconstitutional source acquisition / generation / authority behavior
→ independently adapt or reimplement behind our contracts
```

Examples include remote visual-stock fallback, default generated visual content, generative uncrop/outpainting, or an upstream agent directly owning the timeline.

The Product Constitution always wins over historical research or Architecture Contract text.

## Status vocabulary

- **DIRECT-CANDIDATE** — potentially suitable for direct adaptation/integration after complete dependency/license verification.
- **REFERENCE-STRONG** — strong architectural/algorithmic reference; reimplement or adapt behind local contracts.
- **REFERENCE-ONLY** — useful ideas, but license/product mismatch or technical weight makes direct reuse unattractive.
- **BLOCKED-PENDING-REVIEW** — promising but cannot be approved before dependency/model/license or benchmark review.
- **FOCUSED SURVEY PASS** — capability family is sufficiently understood for architecture/specification work; implementation choices remain evidence-gated.

No status in this directory is a legal opinion or final dependency approval.

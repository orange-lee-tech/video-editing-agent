# Research Archive

**Status:** Working research archive  
**Authority:** Informative, not normative  
**Normative authority:** `docs/product/PRODUCT_CONSTITUTION_V1.0.md` and compatible Architecture Contracts

This directory preserves high-value research conclusions before implementation begins. It exists so later
engineering work does not depend on recovering details from a long chat history.

Research notes here MAY be revised, split, superseded, or rejected after further source review and real
benchmarks. A research conclusion does not become architecture merely because it is documented here.

## Current documents

- `OPEN_SOURCE_CAPABILITY_SURVEY_V2.md` — capability-by-capability upstream map, current reuse posture,
  licensing/deployment risks, and unresolved survey work.
- `AI_EDITING_CORE_MECHANISM.md` — current best model for Director → retrieval → evidence escalation →
  anchors → Resolver → EDL → review, with explicit cost-control principles.
- `LOCAL_TOOLBOX_AND_DEPLOYMENT.md` — local-first execution, optional GPU acceleration, environment doctor,
  proxy/cache strategy, Windows runtime guidance, and user installation assistance principles.

## Research discipline

For each major capability:

1. survey several mature repositories / papers / official implementations;
2. separate source-code license from model-weight/data/license constraints;
3. distinguish direct reuse, adaptation, independent reimplementation, and idea-only reference;
4. evaluate Windows deployment and CPU-only behavior rather than assuming a GPU;
5. prefer real product benchmarks over README claims;
6. preserve important findings here before the conversation moves far enough that evidence may be lost;
7. only after the map is sufficiently complete, convert selected conclusions into Architecture Contracts,
   ADRs, capability specifications, and a Roadmap.

## Status vocabulary

- **DIRECT-CANDIDATE** — potentially suitable for direct adaptation/integration after verification.
- **REFERENCE-STRONG** — strong architectural/algorithmic reference; reimplement behind local contracts.
- **REFERENCE-ONLY** — useful ideas, but license/product mismatch or technical weight makes direct reuse
  unattractive.
- **BLOCKED-PENDING-REVIEW** — promising but cannot be approved before dependency/model/license or benchmark
  review.

No status in this directory is a legal opinion or final dependency approval.

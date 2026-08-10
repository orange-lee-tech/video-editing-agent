# ADR-007 — SpatialComposer Owns Auto Reframe; Crop Path Is Deterministic

**Status:** ACCEPTED  
**Date:** 2026-08-11

## Context

Aspect-ratio conversion requires semantic focus and temporal framing stability. If Renderer chooses crop coordinates itself, it gains hidden creative authority. If a VLM writes every crop coordinate, output becomes costly/jittery/unverifiable.

## Decision

Introduce a provider-neutral `SpatialComposer` capability:

```text
EditSlot/CommercialSkill spatial intent
+
tracked/saliency/semantic evidence
→ ReframeDecision / SpatialTransformPlan
→ EDLBuilder
→ exact transform curve
→ Renderer
```

Crop/scale trajectory is validated and optimized deterministically over grounded candidates/keyframes.

Normal fallback remains non-generative.

## Consequences

- detector/tracker vendor remains replaceable;
- EDL must support time-varying transforms;
- user crop locks/keyframes can become explicit constraints;
- multi-subject/impossible-fit cases can return fallback/unresolved instead of fabricating pixels;
- generative outpainting/uncrop is not introduced by Auto Reframe.

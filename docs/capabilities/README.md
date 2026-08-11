# Capability Specifications

**Status:** ACTIVE SPECIFICATION SET — accepted with Planning Baseline A0 on 2026-08-11  
**Authority:** Below Product Constitution and accepted Architecture Contract v0.2; above implementation/provider details.

These files split the product into durable capability boundaries so implementation does not depend on recovering design intent from research notes or chat history.

## Specification set

1. `CAP-01_PREPRODUCTION.md` — Brief, ScriptPlan, ShootingPlan, reference analysis, locks, coverage/reshoot semantics.
2. `CAP-02_ASSET_RIGHTS_MEDIA_TIME.md` — Asset identity, usage role, rights/license evidence, canonical rational media time, derivatives/proxies.
3. `CAP-03_MEDIA_UNDERSTANDING_SPEECH_TEMPORAL.md` — Shot analysis, ASR/VAD, local/cloud visual evidence, camera-compensated motion, TemporalAnchors.
4. `CAP-04_RETRIEVAL_DIRECTOR_RESOLVER.md` — Director/EditSlots, hybrid retrieval, CandidateWindows, scoring/uncertainty, deterministic sequence optimizer.
5. `CAP-05_COMMERCIAL_SKILLS.md` — PlatformProfile, Commercial/Vlog skills, marketing objective, pairwise preference calibration and UserStyle overlays.
6. `CAP-06_MUSIC_AUDIO_EDITORIAL.md` — rights-aware music discovery/selection, BeatMap, music moment selection, audio ducking/mixing.
7. `CAP-07_SPATIAL_COMPOSITION_AUTO_REFRAME.md` — semantic focus, crop candidates, smooth path optimization, safe zones, manual spatial locks and non-generative fallbacks.
8. `CAP-08_EDL_RENDER_PREVIEW_SUBTITLE.md` — executable EDL, time-varying transforms/audio automation, FFmpeg renderer seam, subtitles, preview/proxy/cache.
9. `CAP-09_REVIEW_BENCHMARKS.md` — layered review, repair routing, technical QC, product benchmarks and cost telemetry.
10. `CAP-10_DEPLOYMENT_SECURITY_AUTONOMY.md` — Environment Doctor, CPU/GPU/cloud tiers, install assistance, trust/security boundaries and autonomy-policy seam.

## Reading order

For architecture or implementation work:

```text
Product Constitution
→ Architecture Contract v0.2
→ relevant CAP specification(s)
→ ADR(s)
→ Upstream Ledger / dependency approval
→ Roadmap phase
→ implementation/tests
```

Research files under `docs/research/` explain why these choices emerged but are not normative.

## Cross-cutting invariants

Every capability must preserve:

- user-supplied local visual source policy;
- typed Proposal → validation → authoritative owner commit;
- EDL as sole exact executable timeline authority;
- provider/model neutrality;
- local deterministic execution for measurable/mechanical work;
- revision/provenance traceability;
- no direct model-generated shell/timeline mutation;
- score and uncertainty separated where relevant;
- incremental recompute/repair;
- source-code/model/data/transitive-license review before direct dependency adoption;
- CPU-capable baseline where practical, GPU optional;
- real product benchmarks before claiming quality improvement.

## Acceptance meaning

Acceptance freezes **capability boundaries and invariants**, not benchmark winners or arbitrary constants.

Exact provider/model/algorithm choices remain governed by ADRs, Upstream Ledger approval and Product/Engineering Probes. A model or library named in research does not become an approved dependency merely because the capability it may implement is now active.

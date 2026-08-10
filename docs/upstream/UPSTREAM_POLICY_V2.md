# Upstream Reuse Policy V2

**Status:** CANDIDATE ACTIVE POLICY — post Survey V2  
**Date:** 2026-08-11  
**Ledger:** `UPSTREAM_COMPONENTS_V2.md`

---

## 1. Constitution first

No upstream code, model, provider or product workflow may override the Product Constitution.

If an upstream combines useful engineering with prohibited behavior, apply the neutralization rule:

```text
identify useful mechanism
→ remove unconstitutional source/generation/authority behavior
→ adapt/reimplement behind our contracts
```

Examples:

- stock-video provider logic: caching/retry/provenance ideas may survive; autonomous remote visual fallback does not;
- generative visual project: orchestration/benchmark idea may survive; generated source pixels do not enter normal workflow;
- Auto Reframe project with generative uncrop: crop-path optimization may survive; synthesized missing pixels do not;
- Agent that directly mutates timeline: reasoning/tool ideas may survive; ownership bypass does not.

---

## 2. Direct reuse requires complete-chain review

Before source/package/model/provider enters production dependency tree, audit:

```text
source-code license
model/checkpoint license
training/data caveat
transitive/native dependency licenses
provider/API commercial terms
codec/patent implications
binary redistribution terms
Windows/runtime requirements
```

Repository badge alone is insufficient.

---

## 3. Exact provenance

For copied/adapted source record:

- upstream repository;
- exact commit/tag;
- exact path(s);
- license at that revision;
- local destination;
- copied/adapted/independently reimplemented classification;
- required notices;
- local modification summary.

For models record:

- model repository;
- exact model revision/hash;
- model license;
- source framework/runtime;
- known training/data caveats;
- file hash;
- distribution method.

---

## 4. Status does not equal approval

Research labels such as `DIRECT-CANDIDATE` mean “worth validating”, not “ship this now”.

Only `DIRECT-APPROVED` for an exact revision/use case authorizes normal production adoption.

A project can remain `REFERENCE-STRONG` forever and still be highly valuable.

---

## 5. Prefer independent reimplementation when ownership/product semantics differ

Even under a permissive license, do not copy an upstream subsystem wholesale when it would import:

- foreign Domain objects;
- conflicting timeline authority;
- incompatible database schema;
- remote/generated visual source behavior;
- giant task orchestrator;
- natural-language machine protocol;
- opaque filesystem state machine.

Borrow algorithms/patterns and implement against our Ports/contracts.

---

## 6. Models are dependencies

Treat checkpoint files as dependencies with their own provenance and license gate.

Permissive Python/C++ source does not approve a restrictive/non-commercial/unclear model.

Likewise a permissive checkpoint label does not erase relevant training/data or provider-use caveats that need legal/release review.

---

## 7. Provider terms are dependencies

Remote audio/search APIs may have:

- noncommercial/free API restrictions;
- per-project licenses;
- platform-specific scopes;
- download restrictions;
- attribution;
- purchase/certificate requirements.

Provider adapter must preserve these facts rather than treating every result as generic downloadable media.

Remote visual acquisition remains constitutionally unavailable regardless of provider terms.

---

## 8. Codec/binary distribution gate

FFmpeg/GStreamer/mpv/etc may change effective redistribution obligations depending on build/plugins/external libraries.

Record exact binary build/configuration.

Codec patent/licensing review is separate from open-source copyright compliance.

---

## 9. Windows and CPU baseline

Every candidate intended for default desktop capability must document:

- Windows viability;
- CPU-only path;
- install/package complexity;
- disk/RAM footprint;
- optional GPU path.

A GPU-only model may still be an optional Tier-2 provider.

---

## 10. Benchmark gate

Do not adopt a heavier dependency merely because it is more sophisticated.

Compare against the simplest baseline that already satisfies the capability.

Examples:

- exact local vector scan before vector DB;
- FFmpeg audio mix before separate DSP engine;
- CPU motion/tracking before heavyweight temporal model;
- metadata/BeatMap music selection before large audio-text embedding;
- simple crop optimizer before a large grounding model.

---

## 11. Security/trust gate

Upstream text/media/provider responses remain untrusted data.

No imported Agent framework may create a direct path from external/model text to shell/EDL/database authority.

All integrations preserve:

```text
Proposal/result
→ validation
→ local owner
→ deterministic executor
```

---

## 12. Update process

When evaluating an upstream:

```text
Survey / discovery
→ ledger candidate entry
→ exact dependency/license review
→ isolated prototype/benchmark if justified
→ architecture compatibility review
→ DIRECT-APPROVED or rejected/reference-only
→ provenance record
→ implementation commit
```

License/terms changes can downgrade an entry later without rewriting historical project provenance.

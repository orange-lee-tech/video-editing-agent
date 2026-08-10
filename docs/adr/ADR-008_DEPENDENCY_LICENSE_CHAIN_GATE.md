# ADR-008 — Complete Dependency License Chain Gate

**Status:** ACCEPTED  
**Date:** 2026-08-11

## Context

Survey V2 repeatedly found projects with permissive top-level code licenses but restrictive model weights, training/data caveats, AGPL/NC transitive dependencies, codec patent considerations or commercial API terms.

Examples include audio-text models whose weights have a different license than code, and an MIT auto-reframe project whose primary detector runtime/model uses Ultralytics licensing terms unsuitable for default proprietary embedding without an Enterprise agreement.

## Decision

No dependency receives release approval from repository license alone.

Before direct adoption audit:

```text
exact upstream revision
source-code license
model/checkpoint license
training/data caveat
native/transitive dependency licenses
provider/API commercial terms
codec/patent implications where relevant
Windows/runtime redistribution terms
required notices/provenance
```

Record the result in Upstream Component Ledger V2.

## Classification

Possible statuses:

```text
DIRECT-APPROVED
DIRECT-CANDIDATE
REFERENCE-STRONG
REFERENCE-ONLY
BLOCKED-PENDING-LICENSE
BLOCKED-PENDING-BENCHMARK
```

## Consequences

- a technically useful upstream can be neutralized into architecture/algorithm reference;
- dependency choices stay replaceable behind capability ports;
- release/legal gates remain explicit rather than discovered after product packaging.

# FireRed Split Shots — R0.1 Provenance Record

## Scope

Repository Bootstrap v0.1 established the local architecture before any upstream implementation reuse.

R0.1 examines the shot-splitting implementation in FireRed-OpenStoryline and selectively adopts useful engineering ideas without importing FireRed's node framework or media-object model.

## Upstream reference

- Repository: `FireRedTeam/FireRed-OpenStoryline`
- Revision: `c9e945215586f45c12a61c1951ee9a8e9c43a027`
- Source path: `src/open_storyline/nodes/core_nodes/split_shots.py`
- License at reviewed revision: Apache-2.0
- Upstream `NOTICE`: none found at the reviewed revision

## R0.1-A classification

Local destination:

`src/video_editing_agent/media/shot_detection/policy.py`

Reuse classification:

**Independently reimplemented from reviewed behavior and architecture ideas. No upstream source code is copied into the local implementation.**

Therefore R0.1-A does not add FireRed source code to this repository and does not populate `LICENSES/` with an upstream license copy yet. If a later phase copies or adapts Apache-2.0 source, the repository's upstream policy requires preserving the appropriate license and notices at that time.

## Ideas retained

R0.1-A retains these useful concepts observed in FireRed:

1. model-specific scene output should be converted into deterministic split points before media segmentation;
2. minimum shot duration is enforced by removing cut points and merging short intervals;
3. maximum shot duration is enforced before rendering/segmentation by inserting internal cut points;
4. duration policy is applied before FFmpeg work, avoiding a split-then-rejoin pipeline.

## Intentional architectural changes

The local implementation is millisecond-native and pure Python.

It does not depend on:

- `BaseNode`
- `NodeMeta`
- `NodeState`
- `NodeSummary`
- `NODE_REGISTRY`
- FireRed media dictionaries
- TransNetV2
- Torch
- NumPy
- FFmpeg

The detector/model adapter will be introduced separately in a later R0.1 phase.

## Intentional behavioral change

The reviewed FireRed implementation first merges segments shorter than the minimum and then evenly subdivides segments longer than the maximum. It does not subsequently verify that subdivisions introduced by the maximum-duration pass still satisfy the minimum-duration constraint.

R0.1-A treats this as an invariant gap rather than inheriting it.

When a segment cannot mathematically be partitioned such that both minimum and maximum duration constraints hold, the local policy raises an explicit `ValueError` instead of silently returning boundaries that violate the configured policy.

A complete source shorter than the configured minimum remains one unavoidable shot because boundary manipulation cannot make source media longer.

## R0.1-B capability contract

Local destination:

`src/video_editing_agent/application/ports/shot_detector.py`

R0.1-B formalizes the architecture boundary already required by Architecture Contract v0.1.2:

`Asset revision -> ShotDetector -> ShotBoundaryProposal[]`

The port defines:

- `ShotDetectionOptions` for model-agnostic minimum/maximum duration policy;
- `ShotBoundaryProposal` for asset-scoped source intervals, detection method and optional confidence;
- `ShotDetector` as the application-facing capability protocol.

Model-specific controls such as TransNetV2 threshold, frame sampling rate, model weights and device are intentionally excluded from the application port. They belong to the concrete detector adapter configuration introduced later.

A `ShotBoundaryProposal` is not a `Shot` and cannot create Shot identity. Shot identity remains owned by the future `ShotCatalog` owner.

R0.1-B is also independently implemented and copies no FireRed source.

## Deferred after R0.1-B

The following FireRed-related capabilities remain intentionally deferred:

- TransNetV2 model loading and caching;
- FFmpeg RGB frame extraction;
- model prediction and confidence mapping;
- concrete `ShotDetector` adapter implementation;
- actual media segmentation;
- Shot identity creation;
- Artifact/session integration.

These belong to later adapters or owners under Architecture Contract v0.1.2.

## Contract mapping

R0.1-A lives under:

`media/shot_detection`

R0.1-B exposes the inward-facing port under:

`application/ports`

Neither owns a Domain Entity.

The flow remains:

`Asset -> ShotDetector -> ShotBoundaryProposal[] -> ShotCatalog -> Shot[]`

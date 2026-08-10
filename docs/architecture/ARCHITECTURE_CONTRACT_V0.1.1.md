# Architecture Contract v0.1.1 — Object Relations & Schema Matrix

Status: Repository Bootstrap baseline.

## Field classes

- R — Required: required before an object enters valid state.
- O — Optional: may be absent without invalidating the object.
- D — Derived: calculated or analyzed from authoritative facts; may be cached but is not primary input authority.

## Shared entity envelope

Every top-level domain object has:

- id (R)
- revision (R)
- schema_version (R)
- status (R)
- created_at (R)
- created_by (R)
- derived_from (O)
- metadata (O)

Cross-object references use exact `EntityRevisionRef(entity_id, revision)`.

## Core schema summary

### Brief
R: title, objective, audience, platform, target_duration, aspect_ratio, core_message, language.
O: style, emotion, CTA, references, brand constraints, prohibited content, user notes, success criteria.
D: normalized constraints.

### ScriptPlan
R: brief_ref, title, target_duration, narrative_strategy, sections, language.
O: tone, reference style, global visual intent, global music intent.
D: estimated duration and coverage.

### ShootingPlan
R: script_plan_ref, requirements.
O: production notes, shooting order.
D: effort and coverage.

### ShotRequirement
R: requirement_id, script_section_ref, purpose, subject, target_duration, priority, source_policy, visual_intent.
O: action, environment, framing, camera motion, orientation, dialogue/audio requirements, continuity hints, search hints and fallback policy.
D: normalized constraints.

### Asset
R: media kind, origin, storage ref, content hash, byte size, provenance, imported_at.
O: labels and collection refs.
D: technical media metadata.

### Shot
R: asset_ref, source_start, source_end, boundary_method.
O: neighbors and scene ref.
D: duration and all media understanding: technical, semantic, speech and retrieval features.

### BeatMap
R: audio_asset_ref.
O/D: optional detected meter metadata.
D: BPM, beats, downbeats, accents, phrase anchors, sections, energy/onset curves and structural music events.

### EditPlan / EditSlot
EditPlan R: script_plan_ref, shooting_plan_ref, asset_catalog_snapshot_ref, slots, editorial_strategy, target_duration.
EditPlan O: beatmap_ref, user instruction, pacing/global source/continuity strategy.
EditPlan D: coverage and unresolved slots.

EditSlot R: slot_id, script_section_ref, narrative_role, purpose, target timeline budget, target duration, desired visual and source policy.
EditSlot O: requirement refs, pacing, selection, continuity, reuse, music alignment and transition intent.
EditSlot D: candidate/selected shot references and resolution score/status.

### EDL / EDLSegment
EDL R: edit_plan_ref, tracks/output canvas/output FPS/audio policy.
EDL O: render hints.
EDL D: timeline duration and validation state.

EDLSegment R: segment_id, track, asset_ref, source in/out, timeline in/out, playback rate.
EDLSegment O: slot_ref, shot_ref, transforms, audio gain, transitions, effects and subtitle ref.
EDLSegment D: duration.

### ReviewReport
R: stage, target_ref, checks, reviewer_type, reviewed_at.
D: pass/fail, findings, metrics and suggested actions.

## Source policy

Frozen values:

- captured_only
- local_only
- local_preferred
- remote_allowed
- remote_only
- generated_allowed

Source policy is a hard constraint.

## Matching contract

The central chain is:

`ShotRequirement -> Shot -> EditSlot -> EDLSegment`

These answer four different questions:

1. ShotRequirement — what footage is needed?
2. Shot — what real footage exists?
3. EditSlot — what should occupy this editorial position?
4. EDLSegment — what exact source interval is placed at what exact timeline interval?

The relationships are not 1:1.

## Eligibility and ranking

Shot matching is two-stage:

1. Eligibility Gate — hard constraints such as source, duration, media kind, mandatory dialogue/subject and prohibited content.
2. Candidate Ranking — soft dimensions such as semantics, visuals, action, framing, motion, quality, continuity, novelty and source preference.

Resolver weights are strategy, not domain contract.

## Resolution

A non-top-level `ResolutionDecision` records:

- slot_ref
- selected_shot_ref
- selected_source_window
- match_score
- decision_type
- reasons
- alternatives
- warnings

Valid decision types include automatic, manual_override, remote_fallback, generated_fallback and unresolved.

## Timeline authority

Three time concepts remain separate:

- Source time — Shot/EDL.
- Narrative time — ScriptPlan/EditPlan.
- Final timeline time — EDL only.

EDL is the only final timeline authority.

## Remote fallback

Remote material may be queried only when source policy permits it.
Remote media must pass through:

`MaterialProvider -> MediaSource -> AssetIngest -> Asset -> Shot/Analysis -> Resolver`

A remote URL never enters EDL directly.

## Staleness

Upstream changes mark only affected downstream artifacts stale or replan-available.
New assets do not invalidate historical ScriptPlans and existing asset understanding is not recomputed unnecessarily.

## Forbidden shortcuts

- ScriptPlan -> Shot
- ShootingPlan -> EDL
- ShotRequirement -> EDLSegment
- BeatMap -> EDLSegment
- Shot -> Timeline
- Agent text -> Renderer
- Remote URL -> EDL
- Renderer mutation of EDL

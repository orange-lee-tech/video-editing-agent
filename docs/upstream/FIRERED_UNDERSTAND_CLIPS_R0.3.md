# FireRed `understand_clips` — R0.3 Selective Audit

Upstream:

- repository: `FireRedTeam/FireRed-OpenStoryline`
- revision: `c9e945215586f45c12a61c1951ee9a8e9c43a027`
- node: `src/open_storyline/nodes/core_nodes/understand_clips.py`
- detail prompt: `prompts/tasks/understand_clips/zh/system_detail.md`
- overall prompts: `prompts/tasks/understand_clips/zh/system_overall.md` and `user_overall.md`

Reuse classification: **engineering/prompt-structure reference only; no FireRed source or prompt text is copied.**

## Useful ideas retained

The reviewed detail prompt asks for grounded visual description focused on subject, action, scene,
environment, view/composition and emotion, with special attention to actions and facial expression. It
also asks for a normalized 0.0–1.0 aesthetic/visual-quality score based on clarity, exposure/color,
composition/subject salience and camera stability/motion.

The node isolates failures per clip and retries failed VLM calls up to three attempts with increasing
short delays. These are useful operational patterns.

R0.3-E maps those ideas to provider-neutral contracts:

- provider semantics remain structured `VisualSemanticsProposal` fields;
- provider quality values are `VisualQualityScoreProposal` values constrained to `[0, 1]`;
- the first retained quality dimension is named `aesthetic` and commits as a derived
  `NamedQualityScore` only after deterministic validation;
- only explicit `VisualProviderTransientError` failures are retried;
- schema/response failures are structured `VisualProviderResponseError` values and are not retried;
- failures never become fake captions or sentinel quality scores.

## Explicitly rejected upstream behavior

The following are not inherited:

- `BaseNode`, `NodeState`, registry and FireRed input/output dictionaries;
- direct file-path/media dictionaries passed through the node graph;
- sequential orchestration embedded inside the capability implementation;
- caption strings beginning with `Error:` as failure transport;
- `aes_score = -1.0` as a failure sentinel;
- raw unparsed model text silently accepted as a valid caption;
- per-shot understanding and all-material overall summarization in the same owner;
- a second LLM summary call from inside the Shot understanding node;
- implicit `clip_id`/`clip_instance_id` dictionary conventions.

The reviewed code appears to build overall-summary lines from `clip_instance_id` even though its local
output items are created with `clip_id`; this reinforces the decision to use typed identifiers instead
of ad-hoc dictionaries.

## Overall summary ownership

FireRed's overall prompt asks for a 1–2 paragraph objective summary of multiple clip captions for later
highlight detection and script generation. That is a useful future capability, but it is deliberately
**not** part of `ShotAnalysis` or `UnderstandingService`.

If introduced later, it belongs to a collection/catalog/grouping capability consuming persisted
ShotAnalysis revisions. It must not make individual Shot identity or analysis revision mutable.

## Provider adapter requirements derived from this audit

A future real visual provider adapter must:

1. consume `VisualUnderstandingRequest` and retrieve image bytes by ArtifactStore reference;
2. request grounded structured output matching the provider-neutral proposal schema;
3. map temporary transport/service failures to `VisualProviderTransientError`;
4. map malformed/invalid responses to `VisualProviderResponseError`;
5. never return sentinel quality scores;
6. never create `ShotAnalysis` or choose its revision;
7. remain replaceable without changing Domain/Application contracts.

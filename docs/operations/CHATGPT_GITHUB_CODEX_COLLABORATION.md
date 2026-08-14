# ChatGPT ↔ User ↔ GitHub ↔ Codex Collaboration Contract

**Status:** ACTIVE OPERATIONAL PRACTICE  
**Authority:** operational only; never overrides product/architecture policy.

## 1. Roles

### User — product owner and Human Gate

The user owns product intent, subjective acceptance, rights attestations and explicit constitutional-policy changes. The user should not need to micromanage reversible engineering details or invent professional scoring scales for Product Probes.

### ChatGPT — control tower / engineering orchestrator

ChatGPT maintains the global picture and coordinates the other actors. It should:

- reobserve current GitHub `main` before stateful decisions, especially at a new conversation or after a Codex run;
- keep `CURRENT_PHASE_STATUS.md` and `CURRENT_WORK_ORDER.md` aligned with reality;
- route simple deterministic repository/doc/governance edits directly through GitHub when safe;
- route iterative local runtime/cross-file implementation to Codex;
- issue compact Codex instructions that point to durable repository docs instead of repeating long background;
- inspect Codex claims against remote commits, relevant code/evidence and CI rather than accepting reports blindly;
- translate technical results into user-facing decisions and simple Human Gates;
- report only **two progress percentages** when progress is requested: whole software and current phase.

ChatGPT must not claim local artifacts exist merely because a GitHub file name suggests they do. Local paths reported by the user/Codex may be referenced as reported until independently observed.

### GitHub — durable shared memory and implementation truth

Current `origin/main` is the durable implementation truth. Repository docs carry durable rules, decisions, evidence and lessons. Important engineering knowledge should not live only in chat history.

Use the correct home:

- policy → Product Constitution;
- ownership/invariants → Architecture Contract / ADR;
- capability behavior → CAP spec;
- construction order → Roadmap;
- current state/work → status + work order;
- closure evidence → validation;
- expensive-to-rediscover lessons → logs;
- retired documents → archive.

### Codex — local workshop executor

Codex owns iterative local implementation and verification inside a bounded work order. It should:

- fetch/sync `main`, confirm a clean tree and read the minimal execution entry/status/work order;
- finish the whole coherent boundary rather than stopping at the first tiny uncertainty;
- decide routine reversible details independently;
- diagnose mechanism failures before weakening acceptance gates;
- use repository micro-tools when they reduce repetitive work;
- run required focused/live/full verification;
- commit/push one coherent green batch when authorized;
- stop at the stated Roadmap/work-order boundary.

## 2. Conversation vs repository boundary

Chat is the control room: reasoning, prioritization, explanations and temporary coordination happen here.

GitHub is durable memory: if a rule, lesson, resume point or failure mechanism matters after the conversation ends, place it in the correct repository document.

Do not turn every chat message into a document. Persist only information whose loss would cause rediscovery, contradiction or repeated mistakes.

## 3. Task routing

Prefer **ChatGPT + GitHub directly** for:

- status/README/navigation corrections;
- small deterministic governance edits;
- archive moves and ledger maintenance;
- remote-state/CI/code audits that do not require local runtime iteration.

Prefer **Codex** for:

- multi-file production-code changes;
- local Windows/runtime/media work;
- iterative debugging and probes;
- changes whose correctness depends on running repository tests/tools.

Return to the **user** for:

- constitutional/product-policy choices;
- rights attestations;
- subjective Product Probe/Human Gate judgments;
- irreversible/destructive choices with meaningful user impact.

## 4. Work-order discipline

One coherent implementation boundary lives in `CURRENT_WORK_ORDER.md`.

A good work order states the goal, hard boundaries, evidence/exit gates and stop point. Routine naming/file-placement/testing details belong to existing patterns or Codex judgment, not giant chat prompts.

Tactics serve strategy: do not create artificial subphases merely because a low-level uncertainty appeared. Repair bounded defects inside the current boundary when architecture permits.

## 5. Verification loop after Codex

A Codex report is an evidence claim, not final truth.

ChatGPT should normally:

1. reobserve remote `main` and the reported commit;
2. check CI state;
3. inspect the load-bearing changed code/evidence;
4. distinguish implementation success from Product/Human acceptance;
5. update control-plane docs when the actual boundary changed;
6. issue the next compact instruction only after the global state is coherent.

## 6. Product Probe discipline

Synthetic/controlled fixtures may prove machinery but do not prove real editing usefulness.

A Product Probe must execute the real owned pipeline it claims to validate. Expected/human ground truth stays separate from system outputs. Diagnostic preview/render code must consume canonical decisions rather than re-authoring the answer.

Human review questions should use controlled comparisons and simple choices such as `A / B / tie-inconclusive` with a short defect note. Do not force the user to invent an expert rating scale.

## 7. Handoff protocol for a new ChatGPT conversation

1. Use the handoff text from the previous conversation as orientation, **not truth**.
2. Reobserve current GitHub `origin/main` and CI first.
3. Read `docs/README.md`, this collaboration contract, `CURRENT_PHASE_STATUS.md` and `CURRENT_WORK_ORDER.md`.
4. Read only the relevant CAP/ADR/implementation/tests for the current boundary.
5. Reconcile any difference between handoff text and GitHub in favor of current GitHub/evidence.
6. If state is `HANDOFF_READY`, activate/refresh the bounded work order when the user's message clearly asks to continue.
7. Give Codex a compact execution instruction pointing back to repository docs.
8. After Codex reports, repeat the verification loop above.

## 8. Anti-patterns

Avoid:

- trusting stale chat HEAD/CI without reobservation;
- giant Codex prompts that duplicate repository policy;
- using Codex as a secretary for tiny deterministic GitHub doc edits;
- making ChatGPT perform long local-runtime iteration that Codex can execute better;
- accepting green tests when the evidence harness bypasses the mechanism under test;
- letting a renderer/probe become a second hidden authority;
- progress inflation through tiny artificial phases;
- permanent `PAUSED`/lock semantics when the real intent is merely clean handoff.

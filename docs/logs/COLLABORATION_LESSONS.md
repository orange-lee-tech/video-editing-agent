# Collaboration Lessons

Non-authoritative durable lessons for orchestrating User ↔ ChatGPT ↔ GitHub ↔ Codex.

## 1. Reobserve before acting

A handoff message, previous HEAD or previous CI result is orientation only. New conversations and post-Codex reviews must reobserve current `origin/main`; otherwise a correct instruction can target an obsolete repository state.

## 2. GitHub holds durable context; chat should stay lean

Long background, architecture boundaries and recurring constraints belong in repository docs. Chat/Codex prompts should mostly identify the current boundary, required evidence and stop point, then point to those docs.

This reduces prompt noise and prevents later conversations from reconstructing policy from memory.

## 3. Route work by where evidence lives

Small deterministic GitHub navigation/status/log edits are usually faster and safer for ChatGPT to perform directly. Iterative Windows/runtime/media implementation belongs with Codex because it can run the local repository and repair bounded defects without conversational ping-pong.

## 4. Codex should reach the planned boundary

Stopping for naming, obvious test placement, small refactors or reversible threshold plumbing creates expensive empty turns. Codex should choose consistent low-risk details and continue. Stop only for material architecture conflicts, unavailable required dependencies, destructive risk, unauthorized paid action or invalid evidence mechanisms.

## 5. Codex reports need independent review

A report saying `PASS` is not enough. Reobserve the pushed commit, inspect load-bearing code/evidence and check CI. This caught both the R0.9 Product Probe answer-injection defect and the R0.10 decision→execution bypass.

## 6. Human Gates need usable questions

Users should not be asked to judge with undefined professional criteria. Control variables and ask simple comparative questions. `A / B / tie-inconclusive` plus a defect note is often more informative than an invented 1–10 score.

## 7. Engineering green ≠ product accepted

Unit tests, live engineering probes and diagnostic previews can prove machinery. Product usefulness still needs real inputs and the Human Gate defined by the Roadmap.

## 8. Avoid artificial phase inflation

A bounded defect inside an existing phase should normally be repaired inside that phase. Creating R0.xC/R0.xD merely to label every repair makes the roadmap noisy and progress misleading.

## 9. Progress reporting must stay stable

When the user asks for progress, report only two percentages:

- entire software;
- current phase.

Do not inflate progress because documentation or housekeeping produced many changed files.

## 10. Handoff-ready is different from paused

A temporary stop for cleanup/handoff should not become a permanent lock. `HANDOFF_READY` preserves a safe resume point: ChatGPT must reobserve GitHub before activating work, but the next conversation can continue without a new roadmap or artificial approval ritual.

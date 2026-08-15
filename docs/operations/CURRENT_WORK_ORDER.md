# Current Work Order

**ID:** `R0.12-SUBTITLE-001`  
**Status:** CLOSED  
**Phase:** R0.12 — structured subtitle execution audit closure  
**Owner/writer:** Codex + ChatGPT acceptance

## Result

PASS at accepted code baseline `827b84941e1726bab374f2ffea9a746f49f6e570`.

The existing structured subtitle implementation was preserved and only the recorded execution-authority guards were closed:

- non-centisecond canonical cue boundaries fail closed before FFmpeg invocation;
- unsupported multiple SUBTITLE tracks or nonzero subtitle layers fail closed before invocation;
- the real ASS/libass filter path is exercised under a parent directory containing comma and apostrophe punctuation.

No Graphics, transitions, Preview, Proxy/cache, hardware-routing, packaging or UI work was entered.

## Verification accepted

- Focused subtitle/EDL/Renderer tests: 39 PASS.
- Subtitle live Engineering Probe: 8/8 PASS.
- Living Resolver → EDLBuilder → Renderer smoke: 10/10 PASS.
- Ruff: PASS.
- mypy: PASS.
- Full pytest: 541 PASS.
- import-linter: 3 contracts kept.
- `uv build`: PASS.
- `git diff --check`: PASS.
- Remote `ci/quality-gate-diagnostic`: success.
- GitHub independent review: one bounded commit, four expected files only, `main` aligned to the accepted commit.

## Durable boundary

- EDL remains sole exact executable timeline authority.
- Renderer must not silently retime, relayer, rewrite or repair canonical subtitle decisions.
- Stage-A subtitle execution remains deliberately small: one layer-zero subtitle track, ASS/libass burn-in, bounded emphasis/layout intent.
- Rich typography, karaoke, multi-layer subtitles and font-packaging quality are not silently implied by this closure.

## Stop state

This work order is finished. Do not run Foreman against it as though it were active.

ChatGPT/Product Owner must pre-process the next coherent R0.12 batch, decide whether GitHub/User PowerShell can complete it without Codex, then replace this file with a new ACTIVE work order only when execution is ready.

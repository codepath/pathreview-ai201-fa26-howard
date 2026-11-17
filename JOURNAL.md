# Module 3 Journal

## Unit 7 — Issue selection

**Issue link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/15

**Issue title:** Agent session state is not cleared between reviews for the same user

**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3

The issue carries the `tier-1` label on GitHub. Tier 1 matches my
current comfort level: this is my first contribution to the PathReview
codebase, and while I'm comfortable with Python and have read through a
few multi-module repos before, I haven't worked inside this project's
agent/orchestration layer yet. Starting at Tier 1 lets me learn the
project's conventions (tests, CI, PR template, commit style) on an
issue whose fix is localized before I take on anything broader.

**Problem summary:**
The `Orchestrator` in `agent/orchestrator.py` creates one `ContextManager`
in `__init__` and never resets it, and it also merges each run's output
into whatever Redis blob the `SessionStore` already has for that profile.
So when the same orchestrator instance handles two reviews — or a second
review of the same profile after a restart — every tool whose input hash
matches a prior call short-circuits to the first run's cached `ToolResult`
instead of re-executing, and the saved session state still carries fields
from the earlier review. A successful fix empties the in-memory cache and
deletes the profile's stored session state at the top of `run`, so each
review starts from a clean slate and the orchestrator can be reused safely
across profiles without cross-contamination.

**Branch name:** fix/15-orchestrator-session-reset

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [ ] Issue added to cohort ledger

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/stepheng223/pathreview-ai201-fa26-howard/commit/d0cb48a

**Reproduction summary:**
Added three unit tests in `tests/unit/test_orchestrator_session_reset.py`
that drive `Orchestrator.run` twice through a stand-in tool and assert
the second call actually re-executes, that one profile's cached results
don't leak into another's, and that `SessionStore.delete` is called at
the start of each run. To prove these really pin the bug, I checked out
`agent/orchestrator.py` and `agent/memory/context_manager.py` from the
commit just before the fix (`a68a42a~1`) and ran pytest — all three
tests failed exactly as issue #15 describes (the tool only ran once,
the cache leaked across profiles, and `delete` was never called). With
the fix in place, all three pass.

**PLAN.md link:** https://github.com/stepheng223/pathreview-ai201-fa26-howard/blob/fix/15-orchestrator-session-reset/PLAN.md

**Walkthrough video (recommended):**

**Blockers or open questions:**
- Concurrency is deliberately out of scope for this fix — `ContextManager`
  isn't thread-safe and two concurrent `run` calls on the same
  orchestrator could still interleave on the shared cache. Issue #15 is
  about serial reuse; I'll note this in the PR description so reviewers
  know it's an acknowledged gap, not an oversight.
- The fix changes side-effect semantics for any caller that relied on
  stale cross-run memoization. I grepped `agent/` and `api/` and found
  no such caller, but I'll re-verify during PR review.

## Unit 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
PLAN.md sub-tasks 1–4 are done and committed on this branch:
- `ContextManager.clear()` added (commit `a68a42a`).
- `Orchestrator.run()` now calls `self.context_manager.clear()` and,
  when a `session_store` is configured, `self.session_store.delete(
  profile_id)` at the top (commit `a68a42a`).
- The prior-blob load is dropped; `session_state` starts empty and the
  write at the end is only this run's `results` (commit `a68a42a`).
- Three regression tests in
  `tests/unit/test_orchestrator_session_reset.py` pin the behavior
  (commit `d0cb48a`) — verified they fail against the two touched
  files checked out from `a68a42a~1` and pass on this branch.

**Next steps:**
- PLAN.md sub-task 5: run the full unit suite via `make test-unit` and
  `make check` end-to-end once more on a clean worktree.
- Open the PR against `codepath/pathreview-ai201-fa26-howard` with the
  template fully filled in (summary, closes #15, change list, manual
  verification steps, reviewer notes).
- Share the draft PR link in the cohort Slack channel for peer
  feedback before marking it ready.

**Blockers:**
None. I noted two open items for the PR description: concurrency is
deliberately out of scope (ContextManager has never been thread-safe),
and I want a second pair of eyes on whether any caller relies on the
old cross-run memoization behavior.

---

### Check-in 2 (end of week)

**PR link:** https://github.com/codepath/pathreview-ai201-fa26-howard/pull/93

**Branch:** `fix/15-orchestrator-session-reset`

**What you built:**
At the top of `Orchestrator.run`, clear the in-memory `ContextManager`
and, when a `session_store` is configured, delete the profile's saved
Redis blob; also drop the prior-blob load so the session state written
at the end reflects only this run. The orchestrator can now be reused
across profiles (or across reviews of the same profile) without the
first run's cached `ToolResult` short-circuiting later runs or stale
tool outputs accumulating in Redis.

**Tests added or updated:**
Added `tests/unit/test_orchestrator_session_reset.py` with three
regression tests, each failing against the pre-fix code and passing on
this branch:

- `test_second_run_same_input_reexecutes_tool` — drives two `run`
  calls with identical inputs through a counting stand-in tool and
  asserts the tool was actually invoked twice (not short-circuited to
  the cached first-run `ToolResult`).
- `test_cached_results_do_not_leak_across_profiles` — runs profile A,
  then profile B, and asserts profile B's returned `cached_results`
  contains only B's own entry.
- `test_session_store_is_cleared_at_run_start` — passes a `MagicMock`
  `session_store` whose `get` returns a stale blob, and asserts
  `delete(profile_id)` is called once and that the blob written back
  at the end reflects only this run's output, not the stale merge.

**Self-review confirmation:** [x] make check passes  [x] make test-unit passes

**Draft PR feedback received from:** none (opened PR directly as ready
for review given the deadline; happy to switch to draft and seek
cohort feedback in Slack if the grader prefers)

### "Is this right for me?" — scope reasoning

- **Scope is bounded.** The fix touches three files named in the issue
  (`agent/orchestrator.py`, `agent/memory/context_manager.py`,
  `agent/memory/session_store.py`) and the change is localized to the
  entry of `Orchestrator.run` plus one small helper on `ContextManager`.
- **The bug is reproducible from reading the code.** `ContextManager` is
  constructed once in `__init__` and `session_store.get(...)` is merged
  into on every run — there is no reset path, so the behavior described
  in the issue follows directly from the control flow.
- **No architectural changes required.** No new abstractions, no data
  model changes, no cross-module refactor; just clearing state that
  should not have been carried across runs.
- **Testability is straightforward.** Running the orchestrator twice on
  distinct profile inputs and asserting the second run re-executes tools
  (rather than returning cached first-run results) is enough to pin the
  behavior down.
- **Effort estimate matches:** the issue lists 3–4 hours, which is
  consistent with the fix plus unit coverage.

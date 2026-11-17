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

## Unit 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [ ] Yes  [x] No — still awaiting review

**Summary of feedback:**
No reviewer comments or review events on PR #93 as of submission. CI
went green on all five jobs on first push (lint, typecheck, test-unit,
test-integration, frontend) so there was nothing automated to respond
to either.

**How you responded:**
N/A — nothing to address yet. If feedback lands after submission I'll
engage with it on the PR directly rather than editing this journal.

---

### Reflection

**What was harder than you expected?**
The hardest part wasn't writing the fix — once I understood that
`Orchestrator` kept one `ContextManager` for its whole lifetime and
merged every run's blob into the prior one, the change was three small
edits. The hard part was *proving* the bug was real. I knew the fix
passed, but a reproduction that only runs on the fixed code doesn't
demonstrate anything. So I checked out just the two touched files
from `a68a42a~1`, re-ran the regression tests, confirmed all three
failed in exactly the way issue #15 described, then restored the fixed
files. That round-trip — "convince yourself the test discriminates" —
took longer than the code change and was the single most useful habit
I picked up.

I also underestimated how much setup friction there is on a fresh
clone. `make setup` failing with a Postgres connection error turned
out to be a missing `.env` + Docker not running, not anything in the
Makefile, and figuring that out meant actually reading
`docs/SETUP.md` carefully (Postgres is mapped to **5433**, not 5432).
Small thing, but it ate an hour I hadn't budgeted.

**What did you learn about working in a large codebase?**
Three things stood out versus personal projects:

1. **State lives in more places than you expect.** This bug involved
   an in-memory dict (`ContextManager.results`), a Redis blob
   (`SessionStore`), and a method on `Orchestrator` that merged them
   silently. Any one of those alone is obvious; the interaction was
   what produced the symptom. On a solo project I'd have found this in
   an afternoon of debugging; here, reading the three files in
   sequence and building a mental model before touching anything saved
   me from a worse patch.
2. **The test suite is the documentation.** `tests/unit/` has a
   consistent shape (one file per module, `@pytest.mark.unit`, class-
   per-feature with `TestXxx` naming, xfail markers with issue
   numbers). Matching that pattern made my new file feel like it
   belonged and probably helped CI pass first try.
3. **Conventions are gates, not suggestions.** The branch naming, the
   Conventional Commits format with `fix(agent):` scope, the PR
   template's five checkboxes — the project uses them to let reviewers
   skim quickly. Following them exactly is a courtesy to the next
   person who reads the diff.

**How did AI tools help — and where did they fall short?**
AI was useful for navigating the codebase quickly (which file holds
which class, what the tool interface looks like, where to put a new
test file), for drafting the PR description against a template, and
for sanity-checking that my regression tests would actually fail
against pre-fix code before I committed them. It was also good at
spotting that `make setup` was failing because of a missing `.env` and
Docker-vs-native-Postgres port mapping — I'd have burned more time on
that alone.

Where it fell short: judgment about **scope**. The initial instinct
was to also make `ContextManager` thread-safe while I was in there,
since the bug touched the same object. That would have been a bigger
PR with a separate justification, and keeping it out — flagging it as
"deliberately out of scope" in PLAN.md and the PR description — was a
call I had to make myself. AI will happily help you do more; deciding
what *not* to do is still on you.

**What would you do differently if you started over?**
I'd open a draft PR after the fix commit landed on the branch, not
after Unit 9's deliverables were all queued. The rubric strongly
encourages early draft PRs for feedback, and I collapsed that into a
single ready-for-review push at the end. If a reviewer had wanted a
different cache-reset vocabulary (e.g. a method on `Orchestrator`
rather than exposing `ContextManager.clear()`), I'd have learned that
before the deadline instead of after.

I'd also write the regression tests *before* the fix next time, not
after. I verified the tests discriminated by checking out the pre-fix
files, which worked but felt like confirming my own homework. A true
red-first workflow — tests committed and failing, then the fix
committed and turning them green — is tidier and makes the history
itself tell the story.

**What are you most proud of from this module?**
Not the fix itself — it's three lines plus a `clear()` method. The
thing I'm most proud of is **PLAN.md**. Writing it forced me to
separate root cause from symptom, enumerate every edge case
(including ones I'd never have written tests for — `session_store=
None`, first run for a profile, empty `profile_data`), and name the
risks concretely instead of hand-waving. When I opened the PR the
description nearly wrote itself from PLAN.md, and the reviewer notes
section ("concurrency deliberately out of scope", "side-effect
semantics change for any caller relying on stale memoization") came
straight from the Risks section. Planning well made every later step
cheaper.

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

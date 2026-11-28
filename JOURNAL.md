# Module 3 Journal

## Unit 7 — Issue selection

**Issue link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/61

**Issue title:** Health check DB probe passes a raw SQL string, which fails under SQLAlchemy 2.x

**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The `GET /health` endpoint in `api/routes/health.py` checks that PostgreSQL is reachable by running `await db.execute("SELECT 1")`. SQLAlchemy 2.x no longer accepts a plain string as executable SQL and raises an `ArgumentError` that asks for `text("SELECT 1")` instead. The probe therefore fails every time, and the endpoint reports Postgres as "unhealthy" (and the overall status as unhealthy) even when the database is up. A successful fix wraps the query in `sqlalchemy.text()`, so the endpoint reports the database as healthy when it is reachable and unhealthy only when it is actually down. I'd also add a unit test covering both cases.

**Is this right for me? (scope reasoning):**
- *Tier fit:* Tier 1 matches where I am. This is my first contribution to a large multi-module codebase, so I want a change where most of the work is understanding the code path, not writing a lot of code.
- *Scope:* The root cause is already identified and sits in one file, on one line. The fix is a one-line change plus an import, with a small test in `tests/unit`. It doesn't touch the frontend, the database schema, or any other module.
- *Unclaimed:* When I checked on Nov 11, the issue had no comments, so nobody else was working on it.
- *Verifiable:* I can reproduce the bug against the running stack (Docker Postgres) and show it fixed, plus a unit test with a mocked session that fails before the change and passes after.
- *Risks:* Issues #62 (`settings.redis_host`) and #26 (safety event count) edit other lines in the same file, so I may need to rebase to resolve a merge conflict. I'll keep my change to the Postgres probe lines only.
- *Alternatives considered:* #59 (faithfulness checker) is unclaimed but its fix needs a design choice the issue doesn't specify, and it has a second hidden bug (punctuation in tokenization). #18 spans two modules. #11 and #12 are docs/tests-only with no bug to fix.

**Branch name:** fix/61-health-check-sql-text

**Setup confirmation:** [x] App runs locally at localhost:5173 (frontend returns 200; backend on :8000). I also reproduced the bug live: `GET /health` returns 503 and the log shows `Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')`.

**Cohort ledger:** [x] Issue added to cohort ledger

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/Wayles3/pathreview-ai201-fa26-howard/commit/00d0ba05a59779a37aa94d5a207a9a67d38040bc

**Reproduction summary:**
With the stack running, `curl -i localhost:8000/health` returns `503` with `"postgres":"unhealthy"` even though the Docker Postgres container is up; the log shows `postgres_health_check_failed` caused by raw `"SELECT 1"` being rejected by SQLAlchemy 2.x (`ObjectNotExecutableError: Not an executable object: 'SELECT 1'` on a bare connection, `ArgumentError: Textual SQL expression ... text('SELECT 1')` on a session). I also committed `tests/unit/test_health.py`, an `xfail(strict=True)` test using a fake session that rejects bare strings, so the bug is pinned in the suite until it is fixed.

**PLAN.md link:** https://github.com/Wayles3/pathreview-ai201-fa26-howard/blob/fix/61-health-check-sql-text/PLAN.md

**Walkthrough video (recommended):** not recorded

**Blockers or open questions:**
After my fix `/health` will still return 503 because Redis is also reported unhealthy (issue #62, `settings.redis_host`). I need to verify my fix via `dependencies.postgres` rather than the status code, and confirm with the course team that #62 stays a separate issue.

## Unit 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
Plan steps 1–3 are done. I confirmed the baseline (the strict-xfail test and `postgres: "unhealthy"` on `/health`), wrapped the probe in `text()` in `api/routes/health.py`, removed the #61 xfail marker, and added a DB-down test. The xfail test needed a fix of its own: it patched `core.config.settings.redis_host` with `create=True`, which pydantic rejects, so I patch the whole `settings` object instead.

**Next steps:**
Run `make check` and `make test-unit`, verify against the live stack, open the PR, and ask for review.

**Blockers:**
None. Redis (#62) still makes the overall `/health` status 503, so I verify using `dependencies.postgres`.

---

### Check-in 2 (end of week)

**PR link:** https://github.com/codepath/pathreview-ai201-fa26-howard/pull/105

**Branch:** `fix/61-health-check-sql-text`

**What you built:**
The `/health` Postgres probe now runs `db.execute(text("SELECT 1"))` instead of a raw string, so SQLAlchemy 2.x accepts it and Postgres is reported healthy when reachable and unhealthy only when the query actually fails.

**Tests added or updated:**
`tests/unit/test_health.py`: removed the #61 strict-xfail marker from the "DB reachable reports healthy" test, and added a "DB down" test (`OperationalError` gives `postgres == "unhealthy"` and a 503 `HTTPException`). Both tests patch Redis settings so they don't depend on #62.

**Self-review confirmation:** [x] make check passes  [x] make test-unit passes (377 passed, 53 xfailed)

**Draft PR feedback received from:** none

## Unit 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [ ] Yes  [x] No — still awaiting review

**Summary of feedback:**
No review has come in on PR #105 (https://github.com/codepath/pathreview-ai201-fa26-howard/pull/105) as of Nov 28. I checked the PR conversation, inline review comments, and formal reviews, and all three are empty. The PR is still open and unmerged. All five CI checks pass (lint, typecheck, test-unit, test-integration, frontend), so nothing is blocking a reviewer on my side. My draft-PR check-in in Unit 9 also drew no feedback.

**How you responded:**
There was nothing to reply to, so I made no changes. I re-ran the check and left the PR as submitted. I'll respond promptly if a maintainer comments after this entry. The branch tip matches what the PR points at, so any later feedback can be addressed with a follow-up commit on the same branch.

---

### Reflection

**What was harder than you expected?**
The fix was one line, `text("SELECT 1")`. Nearly all the difficulty was around that line.

- **Proving the bug.** After I wrapped the probe in `text()`, `/health` still returned 503 because Redis was also unhealthy (issue #62, `settings.redis_host`). I couldn't use the status code as proof of the fix, so I had to check `dependencies.postgres` instead and make my tests patch Redis settings so they didn't depend on #62.
- **My own test failed.** The strict-xfail test I wrote in Unit 8 patched `core.config.settings.redis_host` with `create=True`, and pydantic rejects that. I replaced it with a patch of the whole `settings` object.
- **Two different errors for one bug.** The same raw string gives `ObjectNotExecutableError` on a bare connection and `ArgumentError` on a session. I had to learn which one the app actually hits before I could write a fake session that fails the right way.
- **Waiting.** I had no control over whether anyone would review the PR. A finished, green PR with no reviewer is an odd place to be, and nothing I did in the codebase could change it.

**What did you learn about working in a large codebase?**
In my own projects I know where everything is and can change anything. Here the first job was finding the smallest region I was allowed to touch.

- **Neighbouring issues.** #62 and #26 edit other lines of the same file, and I had to keep my diff to the Postgres probe lines so rebases stayed clean. A change is only "done" in relation to what else is in flight.
- **Fixing the right amount.** I saw the Redis problem and didn't fix it, because it was a separate issue. I only confirmed with the course team that it should stay separate. Leaving a visible bug alone felt wrong, but bundling it would have made the PR harder to review.
- **The suite is part of the codebase.** `make check` and `make test-unit` (377 passed, 53 xfailed) mattered as much as the code. The 53 xfails show that this project records known bugs as tests, and I followed that convention. I pinned the bug with a strict xfail, then removed the marker when I fixed it.

**How did AI tools help — and where did they fall short?**
I used Claude throughout the module, and it is a co-author on every commit on this branch, from the Unit 7 journal entry through the Unit 9 fix.

- **Where it helped.** It was fastest at reading. It traced `GET /health` to the failing `db.execute("SELECT 1")` in `api/routes/health.py` and explained why SQLAlchemy 2.x rejects a raw string and wants `text()`. It also helped me compare candidate issues against my criteria (one file, unclaimed, verifiable), which is how I ruled out #59 (its fix needs a design choice the issue doesn't specify) and #18 (it spans two modules). It also drafted the Unit 8 strict-xfail test, `tests/unit/test_health.py`, and the PLAN.md.
- **Where it fell short.** The drafted test did not work when I ran it. It patched `core.config.settings.redis_host` with `create=True`, and pydantic rejects that, so I had to patch the whole `settings` object. The Redis problem (#62) also never showed up in reading the code. I only found it when I ran the stack myself and `/health` still returned 503 after the fix, which is why I now verify through `dependencies.postgres` and not the status code. AI also could not decide whether #62 should stay a separate issue, because that was a question for the course team.
- **Takeaway.** The code the AI wrote looked right until I executed it, so I treated it as a draft to test against the live stack and `make test-unit`, not as an answer.

**What would you do differently if you started over?**
- **Ask early about the dependency.** I would have asked about #62 in Unit 7 instead of finding it in Unit 8. I did note the same-file risk in my scope reasoning, but I only discovered the Redis interaction after reproducing the bug against the live stack.
- **Reproduce before committing to an issue.** Reproducing first would have shown that "fixed" and "returns 200" are different things for this endpoint.
- **Get review earlier.** I recorded no draft-PR feedback, so the first outside eyes would have been at submission. I would post the plan and draft to the issue thread sooner and ask a named maintainer or cohort peer to look. That would have improved the odds of getting a review.

**What are you most proud of from this module?**
The strict-xfail test from Unit 8. It pinned the bug in the suite before the fix, so removing the marker in Unit 9 gave direct proof that the change fixed the bug. That reproduction commit made the fix verifiable, and it fit the project's own xfail convention.

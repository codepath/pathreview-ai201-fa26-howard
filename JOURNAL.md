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

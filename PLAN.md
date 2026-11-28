## Solution plan

**Issue:** Health check DB probe passes a raw SQL string, which fails under SQLAlchemy 2.x — https://github.com/codepath/pathreview-ai201-fa26-howard/issues/61

### Understand
**In short:** I'm fixing the `/health` endpoint so it reports Postgres as healthy when the database is actually reachable, instead of always reporting it as down.

**Root cause.** `health_check()` in `api/routes/health.py` (line ~32) runs `await db.execute("SELECT 1")`. SQLAlchemy 2.x (`pyproject.toml` pins `sqlalchemy>=2.0.0`) no longer coerces plain strings into executable SQL; they must be wrapped in `sqlalchemy.text()`. The call raises (`ArgumentError: Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')` on a session; `ObjectNotExecutableError` on a bare connection, which I saw when reproducing). The surrounding `except Exception` swallows it, so the probe always marks Postgres unhealthy.

**Expected:** with Postgres reachable, `dependencies.postgres == "healthy"`; unhealthy only when the DB is actually down.
**Actual:** `GET /health` returns 503 with `"postgres": "unhealthy"` while the Docker Postgres container is up (reproduced locally; see `tests/unit/test_health.py` and the Unit 8 journal entry).

### Map
- `api/routes/health.py` — the one-line fix plus `from sqlalchemy import text` (the only production file I expect to change).
- `tests/unit/test_health.py` — new in the reproduction commit; I will remove its `xfail` marker and add a "DB down" test.
- `core/database.py` — read-only; provides `get_db()` yielding an `AsyncSession` (the object `db.execute` is called on).
- `pyproject.toml` — read-only; the baseline ruff/mypy suppression list is checked in case any entry refers to this probe (CONTRIBUTING.md says to remove suppressions for a fixed issue; the one named for health.py is #62, not mine).

### Plan
1. Re-run `tests/unit/test_health.py` and `curl localhost:8000/health` to confirm the baseline (XFAIL, postgres "unhealthy").
2. In `api/routes/health.py`, add `from sqlalchemy import text` and change the probe to `await db.execute(text("SELECT 1"))`. Touch no other lines (Redis and safety-count lines belong to #62 and #26).
3. In `tests/unit/test_health.py`, delete the `@pytest.mark.xfail(strict=True, ...)` marker (required by CONTRIBUTING.md, otherwise CI fails with XPASS(strict)) and add a test where `db.execute` raises `OperationalError`/`ConnectionRefusedError`, asserting `postgres == "unhealthy"` and the route raises a 503 `HTTPException`.
4. Run `make test-unit`, `make lint` and `make typecheck`; then `curl localhost:8000/health` and confirm `dependencies.postgres` is `"healthy"` with the live DB, and `"unhealthy"` after `docker compose stop postgres`.
5. Open the PR (branch `fix/61-health-check-sql-text`) with before/after output; rebase if #62 or #26 merge first.

### Inputs & outputs
**Input:** a FastAPI request to `GET /health` with an `AsyncSession` injected via `Depends(get_db)`.
**Output:** the same JSON shape as today. Only the value of `dependencies.postgres` changes: `"healthy"` when `SELECT 1` succeeds, `"unhealthy"` (and overall `"unhealthy"` / HTTP 503) only when the query actually fails. No schema, API or frontend changes.

### Risks & unknowns
- **Overall status stays 503 after my fix.** Redis is separately broken (`settings.redis_host` does not exist in `core/config.py`, issue #62), so the endpoint still returns 503 locally. I must verify with the `dependencies.postgres` field, not the status code, and my unit test must patch Redis so the success test is independent of #62.
- **Merge conflicts** with #62 and #26, which edit other lines of `api/routes/health.py`. Mitigation: a one-line change plus an import; rebase before opening the PR.
- **Test fidelity.** My fake session mimics SQLAlchemy's rejection of `str`; I am not yet sure whether a real in-memory async engine (e.g. aiosqlite) is installed to test against a real `AsyncSession`. I'll check `.venv` and fall back to the fake if not.
- **Hidden second bug in the probe?** I plan to read the `except` block and `get_db()` to confirm that a failed probe does not leave the session in a bad state (e.g. needing `rollback()`).

### Edge cases
- Postgres reachable: `postgres == "healthy"`, no error log.
- Postgres down / connection refused / timeout: `execute` raises, caught, `postgres == "unhealthy"`, response is 503.
- `execute` raises a non-DB exception: still handled by the broad `except`, no 500.
- Redis and vector DB failing while Postgres is healthy: Postgres must still be reported `"healthy"` independently, overall status `"unhealthy"`.
- `pool_pre_ping`/stale connection in the pool: the probe should still report correctly rather than crash.

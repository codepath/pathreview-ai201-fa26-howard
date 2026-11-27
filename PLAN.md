## Solution plan

**Issue:** [Issue 26: Adding a safety event count to the health check endpoint][https://github.com/codepath/pathreview-ai201-fa26-howard/issues/26]

### Understand
What is the root cause of this issue? What behavior is expected vs. actual?

The health check reports safety_events_last_hour, but currently it has a placeholder set to 0. The function log_event() is in the safety/monitoring.py file. I need to trace back where the call needs to be in the health.py file and make sure it calls the real total. After getting Claude to help me analyze the code, it found some other issues that I will run into when I may be fixing my issue such as the window_hours being ignored and the need for testing files. 

### Map
Which files, functions, or modules are involved?
List the specific files you expect to touch.

| File | What's there | What I'll change |
|---|---|---|
| `api/routes/health.py` | `health_check()`: the `/health` route. Line 80 hard-codes `safety_events_last_hour = 0`. | Replace the placeholder with a real count from `SafetyMonitor`. |
| `safety/monitoring.py` | `SafetyMonitor`: `log_event()` increments a Redis key per event type (`safety:events:<type>`); `get_event_count()` reads one back. `VALID_EVENT_TYPES` lists the five types. | Read only, no changes. I'll call `get_event_count()` for each type. |
| `core/config.py` | `settings.redis_url` (`redis://localhost:6379/0`). There is no `redis_host`/`redis_port`. | Read only. I'll build the Redis client from `redis_url`. |
| `tests/unit/test_health.py` (new) | Doesn't exist yet. | New unit tests for the safety count. I'll follow the mock-Redis pattern in `tests/unit/test_rate_limiter.py`. |

### Plan
What are the steps to fix this issue?
Break it into 3–5 concrete sub-tasks.

1. **Reproduce.** With Docker and `make run` up, `curl http://localhost:8000/health` and record the response. Then increment a counter by hand (`docker compose exec redis redis-cli INCR safety:events:pii_detected`), call `/health` again, and show that `safety_events_last_hour` still says `0`. That's my reproduction commit.
2. **Get a working Redis client in `health_check()`.** Create it once with `redis.from_url(settings.redis_url, decode_responses=True)` and use it for both the existing Redis ping and the safety count. This also fixes the `settings.redis_host` crash that currently marks Redis unhealthy. I need that client anyway, so the fix comes along with my change.
3. **Replace the placeholder.** Build `SafetyMonitor(redis_client)`, loop over `SafetyMonitor.VALID_EVENT_TYPES`, sum `get_event_count(event_type)` into `safety_events_last_hour`, and also return a per-type breakdown (e.g. `safety_events_by_type`), since the issue says the monitor "can supply per-type counts."
4. **Write unit tests** in `tests/unit/test_health.py` (marked `@pytest.mark.unit`, async via `pytest-asyncio`). Mock the DB session and patch `redis.from_url` so no Docker is needed. Cases:
   - counts from several types are summed correctly
   - no events gives `0`
   - Redis down does not crash the endpoint (see edge cases)
5. **Verify end to end.** Run `make test-unit`, `make lint`, `make format`, then repeat step 1's manual check and confirm the number now matches what I put in Redis.

### Inputs & outputs
What does your fix take as input? What should it produce or change?

- **Input:** a `GET /health` request. The data comes from the Redis keys `safety:events:<type>` that `SafetyMonitor.log_event()` writes, one per type in `VALID_EVENT_TYPES`.
- **Output:** the same JSON as before, but `safety_events_last_hour` is the real total across all event types, plus a per-type breakdown.
  - Before: `"safety_events_last_hour": 0`, always.
  - After (with 2 `pii_detected` + 1 `injection_attempt` recorded): `"safety_events_last_hour": 3`, `"safety_events_by_type": {"pii_detected": 2, "injection_attempt": 1, ...}`.
- **Unchanged:** the 200/503 status logic and the `postgres`/`redis`/`vector_db` fields.

### Risks & unknowns
What could go wrong? What are you still unsure about?

- **"Last hour" isn't really last hour.** `get_event_count()` ignores `window_hours`, and `log_event()` never stores the timestamp (it's marked as a seeded defect). The Redis keys expire after 24 hours, so my number is really "events in roughly the last 24 hours." I'm **not** fixing that here because it's out of scope for this issue. I'll note it in my PR and ask whether a follow-up issue exists.
- **Scope of the Redis fix.** Fixing `redis_host` → `redis_url` is technically a separate bug. I think it belongs in this PR because the safety count can't work without it, but I'll call it out clearly in the PR description in case the maintainer wants it split out.
- **The Postgres check is also broken.** `db.execute("SELECT 1")` needs `text("SELECT 1")` in SQLAlchemy 2, so `/health` returns 503 regardless. That's outside my issue. My tests will mock the DB so they don't depend on it, and I'll mention it in the PR.
- **Nothing calls `log_event()` yet**, so in the running app the count will be `0` until another part of the safety layer records events. That's expected. My tests and manual check create the events themselves.
- **Unsure:** whether the per-type breakdown is wanted or just the total. I'll ask on the issue before finalizing.

### Edge cases
What inputs or states should your fix handle gracefully?

- **No events recorded** (keys don't exist): count is `0`, not an error. `get_event_count()` already returns `0` for a missing key.
- **Redis is down:** `get_event_count()` catches errors and returns `0`. The Redis check should already mark Redis unhealthy, and the safety count must not crash the endpoint or hide the real problem.
- **Safety count fails for an unexpected reason:** log it and leave the count at `0`. It's informational, so it shouldn't flip `status` to unhealthy on its own.
- **Unknown event types in Redis:** only the types in `VALID_EVENT_TYPES` are counted, so stray keys are ignored.
- **Many events:** values are summed as ints, so there are no overflow or formatting issues at realistic volumes.
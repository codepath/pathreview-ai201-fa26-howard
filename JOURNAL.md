## Unit 7 — Issue selection

**Issue link:** [[https://github.com/codepath/pathreview-ai201-fa26-howard/issues/34]] 
**Issue title:** [Add an API rate limiting header (X-RateLimit-Remaining) to responses]

**Tier:** [ ] Tier 1  [X] Tier 2  [ ] Tier 3

**Problem summary:**
[PathReview's API has rate-limiting logic, but nothing ever uses it. The check_rate_limit function in safety/rate_limiter.py is defined but never called from the FastAPI app in api/. So clients can send unlimited requests, the API never returns a 429 Too Many Requests error, and responses don't tell callers their limit or how many requests they have left. A successful fix adds a middleware in api/middleware/ and registers it in api/main.py, so every request goes through check_rate_limit. That middleware would add X-RateLimit-Limit and X-RateLimit-Remaining headers to each response and return 429 once a client goes over its limit.]

**Branch name:** [feat/34-Add-an-API-rate-limiting-header]

**Setup confirmation:** [Y] App runs locally at localhost:5173

**Cohort ledger:** [Y] Issue added to cohort ledger

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** [https://github.com/ndorvelus/pathreview-ai201-fa26-howard/commit/c742db46d832dae1fb7b3915e15ca67ad7f76f32]

**Reproduction summary:**
Using FastAPI's TestClient against `api.main:app`, I sent 70 requests to `GET /`, 10 more than the configured `rate_limit_per_minute = 60` in `core/config.py`, and all 70 returned `200` with no `429` and no `X-RateLimit-Limit` or `X-RateLimit-Remaining` header (only `x-request-id`). The app's only middleware is `RequestIDMiddleware` and `CORSMiddleware`, and `RateLimiter.check_rate_limit` in `safety/rate_limiter.py` is never called outside its own unit tests, which all pass.

**PLAN.md link:** [https://github.com/ndorvelus/pathreview-ai201-fa26-howard/blob/feat/34-Add-an-API-rate-limiting-header/PLAN.md]

**Walkthrough video (recommended):** [link to your Loom video, ≤2 min — recommended, not graded]

**Blockers or open questions:**
[Anything you're still uncertain about going into Unit 9, or leave blank]

## Unit 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
PLAN.md sub-tasks 1–4 are done. I wrote `RateLimitMiddleware` in `api/middleware/rate_limit.py`. It calls `check_rate_limit` with the client IP, sets `X-RateLimit-Limit` and `X-RateLimit-Remaining`, and returns `429` with `Retry-After` once a client is over the limit. I registered it in `api/main.py` inside CORS and exposed the headers to the frontend. It skips `/health`, the docs routes, and CORS preflights. I also wrote 15 unit tests in `tests/unit/test_rate_limit_middleware.py`, and they all pass.

**Next steps:**
Finish sub-task 5: run `make check` and `make test-unit` and rerun the 70-request reproduction. Then commit following CONTRIBUTING.md, open a draft PR, and ask for peer feedback in Slack.

**Blockers:**
Docker isn't running locally, so I can't test against a real Redis. I'll verify the 429 behavior with an in-memory Redis stand-in instead. I'm also still unsure whether maintainers want limits per IP or per user.

---

### Check-in 2 (end of week)

**PR link:** [https://github.com/codepath/pathreview-ai201-fa26-howard/pull/114]

**Branch:** `feat/34-Add-an-API-rate-limiting-header`

**What you built:**
I added `RateLimitMiddleware`, which runs every API request through the existing `RateLimiter.check_rate_limit`, keyed by client IP and `settings.rate_limit_per_minute`. Allowed responses now carry `X-RateLimit-Limit` and `X-RateLimit-Remaining`. Requests over the limit get `429` with `Retry-After` and never reach the route. Rerunning the 70-request reproduction now gives 60 `200`s (remaining counts down from 59 to 0) followed by 10 `429`s.

**Tests added or updated:**
I added `tests/unit/test_rate_limit_middleware.py` with 15 tests. They cover:
- headers on allowed responses
- the countdown to `429`, and the route not running on `429`
- exempt paths and CORS preflights
- a limit of 0 turning limiting off
- the limiter failing (requests are still served)
- CORS headers on `429`
- the middleware's registration order in `api/main.py`

No xfail markers were tied to #34.

**Self-review confirmation:** [x] make check passes  [x] make test-unit passes

**Draft PR feedback received from:** Nathan Dorvelus
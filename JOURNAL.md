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

**Reproduction commit link:** [link to commit documenting the reproduced issue]

**Reproduction summary:**
Using FastAPI's TestClient against `api.main:app`, I sent 70 requests to `GET /`, 10 more than the configured `rate_limit_per_minute = 60` in `core/config.py`, and all 70 returned `200` with no `429` and no `X-RateLimit-Limit` or `X-RateLimit-Remaining` header (only `x-request-id`). The app's only middleware is `RequestIDMiddleware` and `CORSMiddleware`, and `RateLimiter.check_rate_limit` in `safety/rate_limiter.py` is never called outside its own unit tests, which all pass.

**PLAN.md link:** [link to PLAN.md in your fork]

**Walkthrough video (recommended):** [link to your Loom video, ≤2 min — recommended, not graded]

**Blockers or open questions:**
[Anything you're still uncertain about going into Unit 9, or leave blank]
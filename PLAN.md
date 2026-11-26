## Solution plan

**Issue:** [Add an API rate limiting header (X-RateLimit-Remaining) to responses https://github.com/codepath/pathreview-ai201-fa26-howard/issues/34]

### Understand
`RateLimiter.check_rate_limit` in `safety/rate_limiter.py` works, but nothing in `api/` calls it. `api/main.py` only registers `CORSMiddleware` and `RequestIDMiddleware`, and `rate_limit_per_minute = 60` in `core/config.py` is never read.

Expected: every response carries `X-RateLimit-Limit` and `X-RateLimit-Remaining`, and a client over the limit gets `429`.
Actual: I sent 70 requests to `GET /` and all 70 returned `200` with neither header.

### Map
Files I'll touch:
- `api/middleware/rate_limit.py` (new): `RateLimitMiddleware`, built like `api/middleware/request_id.py`.
- `api/main.py`: create the Redis client, register the middleware, and expose the new headers through CORS.
- `tests/unit/test_rate_limit_middleware.py` (new): middleware tests with a mocked Redis client.

Files I'll rely on without changing: `safety/rate_limiter.py` and `core/config.py`.

### Plan
1. Write `RateLimitMiddleware`. It calls `check_rate_limit` with the client IP and `settings.rate_limit_per_minute`, adds both headers to the response, and returns a `429` with `Retry-After: 60` when the client is over the limit.
2. In `api/main.py`, create the client with `redis.Redis.from_url(settings.redis_url)` and register the middleware. Add the headers to CORS `expose_headers` so the frontend can read them.
3. Skip `OPTIONS` requests, `/health`, and the docs routes so they don't count against the limit.
4. Write tests for the headers, the 429 after the limit, skipped paths, and Redis being down.
5. Rerun the 70-request reproduction. I expect 60 `200`s and then 10 `429`s. Then run `tests/unit`.

### Inputs & outputs
Input: each request's method, path, and client IP, plus `rate_limit_per_minute` and `redis_url` from config.
Under the limit: the normal response plus `X-RateLimit-Limit: 60` and `X-RateLimit-Remaining: <n>`.
Over the limit: `429`, `{"detail": "Rate limit exceeded"}`, `Remaining: 0`, and `Retry-After: 60`. The route handler doesn't run.

### Risks & unknowns
- `RateLimiter` uses the synchronous Redis client, so it blocks the event loop inside async middleware. I may need `run_in_threadpool` or `redis.asyncio`.
- If Redis is down, the limiter lets the request through but reports the full limit as remaining, which is misleading. I haven't decided whether to send the headers in that case. I also can't test against real Redis yet because it only runs through `docker-compose.yml`.
- Middleware runs before auth (`get_current_user` in `api/middleware/auth.py` is a per-route dependency), so I'll limit by IP for now. Behind a proxy every client could share one IP, and `X-Forwarded-For` can be spoofed. I'll ask on the issue whether maintainers want per-user limits.
- Starlette runs the last-added middleware first. The limiter has to be added before CORS so `429` responses still get CORS headers.
- `health.py` uses `settings.redis_host`, which doesn't exist (issue #62), so I'll use `redis_url` instead.
- The existing `test_rate_limiter.py` took about 4m45s to run locally. I don't know why yet.

### Edge cases
- Request 60 is allowed with `Remaining: 0`, and request 61 gets `429`. The header should never go negative.
- A limit of 0 or below in the environment would reject every request. I'll either validate it in config or treat it as disabled.
- When Redis is down, requests should still be served instead of returning a 500.
- `request.client` can be `None`, so I'll fall back to a fixed identifier.
- If the route raises an exception, the existing 500 handler should still work.
- After 60 quiet seconds, the window should reset to the full limit.

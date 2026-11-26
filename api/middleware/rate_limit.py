from collections.abc import Iterable

import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from safety.rate_limiter import RateLimiter

log = structlog.get_logger()

DEFAULT_EXEMPT_PATHS: frozenset[str] = frozenset(
    {"/health", "/docs", "/docs/oauth2-redirect", "/redoc", "/openapi.json"}
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Enforce a per-client rate limit and report it in response headers.

    Each request is counted against the client's IP address using
    ``RateLimiter.check_rate_limit``. Allowed responses get ``X-RateLimit-Limit``
    and ``X-RateLimit-Remaining`` headers. Requests over the limit get a 429 with
    the same headers plus ``Retry-After`` and never reach the route handler.

    CORS preflight requests and the paths in ``exempt_paths`` are not counted.
    A ``limit`` of 0 or below disables rate limiting. If the limiter raises, the
    request is served without rate limit headers (fail open).
    """

    def __init__(
        self,
        app: ASGIApp,
        limiter: RateLimiter,
        limit: int,
        window_seconds: int = 60,
        exempt_paths: Iterable[str] = DEFAULT_EXEMPT_PATHS,
    ) -> None:
        """Initialize the middleware.

        Args:
            app: The ASGI application to wrap.
            limiter: Rate limiter that tracks requests per identifier.
            limit: Maximum requests allowed per client in each window.
            window_seconds: Length of the rolling window in seconds.
            exempt_paths: Paths that are never counted or limited.
        """
        super().__init__(app)
        self.limiter = limiter
        self.limit = limit
        self.window_seconds = window_seconds
        self.exempt_paths = frozenset(exempt_paths)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Check the rate limit, then either reject the request or add headers.

        Args:
            request: The incoming request.
            call_next: Calls the next middleware or the route handler.

        Returns:
            The route's response with rate limit headers, or a 429 response.
        """
        if self._is_exempt(request):
            return await call_next(request)

        identifier = request.client.host if request.client else "unknown"

        try:
            # RateLimiter uses the synchronous Redis client, so keep it off the event loop.
            allowed, remaining = await run_in_threadpool(
                self.limiter.check_rate_limit,
                identifier,
                limit=self.limit,
                window_seconds=self.window_seconds,
            )
        except Exception as exc:
            log.error("rate_limit_check_failed", identifier=identifier, error=str(exc))
            return await call_next(request)

        headers = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(max(remaining, 0)),
        }

        if not allowed:
            log.warning("rate_limit_rejected", identifier=identifier, path=request.url.path)
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={**headers, "Retry-After": str(self.window_seconds)},
            )

        response = await call_next(request)
        response.headers.update(headers)
        return response

    def _is_exempt(self, request: Request) -> bool:
        """Return True if this request should skip rate limiting.

        Args:
            request: The incoming request.

        Returns:
            True for disabled limits, CORS preflights, and exempt paths.
        """
        return (
            self.limit <= 0 or request.method == "OPTIONS" or request.url.path in self.exempt_paths
        )

"""Tests for api/middleware/rate_limit.py"""

from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from api.middleware.rate_limit import RateLimitMiddleware


def build_app(limiter: Mock, limit: int = 5, window_seconds: int = 60) -> FastAPI:
    """Build a minimal app wrapped in RateLimitMiddleware."""
    app = FastAPI()
    handler_calls: list[str] = []

    @app.get("/items")
    async def items():
        handler_calls.append("items")
        return {"ok": True}

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    @app.get("/boom")
    async def boom():
        raise RuntimeError("route failure")

    app.add_middleware(
        RateLimitMiddleware,
        limiter=limiter,
        limit=limit,
        window_seconds=window_seconds,
    )
    app.state.handler_calls = handler_calls
    return app


@pytest.mark.unit
class TestRateLimitMiddleware:
    """Test suite for RateLimitMiddleware."""

    @pytest.fixture
    def limiter(self):
        """Create a mock RateLimiter that allows requests."""
        limiter = Mock()
        limiter.check_rate_limit = Mock(return_value=(True, 4))
        return limiter

    def test_allowed_request_sets_headers(self, limiter):
        """Allowed responses carry the limit and remaining headers."""
        client = TestClient(build_app(limiter, limit=5))

        response = client.get("/items")

        assert response.status_code == 200
        assert response.headers["X-RateLimit-Limit"] == "5"
        assert response.headers["X-RateLimit-Remaining"] == "4"

    def test_limiter_called_with_client_ip_and_settings(self, limiter):
        """The limiter is keyed on client IP with the configured limit and window."""
        client = TestClient(build_app(limiter, limit=5, window_seconds=30))

        client.get("/items")

        limiter.check_rate_limit.assert_called_once_with("testclient", limit=5, window_seconds=30)

    def test_rejected_request_returns_429(self, limiter):
        """Requests over the limit get 429 and never reach the route handler."""
        limiter.check_rate_limit.return_value = (False, 0)
        app = build_app(limiter, limit=5, window_seconds=60)
        client = TestClient(app)

        response = client.get("/items")

        assert response.status_code == 429
        assert response.json() == {"detail": "Rate limit exceeded"}
        assert response.headers["X-RateLimit-Limit"] == "5"
        assert response.headers["X-RateLimit-Remaining"] == "0"
        assert response.headers["Retry-After"] == "60"
        assert app.state.handler_calls == []

    def test_remaining_counts_down_then_rejects(self, limiter):
        """Remaining counts down to 0, then the next request is rejected."""
        limiter.check_rate_limit.side_effect = [(True, 2), (True, 1), (True, 0), (False, 0)]
        client = TestClient(build_app(limiter, limit=3))

        responses = [client.get("/items") for _ in range(4)]

        assert [r.status_code for r in responses] == [200, 200, 200, 429]
        assert [r.headers["X-RateLimit-Remaining"] for r in responses] == ["2", "1", "0", "0"]

    def test_remaining_never_negative(self, limiter):
        """A negative remaining value from the limiter is clamped to 0."""
        limiter.check_rate_limit.return_value = (True, -1)
        client = TestClient(build_app(limiter, limit=5))

        response = client.get("/items")

        assert response.headers["X-RateLimit-Remaining"] == "0"

    @pytest.mark.parametrize("path", ["/health", "/docs", "/openapi.json"])
    def test_exempt_paths_skip_limiter(self, limiter, path):
        """Health and docs routes are not counted and carry no rate limit headers."""
        client = TestClient(build_app(limiter))

        response = client.get(path)

        assert response.status_code == 200
        assert "X-RateLimit-Limit" not in response.headers
        limiter.check_rate_limit.assert_not_called()

    def test_options_preflight_skips_limiter(self, limiter):
        """CORS preflight requests are not counted against the limit."""
        client = TestClient(build_app(limiter))

        client.options("/items")

        limiter.check_rate_limit.assert_not_called()

    def test_zero_limit_disables_rate_limiting(self, limiter):
        """A limit of 0 or below turns rate limiting off instead of rejecting everything."""
        client = TestClient(build_app(limiter, limit=0))

        response = client.get("/items")

        assert response.status_code == 200
        assert "X-RateLimit-Limit" not in response.headers
        limiter.check_rate_limit.assert_not_called()

    def test_limiter_error_fails_open(self, limiter):
        """An unexpected limiter error still serves the request without headers."""
        limiter.check_rate_limit.side_effect = ConnectionError("redis down")
        client = TestClient(build_app(limiter))

        response = client.get("/items")

        assert response.status_code == 200
        assert "X-RateLimit-Limit" not in response.headers

    def test_route_exception_still_propagates(self, limiter):
        """A failing route still surfaces as a server error, not a rate limit response."""
        client = TestClient(build_app(limiter), raise_server_exceptions=False)

        response = client.get("/boom")

        assert response.status_code == 500

    def test_rejection_keeps_cors_headers(self, limiter):
        """A 429 still carries CORS headers when CORS wraps the rate limiter."""
        limiter.check_rate_limit.return_value = (False, 0)
        app = build_app(limiter)
        app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"])
        client = TestClient(app)

        response = client.get("/items", headers={"Origin": "http://localhost:5173"})

        assert response.status_code == 429
        assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


@pytest.mark.unit
class TestRateLimitMiddlewareRegistration:
    """Tests that api.main wires the middleware in the right place."""

    def test_registered_inside_cors(self):
        """RateLimitMiddleware is registered and sits inside CORSMiddleware."""
        from api.main import app

        names = [m.cls.__name__ for m in app.user_middleware]

        assert "RateLimitMiddleware" in names
        # user_middleware is ordered outermost first.
        assert names.index("CORSMiddleware") < names.index("RateLimitMiddleware")

    def test_cors_exposes_rate_limit_headers(self):
        """The frontend can read the rate limit headers through CORS."""
        from api.main import app

        cors = next(m for m in app.user_middleware if m.cls.__name__ == "CORSMiddleware")

        exposed = cors.kwargs["expose_headers"]
        assert "X-RateLimit-Limit" in exposed
        assert "X-RateLimit-Remaining" in exposed

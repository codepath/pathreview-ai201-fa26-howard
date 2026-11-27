from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from api.routes.health import health_check
from safety.monitoring import SafetyMonitor


@pytest.mark.unit
class TestHealthCheck:
    """Test suite for Health Check."""

    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        return Mock()

    @pytest.fixture
    def safety_monitor(self, mock_redis):
        """Create a SafetyMonitor instance with mock Redis."""
        return SafetyMonitor(redis_client=mock_redis)

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, safety_monitor):
        """Test health check when all dependencies are healthy."""
        # Mock Redis ping to succeed
        safety_monitor.redis.ping.return_value = True

        with patch("redis.from_url", return_value=safety_monitor.redis):
            response = await health_check(db=AsyncMock())

        assert response["status"] == "healthy"
        assert response["dependencies"]["postgres"] == "healthy"
        assert response["dependencies"]["redis"] == "healthy"
        assert response["dependencies"]["vector_db"] in ["healthy", "unavailable"]

    @pytest.mark.asyncio
    async def test_health_check_unhealthy_redis(self, safety_monitor):
        """Test health check when Redis is unhealthy."""
        # Mock Redis ping to raise an exception
        safety_monitor.redis.ping.side_effect = Exception("Redis down")

        # When a dependency is down, health_check() raises a 503 instead of returning
        with (
            patch("redis.from_url", return_value=safety_monitor.redis),
            pytest.raises(HTTPException) as exc_info,
        ):
            await health_check(db=AsyncMock())

        assert exc_info.value.status_code == 503
        detail: dict = exc_info.value.detail  # type: ignore[assignment]  # health.py passes a dict
        assert detail["status"] == "unhealthy"
        assert detail["dependencies"]["redis"] == "unhealthy"
        # Safety counts are skipped when Redis is down, so the field stays at 0
        assert detail["safety_events_last_hour"] == 0

    @pytest.mark.asyncio
    async def test_health_count_safety_events(self, safety_monitor):
        """Test that the health check includes safety event counts."""
        # Mock Redis to return a count for a specific event type
        safety_monitor.redis.get.return_value = "5"

        with patch("redis.from_url", return_value=safety_monitor.redis):
            response = await health_check(db=AsyncMock())

        # The mock returns "5" for every key, and there are 5 event types: 5 x 5 = 25
        assert response["safety_events_last_hour"] == 25

    @pytest.mark.asyncio
    async def test_health_log_safety_event(self, safety_monitor):
        """Test that logging a safety event works and increments the count."""
        # Log a safety event
        event_type = "pii_detected"
        details = {"user_id": "123", "severity": "high"}
        safety_monitor.log_event(event_type, details)

        # Check that Redis incr was called with the correct key
        expected_key = f"safety:events:{event_type}"
        safety_monitor.redis.incr.assert_called_with(expected_key)

"""Tests for the /health route (api/routes/health.py)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import ArgumentError, OperationalError
from sqlalchemy.sql.elements import ClauseElement

from api.routes.health import health_check


def make_session():
    """Fake AsyncSession whose execute() mimics SQLAlchemy 2.x: a bare str is rejected."""

    async def execute(statement, *args, **kwargs):
        if not isinstance(statement, ClauseElement):
            raise ArgumentError(
                f"Textual SQL expression {statement!r} should be explicitly "
                f"declared as text({statement!r})"
            )

    session = AsyncMock()
    session.execute = AsyncMock(side_effect=execute)
    return session


@pytest.mark.unit
class TestHealthPostgresProbe:
    """Postgres probe in health_check."""

    @pytest.mark.asyncio
    async def test_postgres_reported_healthy_when_db_reachable(self):
        """A reachable DB must be reported healthy (Redis patched out of the picture)."""
        session = make_session()
        with patch("redis.Redis") as redis_cls:
            redis_cls.return_value.ping.return_value = True
            with (
                patch("core.config.settings", MagicMock(redis_host="localhost", redis_port=6379)),
            ):
                result = await health_check(db=session)
        assert result["dependencies"]["postgres"] == "healthy"

    @pytest.mark.asyncio
    async def test_postgres_reported_unhealthy_when_db_down(self):
        """A failing DB must be reported unhealthy and the route must return 503."""
        session = AsyncMock()
        session.execute = AsyncMock(
            side_effect=OperationalError("SELECT 1", {}, ConnectionRefusedError())
        )
        with patch("redis.Redis") as redis_cls:
            redis_cls.return_value.ping.return_value = True
            with (
                patch("core.config.settings", MagicMock(redis_host="localhost", redis_port=6379)),
                pytest.raises(HTTPException) as exc_info,
            ):
                await health_check(db=session)
        assert exc_info.value.status_code == 503
        assert exc_info.value.detail["dependencies"]["postgres"] == "unhealthy"

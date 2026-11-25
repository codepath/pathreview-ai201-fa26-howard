"""Login-route regression tests using the real password verifier."""

from collections.abc import AsyncIterator, Iterator
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routes.auth import router
from core.database import get_db
from core.security import decode_access_token, hash_password


@pytest.fixture
def login_context() -> Iterator[tuple[TestClient, SimpleNamespace]]:
    """Provide an isolated auth app with a synthetic database user."""
    user = SimpleNamespace(
        id=str(uuid4()),
        email="login-test@example.com",
        hashed_password="",
        is_active=True,
    )
    result = Mock()
    result.scalar_one_or_none.return_value = user
    database = SimpleNamespace(execute=AsyncMock(return_value=result))

    async def override_db() -> AsyncIterator[SimpleNamespace]:
        """Replace database I/O while keeping authentication code real."""
        yield database

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = override_db

    with TestClient(app) as client:
        yield client, user


@pytest.mark.unit
class TestLogin:
    """Test credential rejection and the valid-login control."""

    @pytest.mark.parametrize(
        "stored_hash",
        [
            "not_a_valid_bcrypt_hash",
            "",
            "5f4dcc3b5aa765d61d8327deb882cf99",
            "$2b$12$invalid",
        ],
        ids=["unrecognized", "empty", "unsupported", "truncated-bcrypt"],
    )
    def test_malformed_stored_hash_returns_401(self, login_context, stored_hash):
        """Reject malformed stored hashes with the normal credentials error."""
        client, user = login_context
        user.hashed_password = stored_hash

        response = client.post("/auth/login", data={"username": user.email, "password": "password"})

        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid email or password"}
        assert response.headers["www-authenticate"] == "Bearer"

    def test_valid_password_returns_access_token(self, login_context):
        """Keep a valid password able to authenticate the synthetic user."""
        client, user = login_context
        user.hashed_password = hash_password("correct_password")

        response = client.post(
            "/auth/login", data={"username": user.email, "password": "correct_password"}
        )

        assert response.status_code == 200
        assert response.json()["token_type"] == "bearer"
        claims = decode_access_token(response.json()["access_token"])
        assert claims is not None
        assert claims["sub"] == user.id

    def test_wrong_password_returns_401(self, login_context):
        """Keep incorrect passwords rejected against a valid stored hash."""
        client, user = login_context
        user.hashed_password = hash_password("correct_password")

        response = client.post(
            "/auth/login", data={"username": user.email, "password": "wrong_password"}
        )

        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid email or password"}
        assert response.headers["www-authenticate"] == "Bearer"

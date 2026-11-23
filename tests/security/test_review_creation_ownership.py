"""Regression coverage for profile ownership when creating reviews (issue #67)."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI

from api.middleware.auth import get_current_user
from api.routes.reviews import router
from core.database import get_db


@pytest.mark.security
@pytest.mark.asyncio
@pytest.mark.parametrize("profile_case", ["another_user", "missing", "owned"])
async def test_create_review_checks_profile_ownership(
    profile_case, make_profile_lookup_session, user_a_profile, user_a_id, user_b_id
):
    profile_id = uuid4() if profile_case == "missing" else user_a_profile.id
    user_id = user_b_id if profile_case == "another_user" else user_a_id
    owned_profile = user_a_profile if profile_case == "owned" else None
    db = make_profile_lookup_session(query_result=owned_profile)

    async def refresh(review):
        review.id = uuid4()
        review.created_at = datetime.now()
        review.updated_at = review.created_at

    db.refresh.side_effect = refresh
    app = FastAPI()
    app.include_router(router)

    async def current_user():
        return Mock(id=user_id)

    async def database():
        return db

    app.dependency_overrides[get_current_user] = current_user
    app.dependency_overrides[get_db] = database

    with patch("api.routes.reviews.process_review", new_callable=AsyncMock) as process:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post("/reviews", json={"profile_id": str(profile_id)})

    # Verify that the database lookup includes both the requested profile and caller.
    query = db.execute.call_args.args[0]
    params = query.compile().params
    assert params == {"id_1": profile_id, "user_id_1": user_id}

    if profile_case == "owned":
        assert response.status_code == 200
        assert response.json()["status"] == "pending"
        assert response.json()["profile_id"] == str(profile_id)
        db.add.assert_called_once()
        db.commit.assert_awaited_once()
        process.assert_awaited_once()
    else:
        assert response.status_code == 404
        assert response.json() == {"detail": "Profile not found"}
        db.add.assert_not_called()
        db.commit.assert_not_called()
        db.refresh.assert_not_called()
        process.assert_not_called()

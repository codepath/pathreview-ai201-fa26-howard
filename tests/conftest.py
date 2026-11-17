"""Shared test fixtures for PathReview."""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest


@pytest.fixture
def user_a_id():
    """ID of the user who owns the profile (User A)."""
    return uuid4()


@pytest.fixture
def user_b_id():
    """ID of a different authenticated user (User B)."""
    return uuid4()


@pytest.fixture
def user_a_profile(user_a_id):
    """A profile owned by User A."""
    profile = Mock()
    profile.id = uuid4()
    profile.user_id = user_a_id
    return profile


@pytest.fixture
def make_profile_lookup_session():
    """
    Factory for a mock async DB session whose profile lookups are scripted.

    ``query_result`` is what an ownership-filtered query returns
    (``select(Profile).where(Profile.id == ..., Profile.user_id == ...)``):
    the profile when the caller owns it, otherwise None.

    ``get_result`` is what an unfiltered primary-key lookup
    (``db.get(Profile, profile_id)``) returns: the profile whenever it exists,
    regardless of who owns it.

    Both styles are scripted so the tests hold no matter which lookup the fix uses.
    The result object is a plain Mock (not AsyncMock), since ``Result.scalars()``
    is synchronous in SQLAlchemy.
    """

    def _make(query_result=None, get_result=None):
        result = Mock()
        result.scalars.return_value.first.return_value = query_result
        result.scalar_one_or_none.return_value = query_result
        result.scalar.return_value = query_result
        result.first.return_value = query_result

        session = AsyncMock()
        session.add = Mock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.rollback = AsyncMock()
        session.execute = AsyncMock(return_value=result)
        session.get = AsyncMock(return_value=get_result)
        return session

    return _make


@pytest.fixture
def sample_resume_text() -> str:
    """Return a sample resume text for testing."""
    return """
    Jane Doe
    Software Engineer
    jane.doe@example.com | github.com/janedoe

    Experience:
    - Software Engineer at TechCorp (2022-2024)
      Built REST APIs using Python and FastAPI.

    Education:
    - B.S. Computer Science, State University (2022)

    Skills: Python, JavaScript, React, PostgreSQL, Docker
    """


@pytest.fixture
def sample_readme_text() -> str:
    """Return a sample README text for testing."""
    return """
    # Weather App
    A weather forecasting application built with React and OpenWeatherMap API.

    ## Features
    - Current weather display
    - 5-day forecast
    - Location search

    ## Tech Stack
    - React 18
    - TypeScript
    - Tailwind CSS
    - OpenWeatherMap API
    """

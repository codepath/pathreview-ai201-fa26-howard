"""Shared test fixtures for PathReview."""

from collections.abc import Iterator

import pytest
import structlog

from core.logging import configure_logging


@pytest.fixture(scope="session", autouse=True)
def _route_structlog_to_stdlib() -> Iterator[None]:
    """Configure structlog to log through the standard library during tests.

    Without this, structlog uses its unconfigured default and prints straight
    to the terminal, so pytest's ``caplog`` never receives any log records.
    """
    configure_logging()
    yield
    structlog.reset_defaults()


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

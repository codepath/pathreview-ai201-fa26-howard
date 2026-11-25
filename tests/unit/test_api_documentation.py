"""Validate the API reference's request examples against the request schemas."""

import json
import re
import shlex
from pathlib import Path

import pytest

from api.schemas.profile import ProfileCreate
from api.schemas.review import ReviewCreate


@pytest.fixture
def api_reference() -> str:
    """Read the checked-in reference so tests validate the published examples."""
    return (Path(__file__).resolve().parents[2] / "docs" / "API.md").read_text()


@pytest.mark.unit
def test_documented_review_example_matches_request_schema(api_reference: str):
    """Ensure readers get a complete, valid JSON request for review creation."""
    reviews = api_reference.split("### Reviews", 1)[1].split("## Interactive Docs", 1)[0]
    examples = re.findall(r"```json\n(.*?)\n```", reviews, re.DOTALL)
    assert len(examples) == 1, "Document one JSON request example for POST /reviews"
    payload = json.loads(examples[0])
    assert set(payload) == set(ReviewCreate.model_fields)
    ReviewCreate.model_validate(payload)
    commands = re.findall(r"```bash\n(.*?)\n```", reviews, re.DOTALL)
    assert len(commands) == 1
    tokens = shlex.split(commands[0].replace("\\\n", ""))
    assert tokens[0] == "curl"
    assert "http://localhost:8000/reviews" in tokens
    assert "Authorization: Bearer $TOKEN" in tokens
    assert "Content-Type: application/json" in tokens
    assert json.loads(tokens[tokens.index("-d") + 1]) == payload


@pytest.mark.unit
def test_documented_profile_command_uses_valid_multipart_fields(api_reference: str):
    """Catch wrong content types, field names, and invalid profile example values."""
    profiles = api_reference.split("### Profiles", 1)[1].split("### Reviews", 1)[0]
    examples = re.findall(r"```bash\n(.*?)\n```", profiles, re.DOTALL)
    assert len(examples) == 1, "Document one curl request example for POST /profiles"
    tokens = shlex.split(examples[0].replace("\\\n", ""))
    assert tokens[0] == "curl"
    assert "http://localhost:8000/profiles" in tokens
    assert "Authorization: Bearer $TOKEN" in tokens
    assert not any(token.lower().startswith("content-type:") for token in tokens)
    fields = dict(
        tokens[index + 1].split("=", 1)
        for index, token in enumerate(tokens)
        if token in {"-F", "--form"}
    )
    assert set(fields) == set(ProfileCreate.model_fields) | {"resume_file"}
    upload = fields.pop("resume_file")
    assert upload.startswith("@"), "Upload the file contents rather than its path as text"
    assert upload.endswith(";type=text/markdown")
    ProfileCreate.model_validate(fields)

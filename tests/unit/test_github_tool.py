"""Tests for reading dependency manifests from a submitted repository."""

import base64
import json
from pathlib import Path

import httpx
import pytest

from agent.tools.github_tool import GitHubTool

pytestmark = pytest.mark.unit
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "dependency_audit"


def test_fetches_nested_manifest_and_keeps_results_after_partial_failure(monkeypatch):
    """Read regular files from the default branch and report incomplete coverage."""
    called = []
    repo = "/repos/user/project"
    manifest = '{"dependencies":{}}'
    tree = json.loads((FIXTURES / "github_tree.json").read_text())

    def respond(request):
        called.append(request.url.path)
        assert request.url.host == "api.github.com"
        assert request.headers["Authorization"] == "token test-token"
        if request.url.path == repo:
            return httpx.Response(200, json={"default_branch": "default-branch"})
        if request.url.path == f"{repo}/git/trees/default-branch":
            assert request.url.params["recursive"] == "1"
            return httpx.Response(200, json=tree)
        if request.url.path == f"{repo}/git/blobs/{'1' * 40}":
            return httpx.Response(
                200,
                json={
                    "encoding": "base64",
                    "content": base64.b64encode(manifest.encode()).decode(),
                },
            )
        if request.url.path == f"{repo}/git/blobs/{'2' * 40}":
            return httpx.Response(403)
        pytest.fail(f"Unexpected request: {request.url}")

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        monkeypatch.setattr(httpx, "stream", client.stream)
        manifests, warnings = GitHubTool(api_token="test-token").fetch_dependency_manifests(
            "user", "project"
        )

    assert manifests == {"frontend/package.json": manifest}
    assert len(called) == 4
    assert any("truncated" in warning for warning in warnings)
    assert any("pyproject.toml" in warning and "403" in warning for warning in warnings)
    assert any("large/requirements.txt" in warning for warning in warnings)


def test_returns_warning_when_repository_lookup_fails(monkeypatch):
    """Expose a repository lookup failure as incomplete discovery."""
    with httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(404))) as client:
        monkeypatch.setattr(httpx, "stream", client.stream)
        manifests, warnings = GitHubTool().fetch_dependency_manifests("user", "missing")

    assert manifests == {}
    assert any("404" in warning for warning in warnings)

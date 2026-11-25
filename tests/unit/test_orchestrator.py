"""Tests for dependency audit planning and execution."""

from pathlib import Path

import pytest

from agent.orchestrator import Orchestrator
from agent.tools import dependency_audit_tool
from agent.tools.base import ToolResult
from agent.tools.dependency_audit_tool import DependencyAuditTool
from agent.tools.github_tool import GitHubTool
from agent.tools.market_analyzer import MarketAnalyzer
from agent.tools.tech_detector import TechDetector

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[2]


def test_default_audit_finds_outdated_dependencies_in_pathreview(monkeypatch):
    """Repeat the journal reproduction with manifest contents and fixed releases."""
    current = {"vite": "8.0.0", "vitest": "5.0.0"}
    monkeypatch.setattr(
        dependency_audit_tool, "_fetch_latest_version", lambda ecosystem, name: current.get(name)
    )
    tools = {tool.name: tool for tool in (TechDetector(), MarketAnalyzer())}
    path = "frontend/package.json"
    profile = {
        "files": ["pyproject.toml", path, "frontend/package-lock.json"],
        "manifests": {path: (ROOT / path).read_text()},
    }
    results = Orchestrator(tools).run("issue-20", profile)["tool_results"]

    assert [
        (item["package"], item["major_gap"]) for item in results["dependency_audit"]["findings"]
    ] == [
        ("vite", 3),
        ("vitest", 4),
    ]
    assert "tech_detector" in results
    assert "dependency_audit" not in tools


def test_audit_reuses_configured_github_tool_and_reads_fresh_manifests(monkeypatch):
    """Select the first submitted repository and fetch its manifests on each run."""
    github = GitHubTool(api_token="test-token")
    monkeypatch.setattr(github, "execute", lambda _: ToolResult(True, {}))
    monkeypatch.setattr(dependency_audit_tool, "_fetch_latest_version", lambda *_: "8.0.0")
    contents = iter(("example==1.0", "example==8.0"))
    fetches = []

    def fetch(username, repo_name):
        fetches.append((username, repo_name, github.api_token))
        return {"requirements.txt": next(contents)}, ["One manifest could not be read"]

    monkeypatch.setattr(github, "fetch_dependency_manifests", fetch)
    orchestrator = Orchestrator({github.name: github, MarketAnalyzer.name: MarketAnalyzer()})
    profile = {
        "github_username": "user",
        "projects": [{}, {"github_repo": "first"}, {"github_repo": "second"}],
    }
    first = orchestrator.run("profile", profile)["tool_results"]["dependency_audit"]
    second = orchestrator.run("profile", profile)["tool_results"]["dependency_audit"]

    assert fetches == [("user", "first", "test-token")] * 2
    assert first["findings"][0]["major_gap"] == 7
    assert second["findings"] == []
    assert first["warnings"] == second["warnings"] == ["One manifest could not be read"]


def test_supplied_audit_recovers_after_failed_lookup_and_uses_local_manifest():
    """A caller-supplied tool retries lookups on later runs and gets local input first."""
    versions = iter((None, "4.0.0"))
    tool = DependencyAuditTool(latest_version=lambda *_: next(versions))
    github = GitHubTool()
    orchestrator = Orchestrator({tool.name: tool})
    profile = {
        "manifests": {"requirements.txt": "example==1.0"},
        "github_username": "user",
        "projects": [{"github_repo": "project"}],
    }

    first = orchestrator.run("profile", profile)["tool_results"][tool.name]
    second = orchestrator.run("profile", profile)["tool_results"][tool.name]

    assert first["findings"] == []
    assert "example" in first["warnings"][0]
    assert second["warnings"] == []
    assert second["findings"][0]["major_gap"] == 3
    assert github.name not in orchestrator.tools


def test_audit_skips_profiles_without_manifest_input():
    """A file path alone does not supply dependency declarations."""
    orchestrator = Orchestrator(
        {"tech_detector": TechDetector(), "market_analyzer": MarketAnalyzer()}
    )
    results = orchestrator.run("profile", {"files": ["package.json"]})["tool_results"]
    assert "tech_detector" in results
    assert "dependency_audit" not in results

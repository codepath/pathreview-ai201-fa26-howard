"""Audit direct dependency declarations against current registry releases."""

from __future__ import annotations

import json
import re
import time
import tomllib
from pathlib import PurePosixPath
from typing import TYPE_CHECKING
from urllib.parse import quote

import httpx
from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion, Version

from .base import BaseTool, ToolResult
from .github_tool import MANIFEST_NAMES, GitHubTool

if TYPE_CHECKING:
    from collections.abc import Callable

NPM_PACKAGE = re.compile(r"(?:@[a-z0-9._-]+/)?[a-z0-9._-]+", re.IGNORECASE)
NPM_RANGE = re.compile(r"(?P<operator>[~^=]?)v?(?P<major>0|[1-9]\d*)(?:\.(?:0|[1-9]\d*)){0,2}")
NPM_STABLE = re.compile(r"(?:0|[1-9]\d*)(?:\.(?:0|[1-9]\d*)){2}(?:\+[a-zA-Z0-9.-]+)?")
MAX_REGISTRY_LOOKUPS = 100
REGISTRY_DEADLINE_SECONDS = 15.0
REGISTRY_LIMIT_WARNING = "Registry lookup limit reached. Some dependencies could not be checked."


class DependencyAuditTool(BaseTool):
    """Flag direct dependency declarations two or more majors behind."""

    name = "dependency_audit"
    description = "Check repository manifests for dependencies two or more major versions behind"

    def __init__(
        self,
        latest_version: Callable[[str, str], str | None] | None = None,
        *,
        github_tool: GitHubTool | None = None,
    ) -> None:
        """Initialize the tool.

        Args:
            latest_version: Optional lookup accepting an ecosystem and package name.
            github_tool: Optional GitHub client for reading submitted repositories.
        """
        self._latest_version = latest_version or _fetch_latest_version
        self._github_tool = github_tool if github_tool is not None else GitHubTool()

    def execute(self, input_data: dict) -> ToolResult:
        """Audit supplied manifest contents or a submitted repository.

        Args:
            input_data: A manifests mapping from paths to text, or github_username and repo_name.

        Returns:
            Findings and warnings about incomplete coverage.
        """
        manifests = input_data.get("manifests")
        warnings: list[str] = []
        if "manifests" not in input_data:
            username = input_data.get("github_username")
            repo_name = input_data.get("repo_name")
            if isinstance(username, str) and isinstance(repo_name, str):
                manifests, warnings = self._github_tool.fetch_dependency_manifests(
                    username, repo_name
                )
        if not isinstance(manifests, dict):
            message = "Provide manifest contents or a GitHub repository reference"
            return ToolResult(False, {"findings": [], "warnings": [message]}, message)

        findings = []
        versions: dict[tuple[str, str], tuple[str, int] | None] = {}
        registry_deadline = time.monotonic() + REGISTRY_DEADLINE_SECONDS
        for path, contents in manifests.items():
            if not isinstance(path, str) or not isinstance(contents, str):
                warnings.append(f"{path}: expected a manifest path and text contents")
                continue
            filename = PurePosixPath(path).name
            if filename not in MANIFEST_NAMES:
                continue
            try:
                dependencies = _parse_manifest(filename, contents)
            except (TypeError, ValueError) as exc:
                warnings.append(f"{path}: could not parse manifest ({exc})")
                continue

            for ecosystem, name, specifier, highest_major in dependencies:
                if highest_major is None:
                    warnings.append(
                        f"{path}: cannot establish a major bound for {name} {specifier}"
                    )
                    continue

                key = (ecosystem, name)
                if key not in versions:
                    if (
                        len(versions) >= MAX_REGISTRY_LOOKUPS
                        or time.monotonic() >= registry_deadline
                    ):
                        if REGISTRY_LIMIT_WARNING not in warnings:
                            warnings.append(REGISTRY_LIMIT_WARNING)
                        continue
                    try:
                        latest = self._latest_version(*key)
                        versions[key] = (
                            (latest, _stable_major(ecosystem, latest)) if latest else None
                        )
                    except (httpx.HTTPError, KeyError, TypeError, ValueError):
                        versions[key] = None
                resolved = versions[key]
                if resolved is None:
                    warnings.append(f"{path}: no current stable version available for {name}")
                    continue

                latest, latest_major = resolved
                gap = latest_major - highest_major
                if gap > 1:
                    findings.append(
                        {
                            "ecosystem": ecosystem,
                            "package": name,
                            "manifest": path,
                            "specifier": specifier,
                            "highest_allowed_major": highest_major,
                            "latest_version": latest,
                            "major_gap": gap,
                        }
                    )

        return ToolResult(True, {"findings": findings, "warnings": warnings})


def _parse_manifest(filename: str, contents: str) -> list[tuple[str, str, str, int | None]]:
    if filename == "package.json":
        manifest = _mapping(json.loads(contents))
        dependencies = []
        for section in ("dependencies", "devDependencies"):
            for name, specifier in _mapping(manifest.get(section, {})).items():
                bound = None
                if isinstance(specifier, str) and NPM_PACKAGE.fullmatch(name):
                    version_range = specifier.strip()
                    match = NPM_RANGE.fullmatch(version_range)
                    if match and (match["operator"] in ("^", "~") or version_range.count(".") == 2):
                        bound = int(match["major"])
                dependencies.append(("npm", name, str(specifier), bound))
        return dependencies

    if filename == "pyproject.toml":
        project = _mapping(tomllib.loads(contents).get("project", {}))
        requirements = _string_list(project.get("dependencies", []))
        for group in _mapping(project.get("optional-dependencies", {})).values():
            requirements += _string_list(group)
    else:
        requirements = [re.split(r"^#|\s+#", line, maxsplit=1)[0] for line in contents.splitlines()]
    return [_parse_python_requirement(line.strip()) for line in requirements if line.strip()]


def _mapping(value: object) -> dict:
    if not isinstance(value, dict):
        raise ValueError("expected a table or object")
    return value


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError("expected a list of dependency strings")
    return list(value)


def _parse_python_requirement(declaration: str) -> tuple[str, str, str, int | None]:
    try:
        requirement = Requirement(declaration)
    except InvalidRequirement:
        return "pypi", declaration, "", None

    prefix = re.match(r"^[\w.-]+(?:\s*\[[^\]]*\])?", declaration)
    specifier = declaration[prefix.end() :].strip() if prefix else declaration
    bound = None if requirement.url or requirement.marker else _python_upper_major(requirement)
    return "pypi", canonicalize_name(requirement.name), specifier, bound


def _python_upper_major(requirement: Requirement) -> int | None:
    lower_bounds: list[tuple[Version, bool]] = []
    upper_bounds: list[tuple[Version, bool]] = []
    excluded_majors = set()
    exact_versions = set()
    for specifier in requirement.specifier:
        operator = specifier.operator
        if operator == "===":
            return None
        wildcard = specifier.version.endswith(".*")
        version = Version(specifier.version.removesuffix(".*"))
        if version.epoch or version.is_prerelease or version.local:
            return None
        if operator == "!=":
            if wildcard and len(version.release) == 1:
                excluded_majors.add(version.major)
            elif wildcard:
                return None
        elif operator == "==" and not wildcard:
            exact_versions.add(version)
        elif operator in ("==", "~="):
            prefix = version.release if wildcard else version.release[:-1]
            upper_release = (*prefix[:-1], prefix[-1] + 1)
            upper_bounds.append((Version(".".join(map(str, upper_release))), False))
            lower_bounds.append((version, False))
        elif operator in (">=", ">"):
            lower_bounds.append((version, operator == ">"))
        else:
            upper_bounds.append((version, operator == "<="))

    if exact_versions:
        exact = next(iter(exact_versions))
        if len(exact_versions) == 1 and requirement.specifier.contains(exact):
            return exact.major
        return None
    if not upper_bounds:
        return None

    upper, inclusive = min(upper_bounds)
    lower, exclusive = max(lower_bounds, default=(Version("0"), False))
    if lower > upper:
        return None
    if lower == upper and (exclusive or not inclusive or not requirement.specifier.contains(lower)):
        return None

    ceiling = upper.major
    if not inclusive and not any(upper.release[1:]) and not upper.is_postrelease:
        ceiling -= 1
    while ceiling in excluded_majors:
        ceiling -= 1
    return ceiling if ceiling >= lower.major else None


def _stable_major(ecosystem: str, version: str) -> int:
    if ecosystem == "npm":
        if not NPM_STABLE.fullmatch(version):
            raise ValueError("expected a stable npm version")
        return int(version.split(".", 1)[0])
    parsed = Version(version)
    if parsed.is_prerelease or parsed.epoch:
        raise ValueError("expected a stable Python release without an epoch")
    return parsed.major


def _fetch_latest_version(ecosystem: str, name: str) -> str | None:
    package = quote(name, safe="")
    if ecosystem == "npm":
        response = httpx.get(f"https://registry.npmjs.org/{package}/latest", timeout=5.0)
        response.raise_for_status()
        return _mapping(response.json())["version"]

    response = httpx.get(f"https://pypi.org/pypi/{package}/json", timeout=5.0)
    response.raise_for_status()
    releases = _mapping(_mapping(response.json())["releases"])
    stable = []
    for release, files in releases.items():
        try:
            version = Version(release)
        except InvalidVersion:
            continue
        if not version.is_prerelease and any(not _mapping(file)["yanked"] for file in files):
            stable.append(version)
    return str(max(stable)) if stable else None

"""GitHub repository metadata tool."""

import base64
import json
import re
import time
from pathlib import PurePosixPath
from urllib.parse import quote

import httpx
import structlog

from .base import BaseTool, ToolResult

logger = structlog.get_logger()

MANIFEST_NAMES = frozenset({"requirements.txt", "package.json", "pyproject.toml"})
VENDORED_DIRECTORIES = frozenset({"node_modules", ".venv", "venv", "vendor"})
MAX_MANIFESTS = 20
MAX_MANIFEST_BYTES = 256 * 1024
MAX_TREE_BYTES = 8 * 1024 * 1024
DISCOVERY_TIMEOUT = 15.0


class GitHubTool(BaseTool):
    """Fetch repository metadata from GitHub."""

    name = "github_tool"
    description = "Fetch repository metadata from GitHub"

    def __init__(self, api_token: str | None = None):
        """Initialize GitHub tool.

        Args:
            api_token: GitHub API token (optional for unauthenticated requests)
        """
        self.api_token = api_token
        self.base_url = "https://api.github.com"

    def execute(self, input_data: dict) -> ToolResult:
        """Fetch GitHub repository metadata.

        Args:
            input_data: Must contain 'github_username' and 'repo_name'

        Returns:
            ToolResult with repository metadata
        """
        username = input_data.get("github_username")
        repo_name = input_data.get("repo_name")

        if not username or not repo_name:
            return ToolResult(success=False, data={}, error="Missing github_username or repo_name")

        try:
            repo_data = self._fetch_repo_metadata(username, repo_name)
            return ToolResult(success=True, data=repo_data)

        except httpx.HTTPStatusError as e:
            logger.error(
                "github_request_failed",
                status=e.response.status_code,
                username=username,
                repo=repo_name,
            )
            if e.response.status_code == 404:
                return ToolResult(success=False, data={}, error="Repository not found")
            elif e.response.status_code == 403:
                return ToolResult(success=False, data={}, error="Rate limited or access denied")
            return ToolResult(
                success=False, data={}, error=f"GitHub API error: {e.response.status_code}"
            )

        except Exception as e:
            logger.error("github_tool_error", error=str(e))
            return ToolResult(success=False, data={}, error=str(e))

    def _fetch_repo_metadata(self, username: str, repo_name: str) -> dict:
        """Fetch repository metadata from GitHub API.

        Args:
            username: GitHub username
            repo_name: Repository name

        Returns:
            Dict with repository metadata
        """
        url = f"{self.base_url}/repos/{username}/{repo_name}"

        response = httpx.get(url, headers=self._headers(), timeout=10.0)
        response.raise_for_status()

        repo_json = response.json()

        # Extract metadata, handling null values
        metadata = {
            "name": repo_json.get("name", ""),
            "description": repo_json.get("description") or "",
            "primary_language": repo_json.get("language") or "Unknown",
            "star_count": repo_json.get("stargazers_count", 0),
            "fork_count": repo_json.get("forks_count", 0),
            "open_issues_count": repo_json.get("open_issues_count", 0),
            "last_commit_date": repo_json.get("pushed_at", ""),
            "has_readme": self._has_readme(username, repo_name),
            "topics": repo_json.get("topics", []),
            "homepage": repo_json.get("homepage") or "",
        }

        logger.info(
            "github_repo_fetched",
            username=username,
            repo=repo_name,
            language=metadata["primary_language"],
            stars=metadata["star_count"],
        )

        return metadata

    def fetch_dependency_manifests(
        self, username: str, repo_name: str
    ) -> tuple[dict[str, str], list[str]]:
        """Read regular manifest files from a snapshot of the default branch.

        Args:
            username: Repository owner.
            repo_name: Repository name.

        Returns:
            Manifest contents by repository path and warnings about skipped coverage.
        """
        if (
            not re.fullmatch(r"[a-zA-Z0-9-]+", username)
            or not re.fullmatch(r"[a-zA-Z0-9_.-]+", repo_name)
            or repo_name in {".", ".."}
        ):
            return {}, ["Invalid GitHub repository reference"]

        url = f"{self.base_url}/repos/{username}/{repo_name}"
        deadline = time.monotonic() + DISCOVERY_TIMEOUT
        try:
            branch = self._read_json(url, deadline, MAX_MANIFEST_BYTES)["default_branch"]
            tree_url = f"{url}/git/trees/{quote(branch, safe='')}?recursive=1"
            tree = self._read_json(tree_url, deadline, MAX_TREE_BYTES)
            entries = tree["tree"]
            if not isinstance(entries, list):
                raise ValueError("invalid repository tree")
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            return {}, [f"Could not discover dependency manifests: {exc}"]

        warnings = ["GitHub repository tree was truncated"] if tree.get("truncated") else []
        candidates = []
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                warnings.append("Skipped an invalid GitHub tree entry")
                continue
            if entry.get("type") != "blob" or entry.get("mode") not in ("100644", "100755"):
                continue
            source_path = PurePosixPath(entry["path"])
            if source_path.name in MANIFEST_NAMES and not VENDORED_DIRECTORIES.intersection(
                source_path.parts
            ):
                candidates.append((source_path.as_posix(), entry))

        if len(candidates) > MAX_MANIFESTS:
            warnings.append(f"GitHub manifest discovery limited to {MAX_MANIFESTS} files")
        manifests = {}
        for path, entry in sorted(candidates, key=lambda candidate: candidate[0])[:MAX_MANIFESTS]:
            if time.monotonic() >= deadline:
                warnings.append("GitHub manifest retrieval reached its time limit")
                break
            try:
                if not 0 <= entry["size"] <= MAX_MANIFEST_BYTES:
                    raise ValueError("manifest exceeds the size limit")
                sha = entry["sha"]
                if not re.fullmatch(r"[0-9a-f]{40}", sha):
                    raise ValueError("invalid GitHub blob SHA")
                blob = self._read_json(f"{url}/git/blobs/{sha}", deadline, MAX_MANIFEST_BYTES * 2)
                if blob.get("encoding") != "base64":
                    raise ValueError("unsupported GitHub blob encoding")
                content = base64.b64decode("".join(blob["content"].split()), validate=True)
                if len(content) > MAX_MANIFEST_BYTES:
                    raise ValueError("manifest exceeds the size limit")
                manifests[path] = content.decode("utf-8-sig")
            except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
                warnings.append(f"{path}: could not read GitHub manifest ({exc})")
        return manifests, warnings

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"token {self.api_token}"} if self.api_token else {}

    def _read_json(self, url: str, deadline: float, byte_limit: int) -> dict:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError("GitHub manifest retrieval reached its time limit")
        with httpx.stream(
            "GET", url, headers=self._headers(), timeout=min(5.0, remaining)
        ) as result:
            result.raise_for_status()
            buffer = bytearray()
            for chunk in result.iter_bytes():
                if time.monotonic() >= deadline or len(buffer) + len(chunk) > byte_limit:
                    raise ValueError("GitHub response exceeded its size or time limit")
                buffer.extend(chunk)
        data = json.loads(buffer)
        if not isinstance(data, dict):
            raise ValueError("expected a GitHub JSON object")
        return data

    def _has_readme(self, username: str, repo_name: str) -> bool:
        """Check if repository has a README file.

        Args:
            username: GitHub username
            repo_name: Repository name

        Returns:
            True if README exists
        """
        url = f"{self.base_url}/repos/{username}/{repo_name}/readme"

        try:
            response = httpx.head(url, headers=self._headers(), timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False

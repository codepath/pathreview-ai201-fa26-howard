"""Tests that docs/API.md has a working curl example for every API route (#47)."""

import re
from pathlib import Path

import pytest

from api.main import app

API_DOC = Path(__file__).resolve().parents[2] / "docs" / "API.md"

# Each route is introduced by a line like "`GET /reviews` — ..." and followed by
# a bash example.
ROUTE_LINE = re.compile(r"^`(GET|POST|PUT|PATCH|DELETE) (/\S*)`", re.MULTILINE)
BASH_BLOCK = re.compile(r"```bash\n(.*?)```", re.DOTALL)


@pytest.fixture(scope="module")
def doc() -> str:
    return API_DOC.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def routes() -> dict[tuple[str, str], bool]:
    """Map (method, path) to whether the route requires auth.

    Read from the OpenAPI schema because FastAPI wraps included routers, so
    their routes are not listed in ``app.routes``.
    """
    return {
        (method.upper(), path): bool(operation.get("security"))
        for path, operations in app.openapi()["paths"].items()
        for method, operation in operations.items()
    }


@pytest.fixture(scope="module")
def examples(doc) -> dict[tuple[str, str], str]:
    """Map each documented (method, path) to the bash example that follows it."""
    found = {}
    for match in ROUTE_LINE.finditer(doc):
        block = BASH_BLOCK.search(doc, match.end())
        found[(match.group(1), match.group(2))] = block.group(1) if block else ""
    return found


@pytest.mark.unit
class TestApiDocs:
    """docs/API.md stays in sync with the routes the app registers."""

    def test_documents_exactly_the_registered_routes(self, routes, examples):
        assert set(examples) == set(routes)

    def test_each_example_uses_curl_with_the_right_method(self, examples):
        for (method, path), example in examples.items():
            assert "curl" in example, f"{method} {path}: no curl example"
            if method != "GET":
                assert f"--request {method}" in example, f"{method} {path}: wrong method"

    def test_only_protected_routes_send_the_bearer_token(self, routes, examples):
        for key, requires_auth in routes.items():
            sends_token = 'Authorization: Bearer $TOKEN"' in examples[key]
            assert sends_token == requires_auth, f"{key}: auth header mismatch"

    def test_delete_profile_runs_after_every_example_that_uses_its_ids(self, doc):
        delete_example = BASH_BLOCK.search(doc, doc.index("`DELETE /profiles/"))
        assert delete_example is not None
        assert not re.search(r"\$(PROFILE_ID|REVIEW_ID)", doc[delete_example.end() :])

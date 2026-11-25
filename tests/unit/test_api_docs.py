"""Tests that docs/API.md stays in sync with the routes the API registers (#47)."""

import re
from pathlib import Path

import pytest

from api.main import app

API_DOC = Path(__file__).resolve().parents[2] / "docs" / "API.md"

# A route is documented by a line such as: `GET /profiles/{profile_id}` — ...
ROUTE_LINE = re.compile(r"^`(GET|POST|PUT|PATCH|DELETE) (/\S*)`", re.MULTILINE)
BASH_BLOCK = re.compile(r"```bash\n(.*?)```", re.DOTALL)


def _registered_routes() -> dict[tuple[str, str], bool]:
    """Map each route in the app's OpenAPI schema to whether it requires auth.

    The OpenAPI schema is used instead of walking ``app.routes`` because
    FastAPI wraps included routers, so their routes are not listed there.
    """
    routes = {}
    for path, operations in app.openapi()["paths"].items():
        for method, operation in operations.items():
            routes[(method.upper(), path)] = bool(operation.get("security"))
    return routes


def _documented_examples(doc: str) -> dict[tuple[str, str], str]:
    """Map each documented (method, path) to the first bash example after it."""
    examples = {}
    for match in ROUTE_LINE.finditer(doc):
        block = BASH_BLOCK.search(doc, match.end())
        assert block is not None, f"No example after {match.group(0)}"
        examples[(match.group(1), match.group(2))] = block.group(1)
    return examples


@pytest.fixture(scope="module")
def doc() -> str:
    """Return the contents of docs/API.md."""
    return API_DOC.read_text(encoding="utf-8")


@pytest.mark.unit
class TestApiDocs:
    """docs/API.md documents every route with a runnable curl example."""

    def test_every_registered_route_is_documented(self, doc):
        """Each route registered on the app appears in docs/API.md."""
        missing = set(_registered_routes()) - set(_documented_examples(doc))

        assert not missing, f"Routes missing from docs/API.md: {sorted(missing)}"

    def test_every_documented_route_exists(self, doc):
        """docs/API.md does not describe routes the app no longer registers."""
        stale = set(_documented_examples(doc)) - set(_registered_routes())

        assert not stale, f"docs/API.md documents unknown routes: {sorted(stale)}"

    def test_each_route_has_a_curl_example_with_the_right_method(self, doc):
        """Each example calls curl, and non-GET examples set the HTTP method."""
        for (method, path), example in _documented_examples(doc).items():
            assert "curl" in example, f"{method} {path} has no curl example"
            if method != "GET":
                assert (
                    f"--request {method}" in example
                ), f"{method} {path} example does not use --request {method}"

    def test_protected_route_examples_send_bearer_token(self, doc):
        """Examples for authenticated routes send the Authorization header."""
        examples = _documented_examples(doc)
        for key, requires_auth in _registered_routes().items():
            if requires_auth:
                assert (
                    'Authorization: Bearer $TOKEN"' in examples[key]
                ), f"{key[0]} {key[1]} example is missing the bearer token header"

    def test_public_route_examples_do_not_need_a_token(self, doc):
        """Examples for public routes work before a token exists."""
        examples = _documented_examples(doc)
        for key, requires_auth in _registered_routes().items():
            if not requires_auth:
                assert "$TOKEN" not in examples[key], f"{key} example uses $TOKEN"

    def test_delete_profile_example_runs_after_examples_that_use_its_ids(self, doc):
        """Deleting the profile comes last, so running the doc in order works."""
        delete_at = doc.index("`DELETE /profiles/{profile_id}`")
        later_uses = [
            m.start()
            for m in re.finditer(r"\$(PROFILE_ID|REVIEW_ID)", doc)
            if m.start() > delete_at
        ]
        delete_example = BASH_BLOCK.search(doc, delete_at)
        assert delete_example is not None
        assert all(
            pos < delete_example.end() for pos in later_uses
        ), "Examples after DELETE /profiles reuse IDs the delete removes"

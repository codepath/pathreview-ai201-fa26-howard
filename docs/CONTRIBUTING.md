# Contributing to PathReview

Thank you for contributing to PathReview! This guide explains our development workflow and standards.

## Getting Started

1. **Fork** the repository and clone your fork
2. **Set up** your development environment following [SETUP.md](SETUP.md)
3. **Browse issues** and find one that interests you
4. **Comment** on the issue to let others know you're working on it

## Branch Naming Convention

Create a branch from `main` using this format:

```txt
<type>/<issue-number>-<short-description>
```

Where `<issue-number>` is the GitHub issue number (the number shown under the issue title in the tracker — e.g., `#54`).

Examples:

- `fix/54-resume-section-whitespace`
- `feat/26-safety-event-health-check`
- `test/44-review-service-coverage`
- `docs/11-hybrid-scoring-formula`

Types: `fix`, `feat`, `test`, `docs`, `refactor`, `perf`, `chore`

## Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/). Every commit message must follow this format:

```txt
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:** `fix`, `feat`, `test`, `docs`, `refactor`, `perf`, `chore`, `ci`

**Scopes:** `ingestion`, `rag`, `agent`, `safety`, `api`, `frontend`

**Examples:**

```md
fix(ingestion): handle leading whitespace in resume section detection

Section headings with leading whitespace were not recognized, so their
content was silently dropped. Strip the line before matching headings.

Fixes #54
```

```md
test(agent): add unit tests for readme_scorer tool
```

## Pull Request Process

1. **Ensure your code passes all checks:** `make check && make test-unit`
2. **Push your branch** and open a PR using the PR template
3. **Confirm CI is green on your PR** — see [CI must be green](#ci-must-be-green) below
4. **Fill out the PR template completely** — incomplete PRs will be sent back
5. **Respond to review feedback** within 48 hours
6. **Squash fixup commits** before final merge if requested

## CI must be green

**A PR with red CI is not ready for review, and green CI is part of the
submission requirement for graded work.** All five jobs must pass: `lint`,
`typecheck`, `test-unit`, `test-integration`, and `frontend`.

`main` is kept green on purpose. That means a red X on your PR is a real signal:
something in *your* change broke, not pre-existing noise. If a job fails and you
cannot connect it to your own diff, say so in the PR rather than ignoring it.

Reproduce the same five checks locally before pushing:

```bash
make lint        # ruff
make format      # black (writes changes)
make typecheck   # mypy
make test-unit   # pytest tests/unit
cd frontend && npm ci && npm test -- --run
```

### Your first PR may need a maintainer to start CI

Workflows on pull requests from forks are gated by GitHub. If your account is new
to GitHub, your first PR will sit at "waiting for approval to run workflows" until
a maintainer releases it. That is expected, and it is not a problem with your
branch. Everyone else's fork PRs run automatically. Ping the course Discord if a
run stays queued.

### Working on a seeded bug: remove its xfail marker

Many issues in the tracker are deliberately-planted bugs, and each one has unit
tests that currently fail. Those tests are marked so the suite can stay green:

```python
@pytest.mark.xfail(strict=True, reason="issue #56: structural chunker drops heading-less docs")
def test_document_with_no_headings(self, chunker):
    ...
```

The marker is `strict=True`, so **when your fix makes the test pass, CI fails
with `XPASS(strict)` until you delete the marker.** That is intentional:
removing the `@pytest.mark.xfail` line is part of fixing the issue. Your PR for
issue #56 should both fix the bug and drop the marker from every test that
covers it.

The same applies to the baseline suppressions in `pyproject.toml`. Some seeded
bugs are also flagged by ruff or mypy and are suppressed there with a comment
naming the defect — for example `api/routes/health.py` `attr-defined` is
issue #62. If you fix one of those, remove its suppression too.

### Do not bulk-fix lint or type findings

Two things will damage the course material, so please avoid them:

- **Never run `ruff check --fix --unsafe-fixes`.** The unsafe fixes rewrite
  unused variables and loop bindings, which is precisely how several seeded
  bugs are expressed. Deleting them deletes the exercise.
- **Don't "clean up" a line marked `# noqa: <RULE>` with a comment explaining
  it.** Those annotations are deliberate. A plain `# noqa` you added yourself to
  silence your own new finding is a different matter — fix the finding instead.

If you want to reduce the baseline debt, that is welcome, but do it as its own
focused PR (one rule at a time) rather than folding it into a bug fix.

## Code Style

- **Python:** Formatted with `black`, linted with `ruff`, type-checked with `mypy`
- **TypeScript/React:** Follows the existing component patterns in `frontend/src/`
- **Tests:** Every code change should include or update relevant tests
- **Docstrings:** All public functions and classes must have Google-style docstrings

## Running Checks Locally

```bash
make lint       # Ruff linter
make format     # Black formatter
make typecheck  # Mypy type checker
make check      # All three
make test-unit  # Unit tests
```

## Adding a New Parser

If your issue involves adding a new document parser to the ingestion pipeline:

1. Create a new file in `ingestion/parsers/` (e.g., `web_parser.py`)
2. Implement the `BaseParser` interface:
   ```python
   from ingestion.parsers.base import BaseParser, ParseResult

   class WebParser(BaseParser):
       def parse(self, content: str | bytes) -> ParseResult:
           ...
   ```
3. Register the parser in `ingestion/pipeline.py`
4. Add unit tests in `tests/unit/test_<parser_name>.py`
5. Add a sample fixture in `tests/fixtures/` if needed

## Adding a New Agent Tool

If your issue involves adding a new tool to the agent system:

1. Create a new file in `agent/tools/` (e.g., `dependency_audit_tool.py`)
2. Implement the `BaseTool` interface:
   ```python
   from agent.tools.base import BaseTool, ToolResult

   class DependencyAuditTool(BaseTool):
       name = "dependency_audit"
       description = "Checks for outdated dependencies in project repos"

       def execute(self, input_data: dict) -> ToolResult:
           ...
   ```
3. Register the tool in `agent/orchestrator.py`
4. Add unit tests in `tests/unit/test_<tool_name>.py`
5. Add mock responses in `tests/fixtures/` if the tool calls external APIs

## Questions?

Open a discussion or reach out in the course Discord channel.

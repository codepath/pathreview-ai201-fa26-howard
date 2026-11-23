## Solution plan

**Issue:** Heading hierarchy test fixture is indented, so it contains no headings — https://github.com/codepath/pathreview-ai201-fa26-howard/issues/71

### Understand

**Root cause:** The bug is in the test, not in the parser. `test_extract_heading_hierarchy` builds its sample markdown with a triple-quoted string that is indented to match the surrounding code, so every line of the string actually begins with 8 spaces (for example `"        # Main Title"`). `ReadmeParser._extract_heading_hierarchy` matches headings with the regex `^(#{1,6})\s+(.+)$`, which requires `#` to be the very first character of the line. That is correct Markdown behavior: CommonMark only allows up to 3 spaces before a heading, and 4+ spaces of indentation makes the line an indented code block. So none of the fixture's lines count as headings.

**Expected behavior:** Given a markdown string with `#`, `##`, and `###` headings, the method returns one entry per heading, and the test sees levels 1, 2, and 3.

**Actual behavior:** The method returns an empty list `[]`. With the `xfail` marker bypassed (`pytest --runxfail`), the test fails on `assert len(headings) > 0` with `AssertionError: assert 0 > 0`. With the marker in place, pytest reports it as `XFAIL`.

### Map

- `tests/unit/test_readme_parser.py` — **will change.** The `test_extract_heading_hierarchy` test (around line 138): its `markdown = """..."""` fixture and the `@pytest.mark.xfail(strict=True, reason="issue #71 ...")` decorator directly above it. Also the import block at the top of the file (add `import textwrap`).
- `ingestion/parsers/readme_parser.py` — **read only, will not change.** `ReadmeParser._extract_heading_hierarchy()` (around line 47) holds the heading regex. I confirmed it already returns the right levels when given un-indented input, so changing it would be fixing the wrong thing.
- `tests/conftest.py` — **will not change.** Its `sample_readme_text` fixture has the same indentation problem, but that is issue #70, which is a separate issue another contributor can claim.

### Plan

1. **Add the import.** Add `import textwrap` to the imports at the top of `tests/unit/test_readme_parser.py`, keeping standard-library imports grouped above `import pytest` so ruff's import sorting stays happy.
2. **Fix the fixture.** Wrap the test's markdown string in `textwrap.dedent(...)` so the common 8-space indent is stripped and each heading line starts with `#`. I'm choosing `dedent` over manually un-indenting the string because it keeps the test readable and matches the code's indentation.
3. **Remove the xfail marker.** Delete the full `@pytest.mark.xfail(strict=True, reason="issue #71 ...")` decorator above `test_extract_heading_hierarchy`. Because it is `strict=True`, leaving it would make CI fail with `XPASS(strict)` once the test passes. I will not touch the #70 marker on `test_parse_standard_readme`.
4. **Verify locally.** Run `.venv/Scripts/pytest tests/unit/test_readme_parser.py -v` and confirm the test shows `PASSED` (not `XFAIL`/`XPASS`), then run `make test-unit` to make sure nothing else in the suite broke.
5. **Run the CI checks and open the PR.** Run `make lint`, `make format`, and `make typecheck`, commit with a Conventional Commit message ending in `Fixes #71`, push the branch, and open a PR against upstream using the PR template.

### Inputs & outputs

- **Input to the fix:** the existing test file and its indented multi-line markdown fixture.
- **What changes:** the fixture string passed into `_extract_heading_hierarchy` becomes properly un-indented markdown, and the xfail marker is removed.
- **Expected output:** `_extract_heading_hierarchy` returns 4 headings — `Main Title` (level 1), `Subsection` (level 2), `Sub-subsection` (level 3), `Another Section` (level 2) — and the test reports `PASSED`. No application code or runtime behavior changes.

### Risks & unknowns

- **Forgetting the xfail marker:** if I fix the fixture but leave the `strict=True` marker, `make test-unit` and CI will fail with `XPASS(strict)`. Mitigation: step 3 of the plan, and check the pytest output says `PASSED`.
- **Removing the wrong marker:** `test_readme_parser.py` also has a near-identical marker for issue #70 on `test_parse_standard_readme`. I need to delete only the one whose reason says `issue #71`.
- **`dedent` and the first line:** the string starts with a newline right after `"""`, and `textwrap.dedent` ignores blank lines when finding the common indent, so this should be fine — but I'll verify by printing the parser's result in a Python shell before committing.
- **Lint/format hooks:** the pre-commit hooks run ruff and black on `.py` files. If ruff reorders imports or black reformats the call, the first commit may be rejected and need a re-add. `pyproject.toml` enables ruff's `I` (isort) rule, so `import textwrap` must sit in its own standard-library group above `import pytest`, separated by a blank line, or `make lint` will flag it.
- **Scope creep:** it's tempting to also fix `tests/conftest.py` (issue #70) since it has the same root cause. I will leave it alone so my PR only closes #71 and doesn't collide with another contributor's work.

### Edge cases

- **Mixed headings and body text:** the fixture interleaves headings with content lines and blank lines; only the 4 `#` lines should be returned, and body lines like `Some content` should not be.
- **Repeated heading levels:** level 2 appears twice (`Subsection`, `Another Section`); both should be captured, not deduplicated.
- **Leading/trailing blank lines:** the fixture starts and ends with blank/whitespace lines; these must not produce empty headings or crash the parser.
- **Text with no headings:** the existing `test_extract_heading_hierarchy_no_headings` test must still return `[]`, which confirms I did not loosen the parser.
- **Lightly indented headings (1–3 spaces):** valid in CommonMark but not matched by the current regex. That's outside this issue's scope; I'll note it in my PR as a possible follow-up rather than change parser behavior here.

## Solution plan

**Issue:** [#70 — README parser test fixture is indented, so it contains no headings](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/70)  
**Tier:** Tier 2 (`tier-2`)  
**Working branch:** `fix/70-readme-parser-fixture`  
**Status:** Unit 9 implementation and local validation complete. Implementation committed and pushed; [PR #96](https://github.com/codepath/pathreview-ai201-fa26-howard/pull/96) is open and ready for review. All five CI jobs passed on implementation commit `cf9b61a`; Unit 9 was submitted with 4 hours. Peer/mentor feedback remains outstanding.

### Understand

The shared sample README is written inside an indented Python triple-quoted string. The resulting value retains four spaces before every heading, including `    # Weather App`. The parser's heading matcher starts with `^#`, so it finds no headings, although `test_parse_standard_readme` expects at least one. This is a test-data defect: a standard Markdown heading should start at column zero in this fixture, while the production parser should continue to preserve the text it receives.

Locally, the existing test is `XFAIL`; running it with `--runxfail` exposes `assert 0 > 0` at `tests/unit/test_readme_parser.py:31`. Passing an in-memory `textwrap.dedent` copy to the unchanged parser yields three headings and the same 39 words. The baseline README parser suite is **13 passed, 2 xfailed**. See [reproduction steps and observed output](docs/REPRODUCTION-70.md).

The completed fix should make the standard README test pass normally, with three headings recognized from realistic input and no #70 expected-failure marker. The separate #71 hierarchy fixture is outside this issue's scope.

### Map

Files expected to change during implementation:

- `tests/conftest.py` — import `dedent` from `textwrap` and apply it specifically to the string returned by `sample_readme_text()`. Preserve the sample's words and relative indentation.
- `tests/unit/test_readme_parser.py` — remove only the `@pytest.mark.xfail(...)` block for `TestReadmeParser.test_parse_standard_readme`. Strengthen its regression assertions to verify the known three-heading fixture and expected heading names/levels; retain the text-preservation and metadata assertions.
- `JOURNAL.md` and this `PLAN.md` — record Unit 9 implementation decisions and actual validation results as work proceeds.

Read for context and verify without planned production edits:

- `ingestion/parsers/readme_parser.py` — `ReadmeParser.parse(content: str | bytes) -> ParseResult` and `_extract_heading_hierarchy(content: str) -> list[dict]` define the behavior under test.
- `ingestion/parsers/base.py` — `ParseResult` describes the returned text, metadata, and source type.
- `docs/CONTRIBUTING.md` — the seeded-bug contract requires deleting the matching strict `xfail` marker when the fix passes.

### Plan

1. **Confirm the baseline and fixture consumers.** Re-run the focused test with `--runxfail` and search `sample_readme_text` across the repository. Compare the raw fixture lines with the heading regex. Currently, the search under `tests/` finds only the standard README parser test consuming this fixture; recheck before editing in case the branch changes.
2. **Correct the shared fixture's indentation.** Wrap the returned sample in `textwrap.dedent(...)` in `tests/conftest.py`. Keep its leading/trailing newlines and all words, list entries, and relative indentation. Verify the three heading lines start with `#`, `##`, and `##` at column zero. Do not strip each line individually or normalize all documents in the parser.
3. **Enable and strengthen the relevant regression test.** Remove the #70/H-03 strict `xfail` block only. Verify a count of three and the heading sequence `Weather App`/1, `Features`/2, `Tech Stack`/2 through the existing hierarchy helper, while keeping `result.text == sample_readme_text`, `source_type`, and metadata checks. Keep the #71 marker and its separate fixture unchanged.
4. **Check boundaries and regressions.** Exercise the edge cases below with the existing README parser tests and focused additions only where coverage is missing. Run the focused standard README test normally, the complete README parser test file, then `make test-unit`. Investigate any new failure or strict XPASS caused by the fixture change; do not delete unrelated markers to hide it.
5. **Validate and document the final patch.** Run `make lint`, `.venv/bin/black --check .`, and `make typecheck`; inspect `git diff --check` and the diff for unrelated changes. Update the journal with results, commit the fixture/test fix using the contribution convention, push this same branch, and prepare the Unit 9 PR with issue #70 and reproduction evidence.

### Inputs & outputs

**Input being corrected:** the `str` returned by `sample_readme_text()`, containing a Weather App title, Features section, Tech Stack section, and bullet lists. Only the accidental common Python-source indentation should disappear. No new user input, endpoint, database field, or public signature is needed.

**Parser contract retained:** `ReadmeParser.parse(content: str | bytes) -> ParseResult` returns text identical to the supplied string (or decoded bytes), `source_type='readme'`, and metadata containing heading count, word count, code-block detection, and badge detection. The helper returns heading dictionaries with `level`, `text`, and zero-based `line` fields.

**Expected observable output for the corrected fixture:** `heading_count=3`, `word_count=39`, `has_code_blocks=False`, and `has_badges=False`; hierarchy levels `[1, 2, 2]` with the names above. With newlines preserved, the observed in-memory control has heading line indexes `[1, 4, 9]`. The standard test should report **PASS**, rather than XFAIL, under a normal pytest run. The existing 15-test README parser file should become **14 passed, 1 xfailed** before any new tests are added, with #71 remaining the expected failure.

### Risks & unknowns

- **Shared-fixture impact (`tests/conftest.py::sample_readme_text`):** another test could depend on its exact whitespace. Search the entire repo before editing and run the unit suite afterward. Current `tests/` search shows one consuming test; this is observed scope, not an assumption that future consumers cannot exist.
- **Over-normalization (`tests/conftest.py`):** per-line `strip()` would destroy intentional nested-list or code indentation in future samples. Use common-margin `dedent` on this fixture only, and inspect relative indentation and retained newlines. Do not apply it to `sample_resume_text()`.
- **Strict XPASS (`tests/unit/test_readme_parser.py::test_parse_standard_readme`):** fixing the fixture while leaving `strict=True` causes pytest to fail with XPASS. Remove its complete #70 marker in the same implementation commit; run the test without `--runxfail` for acceptance.
- **Neighboring defect (`tests/unit/test_readme_parser.py::test_extract_heading_hierarchy`):** #71 has its own locally indented string. Keep it unchanged and distinguish its remaining XFAIL from a regression introduced by #70.
- **Parser scope (`ReadmeParser._extract_heading_hierarchy`):** the regex is a limited heading recognizer, not a complete Markdown parser. Supporting up to three leading spaces or excluding headings inside fenced code blocks would require separate investigation. This fixture correction should not silently broaden those production semantics.
- **Environment differences (`pyproject.toml`):** dependency versions are lower-bounded. The local reproduction uses pytest 9.2.0 and emits an unrelated asyncio configuration deprecation warning. Record versions/results and check CI when the Unit 9 PR is opened; do not change dependency policy for this fixture fix.

### Edge cases

- **Leading/trailing blank lines in the shared fixture:** retain them while removing the four-space common margin; still recognize the same three headings and preserve returned text exactly.
- **Empty or whitespace-only input (`""`, `"   \n\t"`):** retain the existing parser tests expecting zero headings/words and no crash. This fix must not invent a heading for empty content.
- **Plain text without `#` headings:** the hierarchy should stay empty; keep `test_extract_heading_hierarchy_no_headings` passing.
- **Genuinely indented text such as `"    # code example"`:** leave production behavior at zero headings. The correction applies to test-data construction, not every string passed into `parse`; add a focused assertion if this boundary lacks coverage.
- **UTF-8 bytes such as `b"# Test README\nContent here"` or an encoded `"# Café README"`:** preserve existing successful decoding and text tests; no public input-type change is intended.
- **The separate #71 fixture remains broken:** a normal README parser suite run must still report that known XFAIL, rather than accidentally changing its test input or marker as part of #70.

### Unit 9 implementation results

- Applied `textwrap.dedent` only to `sample_readme_text()` and removed the #70/H-03 strict expected-failure marker. The standard test now checks three headings with the expected names and levels, while retaining text-preservation and metadata assertions.
- Added `test_parse_indented_heading_as_plain_text` to confirm that genuinely indented input remains unchanged and produces no headings. Production parser code and the separate #71 fixture/marker are unchanged.
- `make check`: passed (Ruff, Black, and mypy; 76 source files checked by mypy).
- `make test-unit`: **377 passed, 52 xfailed**, with four warnings about existing async mocks. No failing tests or strict XPASS results.
- `cd frontend && npm test -- --run`: **18 passed** across two files.
- `make test-integration`: no tests collected; pytest returned 5 and make returned 2. `.github/workflows/ci.yml` explicitly converts pytest exit 5 to success for this empty suite. This is an unexercised integration suite, not a claim that integration tests passed.
- The focused README parser test result and final diff checks are recorded in the Unit 9 journal. The implementation is committed and pushed, PR #96 is ready for review, and all five CI jobs passed on `cf9b61a`. The ledger PR link is recorded and Unit 9 is submitted. Peer/mentor feedback is still pending.

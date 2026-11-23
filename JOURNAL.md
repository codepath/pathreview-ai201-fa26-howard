# PathReview Journal — Module 3

## Unit 7 — Issue selection

**Issue link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/71

**Issue title:** Heading hierarchy test fixture is indented, so it contains no headings

**Tier:** [x] Tier 1   [ ] Tier 2   [ ] Tier 3

**Problem summary:**
PathReview's README parser (`ingestion/parsers/readme_parser.py`) pulls out a README's headings and their levels (`#`, `##`, `###`) so the rest of the review pipeline knows how the document is structured. The unit test for this, `test_extract_heading_hierarchy` in `tests/unit/test_readme_parser.py`, currently fails and is marked `xfail`, but the parser itself is not the problem — the test's sample markdown is. That sample is written as an indented triple-quoted string, so every line starts with spaces, and the parser correctly only treats a line as a heading when `#` is the first character (in Markdown, heavily indented text is a code block, not a heading). As a result the parser finds zero headings and the test's assertions fail. A successful fix will un-indent the test fixture (for example with `textwrap.dedent`) so it contains real headings, then remove the `xfail` marker so the test runs and passes, without changing the parser's behavior.

**"Is this right for me?" checklist — selection notes:**
- **Scope is small and contained:** the change is limited to one test in one file (`tests/unit/test_readme_parser.py`); no application code needs to change.
- **I can reproduce it:** the test already exists and is marked `xfail` for issue #71, so I can watch it fail and confirm the fix with `make test-unit`, with no API key or extra services needed.
- **I understand the concepts:** it involves Python multi-line strings, indentation, and a simple regex (`^(#{1,6})\s+(.+)$`), all of which I can verify in a Python shell.
- **Clear definition of done:** the heading-hierarchy test passes with its `xfail` marker removed, and every other README parser test still passes.
- **Not already claimed:** issues #53 and #55 were already taken, so I checked #71's comments and the cohort ledger, found it free, and claimed it.
- **Fits the timeline:** as a Tier 1 issue it is realistic to finish well before Unit 9, leaving room to try a second issue from a different tier.

**Branch name:** test/71-heading-hierarchy-fixture-indent

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger

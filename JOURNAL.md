# PathReview Journal — Module 3

## Unit 7 — Issue selection

**Issue link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/71

**Issue title:** Heading hierarchy test fixture is indented, so it contains no headings

**Tier:** [ ] Tier 1   [x] Tier 2   [ ] Tier 3

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

Unit 8 — Reproduction & solution planning

Reproduction commit link: PASTE_COMMIT_LINK_HERE

Reproduction summary:
I ran `.venv/Scripts/pytest tests/unit/test_readme_parser.py -v`, where `test_extract_heading_hierarchy` shows as `XFAIL`, then re-ran it with `--runxfail` to bypass the marker and it failed with `AssertionError: assert 0 > 0` because `_extract_heading_hierarchy` returned an empty list. Every line of the test's markdown starts with 8 spaces, so the parser's `^#` regex never matches; in a Python one-liner the parser returned `[]` for an indented sample but returned the correct headings and levels once the same string was passed through `textwrap.dedent`.

Reproduction steps:
`git checkout test/71-heading-hierarchy-fixture-indent`
`.venv/Scripts/pytest tests/unit/test_readme_parser.py -v` → `test_extract_heading_hierarchy XFAIL`
`.venv/Scripts/pytest "tests/unit/test_readme_parser.py::TestReadmeParser::test_extract_heading_hierarchy" --runxfail` → `FAILED ... assert 0 > 0`
Python one-liner comparing the parser's output on an indented string vs. the same string after `textwrap.dedent` → `[]` vs. the correct heading list
Root cause is the indented fixture in `tests/unit/test_readme_parser.py`, not `ingestion/parsers/readme_parser.py`.

PLAN.md link: https://github.com/laylahadley/pathreview-ai201-fa26-howard/blob/test/71-heading-hierarchy-fixture-indent/PLAN.md

Walkthrough video (recommended): Not recorded this week.

Blockers or open questions:
None blocking. Open question: lightly indented headings (1–3 spaces) are valid Markdown but not matched by the parser's regex — I'm treating that as out of scope for #71 and will mention it in my PR as a possible follow-up.

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

Reproduction commit link: https://github.com/laylahadley/pathreview-ai201-fa26-howard/commit/03dff31efab46252d382b06873b19d814f2f8d43 

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

Unit 9 — Solution building & PR submission

Check-in 1 (mid-week)

Current progress:
PLAN.md sub-tasks 1–4 are done. I added `import textwrap` to `tests/unit/test_readme_parser.py`, passed the heading-hierarchy fixture through `textwrap.dedent` so its headings start at column 0, and removed the `strict=True` xfail marker for issue #71 (leaving the #70 marker alone). I also added two tests: one that checks the exact level and text of every heading in order, and one that confirms a line indented like a code block is not treated as a heading. `make test-unit` and `make check` both pass locally, and I opened a draft PR to get feedback.

Next steps:
Share the draft PR in the course Slack channel for peer review, address any feedback I agree with, confirm all five CI jobs are green on the PR, then mark it ready for review and fill in Check-in 2.

Blockers:
None. My first PR from a fork may need a maintainer to approve the CI run before the checks start.

### Check-in 2 (end of week)

**PR link:** https://github.com/codepath/pathreview-ai201-fa26-howard/pull/106 

**Branch:** `test/71-heading-hierarchy-fixture-indent`

**What you built:**
I fixed the failing heading-hierarchy test by passing its indented sample markdown through `textwrap.dedent`, so the headings start at the beginning of each line and the README parser can recognize them. The parser itself was already correct, so I left `ingestion/parsers/readme_parser.py` unchanged and removed the now-obsolete strict `xfail` marker for issue #71.

**Tests added or updated:**
All changes are in `tests/unit/test_readme_parser.py`. I updated `test_extract_heading_hierarchy` (dedented fixture, xfail marker removed) and added `test_extract_heading_hierarchy_order_and_text`, which checks every heading's level and text in document order, and `test_extract_heading_hierarchy_ignores_indented_lines`, which confirms a line indented like a code block is not counted as a heading.

**Self-review confirmation:** [x] make check passes  [x] make test-unit passes
**Reviewer Name:** None (no response)

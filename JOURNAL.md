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

## Unit 8 — Reproduction & solution planning

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

## Unit 9 — Solution building & PR submission

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

## Unit 10 — Iteration & reflection
Reviewer feedback
Feedback received: [ ] Yes  [x] No — still waiting for review
Summary of feedback:
As of this entry, no maintainer or reviewer has left comments on PR #106. I checked the PR's 'Conversation' and 'Files changed' tabs with no luck, and CI is green on all five jobs.
How I responded:

---
**Reflection**

What was harder than you expected?

The environment and Git workflow were a little harder than the actual fix. On Windows, `make setup` failed immediately because `make` isn't installed by default, and I lost time second-guessing whether my terminal was the problem because Git Bash labeled itself "UCRT64." Later, my first `git push` in Unit 8 was rejected because the branch on GitHub had a commit my local copy didn't, and I had to learn `git pull --rebase` and why the commit ID changed afterward. Issue selection was also harder than I expected: my first two choices (#53 and #55) were already claimed, so I had to go back through the tracker and pick #71.

What did you learn about working in a large codebase?

In someone else's production code, the first job is figuring out where the problem actually lives, not writing code. My issue looked like a parser bug, but reading `ingestion/parsers/readme_parser.py` and running the parser on a dedented string showed the parser was correct and the test fixture was wrong, so the right fix was in `tests/unit/test_readme_parser.py`. I also learned how much the project's conventions shape a contribution: the branch name format, Conventional Commits, strict `xfail` markers that turn a passing test into an `XPASS(strict)` failure, ruff's import-sorting rule, and five CI jobs that all have to be green. Staying in scope mattered too — `tests/conftest.py` has the same indentation bug, but that's issue #70, so I left it alone to avoid colliding with another contributor.

How did AI tools help - and where did they fall short?

I leaned on AI heavily this module, and it was most useful for turning instructions into exact commands, reading unfamiliar parts of the repo quickly, and drafting the plan and PR description. It also fell short in ways I had to catch: it told me my terminal was the wrong one when it was actually Git Bash, it couldn't see which issues were already claimed or which tier they were, and it assumed my files would be in `~/Downloads` when they weren't. The bigger limitation is that relying on step-by-step instructions meant I sometimes ran commands before I fully understood them, so I had to go back and read the diff myself to be able to explain why `textwrap.dedent` fixes the test and why the parser should stay unchanged.

What would you do differently if you started over?

I'd check the cohort ledger and issue comments before getting attached to an issue, and keep two or three backups ready to pick in the event the one I selected isn't available. Also, I would make every edit locally and never on the GitHub website, (no matter how quick it seems) since editing JOURNAL.md manually is what caused my rejected push. Most of all, I'd use AI to explain the code and the error messages first, then make the changes myself, so the understanding comes before the commit instead of after it.

What are you most proud of from this module?

Getting the full contribution cycle working on Windows from scratch - fork, setup, reproduction, plan, fix, tests, and a PR with all five CI checks green. Specifically, I'm proud that I can explain why the bug was in the test rather than the parser, and that I added tests that check the exact heading levels and the indented-line behavior instead of just making the old test pass.

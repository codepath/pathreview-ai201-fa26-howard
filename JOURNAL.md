## Unit 7 — Issue selection

**Issue link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/54 

**Issue title:** Resume section detection fails on text with leading whitespace

**Tier:** [x] Tier 1  

**Problem summary:** The resume parser can't detect any sections when the header lines are indented. In ingestion/parsers/resume_parser.py, _detect_sections() only recognizes a header like "Education" or "Skills" when it's the very first thing on its line. Text extracted from PDFs often keeps its leading spaces, so for those resumes detected_sections comes back empty even though the sections are there. A successful fix would make detection ignore leading whitespace, so indented and non-indented resumes give the same sections and the three related tests in tests/unit/test_resume_parser.py pass.

**Branch name:** bug/54-resume-section-detection

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/josephlewis-codepath/pathreview-ai201-fa26-howard/commit/b06d1322d341f470352bceb19f11cd410cf48f90

**Reproduction summary:**
I ran the five tests tagged #54 with `pytest tests/unit/test_resume_parser.py --runxfail`, and all five failed. Then I fed `_detect_sections()` the same resume twice: flush-left it returned `['Education', 'Experience', 'Skills']`, and indented by four spaces it returned `[]`. I also found that `_strip_markdown()` has the same column-0 anchor: it leaves an indented `# Header` in the text, which is why two markdown tests are tagged #54 too. I committed a focused test (`test_detect_sections_indented_matches_flush`) that captures the bug, marked `xfail(strict=True)` so the suite stays green until the fix lands.

**PLAN.md link:** https://github.com/josephlewis-codepath/pathreview-ai201-fa26-howard/blob/fix/54-resume-section-whitespace/PLAN.md

**Walkthrough video (recommended):** Not recorded.

**Blockers or open questions:**
- My Unit 7 branch was named `bug/54-resume-section-detection`, but CONTRIBUTING.md only allows `fix/`, `feat/`, etc., so from Unit 8 on I'm working on `fix/54-resume-section-whitespace` (branched from it). The old branch is untouched.
- Does `pypdf` really produce non-breaking-space indentation? I'm handling it with `[^\S\n]` and a test, but I haven't seen it in a real PDF yet.
- `test-integration` needs Postgres/Redis, so I'll rely on CI to confirm that job.


## Unit 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
PLAN.md sub-task 1 is done: `_detect_sections()` in `ingestion/parsers/resume_parser.py` now allows leading horizontal whitespace (`^[^\S\n]*`), and I dropped the two redundant `\n`-prefixed patterns, since `^` with `re.MULTILINE` already covers them. Part of sub-task 3 is done too: four of the six #54 tests (`test_parse_single_column_resume_text`, `test_parse_resume_no_work_experience`, `test_detect_sections`, and my `test_detect_sections_indented_matches_flush`) flipped to `XPASS(strict)` exactly as expected, so I removed their xfail markers in the same commit to keep every commit green. `test_resume_parser.py` is at 9 passed, 2 xfailed; ruff, black and mypy are clean on the changed files.

**Next steps:**
- Sub-task 2: fix the header regex in `_strip_markdown()`, which should make the last two #54 tests (`test_strip_markdown_syntax`, `test_parse_markdown_resume`) pass so I can remove their markers.
- Sub-task 4: add the PLAN.md edge-case tests (tabs, mixed indentation, a header word mid-sentence, `\xa0` indentation, blank lines preserved, an indented multi-word header).
- Sub-task 5: run the full set of CI checks, push, and open the PR.

**Blockers:**
None on the fix. The 30 `test_structural_chunker.py` tests error in my sandbox because tiktoken can't download `cl100k_base` (a network proxy blocks it). That's unrelated to #54, and I'll rely on CI to confirm that job.

---

### Check-in 2 (end of week)

**PR link:** https://github.com/codepath/pathreview-ai201-fa26-howard/pull/84

**Branch:** `fix/54-resume-section-whitespace`

**What you built:**
I fixed `ResumeParser` (`ingestion/parsers/resume_parser.py`) so resume section headers are detected even when the line is indented, as PDF-extracted text usually is. `_detect_sections()` and `_strip_markdown()` both anchored their regexes at column 0, so I changed both to allow leading horizontal whitespace with `^[^\S\n]*` (any whitespace except a newline, so a match can't spill onto another line). Indented and flush-left resumes now produce the same `detected_sections`.

**Tests added or updated:**
All in `tests/unit/test_resume_parser.py`:
- Removed the `xfail(strict=True)` marker from the 5 tests seeded for #54: `test_parse_single_column_resume_text`, `test_parse_resume_no_work_experience`, `test_detect_sections`, `test_parse_markdown_resume`, `test_strip_markdown_syntax`. They now pass.
- Added `test_detect_sections_indented_matches_flush`, which checks that the same resume indented 4 spaces gives the same sections as flush-left (this was my Unit 8 reproduction test).
- Added 7 edge-case tests:
  - tab indentation
  - mixed indent levels in one document
  - non-breaking-space (`\xa0`) indentation
  - an indented multi-word header (`Work Experience`)
  - indented markdown headers where the blank line between them must survive
  - two guards against over-loosening: `"I have experience: 5 years"` and a resume with no headers must both return `[]`

The parser file goes from 5 passed / 5 xfailed to 18 passed. The full unit suite is 358 passed / 48 xfailed, vs. 345 / 53 on `main`.

**Self-review confirmation:** [x] make check passes  [x] make test-unit passes

(`make check`: ruff, black and mypy are clean on all 76 source files. `make test-unit`: every test passes except 30 chunker tests that error in my sandbox because tiktoken couldn't download its encoding file. They error the same way on unmodified `main`, so it's a network issue, not my change. I also ran `test-integration` (no tests collected, which CI treats as a pass) and the frontend tests (18 passed).)

**Draft PR feedback received from:** none


## Unit 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [ ] Yes  [x] No — still awaiting review

**Summary of feedback:**
No review has come in yet. I opened PR #84 on November 12 and there are no reviewer or maintainer comments on it so far. It may also be waiting for a maintainer to approve running CI, since it's my first PR from this fork.

**How you responded:**
Nothing to respond to yet. If feedback comes in, I'll reply on the PR and push fixes to `fix/54-resume-section-whitespace`. The thing I most expect a reviewer to push back on is the `Experience-driven engineer` false positive I flagged in Notes for Reviewers. My plan is to open it as its own issue rather than widen this PR.

---

### Reflection

**What was harder than you expected?**
The bug wasn't where the issue title said it was, or at least not only there. Issue #54 is about section *detection*, but when I ran the five tests tagged #54 with `--runxfail`, two of them (`test_strip_markdown_syntax` and `test_parse_markdown_resume`) never call `_detect_sections()` at all. They failed because `_strip_markdown()` had the same column-0 `^#+\s+` anchor. If I had fixed only the function the title named, those two would have stayed xfail and I wouldn't have fully closed the issue. The `xfail(strict=True)` workflow was also counterintuitive at first: the moment my fix worked, the suite went *red* with `XPASS(strict)`, and fixing it meant deleting the markers as part of the fix.

**What did you learn about working in a large codebase?**
The actual code change was two regexes, but most of the work was everything around it. I read `ingestion/pipeline.py` to see that `IngestionPipeline` logs and stores `detected_sections`, so I knew I couldn't change its shape. I followed CONTRIBUTING.md rules I'd never have set for my own project: Conventional Commits with an `(ingestion)` scope, a strict branch-name format, and never running `ruff --fix --unsafe-fixes` because it would delete other students' seeded bugs. I also learned to compare against `main` before trusting a failure: 30 chunker tests errored in my environment, and only running the same suite on unmodified `main` showed it was a tokenizer download blocked by the network, not my change. In my own projects, a red test is always my fault. Here I had to prove it wasn't.

**How did AI tools help — and where did they fall short?**
I used Claude heavily for Units 8–10. It ran the reproduction, spotted that `_strip_markdown()` shared the bug, wrote most of the fix and tests, and drafted PLAN.md and the PR description. The most useful thing it did was test the tests. It confirmed every new test fails on `main`, and it temporarily swapped `[^\S\n]*` for `\s*` to prove the blank-line test catches exactly that mistake. It fell short on everything outside the code. It couldn't open the PR on the course repo (I had to), it can't get a classmate to review a draft, it can't see whether CI turns green on #84, and it couldn't run the chunker tests in its sandbox. Honestly, its biggest limit is that it made it easy to compress four weeks into one sitting, and I skipped the parts of the process it can't do for me.

**What would you do differently if you started over?**
I'd read CONTRIBUTING.md *before* creating my branch in Unit 7. I named it `bug/54-resume-section-detection`, `bug` isn't an allowed type, and I had to switch to `fix/54-resume-section-whitespace` partway through, which changed the URL I submit. I'd also spread the work across the weeks as intended. That means opening a draft PR early and getting a peer to review it in Slack, instead of recording "none" for draft feedback, and recording the walkthrough video, since a real reviewer would probably have caught the `Experience-driven` false positive before I did.

**What are you most proud of from this module?**
The two guard tests that check the fix *doesn't* do too much: `test_detect_sections_ignores_header_word_mid_line` and `test_strip_markdown_indented_headers_keeps_blank_lines`. Making the failing tests pass was the easy part. Thinking about how a looser regex could break things that currently work, and locking that down, is the part that feels like real engineering rather than just closing an issue.

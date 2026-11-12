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

# Unit 7 — Issue Selection

**Issue Link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/58

**Issue Title:** Bias detector patterns are too narrow to match common phrasings

**Issue Tier:** Tier 1

## Problem Summary

PathReview's bias detector currently uses patterns that are too narrow to recognize certain biased statements when they are phrased differently. This can cause the system to miss language that should be flagged, reducing the effectiveness of its bias detection. The issue focuses on improving the detection patterns in `safety/bias_detector.py` while avoiding false positives. A successful fix would recognize more variations of biased language while ensuring that neutral statements are not incorrectly flagged.

## Why I Selected This Issue

I selected this Tier 1 issue because it has a clear scope and connects to my interest in responsible AI. The issue identifies the affected code and provides existing tests that can help verify the changes. I believe this is a manageable issue because I can focus on improving specific detection patterns without changing the overall application architecture. It also provides an opportunity to strengthen my understanding of testing, debugging, and building more reliable AI-related systems.

## Working Branch

`fix/58-bias-detector-patterns`

## Setup and Issue Claim Checklist

- [x] Selected a Tier 1 issue
- [x] Claimed Issue #58 on GitHub
- [x] Added Issue #58 to the Howard cohort ledger
- [x] Created my working branch
- [x] Completed the project setup
- [x] Successfully launched PathReview at localhost:5173
- [x] Committed and pushed `JOURNAL.md` to GitHub
---

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/jjoiles/pathreview-ai201-fa26-howard/commit/0c85268

**Reproduction summary:**
I reproduced the existing bias detector test results by running `.venv/bin/python -m pytest tests/unit/test_bias_detector.py -v` in my Codespace. The suite reported 23 passing tests and 9 expected failures (XFAIL), documenting known cases where the detector does not yet meet the expected behavior.

**PLAN.md link:** https://github.com/jjoiles/pathreview-ai201-fa26-howard/blob/fix/58-bias-detector-patterns/PLAN.md

**Walkthrough video (recommended):** Not recorded; optional and not graded.

**Blockers or open questions:**
I need to inspect the existing matching patterns and expected-failure cases to determine which rules require changes without introducing false positives.


---

## Unit 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
I reviewed the nine expected-failure tests for Issue #58 and implemented additional patterns in `safety/bias_detector.py` to recognize common alternative phrasings of educational-background and demographic assumptions. I removed the nine obsolete issue-specific xfail markers and added eleven focused test cases in `tests/unit/test_bias_detector.py`, including neutral examples that should not be flagged.

**Next steps:**
Run the focused tests, `make check`, and `make test-unit`; correct any errors, request peer or mentor feedback on a draft PR, and verify all five GitHub CI jobs before marking the PR ready.

**Blockers:**
Full local test and CI verification is pending.

---

### Check-in 2 (end of week)

**PR link:** Pending final PR verification.

**Branch:** `fix/58-bias-detector-patterns`

**What you built:**
Added focused patterns to recognize common biased feedback phrasings without changing the detector's public interface.

**Tests added or updated:**
`tests/unit/test_bias_detector.py` — removed nine obsolete issue-specific xfail markers and added eleven positive and negative examples.

**Self-review confirmation:** [ ] make check passes  [ ] make test-unit passes

**Draft PR feedback received from:** None yet; review requested when draft PR opens.

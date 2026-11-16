## Unit 7 — Issue selection

**Issue link:** (https://github.com/codepath/pathreview-ai201-fa26-howard/issues/64)

**Issue title:** Relevance scorer “partial overlap” test fixture actually has full query overlap

**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3

**Selection notes (Issue checklist reasoning):**
This issue is a good fit because it is limited in scope and affects a specific test case rather than a large architectural component. The issue description provides clear reproduction steps and a likely root cause, making it straightforward to verify and fix. I already have experience reading Python test files and running pytest, so I can confidently reproduce the failure and validate the solution. The expected change is small and well-defined, which makes it appropriate for a Tier 1 contribution.

**Problem summary:**
The issue is in the relevance scorer test suite, specifically test_query_with_partial_overlap. The test is intended to verify behavior when a query only partially overlaps with a text chunk, but the current fixture contains all query terms. Because the scorer correctly identifies full keyword coverage, it returns a score of 1.0 and causes the test assertion to fail. A successful fix will update the test data so it represents true partial overlap and accurately validates the intended scoring behavior.

**Branch name:** fix/64-partial-overlap-test-fixture

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** (https://github.com/codepath/pathreview-ai201-fa26-howard/commit/8300055894fda78b1ee828a65a3ea5f33e854118)

**Reproduction summary:**

I ran:

pytest tests/unit/test_relevance_scorer.py -q

The test suite completed with 18 passing tests and 1 expected failure (xfail). Although the specific assertion described in the issue was not reproduced as an active failing test, inspection of the issue and test code indicates that the fixture used by `test_query_with_partial_overlap` may still not accurately represent partial keyword overlap. Further investigation will focus on the test fixture and its expected behavior.

**PLAN.md link:** (https://github.com/codepath/pathreview-ai201-fa26-howard/commit/fdbaba75424ab8aff2e33d00f0b912279337f4b5)

**Blockers or open questions:**
None at the moment

## Unit 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**

I inspected `tests/unit/test_relevance_scorer.py` and confirmed that `test_query_with_partial_overlap` was intended to validate partial keyword overlap but used a fixture that created full overlap. I reproduced the issue through test inspection and local testing, then discussed an unexpected pre-commit mypy failure with the instructor. During that investigation, I found an upstream change intended to address the pre-commit issue and attempted to merge it locally.

**Next steps:**

Finish resolving the pre-commit validation issue, verify the updated test passes without the issue-specific `xfail` marker, run `make test-unit` and `make check`, and open a PR for review.

**Blockers:**

A pre-commit mypy check was failing on `tests/unit/test_relevance_scorer.py` even though `make check` and `make test-unit` passed. I reviewed an upstream fix, discussed the issue with the instructor, and used that guidance to complete the implementation.

---

### Check-in 2 (end of week)


**PR link:** https://github.com/codepath/pathreview-ai201-fa26-howard/pull/90#issue-6396271836

**PR Description:**
```
## Summary
This PR fixes Issue #64 by correcting the fixture used in test_query_with_partial_overlap.

The test was intended to validate partial keyword overlap, but the fixture text contained all query terms from "Python Django web framework", creating full overlap and causing the test expectation to be incorrect. The fixture was updated so only a subset of the query terms are present, allowing the test to accurately validate partial-overlap behavior.

## Issue
Closes #64

## Changes
- Removed the issue-specific @pytest.mark.xfail(...) marker from test_query_with_partial_overlap.
- Updated the fixture text from a full-overlap example to a genuine partial-overlap example.
- Kept the relevance scoring implementation unchanged since the issue was in the test fixture rather than the scorer itself.
- Applied the required test-file update needed to satisfy pre-commit validation during development.

## Testing
- [x] **CI is green on this PR (all five jobs)** — required for review
- [x] Unit tests pass (`make test-unit`)
- [x] Linter passes (`make lint`)
- [x] Type checker passes (`make typecheck`)
- [x] New/updated tests cover the changes
- [x] If this fixes a seeded bug: removed its `@pytest.mark.xfail` marker (and any matching suppression in `pyproject.toml`)

## Tests Ran
- `pytest tests/unit/test_relevance_scorer.py -q`
- `make test-unit`
- `make check`

All tests and validation checks passed after the fixture update.
## Notes for Reviewers
This change only updates test data and removes the issue-specific xfail marker. No production code or relevance-scoring logic was modified. The root cause was that the test fixture represented complete keyword coverage rather than partial keyword overlap, causing the test expectation to conflict with the scorer's correct behavior.

During implementation, a pre-commit `mypy` validation issue was encountered that was not reproduced by the project's normal validation workflow. After discussing the issue with the instructor and reviewing an upstream change intended to address the problem, the required annotation change was applied and the fix was completed successfully.
```

**Branch:** fix/64-partial-overlap-test-fixture

**What you built:**

I updated the fixture used by `test_query_with_partial_overlap` so that it represents genuine partial keyword overlap instead of full overlap. I removed the issue-specific `xfail` marker and verified the test now passes successfully. While implementing the fix, I also resolved a related pre-commit mypy validation issue in the same test file after reviewing an upstream change and discussing the issue with the instructor.

**Tests added or updated:**

Updated `tests/unit/test_relevance_scorer.py`. The modified test now validates partial-overlap scoring using a chunk that contains only a subset of the query terms. I also updated the empty-chunks test annotation required for successful pre-commit validation.

**Self-review confirmation:**

[x] make check passes  
[x] make test-unit passes

**Draft PR feedback received from:**
None yet, however
Instructor (guidance provided regarding the pre-commit mypy issue and upstream fix)
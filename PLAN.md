# Unit 8 — Solution Plan

## Solution plan

**Issue:** #58 — Bias detector patterns are too narrow to match common phrasings

**Issue link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/58

### Understand

The bias detector recognizes several biased statements but does not consistently recognize alternative phrasings of similar assumptions. The current detection patterns appear too narrow to cover all of the cases represented in the test suite.

Expected behavior: The detector should identify biased assumptions even when they use different wording, while leaving neutral technical feedback unflagged.

Actual behavior: Running the existing tests produces 23 passes and 9 expected failures (XFAIL). These expected failures document detection cases that still need improvement.

The likely root cause is incomplete phrase matching in the detector's existing rules. I will inspect the implementation and individual failing test cases to confirm which patterns are responsible before changing code.

### Map

Files involved:

- `safety/bias_detector.py` — contains the bias detection implementation and matching patterns.
- `tests/unit/test_bias_detector.py` — contains tests for recognized bias, alternative phrasings, and neutral feedback.
- `unit8-test-results.txt` — records the initial reproduction results.
- `JOURNAL.md` — documents investigation progress.
- `PLAN.md` — records the proposed implementation approach.

### Plan

1. Review `safety/bias_detector.py` and identify the existing detection patterns and matching logic.
2. Inspect the nine expected-failure cases in `tests/unit/test_bias_detector.py` to identify the wording variations currently missed.
3. Update only the relevant patterns to recognize additional biased phrasing, preserving existing behavior wherever possible.
4. Add or refine focused test cases covering the newly recognized phrases and similar neutral statements.
5. Run the bias detector test suite, compare results with the Unit 8 baseline, and check that existing passing tests remain successful.

### Inputs & outputs

Input: Text containing feedback, statements, or assumptions that may or may not indicate bias.

Expected output: The detector's existing return structure should accurately indicate whether bias was detected and provide the appropriate reason when applicable.

The fix should increase recognition of biased phrasing without changing the public interface or incorrectly flagging neutral feedback.

### Risks & unknowns

- Broadening patterns in `safety/bias_detector.py` may introduce false positives for neutral feedback.
- Some cases in `tests/unit/test_bias_detector.py` may require different matching strategies rather than a single broad regular expression.
- Similar words can have different meanings depending on context.
- The exact cause of each XFAIL needs to be confirmed by inspecting the implementation and test expectations.
- Existing tests must continue passing after any modifications.

### Edge cases

- Different capitalization of the same statement.
- Extra spaces or punctuation.
- Alternative wording for educational background or developer experience.
- Multiple biased indicators in one statement.
- Negative statements about educational qualifications.
- Neutral comparisons between developers and programmers.
- Objective technical feedback that should not be flagged.
- Empty or whitespace-only input.
- Statements that describe an observation without making a biased assumption.

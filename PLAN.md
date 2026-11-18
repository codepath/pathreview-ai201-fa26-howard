## Solution plan

**Issue:** Relevance scorer “partial overlap” test fixture actually has full query overlap
https://github.com/codepath/pathreview-ai201-fa26-howard/issues/64

### Understand

The test `test_query_with_partial_overlap` is intended to verify that the relevance scorer returns a middle-range score when only some query keywords appear in a chunk. However, the current chunk contains all four query terms from "Python Django web framework". Because the scorer correctly detects complete coverage, it returns a full score, causing the test expectation to be invalid.

### Map

Files involved:

- tests/unit/test_relevance_scorer.py

File expected to change:

- tests/unit/test_relevance_scorer.py

### Plan

1. Inspect the fixture used by `test_query_with_partial_overlap`.
2. Replace the chunk text with content containing only a subset of the query keywords.
3. Verify that the updated fixture produces a score below the full-match threshold.
4. Remove or update the xfail marker if the test now behaves correctly.
5. Run the full relevance scorer test suite to confirm no regressions.

### Inputs & outputs

Input:
- Query: "Python Django web framework"
- Test chunk text

Output:
- A fixture representing genuine partial overlap.
- A passing test that accurately validates partial-match scoring behavior.

### Risks & unknowns

- The scorer may tokenize or normalize text differently than expected.
- The replacement fixture must avoid accidentally matching all query terms.
- The xfail marker may need to be updated depending on test behavior after the fixture change.

### Edge cases

- The chunk contains none of the query terms, which should produce a low relevance score.
- The chunk contains only one query term, resulting in minimal overlap.
- The chunk contains some, but not all, query terms, which is the scenario this test should validate.
- The chunk contains all query terms, which should continue to produce a high or perfect relevance score.
- Changes to the fixture should not affect other tests that rely on the same scoring behavior.
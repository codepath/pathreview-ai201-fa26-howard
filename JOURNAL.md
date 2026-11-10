## Unit 7 — Issue selection

**Issue link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/68

**Issue title:** Keyword search raises `ZeroDivisionError` when the index is empty

**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The keyword search in the RAG retriever (`rag/retriever/keyword_search.py`) crashes if it is asked to index an empty list of documents. `KeywordSearcher.index()` hands the empty corpus straight to the BM25 library, which divides by zero and raises `ZeroDivisionError`. Meanwhile `search()` already handles the empty case by returning an empty list, so the two methods behave inconsistently. A successful fix lets `index([])` finish without an error and leaves search returning no results, and it removes the `xfail` marker (manifest id H-01) from the test in `tests/unit/test_keyword_search.py` so that the test passes for real.

**"Is this right for me?" reasoning:**
- Tier 1 with an estimated effort of 2-4 hours, so it fits the four-week schedule.
- Small scope: one source file and one test file, in the RAG module.
- The bug reproduces with a simple input (`index([])`), and an existing test already describes the expected behavior.
- Risk: another student (gerypilot) has already claimed this issue and opened PR #74. I am working on my own branch and will add my own edge-case tests.

**Branch name:** fix/68-keyword-search-empty-index

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [ ] Issue added to cohort ledger

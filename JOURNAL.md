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

## Unit 8 — Reproduction & solution planning

### Reproduction steps (run locally on branch `fix/68-keyword-search-empty-index`)

```bash
.venv/bin/python -c "
from rag.retriever.keyword_search import KeywordSearcher
KeywordSearcher().index([])
"
```

Observed:

```
File "rag/retriever/keyword_search.py", line 25, in index
    self.bm25 = BM25Okapi(tokenized_corpus)
File ".venv/lib/python3.12/site-packages/rank_bm25.py", line 101, in _calc_idf
    self.average_idf = idf_sum / len(self.idf)
ZeroDivisionError: division by zero
```

The same crash happens with `KeywordSearcher().index([{"text": ""}])`. The divisor in rank-bm25 is `len(self.idf)`, which is the number of distinct words. It is not the number of documents. So any corpus with zero tokens crashes, even when the list of chunks is not empty. The existing `test_empty_index` test (xfail, H-01) covers only the empty-list case. I added two strict-xfail tests for the other cases I found: whitespace-only chunks, and re-indexing a populated searcher with `[]`.

**Reproduction commit link:** https://github.com/joshuadonatien/pathreview-ai201-fa26-howard/commit/5a80d87

**Reproduction summary:**
I called `KeywordSearcher().index([])` from the project venv and got `ZeroDivisionError: division by zero` from `rank_bm25._calc_idf`, which divides by the vocabulary size. Chunks with only empty or whitespace text crash the same way. I recorded this with two new strict-xfail tests next to the existing H-01 test.

**PLAN.md link:** https://github.com/joshuadonatien/pathreview-ai201-fa26-howard/blob/fix/68-keyword-search-empty-index/PLAN.md

**Walkthrough video (recommended):** Not recorded.

**Blockers or open questions:**
PR #74 from another student also targets #68. My plan covers the wider empty-vocabulary case and not only `chunks == []`. Issue #6 (`HybridRetriever` never calls `index()`) is a separate bug that I am leaving out of scope.

## Unit 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
PLAN.md sub-task 1 is done: I reproduced the crash locally and pinned it down with tests (commit 5a80d87). There are three strict-xfail tests: `test_empty_index` (H-01), `test_index_chunks_without_tokens` and `test_reindex_with_empty_corpus_clears_previous_index`. I also checked the "mixed corpus" risk from PLAN.md by hand. BM25 indexes it fine and the token-less chunks score 0.0, so that case needs no code change.

**Next steps:**
Sub-tasks 2–5: add the `if not any(tokenized_corpus)` guard to `KeywordSearcher.index()`, reset `self.bm25` to `None` on that path, remove the three xfail markers, run `make check` and `make test-unit`, then fill in the template on my open PR #87.

**Blockers:**
None.

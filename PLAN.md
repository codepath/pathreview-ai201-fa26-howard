## Solution plan

**Issue:** Keyword search raises `ZeroDivisionError` when the index is empty: https://github.com/codepath/pathreview-ai201-fa26-howard/issues/68

### Understand

`KeywordSearcher.index()` in `rag/retriever/keyword_search.py` tokenizes every chunk and passes the result straight to `rank_bm25.BM25Okapi`. While it builds the index, rank-bm25 runs `_calc_idf()`, which computes `average_idf = idf_sum / len(self.idf)`. `self.idf` has one entry per distinct word, so when the corpus has no tokens the divisor is 0 and the constructor raises `ZeroDivisionError`.

- **Expected:** indexing an empty corpus succeeds, and `search()` then returns `[]`. `search()` already does this when `index()` was never called: it checks `if not self.bm25 or not self.chunks` and logs `keyword_search_empty_index`.
- **Actual:** `index([])` raises before `search()` ever runs.

I reproduced this and found that the root cause is broader than the issue title. An empty **vocabulary** causes the crash, not only an empty list. `index([{"text": ""}])` and `index([{"text": "   "}])` crash the same way.

### Map

| File | Role | Change? |
|---|---|---|
| `rag/retriever/keyword_search.py`: `KeywordSearcher.index()` | Builds the BM25 index; the crash happens here | **Yes**: add the empty-vocabulary guard |
| `rag/retriever/keyword_search.py`: `KeywordSearcher.search()` | Already returns `[]` when `self.bm25` is `None` | No; I rely on its existing guard |
| `tests/unit/test_keyword_search.py` | `test_empty_index` (xfail H-01), plus my 2 new xfail tests | **Yes**: remove the 3 xfail markers |
| `rag/retriever/hybrid.py`: `HybridRetriever.retrieve()` | The only caller of `keyword_searcher.search()` | No; read only, to confirm `[]` is handled (`max(..., default=1.0)`) |
| `.venv/.../rank_bm25.py`: `BM25._calc_idf` | Third-party code that divides by the vocabulary size | No; I don't patch dependencies |

### Plan

1. **Reproduce and pin down the behavior with tests.** *(done in commit `5a80d87`)* Confirm the traceback, then add strict-xfail tests for whitespace-only chunks and for re-indexing a populated searcher with `[]`.
2. **Guard `index()`.** After tokenizing, check whether every token list is empty (`if not any(tokenized_corpus)`). If so, set `self.bm25 = None`, log a `keyword_index_empty` warning, and return early without calling `BM25Okapi`. Otherwise keep the current behavior.
3. **Reset stale state.** Make sure the guard path still assigns `self.chunks = chunks` and clears `self.bm25`. Then a searcher that was indexed before and is re-indexed with `[]` won't return results from the old index.
4. **Remove the xfail markers.** Delete `@pytest.mark.xfail(strict=True)` from `test_empty_index` (H-01) and from my two new tests. Check `pyproject.toml` for any matching suppression.
5. **Verify.** Run `make check` and `make test-unit`, and confirm there are no XPASS failures and the xfail count drops by 3. Then fill in the PR template and push.

### Inputs & outputs

- **Input:** `chunks: list[dict]`, where each dict has a `"text"` field. This could be `[]`, chunks with empty or whitespace-only text, or a normal corpus.
- **Output / state change:** `index()` still returns `None` and its signature does not change. On an empty vocabulary it sets `self.bm25 = None` and `self.chunks = chunks`, and logs `keyword_index_empty` instead of raising. After that, `search(query, top_k)` returns `[]`. Normal corpora behave exactly as before.

### Risks & unknowns

- **Changing search behavior for normal corpora.** The guard has to trigger only when the vocabulary is empty. If I used `if not chunks`, the whitespace-only case would still crash. If I checked something too broad, a valid corpus could lose its index. The 16 existing tests in `tests/unit/test_keyword_search.py` (sorting, top_k, case-insensitivity, 1000-doc corpus) check for regressions.
- **Mixed corpora.** If some chunks have tokens and some don't, BM25Okapi builds fine. I need to confirm that `search()` still returns those token-less chunks with a score of 0 rather than crashing.
- **Interaction with `HybridRetriever`.** `rag/retriever/hybrid.py` has a separate seeded bug (issue #6): it never calls `keyword_searcher.index()`. I'm not fixing that here. Keeping this PR scoped to #68 avoids conflicting with whoever takes #6.
- **Competing PR.** PR #74 (gerypilot) also targets #68. Mine also covers the empty-vocabulary case, which a `len(chunks) == 0` check would miss.
- **mypy.** `self.bm25` is set to `None` in `__init__` and has no annotation, so I have to make sure `make typecheck` still passes once I add a second `None` assignment.

### Edge cases

1. `index([])` → no exception, `search("python")` returns `[]` (existing test `test_empty_index`).
2. `index([{"text": ""}, {"text": "   \n\t"}])` → no exception, and `search()` returns `[]` (`test_index_chunks_without_tokens`).
3. `index(real_chunks)` then `index([])` → the old index is cleared, so `search()` returns `[]` and not stale results (`test_reindex_with_empty_corpus_clears_previous_index`).
4. `search()` before `index()` is ever called → still `[]` (existing `test_index_not_called_returns_empty`).
5. A mixed corpus where only some chunks have text → still indexes and ranks normally.

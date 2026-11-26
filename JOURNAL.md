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

---

### Check-in 2 (end of week)

**PR link:** https://github.com/codepath/pathreview-ai201-fa26-howard/pull/87

**Branch:** `fix/68-keyword-search-empty-index`

**What you built:**
`KeywordSearcher.index()` in `rag/retriever/keyword_search.py` now checks for an empty vocabulary (`if not any(tokenized_corpus)`) before calling `BM25Okapi`. When that check is true it clears `self.bm25`, logs `keyword_index_empty` and returns, so `search()` returns `[]` instead of the index crashing with `ZeroDivisionError`. This handles an empty chunk list, chunks with only whitespace text, and re-indexing a populated searcher with an empty corpus.

**Tests added or updated:**
`tests/unit/test_keyword_search.py`. I removed the strict xfail marker from `test_empty_index` (manifest H-01). It now passes and checks that `index([])` followed by `search()` returns `[]`. I added `test_index_chunks_without_tokens`, which checks that indexing chunks whose text is `""` or `"   \n\t"` doesn't raise and that search returns `[]`. I also added `test_reindex_with_empty_corpus_clears_previous_index`, which checks that after indexing real chunks and then `index([])`, search returns `[]` and not stale results from the old index. Unit suite: 378 passed, 52 xfailed (was 375 passed, 53 xfailed).

**Self-review confirmation:** [x] make check passes  [x] make test-unit passes

**Draft PR feedback received from:** none

## Unit 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [ ] Yes  [x] No — still awaiting review

**Summary of feedback:**
No review has come in on PR #87 yet. No reviewer or maintainer comments, and I didn't get draft feedback in Slack before submitting.

**How you responded:**


---

### Reflection

**What was harder than you expected?**
The bug was bigger than its title. Issue #68 says "when the index is empty," so my first idea was an `if not chunks: return` guard. When I reproduced it, the traceback pointed into `rank_bm25._calc_idf`, which divides by `len(self.idf)`. That's the number of distinct words, not the number of documents. So `index([{"text": "   "}])` crashes too, and the obvious one-line fix would have left a real bug in place. Keeping up with the process was also harder than the code. I opened PR #87 back in Unit 7 with only my journal in it and an empty template, then let it sit, so a lot of the planning, fixing and documenting got squeezed together at the end.

**What did you learn about working in a large codebase?**
Most of the time went to reading code I wasn't going to change. Before I knew my fix was safe, I had to check that `HybridRetriever.retrieve()` in `rag/retriever/hybrid.py` is the only caller of `search()` and that it handles an empty list (`max(..., default=1.0)`). There I found a comment marking a *different* seeded bug (#6: it fetches chunks and never indexes them) that I had to deliberately leave alone. In my own projects I would just have fixed it. Here, fixing it would collide with someone else's issue and make my PR harder to review. I also learned to trust the repo's conventions over my own habits: Conventional Commit scopes like `fix(rag):`, the strict-xfail contract, and the CI comment that explains why `make test-integration` exits 5 locally but is green in CI.

**How did AI tools help — and where did they fall short?**
I used Claude Code for a lot of this: navigating the repo, running the reproduction and drafting PLAN.md and the PR description. It was most useful for going one layer deeper than the issue. It opened the installed `rank_bm25.py` in the venv, found the exact divide-by-zero line and tested the whitespace-only case, which is how the "empty vocabulary" framing came up. It fell short on judgment calls that depend on context outside the code. It couldn't get me peer feedback in Slack, it didn't know whether an older empty PR should be reused or replaced, and when `make test-integration` failed locally I had to read `.github/workflows/ci.yml` to confirm that exit code 5 was expected and not caused by my change. I also had to check that its claims matched real output (375→378 passed, 53→52 xfailed) and not just accept a summary.

**What would you do differently if you started over?**
I'd keep the weekly rhythm the course is built around and not batch the work at the end. Reproduce in Unit 8 week, open a real draft PR early in Unit 9, and post it in Slack so a classmate could review it. As it was, "Draft PR feedback received from" is "none," and that's my fault. I also wouldn't open a PR before there's code in it. PR #87 sat open for weeks with only `JOURNAL.md` and a blank template, which is noise for maintainers. Finally, since PR #74 was already open on the same issue, I'd comment on #68 early to coordinate, or pick an unclaimed Tier 1 issue.

**What are you most proud of from this module?**
I'm most proud of finding the whitespace-only and re-index-to-empty edge cases and writing them up as failing strict-xfail tests *before* writing the fix. The fix is about five lines, but the tests prove it covers the actual root cause (an empty BM25 vocabulary) and not just the symptom in the issue title. That's what sets my PR apart from a `len(chunks) == 0` patch.

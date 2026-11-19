## Unit 7 — Issue selection 

**Issue link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/60
**Issue title:** Faithfulness checker crashes when a context chunk has `text: None`
**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3 

**Problem summary:** 
The `FaithfulnessChecker` crashes with a `TypeError` when a context chunk's text is explicitly set to `None`. This happens because `.get("text", "")` returns `None` instead of the default empty string when the key exists but has a null value, causing the subsequent string join operation to fail. A successful fix will ensure the method handles `None` values correctly without crashing the application.

**Branch name:** fix/60-faithfulness-checker-crash

**Setup confirmation:** 
[x] App runs locally at localhost:5173 

**Cohort ledger:** 
[x] Issue added to cohort ledger

## Unit 8 — Reproduction & solution planning
**Reproduction commit link:** https://github.com/mezier-jamarri/pathreview-ai201-fa26-howard/commit/ba6ad277e17558a478c147f9e017db0667816b11
**Reproduction summary:** I removed the `xfail` marker from `test_none_context_chunk_text`. Running this test successfully reproduced the expected `TypeError` crash because `.get("text", "")` returns `None` instead of an empty string.
**PLAN.md link:** https://github.com/mezier-jamarri/pathreview-ai201-fa26-howard/commit/25035e22ddd1b7e2f1a65fa339b8bc8247c068f8
**Walkthrough video (recommended):** N/A
**Blockers or open questions:** None.

## Unit 9 — Solution building & PR submission

### Check-in 1 
**Current progress:** Implemented the `None`-safe text extraction in `FaithfulnessChecker.check()` (`rag/evaluator/faithfulness_checker.py`), removed the obsolete `xfail` marker from `test_none_context_chunk_text`, and added a unit test covering mixed `None` and valid context chunks in `tests/unit/test_faithfulness_checker.py`.
**Next steps:** Open a draft PR for peer/mentor review, verify all five CI checks pass, mark the PR ready for review, and finalize `JOURNAL.md`.
**Blockers:** None.

---

### Check-in 2 
**PR link:** https://github.com/codepath/pathreview-ai201-fa26-howard/pull/102
**Branch:** `fix/60-faithfulness-checker-crash`
**What you built:** Updated `FaithfulnessChecker.check()` in `rag/evaluator/faithfulness_checker.py` to use `chunk.get("text") or ""` when concatenating context chunks, preventing a `TypeError` when a chunk's `"text"` value is explicitly `None`.
**Tests added or updated:** Updated `tests/unit/test_faithfulness_checker.py` by removing the `@pytest.mark.xfail(strict=True)` marker from `test_none_context_chunk_text` and adding `test_mixed_none_and_valid_context_chunks` to verify valid chunks still score accurately alongside `None` chunks.
**Self-review confirmation:** [x] make check passes  [x] make test-unit passes
**Draft PR feedback received from:** none
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


## Unit 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [ ] Yes  [x] No — still awaiting review

**Summary of feedback:**
No reviewer feedback has come in yet on PR #102.

**How you responded:**


---

### Reflection

**What was harder than you expected?**
The actual bug fix in `rag/evaluator/faithfulness_checker.py` was a one-line change (`chunk.get("text") or ""`), so I expected the rest of the workflow to be quick. What actually took the most effort was navigating the repo's tooling and strict quality gates: dealing with `XPASS(strict)` when my fix made the seeded `test_none_context_chunk_text` test pass, catching a stray whitespace lint error (`W293`) in `ruff`, and hitting a surprise pre-commit `mypy` failure (`var-annotated`) on two pre-existing empty `context_chunks = []` lists in `tests/unit/test_faithfulness_checker.py` that `make check` didn't flag because `make check` only type-checks the main package directories.

**What did you learn about working in a large codebase?**
In a personal project, you can usually change code, run a quick test, and move on. In a production-style codebase like PathReview, the code change is only half the job—the other half is respecting the existing architecture, conventions, and automated checks. I learned how strict `xfail` markers are used to keep `main` green while tracking known bugs, why pre-commit hooks and CI checks (`lint`, `typecheck`, `test-unit`, `test-integration`, `frontend`) matter, and how to write focused commits and a thorough PR description so a reviewer can understand the root cause without guessing.

**How did AI tools help — and where did they fall short?**
AI was most useful for auditing my work against `CONTRIBUTING.md`, translating cryptic tool output (like `XPASS(strict)` and `mypy`'s `var-annotated` hook error) into exact file and line fixes, and structuring my `PLAN.md` and PR description cleanly. Where it fell short was in the local environment and file state—AI can't see my unsaved edits, invisible trailing spaces, or which files are staged in Git until I paste the exact terminal output, so I still had to inspect the diffs, run the test suite in isolation, and verify every check myself.

**What would you do differently if you started over?**
I would start implementing and opening my draft PR earlier in Unit 9 instead of submitting right at the wire. Because my PR went up late, I didn't have time to get peer or mentor feedback on the draft before marking it ready for review. I would also run `pre-commit` / `mypy` on the test file earlier and check `git log` and `CONTRIBUTING.md` before making my first commit so my commit messages followed conventional commit format from the start.

**What are you most proud of from this module?**
Getting PR #102 open on the upstream repo with all 6/6 CI checks passing on the first run—especially after working through the `xfail`, `ruff`, and `mypy` pre-commit hurdles without taking shortcuts or bypassing any checks.
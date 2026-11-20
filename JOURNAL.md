## Unit 7 — Issue selection

**Issue link:** [https://github.com/codepath/pathreview-ai201-fa26-howard/issues/66](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/66)

**Issue title:** structlog output is not captured by pytest caplog — log assertions fail suite-wide

**Tier:** [X] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The app logs through structlog, but structlog isn’t wired into Python’s standard logging during tests, so pytest’s caplog never sees the messages. The code logs correctly, but the log assertions fail. In tests, structlog isn’t configured to hand its output to Python’s standard logging, so every caplog assertion in the suite fails. The fix is to configure structlog in tests/conftest.py so events become standard log records.

**Branch name:** fix/66-structlog-caplog

**Setup confirmation:** [X] App runs locally at localhost:5173

**Cohort ledger:** [X] Issue added to cohort ledger

**Selection notes ("Is this right for me?" checklist):**

- [x] I can explain the problem and the expected behavior in 2–3 sentences without reading the issue.
- [x] I've located the relevant files and confirmed they exist in the codebase.
- [x] I can describe a concrete before-and-after: what the user sees before the fix and what they see after.
- [x] I'm choosing Tier 1.
- [x] I'm not choosing a Tier 3 issue to "challenge myself" if I haven't completed a Tier 1 or 2 first — scope surprises in Unit 9 don't have a safety net.
- [x] I've found and read the specific code the issue references (not just the file — the function or section).
- [x] I've read enough surrounding context that I can write a rough plan for the fix without looking anything up.
- [x] I've found the test file for my module and read at least one test end-to-end.
- [x] I've checked the issue comments and the ledger's Claims count, and I'm fine with how many others are on this issue.
- [x] I've estimated the time this will take and I'm confident I can complete it before the Unit 9 deadline.
- [x] This issue has no open blockers or dependencies on other unresolved issues.

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** [https://github.com/zami116/pathreview-ai201-fa26-howard/commit/46af9b088bdfa353f5f9803603e39d128aa41dad](https://github.com/zami116/pathreview-ai201-fa26-howard/commit/46af9b088bdfa353f5f9803603e39d128aa41dad)

**Reproduction summary:**
I ran the failing test with `--runxfail` and saw the warning print to the terminal while `caplog.text` stayed empty, so the assertion at `tests/unit/test_batch_processor.py:48` fails. This shows structlog's output isn't reaching Python's standard logging during tests.

Steps to reproduce:

```bash
source .venv/Scripts/activate
pytest tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_empty_chunks_list_returns_empty -q -s --runxfail
```

- `--runxfail` is needed because the test is marked `xfail(strict=True)`; without it pytest reports `1 xfailed`.
- Observed: `[warning] Empty chunks list provided to BatchEmbeddingProcessor` prints to the terminal, then `AssertionError: assert ('Empty chunks list' in '' or False)`.
- structlog is configured in `core/logging.py` (line 40). Only one test currently uses `caplog`.

**PLAN.md link:** [PLAN.md](https://github.com/zami116/pathreview-ai201-fa26-howard/blob/fix/66-structlog-caplog/PLAN.md)

**Walkthrough video (recommended):** [link to your Loom video, ≤2 min — recommended, not graded]

**Blockers or open questions:**

- Not sure yet whether cache_logger_on_first_use=True affects loggers created before the test fixture runs; I'll check this in Unit 9.
- `configure_logging()` is only called from `scripts/seed_db.py`, so the API itself doesn't set up logging either. I'm not sure if that's intended, but I'm keeping the fix scoped to the tests as the issue describes.

## Unit 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
Reproduced the failure and finished PLAN.md in Unit 8. Since then I read `core/logging.py` and `tests/conftest.py`, and found that `configure_logging()` already routes structlog through the standard library but is only called from `scripts/seed_db.py`, so the test suite never runs it. That narrowed the fix to `tests/conftest.py`. Sub-tasks 1 (confirm callers of `configure_logging`) is done; I hadn't started the fixture yet.

**Next steps:**
Add a session-scoped autouse fixture in `tests/conftest.py` that calls `configure_logging()`, remove the `xfail(strict=True)` marker from `test_empty_chunks_list_returns_empty`, run `make check` and `make test-unit`, and open a draft PR.

**Blockers:**
None.

---

### Check-in 2 (end of week)

**PR link:** https://github.com/codepath/pathreview-ai201-fa26-howard/pull/103#issue-6501934307

**Branch:** `fix/66-structlog-caplog`

**What you built:**
I added a session-scoped autouse fixture in `tests/conftest.py` that calls the app's existing `configure_logging()` and then resets structlog's defaults when the session ends. Before this, tests ran with structlog's unconfigured default, which printed to the terminal without creating standard-library log records, so `caplog` captured nothing. Now structlog events go through stdlib logging and `caplog` sees them.

**Tests added or updated:**
`tests/unit/test_batch_processor.py`: I removed the `@pytest.mark.xfail(strict=True)` marker from `test_empty_chunks_list_returns_empty`, which now passes and checks that the "Empty chunks list" warning reaches `caplog`. `tests/conftest.py` contains the fixture itself. `make test-unit` gives 376 passed and 52 xfailed.

**Self-review confirmation:** [x] make check passes  [x] make test-unit passes

**Draft PR feedback received from:** none

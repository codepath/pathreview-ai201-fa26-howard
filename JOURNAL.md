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

## Unit 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [ ] Yes  [x] No — still awaiting review

**Summary of feedback:**
No review came in. My instructor told us to skip the peer-review step this cycle because it's close to the end of classes, so I didn't request a draft review.

**How you responded:**
No feedback to respond to. If a reviewer comments after I submit, I'll reply on the PR and make any changes I agree with.

---

### Reflection

**What was harder than you expected?**
Getting the environment working took longer than writing the fix. My `.venv` still pointed at an old folder path, so `make setup` failed with a launcher error and `pytest` couldn't import `structlog` or `tiktoken`. Then `pre-commit` wasn't found when I committed from GitHub Desktop, and the database migration failed with `ConnectionRefusedError` because Docker wasn't running yet. The setup guide also told me to set an OpenRouter key that my `.env.example` didn't have, so I had to check the guide against the actual repo instead of trusting it.

**What did you learn about working in a large codebase?**
In my own projects I know where everything is, but here the fix depended on reading code I didn't write. Issue #66 said log assertions fail "suite-wide," but `grep` showed only one test used `caplog`. I also found that `configure_logging()` in `core/logging.py` already routes structlog through the standard library, but it's only called from `scripts/seed_db.py`, so the tests never ran it. That turned a vague "configure structlog" task into adding one fixture in `tests/conftest.py`. I also learned that a `strict=True` xfail marker has to be removed in the same change as the fix, or the unexpected pass counts as a failure.

**How did AI tools help — and where did they fall short?**
AI helped most with reading error output, like spotting the stale venv path, and with explaining why structlog's default output never reaches `caplog`. It also helped me structure the plan and journal. Where it fell short: my first plan assumed I'd need to write new structlog configuration and that `configure_logging()` ran at app startup. Reading `core/logging.py` and `conftest.py` myself and running `grep` showed that was wrong, so I had to correct the plan. I learned to treat AI suggestions as a hypothesis and check them against the real files and command output.

**What would you do differently if you started over?**
I'd verify my environment first, by running the full test suite right after `make setup`, before choosing an issue or writing anything. That would have caught the broken venv and missing dependencies in minutes. I'd also read the code an issue points to before claiming it, and I'd start the plan from what the files actually contain. I'd also keep unrelated edits, like my `docker-compose.yml` change, out of the working branch from the start.

**What are you most proud of from this module?**
I'm most proud of tracing the root cause myself instead of just following the issue text. I checked where `configure_logging()` was called, found that tests never ran it, and ended up with a small, focused fix that made the test pass and left the other 375 unit tests alone.

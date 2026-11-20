## Solution plan

**Issue:** structlog output is not captured by pytest caplog — log assertions fail suite-wide ([#66](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/66))

### Understand

`core/logging.py::configure_logging()` already routes structlog through the standard library (`LoggerFactory()` plus stdlib processors), which is what `caplog` needs. But nothing in `tests/conftest.py` calls it, so tests run with structlog's unconfigured default, which prints to the terminal and never creates `LogRecord`s. Expected: `caplog.text` contains "Empty chunks list". Actual: `''`. Grep shows `configure_logging()` is only called from `scripts/seed_db.py`, so it isn't run during tests (or by the API code).

### Map

- `core/logging.py` (`configure_logging`, `get_logger`): existing config; probably no change.
- `tests/conftest.py`: add a fixture that calls `configure_logging()`.
- `tests/unit/test_batch_processor.py`: remove the `xfail(strict=True)` marker from `test_empty_chunks_list_returns_empty`.
- `ingestion/embeddings/batch_processor.py`: check how and when its logger is created.
- `scripts/seed_db.py` (line 20): the only place `configure_logging()` is called today; nothing in `api/` or the test suite calls it.

### Plan

1. Confirmed by grep that `configure_logging()` is only called from `scripts/seed_db.py`; still need to check how `BatchEmbeddingProcessor` creates its logger.
2. Add a session-scoped autouse fixture in `tests/conftest.py` that calls `configure_logging()` before any test logs.
3. Remove the `xfail` marker from the test.
4. Run the target test, then `pytest -q` and compare to the baseline.
5. Check that info/debug-level events also appear in `caplog`, and adjust the log level if not.

### Inputs & outputs

Input: structlog events logged by app code during tests (for example the warning from `BatchEmbeddingProcessor.process([])`). Output: standard-library log records that show up in `caplog.text` and `caplog.records`, so `test_empty_chunks_list_returns_empty` passes with the `xfail` marker removed. No application code changes; only `tests/conftest.py` and `tests/unit/test_batch_processor.py` change.

### Risks & unknowns

- `cache_logger_on_first_use=True`: a logger used before the fixture runs keeps the old config. A session-scoped fixture should run first, but I need to verify.
- `logging.basicConfig` does nothing if the root logger already has handlers, and pytest adds its own, so the configured level may not apply.
- Importing `core.logging` imports `core.config.settings`, which may need env vars (`.env`) that aren't present in CI.
- The `xfail` is `strict=True`, so the marker has to be removed in the same commit as the fix.

### Edge cases

- Info and debug events, since the root logger defaults to WARNING.
- `APP_ENV=production` switches to the JSON renderer; the test's substring match should still pass.
- Tests that don't use `caplog` should behave the same.
- A single test run and a full-suite run should give the same result.

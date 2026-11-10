# Contribution Journal

## Unit 7 — Issue selection

**Issue link:** https://github.com/codepath/pathreview-ai201-fa26-howard/issues/5

**Issue title:** Add end-to-end ingestion test with a sample resume fixture

**Tier:** [ ] Tier 1  [x] Tier 2  [ ] Tier 3

**Problem summary:**
The ingestion pipeline turns an uploaded resume into stored, searchable chunks,
but its main entry point, `IngestionPipeline.ingest_resume` in
`ingestion/pipeline.py`, has no test. The resume parser and the batch embedding
processor each have unit tests, but nothing checks that the steps work together
from parsing through chunking to embedding storage. So a break between those
steps could slip through even with all the unit tests passing. A good fix adds
an integration test in `tests/integration/test_ingestion_pipeline.py`. The test
runs a real sample resume from `tests/fixtures/sample_resumes/` through the whole
pipeline and checks that the returned `chunk_count` is correct.

**Branch name:** test/5-ingestion-pipeline-e2e

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger

### Selection notes: "Is this issue right for me?"

**Part 1: Understanding the issue**

- [x] I can explain the problem and the expected behavior in 2–3 sentences
  without reading the issue.
  Notes: `ingest_resume` connects parsing, chunking, embedding, and storage, but
  no test runs those steps together. After the fix, a test feeds a sample resume
  through the whole pipeline and checks the result.
- [x] I've located the relevant files and confirmed they exist in the codebase.
  Notes: `ingestion/pipeline.py` (`IngestionPipeline.ingest_resume`) and
  `tests/fixtures/sample_resumes/` (`new_grad.md`, `mid_career.md`) exist.
  `tests/integration/` exists but `test_ingestion_pipeline.py` does not yet, so
  I'll be creating it. Labels: `ingestion`, `tests`, `enhancement`.
- [x] I can describe a concrete before-and-after.
  Notes: Before, a break between parsing, chunking, and embedding storage can
  ship with every unit test passing. After, `pytest tests/integration` runs a
  real resume end to end and fails if `chunk_count` is wrong or a step breaks.

**Part 2: Tier fit**

- [x] The tier is a realistic match for where I am right now.
  Notes: I've worked in large codebases and contributed to open source before,
  so a Tier 2 issue is a fair match for my skill level. This is a Tier 2 issue. It touches several modules (parser, chunking
  strategy selector, batch embedding processor), but the change is a new test
  file, not changes to production code, which keeps the risk down.

**Part 3: Codebase readiness**

- [x] I've found and read the specific code the issue references.
  Notes: `ingest_resume` hashes the content into a `source_id`, calls
  `_check_skip` (a DB lookup), then `ResumeParser.parse` →
  `StrategySelector.chunk` → `BatchEmbeddingProcessor.process`, records the
  source, and returns `IngestResult(chunk_count=len(chunks))`.
- [x] I can write a rough plan for the fix.
  Notes: Build an `IngestionPipeline` with a mock embedding provider (returning
  one vector per chunk), a mock vector DB, and a mock DB session. The session
  mock must make `.query().filter_by().first()` return `None`. Otherwise the
  default `Mock` is truthy and the pipeline takes the "already ingested" skip
  path with `chunk_count=0`. Load `new_grad.md`, run `ingest_resume`, then assert
  `skipped is False`, `chunk_count > 0`, and that `chunk_count` matches the
  number of chunks sent to the vector DB.
- [x] I've found the test file for my module and read at least one test
  end-to-end.
  Notes: `tests/unit/test_batch_processor.py` uses `Mock()` fixtures for the
  embedding provider and vector DB and is marked `@pytest.mark.unit`. My test
  will follow that pattern in an integration-marked test.

**Part 4: Scope and time**

- [x] I've checked the issue comments and the ledger's Claims count, and I'm
  fine with how many others are on this issue.
  Notes: The only comment on issue #5 is my claim. I've added the issue to the
  cohort ledger and checked its Claims count.
- [x] I've estimated the time and I'm confident I can finish before the Unit 9
  deadline.
  Notes: The issue estimates 4–6 hours. The work is one new test file with no
  production code changes.
- [x] This issue has no open blockers or dependencies on other unresolved
  issues.
  Notes: The issue body has no "blocked by" references and none of its labels
  mark it as blocked.

**Verdict:** Ready to claim. Every box is checked. The scope is one new
integration test file with no production code changes. That fits the Tier 2
estimate of 4–6 hours and my experience, and I already have a plan, including
mocking the DB session so the pipeline doesn't skip ingestion.

## Unit 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/madelinegilmore/pathreview-ai201-fa26-howard/commit/e3080aa19fefd97a1cc1aa2e3352058db66e9662

**Reproduction summary:**
I confirmed that no test calls `IngestionPipeline.ingest_resume`, and that the
unit suite covers 0% of `ingestion/pipeline.py`. I then ran
`tests/fixtures/sample_resumes/new_grad.md` and `mid_career.md` through
`ingest_resume` with mocked dependencies. The pipeline works (`chunk_count=1`,
1 embedding call, 1 `vector_db.add`), but a plain `Mock()` DB session silently
skips ingestion with `chunk_count=0`, so a naive test would never exercise it.

**Reproduction steps:**

1. Search the tests for the pipeline. Nothing references it, and
   `tests/integration/` holds only `__init__.py`:

   ```bash
   grep -rn "ingest_resume\|IngestionPipeline" tests   # no matches
   ```

2. Measure coverage with the unit suite. Result: 375 passed, 53 xfailed.
   `ingestion/pipeline.py` reports 105 statements, 105 missed, **0%** covered:

   ```bash
   .venv/bin/python -m pytest tests/unit -q --cov=ingestion --cov-report=term-missing
   ```

3. Run a fixture through the pipeline with a mock embedding provider (one
   1536-dim vector per text), a mock vector DB, and a mock DB session:

   | DB session mock | Result |
   |---|---|
   | plain `Mock()` | `skipped=True`, `chunk_count=0`, "Source already ingested". Parsing, chunking and embedding never run. |
   | `.query().filter_by().first()` returns `None` | `skipped=False`, `chunk_count=1`. 5 sections parsed, 1 embed call, 1 `vector_db.add`. |

   Both fixtures give the same result.

**Where the gap lives:** `IngestionPipeline.ingest_resume` in
`ingestion/pipeline.py`. Its skip check, `_check_skip`, runs
`db_session.query(...).filter_by(...).first()`. The missing test belongs in
`tests/integration/test_ingestion_pipeline.py`, which doesn't exist yet.

**PLAN.md link:** https://github.com/madelinegilmore/pathreview-ai201-fa26-howard/blob/test/5-ingestion-pipeline-e2e/PLAN.md

**Walkthrough video (recommended):** [link to your Loom video, ≤2 min — recommended, not graded]

**Blockers or open questions:**
- The pipeline's real `_check_skip` and `_record_ingested_source` are
  placeholders (`query("IngestedSource")` and a log-only record). The test
  should mock the DB session rather than use a real database. Confirm that's
  acceptable for an "integration" test.
- Resumes use the semantic chunker (~500-token target), so both fixtures come
  out as 1 chunk. The test should assert that `chunk_count` equals the number of
  stored embeddings, not a per-section count.

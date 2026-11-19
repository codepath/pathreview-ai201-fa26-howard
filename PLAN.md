## Solution plan

**Issue:** [Add end-to-end ingestion test with a sample resume fixture (#5)](https://github.com/codepath/pathreview-ai201-fa26-howard/issues/5)

### Understand
What is the root cause of this issue? What behavior is expected vs. actual?

This is a test gap, not a bug. `IngestionPipeline.ingest_resume` is the entry
point that connects the resume parser, the chunking strategy selector, and the
batch embedding processor. Each piece has unit tests, but nothing tests them
together.

- **Actual:** No test references `ingest_resume` or `IngestionPipeline`. The unit
  suite covers 0% of `ingestion/pipeline.py` (105 of 105 statements missed).
  `tests/integration/` holds only `__init__.py`. The integration CI job only
  passes because of a temporary step that treats "no tests collected" as
  success.
- **Expected:** An integration test runs a real sample resume through parsing,
  chunking, and embedding storage, then asserts on the returned `chunk_count`.
  If the pieces stop fitting together, for example the parser's metadata no
  longer works with the chunker or the processor stops storing chunks, the test
  fails.

During reproduction I found a trap. `_check_skip` runs
`db_session.query(...).filter_by(...).first()`. With a plain `Mock()` session,
that returns a truthy `Mock`, so the pipeline returns `skipped=True,
chunk_count=0` without parsing anything. A naive test would pass while
exercising none of the pipeline.

### Map
Which files, functions, or modules are involved?
List the specific files you expect to touch.

**Files to touch:**
- `tests/integration/test_ingestion_pipeline.py` (**new**): the end-to-end test.
- `.github/workflows/ci.yml` (**likely**): remove the "exit code 5 = success"
  step in the `test-integration` job. Its comment says to delete it once
  `tests/integration/` holds at least one test.

**Code under test (read, not changed):**
- `ingestion/pipeline.py`: `IngestionPipeline.ingest_resume`, `_hash_content`,
  `_check_skip`, `_record_ingested_source`, `IngestResult`.
- `ingestion/parsers/resume_parser.py`: `ResumeParser.parse` (str → markdown
  path, bytes → PDF path).
- `ingestion/chunking/strategy_selector.py`: resumes go to
  `SemanticChunker` (~500-token target, 50-token overlap).
- `ingestion/embeddings/batch_processor.py`: `process` calls
  `embedding_provider.embed(texts)` once per batch of up to 100 chunks, then
  `vector_db.add(ids=..., embeddings=..., metadatas=..., documents=...)` once
  per chunk.

**Fixtures and patterns used:**
- `tests/fixtures/sample_resumes/new_grad.md` and `mid_career.md`.
- `tests/unit/test_batch_processor.py`: the `Mock()` provider and vector DB
  fixture pattern.
- `pyproject.toml`: the `integration` marker is already registered. Run with
  `make test-integration` (`pytest tests/integration -v -m integration`).

### Plan
What are the steps to fix this issue?
Break it into 3–5 concrete sub-tasks.

1. **Build fixtures.** In the new test file, add pytest fixtures for:
   - a mock embedding provider whose `embed` returns one 1536-dim vector per
     input text (`side_effect`, not a fixed list, so it scales with chunk
     count);
   - a mock vector DB;
   - a mock DB session whose `query().filter_by().first()` returns `None`;
   - an `IngestionPipeline` built from those three.

   Mark the module with `pytestmark = pytest.mark.integration`.
2. **Write the happy-path test.** Parametrize over both sample resumes. Read
   each with `Path(...).read_text()` and call
   `ingest_resume("profile-1", content, filename)`. Assert:
   - `skipped is False` and `skip_reason is None`;
   - `chunk_count >= 1`;
   - `chunk_count == vector_db.add.call_count`, so every chunk was stored;
   - `source_id` starts with `resume_profile-1_`;
   - each stored chunk's metadata includes `source_type="resume"`,
     `profile_id`, and `filename`.
3. **Add the skip-path test.** Make `first()` return a truthy record and assert
   `skipped is True` and `chunk_count == 0`. Also assert that `embed` and
   `vector_db.add` were never called. This documents the dedupe behavior that
   makes the happy path's `None` stub necessary.
4. **Run and verify.** Run `make test-integration` and `make test-unit`, and
   check that coverage on `ingestion/pipeline.py`'s resume path goes up from 0%.
   Run `make lint` and `make typecheck`. Check the test fails when it should, for
   example by temporarily making `batch_processor.process` a no-op. Then remove
   the CI step if mentors agree, and open the PR with `Fixes #5`.

### Inputs & outputs
What does your fix take as input? What should it produce or change?

- **Input:** The sample resume markdown files, a fixed `profile_id`, and the
  three mocked dependencies (embedding provider, vector DB, DB session).
- **Output:** A new integration test file that passes locally and in the CI
  `test-integration` job. It raises `ingestion/pipeline.py` resume-path coverage
  from 0%. No production code changes. The pipeline's observable behavior is
  unchanged.

### Risks & unknowns
What could go wrong? What are you still unsure about?

- **Mock vs. real services.** The `integration` marker says "require Docker
  services," but `_check_skip` and `_record_ingested_source` are placeholders
  (`query("IngestedSource")`, a log-only record). A real Postgres session can't
  run them meaningfully, and real embeddings would need an API key in CI. So the
  plan mocks the DB session, the embedding provider, and the vector DB, and runs
  the parser, chunker, and batch processor for real. **Open question for
  mentors:** is that acceptable for an "integration" test, or should the vector
  DB be a real in-memory ChromaDB collection?
- **Chunk count is 1.** Both fixtures are under ~300 tokens, so the semantic
  chunker produces one chunk each. Asserting `chunk_count == 1` would break if
  the chunker settings change. Comparing against `vector_db.add.call_count` tests
  the pipeline's contract instead.
- **Removing the CI step.** If the step is removed and the test is later
  deleted or skipped, the job fails with exit code 5. That's the intended
  behavior per the workflow comment, but I'll confirm before changing CI in the
  same PR.
- **Python version.** CI runs Python 3.11 and I run 3.12 locally. The test uses
  nothing version-specific, but CI is the source of truth.
- **Out of scope (note in the PR):** `BatchEmbeddingProcessor.process` pairs
  chunks with embeddings using `zip`. If the provider returns fewer vectors than
  chunks, it stores fewer embeddings while `ingest_resume` still reports
  `len(chunks)`. My test's `chunk_count == vector_db.add.call_count` assertion
  would catch that mismatch, but fixing it is a separate issue.

### Edge cases
What inputs or states should your fix handle gracefully?

- **Already-ingested source:** `first()` returns a record. Expect
  `skipped=True`, `chunk_count=0`, and no embed or store calls (step 3).
- **DB lookup raises:** `_check_skip` catches the exception, logs a warning,
  and continues ingesting. Optionally test this with `query` set to raise:
  ingestion should still complete.
- **Embedding provider raises:** the error propagates from `ingest_resume`, which
  logs and re-raises. Optionally assert it with `pytest.raises`.
- **Same content twice:** `_hash_content` makes `source_id` deterministic, so
  the same resume gives the same `source_id`. Cheap to assert in step 2.
- **Bytes vs. str:** `bytes` goes to the PDF parser. The fixtures are markdown,
  so the test passes `str`. PDF ingestion is out of scope unless a PDF fixture
  is added.

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

**Cohort ledger:** [ ] Issue added to cohort ledger

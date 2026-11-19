"""Performance benchmark for the ingestion pipeline (issue #46).

A large portfolio (5 repos plus a resume) must ingest within 30 seconds. The
benchmark uses the deterministic ``MockEmbeddingProvider`` and an in-memory fake
vector store, so it measures PathReview's own parsing, chunking and batching
code, not network latency or a real vector database.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from ingestion.embeddings.provider import MockEmbeddingProvider
from ingestion.pipeline import IngestionPipeline, IngestResult

# Maximum acceptable mean time, in seconds, to ingest the large portfolio.
MAX_MEAN_SECONDS = 30

REPO_COUNT = 5
BENCHMARK_ROUNDS = 5

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
PROFILE_ID = "benchmark-profile"


class FakeVectorStore:
    """In-memory stand-in for a ChromaDB collection that counts stored vectors."""

    def __init__(self) -> None:
        """Create an empty store."""
        self.ids: list[str] = []

    def add(self, ids, embeddings, metadatas, documents) -> None:
        """Record the ids of the vectors that would have been stored."""
        self.ids.extend(ids)


def _make_readme(index: int) -> str:
    """Build a multi-section README large enough to produce several chunks."""
    sections = [f"# project-{index}\n\nA sample project used to benchmark ingestion.\n"]
    for section in range(8):
        paragraph = (
            f"This section describes component {section} of project {index}. "
            "It covers the design, the public interface, and how to run the tests. "
        ) * 12
        sections.append(f"## Component {section}\n\n{paragraph}\n")
    return "\n".join(sections)


@pytest.fixture(scope="module")
def large_portfolio() -> dict:
    """Return a resume plus 5 repos (metadata and README text) as ingestion input."""
    resume = (FIXTURES_DIR / "sample_resumes" / "mid_career.md").read_text()
    repos = []
    for i in range(REPO_COUNT):
        repos.append(
            {
                "name": f"project-{i}",
                "description": f"Sample project number {i}",
                "language": "Python" if i % 2 == 0 else "TypeScript",
                "stargazers_count": 10 + i,
                "forks_count": i,
                "open_issues_count": i,
                "pushed_at": "2026-07-28T16:04:11Z",
                "html_url": f"https://github.com/example/project-{i}",
                "topics": ["benchmark", "sample"],
                "readme_content": _make_readme(i),
            }
        )
    return {"resume": resume, "repos": repos}


def _build_pipeline() -> tuple[IngestionPipeline, FakeVectorStore]:
    """Create a pipeline wired to fakes, with a DB session that never dedupes."""
    vector_store = FakeVectorStore()
    db_session = Mock()
    # A bare Mock() returns a truthy object, which _check_skip would read as
    # "already ingested" and skip all the work. Force the "not found" path.
    db_session.query.return_value.filter_by.return_value.first.return_value = None
    pipeline = IngestionPipeline(vector_store, db_session, MockEmbeddingProvider())
    return pipeline, vector_store


def _ingest_portfolio(pipeline: IngestionPipeline, portfolio: dict) -> list[IngestResult]:
    """Ingest the resume and, for every repo, its metadata and README."""
    results = [pipeline.ingest_resume(PROFILE_ID, portfolio["resume"], "mid_career.md")]
    for repo in portfolio["repos"]:
        results.append(pipeline.ingest_repo_metadata(PROFILE_ID, repo))
        results.append(pipeline.ingest_readme(PROFILE_ID, repo["name"], repo["readme_content"]))
    return results


@pytest.mark.benchmark
def test_large_portfolio_ingestion_within_threshold(benchmark, large_portfolio):
    """Ingesting 5 repos plus a resume has a mean time under 30 seconds."""
    stores: list[FakeVectorStore] = []

    def setup():
        # Fresh pipeline per round so no state carries over between rounds.
        # Construction happens here, outside the timed call.
        pipeline, store = _build_pipeline()
        stores.append(store)
        return (pipeline, large_portfolio), {}

    results = benchmark.pedantic(
        _ingest_portfolio, setup=setup, rounds=BENCHMARK_ROUNDS, iterations=1
    )

    # Guard against a "fast" result produced by doing no work.
    expected_sources = 1 + 2 * REPO_COUNT
    assert len(results) == expected_sources
    assert not any(r.skipped for r in results), "sources were skipped, nothing was timed"
    assert all(r.chunk_count > 0 for r in results)
    assert len(stores[-1].ids) == sum(r.chunk_count for r in results)

    # benchmark.stats is None when run with --benchmark-disable.
    if benchmark.stats is not None:
        mean_seconds = benchmark.stats["mean"]
        assert (
            mean_seconds < MAX_MEAN_SECONDS
        ), f"mean ingestion time {mean_seconds:.2f}s exceeds {MAX_MEAN_SECONDS}s"

"""End-to-end tests for IngestionPipeline.ingest_resume.

The resume parser, chunking strategy selector, and batch embedding processor run
for real. Only the external boundaries are mocked: the embedding provider, the
vector DB, and the DB session used for deduplication.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from ingestion.pipeline import IngestionPipeline

SAMPLE_RESUMES_DIR = Path(__file__).parent.parent / "fixtures" / "sample_resumes"
EMBEDDING_DIM = 1536


@pytest.mark.integration
class TestIngestResume:
    """End-to-end test suite for IngestionPipeline.ingest_resume."""

    @pytest.fixture
    def mock_embedding_provider(self):
        """Create a mock embedding provider that returns one vector per input text."""
        provider = Mock()
        provider.embed = Mock(side_effect=lambda texts: [[0.1] * EMBEDDING_DIM for _ in texts])
        return provider

    @pytest.fixture
    def mock_vector_db(self):
        """Create a mock vector database."""
        return Mock()

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock DB session where no source has been ingested yet.

        A bare Mock() would return a truthy Mock from the dedupe lookup, making
        the pipeline skip ingestion entirely, so the lookup must return None.
        """
        session = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = None
        return session

    @pytest.fixture
    def pipeline(self, mock_vector_db, mock_db_session, mock_embedding_provider):
        """Create an IngestionPipeline wired to the mocked dependencies."""
        return IngestionPipeline(
            vector_db=mock_vector_db,
            db_session=mock_db_session,
            embedding_provider=mock_embedding_provider,
        )

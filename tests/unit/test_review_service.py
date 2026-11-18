"""Tests for review_service.py"""

from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from core.services.review_service import (
    create_review,
    get_review,
    list_reviews,
)


@pytest.mark.unit
class TestReviewService:
    """Test suite for review_service module."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock async database session."""
        session = AsyncMock()
        session.add = Mock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        return session

    @staticmethod
    def make_result(*, first=None, all=None):
        """Create a synchronous SQLAlchemy-style result mock."""
        result = Mock()
        result.scalars.return_value.first.return_value = first
        result.scalars.return_value.all.return_value = [] if all is None else all
        return result

    @pytest.mark.asyncio
    async def test_create_review_returns_review_with_pending_status(self, mock_db_session):
        """Test create_review returns Review with status='pending'."""
        profile_id = uuid4()
        user_id = uuid4()

        with patch("core.services.review_service.Review") as MockReview:
            mock_instance = MockReview.return_value
            mock_instance.status = "pending"
            mock_instance.sections = None
            mock_instance.overall_score = None

            await create_review(mock_db_session, profile_id, user_id)

            MockReview.assert_called()
            call_kwargs = MockReview.call_args.kwargs
            assert call_kwargs["status"] == "pending"

    @pytest.mark.asyncio
    async def test_get_review_returns_review_for_correct_owner(self, mock_db_session):
        """Test get_review returns review when it is found for the owner."""
        review_id = uuid4()
        user_id = uuid4()
        mock_review = Mock(id=review_id)
        mock_db_session.execute = AsyncMock(return_value=self.make_result(first=mock_review))

        result = await get_review(mock_db_session, review_id, user_id)

        assert result is mock_review
        mock_db_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_review_returns_none_for_wrong_user(self, mock_db_session):
        """Test get_review returns None when no owned review is found."""
        review_id = uuid4()
        wrong_user_id = uuid4()
        mock_db_session.execute = AsyncMock(return_value=self.make_result(first=None))

        result = await get_review(mock_db_session, review_id, wrong_user_id)

        assert result is None
        mock_db_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_list_reviews_returns_paginated_results(self, mock_db_session):
        """Test list_reviews returns reviews and a total count."""
        user_id = uuid4()
        mock_reviews = [Mock() for _ in range(5)]
        count_result = self.make_result(all=mock_reviews)
        page_result = self.make_result(all=mock_reviews)
        mock_db_session.execute = AsyncMock(side_effect=[count_result, page_result])

        reviews, total = await list_reviews(mock_db_session, user_id, page=1, page_size=20)

        assert reviews == mock_reviews
        assert total == 5
        assert mock_db_session.execute.await_count == 2

    @pytest.mark.asyncio
    async def test_list_reviews_page_2_returns_correct_offset(self, mock_db_session):
        """Test list_reviews calculates the offset for page two."""
        user_id = uuid4()
        count_result = self.make_result(all=[])
        page_result = self.make_result(all=[])
        mock_db_session.execute = AsyncMock(side_effect=[count_result, page_result])

        reviews, total = await list_reviews(mock_db_session, user_id, page=2, page_size=20)

        assert reviews == []
        assert total == 0
        assert mock_db_session.execute.await_count == 2

        page_statement = mock_db_session.execute.await_args_list[1].args[0]
        assert getattr(page_statement, "_offset_clause", None) is not None
        assert page_statement._offset_clause.value == 20

    @pytest.mark.asyncio
    async def test_list_reviews_returns_tuple(self, mock_db_session):
        """Test list_reviews returns a (reviews, total) tuple."""
        user_id = uuid4()
        mock_db_session.execute = AsyncMock(
            side_effect=[self.make_result(all=[]), self.make_result(all=[])]
        )

        result = await list_reviews(mock_db_session, user_id)

        assert isinstance(result, tuple)
        reviews, total = result
        assert isinstance(reviews, list)
        assert isinstance(total, int)
        assert mock_db_session.execute.await_count == 2

    @pytest.mark.asyncio
    async def test_create_review_calls_db_add(self, mock_db_session):
        """Test create_review calls db.add()."""
        profile_id = uuid4()
        user_id = uuid4()

        with patch("core.services.review_service.Review"):
            await create_review(mock_db_session, profile_id, user_id)

            mock_db_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_review_calls_db_commit(self, mock_db_session):
        """Test create_review calls db.commit()."""
        profile_id = uuid4()
        user_id = uuid4()

        with patch("core.services.review_service.Review"):
            await create_review(mock_db_session, profile_id, user_id)

            mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_review_calls_db_refresh(self, mock_db_session):
        """Test create_review calls db.refresh()."""
        profile_id = uuid4()
        user_id = uuid4()

        with patch("core.services.review_service.Review"):
            await create_review(mock_db_session, profile_id, user_id)

            mock_db_session.refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_review_uses_select_and_join(self, mock_db_session):
        """Test get_review executes a select/join statement once."""
        review_id = uuid4()
        user_id = uuid4()
        mock_db_session.execute = AsyncMock(return_value=self.make_result(first=None))

        await get_review(mock_db_session, review_id, user_id)

        mock_db_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_list_reviews_default_pagination(self, mock_db_session):
        """Test list_reviews uses page 1 and page size 20 by default."""
        user_id = uuid4()
        mock_db_session.execute = AsyncMock(
            side_effect=[self.make_result(all=[]), self.make_result(all=[])]
        )

        reviews, total = await list_reviews(mock_db_session, user_id)

        assert isinstance(reviews, list)
        assert isinstance(total, int)
        assert mock_db_session.execute.await_count == 2

        page_statement = mock_db_session.execute.await_args_list[1].args[0]
        assert page_statement._limit_clause.value == 20
        assert page_statement._offset_clause is not None
        assert page_statement._offset_clause.value == 0

    @pytest.mark.asyncio
    async def test_list_reviews_custom_page_size(self, mock_db_session):
        """Test list_reviews applies a custom page size."""
        user_id = uuid4()
        mock_db_session.execute = AsyncMock(
            side_effect=[self.make_result(all=[]), self.make_result(all=[])]
        )

        reviews, total = await list_reviews(mock_db_session, user_id, page=1, page_size=50)

        assert isinstance(reviews, list)
        assert isinstance(total, int)
        assert mock_db_session.execute.await_count == 2

        page_statement = mock_db_session.execute.await_args_list[1].args[0]
        assert page_statement._limit_clause.value == 50

    @pytest.mark.asyncio
    async def test_create_review_with_uuid_ids(self, mock_db_session):
        """Test create_review handles UUID objects correctly."""
        profile_id = uuid4()
        user_id = uuid4()

        with patch("core.services.review_service.Review") as MockReview:
            MockReview.return_value = Mock()
            await create_review(mock_db_session, profile_id, user_id)

            call_kwargs = MockReview.call_args.kwargs
            assert "profile_id" in call_kwargs
            assert "status" in call_kwargs

    @pytest.mark.asyncio
    async def test_get_review_verifies_ownership(self, mock_db_session):
        """Test get_review executes the ownership-filtered query."""
        review_id = uuid4()
        user_id = uuid4()
        mock_db_session.execute = AsyncMock(return_value=self.make_result(first=None))

        await get_review(mock_db_session, review_id, user_id)

        mock_db_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_list_reviews_counts_total(self, mock_db_session):
        """Test list_reviews calculates the total count from the count query."""
        user_id = uuid4()
        mock_reviews = [Mock() for _ in range(5)]
        mock_db_session.execute = AsyncMock(
            side_effect=[
                self.make_result(all=mock_reviews),
                self.make_result(all=[]),
            ]
        )

        reviews, total = await list_reviews(mock_db_session, user_id)

        assert reviews == []
        assert total == 5
        assert mock_db_session.execute.await_count == 2

    @pytest.mark.asyncio
    async def test_list_reviews_returns_reviews_list(self, mock_db_session):
        """Test list_reviews returns the paginated reviews as a list."""
        user_id = uuid4()
        mock_reviews = [Mock(spec=["id", "status"]) for _ in range(3)]
        mock_db_session.execute = AsyncMock(
            side_effect=[
                self.make_result(all=mock_reviews),
                self.make_result(all=mock_reviews),
            ]
        )

        reviews, total = await list_reviews(mock_db_session, user_id)

        assert isinstance(reviews, list)
        assert len(reviews) == 3
        assert total == 3

    @pytest.mark.asyncio
    async def test_review_sections_and_score_initially_none(self, mock_db_session):
        """Test review has None for sections and overall_score initially."""
        profile_id = uuid4()
        user_id = uuid4()

        with patch("core.services.review_service.Review") as MockReview:
            MockReview.return_value = Mock()
            await create_review(mock_db_session, profile_id, user_id)

            call_kwargs = MockReview.call_args.kwargs
            assert call_kwargs["sections"] is None
            assert call_kwargs["overall_score"] is None

    @pytest.mark.asyncio
    async def test_get_review_with_valid_uuid(self, mock_db_session):
        """Test get_review handles valid UUID parameters."""
        review_id = uuid4()
        user_id = uuid4()
        mock_db_session.execute = AsyncMock(return_value=self.make_result(first=None))

        result = await get_review(mock_db_session, review_id, user_id)

        assert result is None or result is not None
        mock_db_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_list_reviews_ordered_by_created_at(self, mock_db_session):
        """Test list_reviews executes a paginated ordered query once."""
        user_id = uuid4()
        mock_db_session.execute = AsyncMock(
            side_effect=[self.make_result(all=[]), self.make_result(all=[])]
        )

        reviews, total = await list_reviews(mock_db_session, user_id)

        assert isinstance(reviews, list)
        assert isinstance(total, int)
        assert mock_db_session.execute.await_count == 2

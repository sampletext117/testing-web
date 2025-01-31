import pytest
from unittest.mock import patch, AsyncMock

from election_app.data_access.vote_repository import PostgresVoteRepository

@pytest.mark.asyncio
class TestPostgresVoteRepository:

    @patch("election_app.data_access.vote_repository.get_connection", new_callable=AsyncMock)
    async def test_record_vote(self, mock_get_conn):
        # Arrange
        fake_conn = AsyncMock()
        # При INSERT ... RETURNING vote_id, вернётся {"vote_id": 9999}
        fake_conn.fetchrow.return_value = {"vote_id": 9999}
        mock_get_conn.return_value = fake_conn

        repo = PostgresVoteRepository()

        # Act
        vid = await repo.record_vote(10, 20, 30)

        # Assert
        assert vid == 9999
        fake_conn.fetchrow.assert_called_once()
        sql = fake_conn.fetchrow.call_args[0][0]
        assert "INSERT INTO elections.vote" in sql

    @patch("election_app.data_access.vote_repository.get_connection", new_callable=AsyncMock)
    async def test_has_already_voted_true(self, mock_get_conn):
        # Arrange
        fake_conn = AsyncMock()
        # Если fetchrow() не None, значит голос существует
        fake_conn.fetchrow.return_value = {"some_column": 1}
        mock_get_conn.return_value = fake_conn

        repo = PostgresVoteRepository()

        # Act
        already = await repo.has_already_voted(10, 20)

        # Assert
        assert already is True
        fake_conn.fetchrow.assert_called_once()
        sql = fake_conn.fetchrow.call_args[0][0]
        assert "SELECT 1" in sql

    @patch("election_app.data_access.vote_repository.get_connection", new_callable=AsyncMock)
    async def test_count_votes_by_election(self, mock_get_conn):
        # Arrange
        fake_conn = AsyncMock()
        # Предположим, метод fetch вернёт список строк — каждая строка словарь
        fake_conn.fetch.return_value = [
            {"candidate_id": 1, "cnt": 100},
            {"candidate_id": 2, "cnt": 250}
        ]
        mock_get_conn.return_value = fake_conn

        repo = PostgresVoteRepository()

        # Act
        summary = await repo.count_votes_by_election(5)

        # Assert
        assert summary == {1: 100, 2: 250}
        fake_conn.fetch.assert_called_once()
        sql = fake_conn.fetch.call_args[0][0]
        assert "SELECT candidate_id, COUNT(*)" in sql

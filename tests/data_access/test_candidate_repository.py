import pytest
from unittest.mock import patch, AsyncMock
from datetime import date

from election_app.data_access.election_repository import PostgresElectionRepository
from election_app.domain.entities.election import Election


@pytest.mark.asyncio
class TestPostgresElectionRepository:

    @patch("election_app.data_access.election_repository.get_connection", new_callable=AsyncMock)
    async def test_create_election(self, mock_get_conn):
        # Arrange
        fake_conn = AsyncMock()
        # При INSERT ... RETURNING election_id, вернём {"election_id": 12}
        fake_conn.fetchrow.return_value = {"election_id": 12}
        mock_get_conn.return_value = fake_conn

        repo = PostgresElectionRepository()

        # Act
        eid = await repo.create_election(
            election_name="Test Election",
            start_date=date(2025,1,1),
            end_date=date(2025,1,10),
            description="Some desc"
        )

        # Assert
        assert eid == 12
        fake_conn.fetchrow.assert_called_once()
        sql_executed = fake_conn.fetchrow.call_args[0][0]
        assert "INSERT INTO elections.election" in sql_executed

    @patch("election_app.data_access.election_repository.get_connection", new_callable=AsyncMock)
    async def test_find_election_by_id_found(self, mock_get_conn):
        # Arrange
        fake_conn = AsyncMock()
        # Вернём строку, аналогичную тому, что отдаёт реальный fetchrow,
        # но с ключами, соответствующими колонкам.
        fake_conn.fetchrow.return_value = {
            "election_id": 12,
            "election_name": "Test E",
            "start_date": date(2025,1,1),
            "end_date": date(2025,1,10),
            "description": "desc"
        }
        mock_get_conn.return_value = fake_conn

        repo = PostgresElectionRepository()

        # Act
        e = await repo.find_election_by_id(12)

        # Assert
        assert e is not None
        assert e.election_name == "Test E"
        fake_conn.fetchrow.assert_called_once()
        sql_executed = fake_conn.fetchrow.call_args[0][0]
        assert "SELECT election_id" in sql_executed

    @patch("election_app.data_access.election_repository.get_connection", new_callable=AsyncMock)
    async def test_update_election_status(self, mock_get_conn):
        # Arrange
        fake_conn = AsyncMock()
        mock_get_conn.return_value = fake_conn

        repo = PostgresElectionRepository()

        # Act
        await repo.update_election_status(12, "FINISHED")

        # Assert
        fake_conn.execute.assert_called_once()
        sql_executed = fake_conn.execute.call_args[0][0]
        assert "UPDATE elections.election" in sql_executed
        assert "WHERE election_id = $2" in sql_executed

import pytest
from unittest.mock import patch, AsyncMock
from datetime import date

from election_app.data_access.voter_repository import PostgresVoterRepository


@pytest.mark.asyncio
class TestPostgresVoterRepository:

    @patch("election_app.data_access.voter_repository.get_connection", new_callable=AsyncMock)
    async def test_create_voter(self, mock_get_conn):
        """
        Пример лондонского подхода:
        - Мокаем get_connection, чтобы не идти в реальную базу.
        - Проверяем, что вызывается нужный SQL-запрос,
          и что репозиторий возвращает корректный voter_id.
        """
        # Arrange
        fake_conn = AsyncMock()
        # Допустим, INSERT ... RETURNING voter_id вернёт {"voter_id": 123}
        fake_conn.fetchrow.return_value = {"voter_id": 123}
        mock_get_conn.return_value = fake_conn

        repo = PostgresVoterRepository()

        # Act
        voter_id = await repo.create_voter(
            full_name="Иванов Иван",
            birth_date=date(1990, 5, 20),
            passport_id=10
        )

        # Assert
        assert voter_id == 123
        fake_conn.fetchrow.assert_called_once()
        called_sql = fake_conn.fetchrow.call_args[0][0]
        assert "INSERT INTO elections.voter" in called_sql

    @patch("election_app.data_access.voter_repository.get_connection", new_callable=AsyncMock)
    async def test_find_voter_by_id_found(self, mock_get_conn):
        # Arrange
        fake_conn = AsyncMock()
        # Симулируем полученную строку из таблицы
        fake_conn.fetchrow.return_value = {
            "voter_id": 7,
            "full_name": "Петров",
            "birth_date": date(1980, 1, 1),
            "passport_id": 2,
            "created_at": None
        }
        mock_get_conn.return_value = fake_conn

        repo = PostgresVoterRepository()

        # Act
        voter = await repo.find_voter_by_id(7)

        # Assert
        assert voter is not None
        assert voter.voter_id == 7
        assert voter.full_name == "Петров"
        fake_conn.fetchrow.assert_called_once()

    @patch("election_app.data_access.voter_repository.get_connection", new_callable=AsyncMock)
    async def test_find_voter_by_id_not_found(self, mock_get_conn):
        # Arrange
        fake_conn = AsyncMock()
        # Нет записей (None)
        fake_conn.fetchrow.return_value = None
        mock_get_conn.return_value = fake_conn

        repo = PostgresVoterRepository()

        # Act
        voter = await repo.find_voter_by_id(999)

        # Assert


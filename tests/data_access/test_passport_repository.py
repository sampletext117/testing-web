import pytest
from unittest.mock import patch, AsyncMock
from datetime import date

from election_app.data_access.passport_repository import PostgresPassportRepository

@pytest.mark.asyncio
class TestPostgresPassportRepository:

    @patch("election_app.data_access.passport_repository.get_connection", new_callable=AsyncMock)
    async def test_create_passport(self, mock_get_conn):
        # Arrange
        fake_conn = AsyncMock()
        # Настраиваем return_value при INSERT ... RETURNING passport_id
        fake_conn.fetchrow.return_value = {"passport_id": 777}
        mock_get_conn.return_value = fake_conn

        repo = PostgresPassportRepository()

        # Act
        pid = await repo.create_passport(
            passport_number="1234 567890",
            issued_by="ОВД г.Москвы",
            issue_date=date(2010, 2, 15),
            country="Россия"
        )

        # Assert
        assert pid == 777
        fake_conn.fetchrow.assert_called_once()
        sql_executed = fake_conn.fetchrow.call_args[0][0]
        assert "INSERT INTO elections.passport" in sql_executed

    @patch("election_app.data_access.passport_repository.get_connection", new_callable=AsyncMock)
    async def test_find_by_number_found(self, mock_get_conn):
        # Arrange
        fake_conn = AsyncMock()
        # Симулируем строку с колонками (passport_id, passport_number, issued_by, issue_date, country)
        fake_conn.fetchrow.return_value = {
            "passport_id": 10,
            "passport_number": "ABCDE",
            "issued_by": "UFMS",
            "issue_date": date(2010,1,1),
            "country": "Россия"
        }
        mock_get_conn.return_value = fake_conn

        repo = PostgresPassportRepository()

        # Act
        p = await repo.find_by_number("ABCDE")

        # Assert
        assert p is not None
        assert p.passport_id == 10
        assert p.passport_number == "ABCDE"
        fake_conn.fetchrow.assert_called_once()
        sql_executed = fake_conn.fetchrow.call_args[0][0]
        assert "SELECT passport_id" in sql_executed

    @patch("election_app.data_access.passport_repository.get_connection", new_callable=AsyncMock)
    async def test_find_by_number_not_found(self, mock_get_conn):
        # Arrange
        fake_conn = AsyncMock()
        # Если нет такой записи - вернётся None
        fake_conn.fetchrow.return_value = None
        mock_get_conn.return_value = fake_conn

        repo = PostgresPassportRepository()

        # Act
        p = await repo.find_by_number("NO_EXIST")

        # Assert
        assert p is None
        fake_conn.fetchrow.assert_called_once()
        sql_executed = fake_conn.fetchrow.call_args[0][0]
        assert "WHERE passport_number = $1" in sql_executed

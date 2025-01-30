import pytest
from unittest.mock import patch, MagicMock
from datetime import date

from election_app.data_access.passport_repository import PostgresPassportRepository

class TestPostgresPassportRepository:
    @patch("election_app.data_access.passport_repository.get_connection")
    def test_create_passport(self, mock_get_conn):
        # Arrange
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = [777]  # допустим, passport_id=777
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresPassportRepository()

        # Act
        pid = repo.create_passport(
            passport_number="1234 567890",
            issued_by="ОВД г.Москвы",
            issue_date=date(2010, 2, 15),
            country="Россия"
        )

        # Assert
        assert pid == 777
        fake_cursor.execute.assert_called_once()
        assert "INSERT INTO elections.passport" in fake_cursor.execute.call_args[0][0]

    @patch("election_app.data_access.passport_repository.get_connection")
    def test_find_by_number_found(self, mock_get_conn):
        # Arrange
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        # Возвращаем строку (passport_id, passport_number, issued_by, issue_date, country)
        fake_cursor.fetchone.return_value = (10, "ABCDE", "UFMS", date(2010,1,1), "Россия")
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresPassportRepository()

        # Act
        p = repo.find_by_number("ABCDE")

        # Assert
        assert p is not None
        assert p.passport_id == 10
        assert p.passport_number == "ABCDE"

    @patch("election_app.data_access.passport_repository.get_connection")
    def test_find_by_number_not_found(self, mock_get_conn):
        # Arrange
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = None
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresPassportRepository()

        # Act
        p = repo.find_by_number("NO_EXIST")

        # Assert
        assert p is None

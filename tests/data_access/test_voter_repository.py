import pytest
from unittest.mock import patch, MagicMock
from datetime import date

from election_app.data_access.voter_repository import PostgresVoterRepository


class TestPostgresVoterRepository:
    @patch("election_app.data_access.voter_repository.get_connection")
    def test_create_voter(self, mock_get_conn):
        """
        Пример лондонского подхода:
        - Мокаем get_connection, чтобы не идти в реальную базу.
        - Проверяем, что вызывается нужный SQL-запрос,
          и что репозиторий возвращает корректный voter_id.
        """
        # Arrange
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = [123]  # допустим, новый ID = 123
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor

        mock_get_conn.return_value = fake_conn

        repo = PostgresVoterRepository()

        # Act
        voter_id = repo.create_voter(
            full_name="Иванов Иван",
            birth_date=date(1990, 5, 20),
            passport_id=10
        )

        # Assert
        assert voter_id == 123
        fake_cursor.execute.assert_called_once()
        # Можно детальнее проверить сам SQL, если хотим:
        called_sql = fake_cursor.execute.call_args[0][0]
        assert "INSERT INTO elections.voter" in called_sql

    @patch("election_app.data_access.voter_repository.get_connection")
    def test_find_voter_by_id_found(self, mock_get_conn):
        # Arrange
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        # Возвращаем строку с данными:
        fake_cursor.fetchone.return_value = (7, "Петров", date(1980,1,1), 2, None)
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresVoterRepository()

        # Act
        voter = repo.find_voter_by_id(7)

        # Assert
        assert voter is not None
        assert voter.voter_id == 7
        assert voter.full_name == "Петров"
        fake_cursor.execute.assert_called_once()

    @patch("election_app.data_access.voter_repository.get_connection")
    def test_find_voter_by_id_not_found(self, mock_get_conn):
        # Arrange
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        # Нет записей (None)
        fake_cursor.fetchone.return_value = None
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresVoterRepository()

        # Act
        voter = repo.find_voter_by_id(999)

        # Assert
        assert voter is None
        fake_cursor.execute.assert_called_once()

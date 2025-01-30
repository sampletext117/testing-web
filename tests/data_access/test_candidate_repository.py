import pytest
from unittest.mock import patch, MagicMock
from datetime import date

from election_app.data_access.candidate_repository import PostgresCandidateRepository

class TestPostgresCandidateRepository:
    @patch("election_app.data_access.candidate_repository.get_connection")
    def test_create_candidate(self, mock_get_conn):
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = [55]  # candidate_id=55
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresCandidateRepository()

        cid = repo.create_candidate(
            full_name="Иванов Иван",
            birth_date=date(1980,1,1),
            passport_id=100
        )
        assert cid == 55
        fake_cursor.execute.assert_called_once()
        assert "INSERT INTO elections.candidate" in fake_cursor.execute.call_args[0][0]

    @patch("election_app.data_access.candidate_repository.get_connection")
    def test_update_candidate_program_and_account(self, mock_get_conn):
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresCandidateRepository()
        repo.update_candidate_program_and_account(55, 200, 300)

        fake_cursor.execute.assert_called_once()
        sql_executed = fake_cursor.execute.call_args[0][0]
        assert "UPDATE elections.candidate" in sql_executed
        assert "campaign_program_id" in sql_executed

    @patch("election_app.data_access.candidate_repository.get_connection")
    def test_find_candidate_by_id_not_found(self, mock_get_conn):
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = None
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresCandidateRepository()
        candidate = repo.find_candidate_by_id(999)
        assert candidate is None

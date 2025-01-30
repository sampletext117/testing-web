import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from election_app.data_access.candidate_account_repository import PostgresCandidateAccountRepository


class TestPostgresCandidateAccountRepository:
    @patch("election_app.data_access.candidate_account_repository.get_connection")
    def test_create_account(self, mock_get_conn):
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = [300]
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresCandidateAccountRepository()
        acct_id = repo.create_account(candidate_id=55, balance=1000.0)
        assert acct_id == 300
        fake_cursor.execute.assert_called_once()
        assert "INSERT INTO elections.candidate_account" in fake_cursor.execute.call_args[0][0]

    @patch("election_app.data_access.candidate_account_repository.get_connection")
    def test_find_by_candidate_id_found(self, mock_get_conn):
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = (300, 55, 1234.56, datetime(2023,1,1,10,0,0))
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresCandidateAccountRepository()
        acct = repo.find_by_candidate_id(55)
        assert acct is not None
        assert acct.account_id == 300
        assert acct.balance == 1234.56

    @patch("election_app.data_access.candidate_account_repository.get_connection")
    def test_update_balance(self, mock_get_conn):
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresCandidateAccountRepository()
        repo.update_balance(account_id=300, new_balance=500.0)

        fake_cursor.execute.assert_called_once()
        sql_executed = fake_cursor.execute.call_args[0][0]
        assert "UPDATE elections.candidate_account" in sql_executed
        assert "SET balance = %s" in sql_executed

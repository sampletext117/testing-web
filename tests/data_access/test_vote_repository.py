# tests/data_access/test_vote_repository.py

import pytest
from unittest.mock import patch, MagicMock

from election_app.data_access.vote_repository import PostgresVoteRepository

class TestPostgresVoteRepository:
    @patch("election_app.data_access.vote_repository.get_connection")
    def test_record_vote(self, mock_get_conn):
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = [9999]  # vote_id
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresVoteRepository()
        vid = repo.record_vote(10, 20, 30)
        assert vid == 9999
        fake_cursor.execute.assert_called_once()
        sql = fake_cursor.execute.call_args[0][0]
        assert "INSERT INTO elections.vote" in sql

    @patch("election_app.data_access.vote_repository.get_connection")
    def test_has_already_voted_true(self, mock_get_conn):
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        # Если fetchone() возвращает что-то не None, значит голос существует
        fake_cursor.fetchone.return_value = (1,)
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresVoteRepository()
        already = repo.has_already_voted(10, 20)
        assert already is True

    @patch("election_app.data_access.vote_repository.get_connection")
    def test_count_votes_by_election(self, mock_get_conn):
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        # Допустим, вернулись две строки: (cand_id=1, count=100), (cand_id=2, count=250)
        fake_cursor.fetchall.return_value = [(1,100), (2,250)]
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresVoteRepository()
        summary = repo.count_votes_by_election(5)
        assert summary == {1:100, 2:250}
        fake_cursor.execute.assert_called_once()
        sql = fake_cursor.execute.call_args[0][0]
        assert "SELECT candidate_id, COUNT(*)" in sql

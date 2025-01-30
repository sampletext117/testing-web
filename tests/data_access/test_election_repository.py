import pytest
from unittest.mock import patch, MagicMock
from datetime import date

from election_app.data_access.election_repository import PostgresElectionRepository

class TestPostgresElectionRepository:
    @patch("election_app.data_access.election_repository.get_connection")
    def test_create_election(self, mock_get_conn):
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = [12]  # election_id=12
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresElectionRepository()

        eid = repo.create_election(
            election_name="Test Election",
            start_date=date(2025,1,1),
            end_date=date(2025,1,10),
            description="Some desc"
        )
        assert eid == 12
        fake_cursor.execute.assert_called_once()
        assert "INSERT INTO elections.election" in fake_cursor.execute.call_args[0][0]

    @patch("election_app.data_access.election_repository.get_connection")
    def test_find_election_by_id_found(self, mock_get_conn):
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = (12, "Test E", date(2025,1,1), date(2025,1,10), "desc")
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresElectionRepository()
        e = repo.find_election_by_id(12)
        assert e is not None
        assert e.election_name == "Test E"

    @patch("election_app.data_access.election_repository.get_connection")
    def test_update_election_status(self, mock_get_conn):
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresElectionRepository()
        repo.update_election_status(12, "FINISHED")

        fake_cursor.execute.assert_called_once()
        sql = fake_cursor.execute.call_args[0][0]
        assert "UPDATE elections.election" in sql

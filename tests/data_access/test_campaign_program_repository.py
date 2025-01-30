import pytest
from unittest.mock import patch, MagicMock

from election_app.data_access.campaign_program_repository import PostgresCampaignProgramRepository

class TestPostgresCampaignProgramRepository:
    @patch("election_app.data_access.campaign_program_repository.get_connection")
    def test_create_program(self, mock_get_conn):
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = [999]  # campaign_program_id
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresCampaignProgramRepository()
        pid = repo.create_program(candidate_id=55, description="Описание программы")

        assert pid == 999
        fake_cursor.execute.assert_called_once()
        assert "INSERT INTO elections.campaign_program" in fake_cursor.execute.call_args[0][0]

    @patch("election_app.data_access.campaign_program_repository.get_connection")
    def test_find_by_candidate_id_found(self, mock_get_conn):
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = (101, 55, "Some description")
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresCampaignProgramRepository()
        pr = repo.find_by_candidate_id(55)
        assert pr is not None
        assert pr.campaign_program_id == 101
        assert pr.candidate_id == 55

    @patch("election_app.data_access.campaign_program_repository.get_connection")
    def test_find_by_candidate_id_not_found(self, mock_get_conn):
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = None
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        repo = PostgresCampaignProgramRepository()
        pr = repo.find_by_candidate_id(999)
        assert pr is None

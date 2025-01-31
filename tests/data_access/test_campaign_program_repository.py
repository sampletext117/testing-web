import pytest
from unittest.mock import patch, AsyncMock

from election_app.data_access.campaign_program_repository import PostgresCampaignProgramRepository
from election_app.domain.entities.campaign_program import CampaignProgram

@pytest.mark.asyncio
class TestPostgresCampaignProgramRepository:

    @patch("election_app.data_access.campaign_program_repository.get_connection", new_callable=AsyncMock)
    async def test_create_program(self, mock_get_conn):
        # Arrange
        fake_conn = AsyncMock()
        # Допустим, при вызове fetchrow() вернётся dict с ключом "campaign_program_id"
        fake_conn.fetchrow.return_value = {"campaign_program_id": 999}
        mock_get_conn.return_value = fake_conn

        repo = PostgresCampaignProgramRepository()

        # Act
        pid = await repo.create_program(candidate_id=55, description="Описание программы")

        # Assert
        assert pid == 999
        # Проверяем, что fetchrow действительно вызывался
        fake_conn.fetchrow.assert_called_once()
        sql_executed = fake_conn.fetchrow.call_args[0][0]
        assert "INSERT INTO elections.campaign_program" in sql_executed

    @patch("election_app.data_access.campaign_program_repository.get_connection", new_callable=AsyncMock)
    async def test_find_by_candidate_id_found(self, mock_get_conn):
        # Arrange
        fake_conn = AsyncMock()
        # Возвращаем структуру с полями, соответствующими колонкам
        fake_conn.fetchrow.return_value = {
            "campaign_program_id": 101,
            "candidate_id": 55,
            "description": "Some description"
        }
        mock_get_conn.return_value = fake_conn

        repo = PostgresCampaignProgramRepository()

        # Act
        pr = await repo.find_by_candidate_id(55)

        # Assert
        assert pr is not None
        assert pr.campaign_program_id == 101
        assert pr.candidate_id == 55
        assert pr.description == "Some description"
        fake_conn.fetchrow.assert_called_once()
        sql_executed = fake_conn.fetchrow.call_args[0][0]
        assert "SELECT campaign_program_id" in sql_executed

    @patch("election_app.data_access.campaign_program_repository.get_connection", new_callable=AsyncMock)
    async def test_find_by_candidate_id_not_found(self, mock_get_conn):
        # Arrange
        fake_conn = AsyncMock()
        # Если в БД нет записи, fetchrow вернёт None
        fake_conn.fetchrow.return_value = None
        mock_get_conn.return_value = fake_conn

        repo = PostgresCampaignProgramRepository()

        # Act
        pr = await repo.find_by_candidate_id(999)

        # Assert
        assert pr is None
        fake_conn.fetchrow.assert_called_once()
        sql_executed = fake_conn.fetchrow.call_args[0][0]
        assert "WHERE candidate_id = $1" in sql_executed

import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime

from election_app.data_access.candidate_account_repository import PostgresCandidateAccountRepository


@pytest.mark.asyncio
class TestPostgresCandidateAccountRepository:

    @patch("election_app.data_access.candidate_account_repository.get_connection", new_callable=AsyncMock)
    async def test_create_account(self, mock_get_conn):
        # Arrange
        fake_conn = AsyncMock()
        # При вызове fetchrow(...) вернём dict с account_id=300
        fake_conn.fetchrow.return_value = {"account_id": 300}
        mock_get_conn.return_value = fake_conn

        repo = PostgresCandidateAccountRepository()

        # Act
        acct_id = await repo.create_account(candidate_id=55, balance=1000.0)

        # Assert
        assert acct_id == 300
        fake_conn.fetchrow.assert_called_once()
        sql_executed = fake_conn.fetchrow.call_args[0][0]
        assert "INSERT INTO elections.candidate_account" in sql_executed

    @patch("election_app.data_access.candidate_account_repository.get_connection", new_callable=AsyncMock)
    async def test_find_by_candidate_id_found(self, mock_get_conn):
        # Arrange
        fake_conn = AsyncMock()
        # Возвращаем словарь, соответствующий полям таблицы
        fake_conn.fetchrow.return_value = {
            "account_id": 300,
            "candidate_id": 55,
            "balance": 1234.56,
            "last_transaction_date": datetime(2023,1,1,10,0,0)
        }
        mock_get_conn.return_value = fake_conn

        repo = PostgresCandidateAccountRepository()

        # Act
        acct = await repo.find_by_candidate_id(55)

        # Assert
        assert acct is not None
        assert acct.account_id == 300
        assert acct.balance == 1234.56
        fake_conn.fetchrow.assert_called_once()
        sql_executed = fake_conn.fetchrow.call_args[0][0]
        assert "FROM elections.candidate_account" in sql_executed

    @patch("election_app.data_access.candidate_account_repository.get_connection", new_callable=AsyncMock)
    async def test_update_balance(self, mock_get_conn):
        # Arrange
        fake_conn = AsyncMock()
        mock_get_conn.return_value = fake_conn

        repo = PostgresCandidateAccountRepository()

        # Act
        await repo.update_balance(account_id=300, new_balance=500.0)

        # Assert
        fake_conn.execute.assert_called_once()
        sql_executed = fake_conn.execute.call_args[0][0]
        assert "UPDATE elections.candidate_account" in sql_executed
        assert "SET balance = $1" in sql_executed

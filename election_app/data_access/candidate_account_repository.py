from typing import Optional
from datetime import datetime
import asyncpg

from election_app.domain.repositories.icandidate_account_repository import ICandidateAccountRepository
from election_app.domain.entities.candidate_account import CandidateAccount
from election_app.data_access.database import get_connection


class PostgresCandidateAccountRepository(ICandidateAccountRepository):
    async def create_account(self, candidate_id: int, balance: float) -> int:
        """
        Создаёт запись о счёте, возвращает account_id.
        """
        conn = await get_connection()
        try:
            now = datetime.now()
            row = await conn.fetchrow(
                """
                INSERT INTO elections.candidate_account (candidate_id, balance, last_transaction_date)
                VALUES ($1, $2, $3)
                RETURNING account_id
                """,
                candidate_id, balance, now
            )
            return row["account_id"] if row else 0
        finally:
            await conn.close()

    async def find_by_candidate_id(self, candidate_id: int) -> Optional[CandidateAccount]:
        """
        Ищет счёт по candidate_id, возвращает CandidateAccount или None.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                SELECT account_id, candidate_id, balance, last_transaction_date
                FROM elections.candidate_account
                WHERE candidate_id = $1
                """,
                candidate_id
            )
            if row:
                return CandidateAccount(
                    account_id=row["account_id"],
                    candidate_id=row["candidate_id"],
                    balance=float(row["balance"]),
                    last_transaction_date=row["last_transaction_date"]
                )
            return None
        finally:
            await conn.close()

    async def update_balance(self, account_id: int, new_balance: float) -> None:
        """
        Обновляет баланс счёта.
        """
        conn = await get_connection()
        try:
            now = datetime.now()
            await conn.execute(
                """
                UPDATE elections.candidate_account
                SET balance = $1,
                    last_transaction_date = $2
                WHERE account_id = $3
                """,
                new_balance, now, account_id
            )
        finally:
            await conn.close()

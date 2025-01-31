from typing import Optional
from datetime import date, datetime
import asyncpg

from election_app.domain.repositories.icandidate_repository import ICandidateRepository
from election_app.domain.entities.candidate import Candidate
from election_app.data_access.database import get_connection


class PostgresCandidateRepository(ICandidateRepository):
    async def create_candidate(
        self,
        full_name: str,
        birth_date: date,
        passport_id: int
    ) -> int:
        """
        Создаёт запись о кандидате, возвращает candidate_id.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                INSERT INTO elections.candidate (full_name, birth_date, passport_id)
                VALUES ($1, $2, $3)
                RETURNING candidate_id
                """,
                full_name, birth_date, passport_id
            )
            return row["candidate_id"] if row else 0
        finally:
            await conn.close()

    async def update_candidate_program_and_account(
        self,
        candidate_id: int,
        campaign_program_id: int,
        account_id: int
    ) -> None:
        """
        Обновляет campaign_program_id и account_id у кандидата.
        """
        conn = await get_connection()
        try:
            await conn.execute(
                """
                UPDATE elections.candidate
                SET campaign_program_id = $1,
                    account_id = $2
                WHERE candidate_id = $3
                """,
                campaign_program_id, account_id, candidate_id
            )
        finally:
            await conn.close()

    async def find_candidate_by_id(self, candidate_id: int) -> Optional[Candidate]:
        """
        Находит кандидата по ID, или None, если не найден.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                SELECT candidate_id, full_name, birth_date, passport_id,
                       campaign_program_id, account_id, created_at
                FROM elections.candidate
                WHERE candidate_id = $1
                """,
                candidate_id
            )
            if row:
                return Candidate(
                    candidate_id=row["candidate_id"],
                    full_name=row["full_name"],
                    birth_date=row["birth_date"],
                    passport_id=row["passport_id"],
                    campaign_program_id=row["campaign_program_id"],
                    account_id=row["account_id"],
                    created_at=row["created_at"]
                )
            return None
        finally:
            await conn.close()

    async def find_by_passport_id(self, passport_id: int) -> Optional[Candidate]:
        """
        Находит кандидата по passport_id, или None.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                SELECT candidate_id, full_name, birth_date, passport_id,
                       campaign_program_id, account_id, created_at
                FROM elections.candidate
                WHERE passport_id = $1
                """,
                passport_id
            )
            if row:
                return Candidate(
                    candidate_id=row["candidate_id"],
                    full_name=row["full_name"],
                    birth_date=row["birth_date"],
                    passport_id=row["passport_id"],
                    campaign_program_id=row["campaign_program_id"],
                    account_id=row["account_id"],
                    created_at=row["created_at"]
                )
            return None
        finally:
            await conn.close()

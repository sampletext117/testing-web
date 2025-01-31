from typing import Optional
from datetime import date
import asyncpg

from election_app.domain.repositories.ivoter_repository import IVoterRepository
from election_app.domain.entities.voter import Voter
from election_app.data_access.database import get_connection


class PostgresVoterRepository(IVoterRepository):
    async def create_voter(
        self,
        full_name: str,
        birth_date: date,
        passport_id: int
    ) -> int:
        """
        Создаёт нового избирателя, возвращает voter_id.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                INSERT INTO elections.voter (full_name, birth_date, passport_id)
                VALUES ($1, $2, $3)
                RETURNING voter_id
                """,
                full_name, birth_date, passport_id
            )
            if row:
                return row["voter_id"]
            return 0
        finally:
            await conn.close()

    async def find_voter_by_id(self, voter_id: int) -> Optional[Voter]:
        """
        Возвращает избирателя по его ID или None, если не найден.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                SELECT voter_id, full_name, birth_date, passport_id, created_at
                FROM elections.voter
                WHERE voter_id = $1
                """,
                voter_id
            )
            if row:
                return Voter(
                    voter_id=row["voter_id"],
                    full_name=row["full_name"],
                    birth_date=row["birth_date"],
                    passport_id=row["passport_id"],
                    created_at=row["created_at"]
                )
            return None
        finally:
            await conn.close()

    async def find_by_passport_id(self, passport_id: int) -> Optional[Voter]:
        """
        Возвращает избирателя по passport_id, или None, если не найден.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                SELECT voter_id, full_name, birth_date, passport_id, created_at
                FROM elections.voter
                WHERE passport_id = $1
                """,
                passport_id
            )
            if row:
                return Voter(
                    voter_id=row["voter_id"],
                    full_name=row["full_name"],
                    birth_date=row["birth_date"],
                    passport_id=row["passport_id"],
                    created_at=row["created_at"]
                )
            return None
        finally:
            await conn.close()

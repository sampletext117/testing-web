from typing import Optional, List
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

    async def list_all_voters(self) -> List[Voter]:
        """
        Возвращает список всех избирателей.
        """
        conn = await get_connection()
        try:
            rows = await conn.fetch(
                """
                SELECT voter_id, full_name, birth_date, passport_id, created_at
                FROM elections.voter
                ORDER BY voter_id
                """
            )
            result = []
            for r in rows:
                result.append(
                    Voter(
                        voter_id=r["voter_id"],
                        full_name=r["full_name"],
                        birth_date=r["birth_date"],
                        passport_id=r["passport_id"],
                        created_at=r["created_at"]
                    )
                )
            return result
        finally:
            await conn.close()

    async def delete_voter(self, voter_id: int) -> bool:
        """
        Удаляет избирателя по ID, возвращает True/False (успешно/нет).
        """
        conn = await get_connection()
        try:
            result = await conn.execute(
                """
                DELETE FROM elections.voter
                WHERE voter_id = $1
                """,
                voter_id
            )
            row_count = int(result.split(" ")[1]) if result else 0
            return (row_count > 0)
        finally:
            await conn.close()

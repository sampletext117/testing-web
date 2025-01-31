from typing import Optional
from datetime import date
import asyncpg

from election_app.domain.repositories.ipassport_repository import IPassportRepository
from election_app.domain.entities.passport import Passport
from election_app.data_access.database import get_connection


class PostgresPassportRepository(IPassportRepository):

    async def create_passport(
        self,
        passport_number: str,
        issued_by: Optional[str],
        issue_date: Optional[date],
        country: str
    ) -> int:
        """
        Создаёт запись в таблице passport и возвращает passport_id.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                INSERT INTO elections.passport (passport_number, issued_by, issue_date, country)
                VALUES ($1, $2, $3, $4)
                RETURNING passport_id
                """,
                passport_number, issued_by, issue_date, country
            )
            if row:
                return row["passport_id"]
            return 0
        finally:
            await conn.close()

    async def find_by_number(self, passport_number: str) -> Optional[Passport]:
        """
        Ищет паспорт по номеру.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                SELECT passport_id, passport_number, issued_by, issue_date, country
                FROM elections.passport
                WHERE passport_number = $1
                """,
                passport_number
            )
            if row:
                return Passport(
                    passport_id=row["passport_id"],
                    passport_number=row["passport_number"],
                    issued_by=row["issued_by"],
                    issue_date=row["issue_date"],
                    country=row["country"]
                )
            return None
        finally:
            await conn.close()

    async def find_by_id(self, passport_id: int) -> Optional[Passport]:
        """
        Ищет паспорт по ID.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                SELECT passport_id, passport_number, issued_by, issue_date, country
                FROM elections.passport
                WHERE passport_id = $1
                """,
                passport_id
            )
            if row:
                return Passport(
                    passport_id=row["passport_id"],
                    passport_number=row["passport_number"],
                    issued_by=row["issued_by"],
                    issue_date=row["issue_date"],
                    country=row["country"]
                )
            return None
        finally:
            await conn.close()

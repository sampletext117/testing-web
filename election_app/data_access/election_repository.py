"""
election_repository.py

Асинхронная реализация IElectionRepository с использованием asyncpg.
"""

from typing import Optional, List
from datetime import date
import asyncpg

from election_app.domain.repositories.ielection_repository import IElectionRepository
from election_app.domain.entities.election import Election
from election_app.data_access.database import get_connection


class PostgresElectionRepository(IElectionRepository):

    async def create_election(
        self,
        election_name: str,
        start_date: date,
        end_date: date,
        description: str
    ) -> int:
        """
        Создаёт запись о выборах, возвращает election_id.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                INSERT INTO elections.election (election_name, start_date, end_date, description)
                VALUES ($1, $2, $3, $4)
                RETURNING election_id
                """,
                election_name, start_date, end_date, description
            )
            return row["election_id"] if row else 0
        finally:
            await conn.close()

    async def find_election_by_id(self, election_id: int) -> Optional[Election]:
        """
        Находит выборы по ID.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                SELECT election_id, election_name, start_date, end_date, description
                FROM elections.election
                WHERE election_id = $1
                """,
                election_id
            )
            if row:
                return Election(
                    election_id=row["election_id"],
                    election_name=row["election_name"],
                    start_date=row["start_date"],
                    end_date=row["end_date"],
                    description=row["description"]
                )
            return None
        finally:
            await conn.close()

    async def update_election_status(self, election_id: int, new_status: str) -> None:
        """
        Если в таблице elections.election есть поле status (или хотим обновить description),
        делаем это асинхронно. В примере ниже используем CONCAT с description,
        как было в исходном коде.
        """
        conn = await get_connection()
        try:
            await conn.execute(
                """
                UPDATE elections.election
                SET description = CONCAT(description, ' [STATUS:', $1, ']')
                WHERE election_id = $2
                """,
                new_status, election_id
            )
        finally:
            await conn.close()

    async def patch_election(
        self,
        election_id: int,
        new_name: str,
        new_start: date,
        new_end: date,
        new_desc: str
    ) -> bool:
        """
        Частично обновляет поля в таблице election:
         - election_name
         - start_date
         - end_date
         - description
        Возвращает True при успехе, False если не было изменений или выборы не найдены.
        """
        conn = await get_connection()
        try:
            result = await conn.execute(
                """
                UPDATE elections.election
                SET election_name = $2,
                    start_date = $3,
                    end_date = $4,
                    description = $5
                WHERE election_id = $1
                """,
                election_id, new_name, new_start, new_end, new_desc
            )
            row_count = int(result.split(" ")[1]) if result else 0
            return (row_count > 0)
        finally:
            await conn.close()


    async def delete_election(self, election_id: int) -> bool:
        """
        Удаляет запись о выборах, возвращает True/False (успешно/нет).
        """
        conn = await get_connection()
        try:
            result = await conn.execute(
                """
                DELETE FROM elections.election
                WHERE election_id = $1
                """,
                election_id
            )
            row_count = int(result.split(" ")[1]) if result else 0
            return (row_count > 0)
        finally:
            await conn.close()


    async def list_all_elections(self) -> List[Election]:
        """
        Возвращает список всех записей в таблице election
        (Ordered by election_id, например).
        """
        conn = await get_connection()
        try:
            rows = await conn.fetch(
                """
                SELECT election_id, election_name, start_date, end_date, description
                FROM elections.election
                ORDER BY election_id
                """
            )
            result = []
            for r in rows:
                result.append(Election(
                    election_id=r["election_id"],
                    election_name=r["election_name"],
                    start_date=r["start_date"],
                    end_date=r["end_date"],
                    description=r["description"]
                ))
            return result
        finally:
            await conn.close()

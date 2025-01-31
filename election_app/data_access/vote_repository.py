from typing import Optional
import asyncpg

from election_app.domain.repositories.ivote_repository import IVoteRepository
from election_app.data_access.database import get_connection


class PostgresVoteRepository(IVoteRepository):
    async def record_vote(self, voter_id: int, candidate_id: int, election_id: int) -> int:
        """
        Создаёт запись в таблице vote, возвращает vote_id.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                INSERT INTO elections.vote (voter_id, candidate_id, election_id)
                VALUES ($1, $2, $3)
                RETURNING vote_id
                """,
                voter_id, candidate_id, election_id
            )
            # Если row не None, возвращаем поле "vote_id"
            return row["vote_id"] if row else 0
        finally:
            await conn.close()

    async def has_already_voted(self, voter_id: int, election_id: int) -> bool:
        """
        Проверяет, голосовал ли уже избиратель на данных выборах (True/False).
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                SELECT 1
                FROM elections.vote
                WHERE voter_id = $1 AND election_id = $2
                LIMIT 1
                """,
                voter_id, election_id
            )
            return row is not None
        finally:
            await conn.close()

    async def count_votes_by_election(self, election_id: int) -> dict:
        """
        Возвращает сводку по голосам для указанных выборов
        в формате {candidate_id: количество_голосов, ...}.
        """
        conn = await get_connection()
        try:
            rows = await conn.fetch(
                """
                SELECT candidate_id, COUNT(*) AS cnt
                FROM elections.vote
                WHERE election_id = $1
                GROUP BY candidate_id
                """,
                election_id
            )
            result = {}
            for row in rows:
                cand_id = row["candidate_id"]
                count = row["cnt"]
                result[cand_id] = count
            return result
        finally:
            await conn.close()

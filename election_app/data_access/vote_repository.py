from typing import Optional, List
import asyncpg
from datetime import datetime

from election_app.domain.repositories.ivote_repository import IVoteRepository
from election_app.domain.entities.vote import Vote
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

    async def find_vote_by_id(self, vote_id: int) -> Optional[Vote]:
        """
        Ищет голос по vote_id, возвращает объект Vote или None, если не найден.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                SELECT vote_id, voter_id, candidate_id, election_id, vote_date
                FROM elections.vote
                WHERE vote_id = $1
                """,
                vote_id
            )
            if row:
                return Vote(
                    vote_id=row["vote_id"],
                    voter_id=row["voter_id"],
                    candidate_id=row["candidate_id"],
                    election_id=row["election_id"],
                    vote_date=row["vote_date"]
                )
            return None
        finally:
            await conn.close()

    async def list_votes_by_election(self, electionId: int) -> List[Vote]:
        """
        Возвращает список голосов (Vote) для конкретных выборов (electionId).
        """
        conn = await get_connection()
        try:
            rows = await conn.fetch(
                """
                SELECT vote_id, voter_id, candidate_id, election_id, vote_date
                FROM elections.vote
                WHERE election_id = $1
                ORDER BY vote_date, vote_id
                """,
                electionId
            )
            result = []
            for r in rows:
                result.append(Vote(
                    vote_id=r["vote_id"],
                    voter_id=r["voter_id"],
                    candidate_id=r["candidate_id"],
                    election_id=r["election_id"],
                    vote_date=r["vote_date"]
                ))
            return result
        finally:
            await conn.close()

    async def list_all_votes(self) -> List[Vote]:
        """
        Возвращает список всех голосов в таблице elections.vote.
        """
        conn = await get_connection()
        try:
            rows = await conn.fetch(
                """
                SELECT vote_id, voter_id, candidate_id, election_id, vote_date
                FROM elections.vote
                ORDER BY vote_date, vote_id
                """
            )
            result = []
            for r in rows:
                result.append(Vote(
                    vote_id=r["vote_id"],
                    voter_id=r["voter_id"],
                    candidate_id=r["candidate_id"],
                    election_id=r["election_id"],
                    vote_date=r["vote_date"]
                ))
            return result
        finally:
            await conn.close()

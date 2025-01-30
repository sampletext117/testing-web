from typing import Optional
import psycopg2

from election_app.domain.repositories.ivote_repository import IVoteRepository
from election_app.domain.entities.vote import Vote
from election_app.data_access.database import get_connection


class PostgresVoteRepository(IVoteRepository):
    def record_vote(self, voter_id: int, candidate_id: int, election_id: int) -> int:
        """
        Создаёт запись в таблице vote, возвращает vote_id.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO elections.vote (voter_id, candidate_id, election_id)
                        VALUES (%s, %s, %s)
                        RETURNING vote_id
                        """,
                        (voter_id, candidate_id, election_id)
                    )
                    new_id = cur.fetchone()[0]
            return new_id
        finally:
            conn.close()

    def has_already_voted(self, voter_id: int, election_id: int) -> bool:
        """
        Проверяет, голосовал ли уже избиратель на данных выборах.
        Возвращает True/False.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT 1
                        FROM elections.vote
                        WHERE voter_id = %s AND election_id = %s
                        LIMIT 1
                        """,
                        (voter_id, election_id)
                    )
                    row = cur.fetchone()
                    return row is not None
        finally:
            conn.close()

    def count_votes_by_election(self, election_id: int) -> dict:
        """
        Возвращает сводку по голосам для указанных выборов
        в формате {candidate_id: количество_голосов, ...}.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT candidate_id, COUNT(*) as cnt
                        FROM elections.vote
                        WHERE election_id = %s
                        GROUP BY candidate_id
                        """,
                        (election_id,)
                    )
                    rows = cur.fetchall()
                    result = {}
                    for row in rows:
                        cand_id = row[0]
                        count = row[1]
                        result[cand_id] = count
                    return result
        finally:
            conn.close()

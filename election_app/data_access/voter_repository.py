from typing import Optional
from datetime import date
import psycopg2

from election_app.domain.repositories.ivoter_repository import IVoterRepository
from election_app.domain.entities.voter import Voter
from election_app.data_access.database import get_connection


class PostgresVoterRepository(IVoterRepository):
    def create_voter(
        self,
        full_name: str,
        birth_date: date,
        passport_id: int
    ) -> int:
        """
        Создаёт нового избирателя, возвращает voter_id.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO elections.voter (full_name, birth_date, passport_id)
                        VALUES (%s, %s, %s)
                        RETURNING voter_id
                        """,
                        (full_name, birth_date, passport_id)
                    )
                    new_id = cur.fetchone()[0]
            return new_id
        finally:
            conn.close()

    def find_voter_by_id(self, voter_id: int) -> Optional[Voter]:
        """
        Возвращает избирателя по его ID или None, если не найден.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT voter_id, full_name, birth_date, passport_id, created_at
                        FROM elections.voter
                        WHERE voter_id = %s
                        """,
                        (voter_id,)
                    )
                    row = cur.fetchone()
                    if row:
                        return Voter(
                            voter_id=row[0],
                            full_name=row[1],
                            birth_date=row[2],
                            passport_id=row[3],
                            created_at=row[4]
                        )
                    return None
        finally:
            conn.close()

    def find_by_passport_id(self, passport_id: int) -> Optional[Voter]:
        """
        Возвращает избирателя по passport_id, или None, если не найден.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT voter_id, full_name, birth_date, passport_id, created_at
                        FROM elections.voter
                        WHERE passport_id = %s
                        """,
                        (passport_id,)
                    )
                    row = cur.fetchone()
                    if row:
                        return Voter(
                            voter_id=row[0],
                            full_name=row[1],
                            birth_date=row[2],
                            passport_id=row[3],
                            created_at=row[4]
                        )
                    return None
        finally:
            conn.close()

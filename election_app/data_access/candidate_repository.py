from typing import Optional
from datetime import date
import psycopg2

from election_app.domain.repositories.icandidate_repository import ICandidateRepository
from election_app.domain.entities.candidate import Candidate
from election_app.data_access.database import get_connection


class PostgresCandidateRepository(ICandidateRepository):
    def create_candidate(
        self,
        full_name: str,
        birth_date: date,
        passport_id: int
    ) -> int:
        """
        Создаёт запись о кандидате, возвращает candidate_id.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO elections.candidate (full_name, birth_date, passport_id)
                        VALUES (%s, %s, %s)
                        RETURNING candidate_id
                        """,
                        (full_name, birth_date, passport_id)
                    )
                    new_id = cur.fetchone()[0]
            return new_id
        finally:
            conn.close()

    def update_candidate_program_and_account(
        self,
        candidate_id: int,
        campaign_program_id: int,
        account_id: int
    ) -> None:
        """
        Обновляет campaign_program_id и account_id у кандидата.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE elections.candidate
                        SET campaign_program_id = %s,
                            account_id = %s
                        WHERE candidate_id = %s
                        """,
                        (campaign_program_id, account_id, candidate_id)
                    )
        finally:
            conn.close()

    def find_candidate_by_id(self, candidate_id: int) -> Optional[Candidate]:
        """
        Находит кандидата по ID, или None, если не найден.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT candidate_id, full_name, birth_date, passport_id, 
                               campaign_program_id, account_id, created_at
                        FROM elections.candidate
                        WHERE candidate_id = %s
                        """,
                        (candidate_id,)
                    )
                    row = cur.fetchone()
                    if row:
                        return Candidate(
                            candidate_id=row[0],
                            full_name=row[1],
                            birth_date=row[2],
                            passport_id=row[3],
                            campaign_program_id=row[4],
                            account_id=row[5],
                            created_at=row[6]
                        )
                    return None
        finally:
            conn.close()

    def find_by_passport_id(self, passport_id: int) -> Optional[Candidate]:
        """
        Находит кандидата по passport_id, или None.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT candidate_id, full_name, birth_date, passport_id,
                               campaign_program_id, account_id, created_at
                        FROM elections.candidate
                        WHERE passport_id = %s
                        """,
                        (passport_id,)
                    )
                    row = cur.fetchone()
                    if row:
                        return Candidate(
                            candidate_id=row[0],
                            full_name=row[1],
                            birth_date=row[2],
                            passport_id=row[3],
                            campaign_program_id=row[4],
                            account_id=row[5],
                            created_at=row[6]
                        )
                    return None
        finally:
            conn.close()

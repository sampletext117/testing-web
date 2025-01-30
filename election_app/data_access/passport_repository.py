from typing import Optional
from datetime import date
import psycopg2

from election_app.domain.repositories.ipassport_repository import IPassportRepository
from election_app.domain.entities.passport import Passport
from election_app.data_access.database import get_connection


class PostgresPassportRepository(IPassportRepository):
    def create_passport(
        self,
        passport_number: str,
        issued_by: Optional[str],
        issue_date: Optional[date],
        country: str
    ) -> int:
        """
        Создаёт запись в таблице passport и возвращает passport_id.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO elections.passport (passport_number, issued_by, issue_date, country)
                        VALUES (%s, %s, %s, %s)
                        RETURNING passport_id
                        """,
                        (passport_number, issued_by, issue_date, country)
                    )
                    new_id = cur.fetchone()[0]
            return new_id
        finally:
            conn.close()

    def find_by_number(self, passport_number: str) -> Optional[Passport]:
        """
        Ищет паспорт по номеру.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT passport_id, passport_number, issued_by, issue_date, country
                        FROM elections.passport
                        WHERE passport_number = %s
                        """,
                        (passport_number,)
                    )
                    row = cur.fetchone()
                    if row:
                        return Passport(
                            passport_id=row[0],
                            passport_number=row[1],
                            issued_by=row[2],
                            issue_date=row[3],
                            country=row[4]
                        )
                    return None
        finally:
            conn.close()

    def find_by_id(self, passport_id: int) -> Optional[Passport]:
        """
        Ищет паспорт по ID.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT passport_id, passport_number, issued_by, issue_date, country
                        FROM elections.passport
                        WHERE passport_id = %s
                        """,
                        (passport_id,)
                    )
                    row = cur.fetchone()
                    if row:
                        return Passport(
                            passport_id=row[0],
                            passport_number=row[1],
                            issued_by=row[2],
                            issue_date=row[3],
                            country=row[4]
                        )
                    return None
        finally:
            conn.close()

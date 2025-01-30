from typing import Optional
from datetime import date
import psycopg2

from election_app.domain.repositories.ielection_repository import IElectionRepository
from election_app.domain.entities.election import Election
from election_app.data_access.database import get_connection


class PostgresElectionRepository(IElectionRepository):
    def create_election(
        self,
        election_name: str,
        start_date: date,
        end_date: date,
        description: str
    ) -> int:
        """
        Создаёт запись о выборах, возвращает election_id.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO elections.election (election_name, start_date, end_date, description)
                        VALUES (%s, %s, %s, %s)
                        RETURNING election_id
                        """,
                        (election_name, start_date, end_date, description)
                    )
                    new_id = cur.fetchone()[0]
            return new_id
        finally:
            conn.close()

    def find_election_by_id(self, election_id: int) -> Optional[Election]:
        """
        Находит выборы по ID.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT election_id, election_name, start_date, end_date, description
                        FROM elections.election
                        WHERE election_id = %s
                        """,
                        (election_id,)
                    )
                    row = cur.fetchone()
                    if row:
                        return Election(
                            election_id=row[0],
                            election_name=row[1],
                            start_date=row[2],
                            end_date=row[3],
                            description=row[4]
                        )
                    return None
        finally:
            conn.close()

    def update_election_status(self, election_id: int, new_status: str) -> None:
        """
        Если в таблице elections.election есть поле status, можно обновить его.
        Если поля status нет, можно убрать этот метод или оставить заглушку.
        """
        # Предположим, что в таблице есть колонка status (VARCHAR).
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE elections.election
                        SET description = CONCAT(description, ' [STATUS:', %s, ']')
                        WHERE election_id = %s
                        """,
                        (new_status, election_id)
                    )
        finally:
            conn.close()
